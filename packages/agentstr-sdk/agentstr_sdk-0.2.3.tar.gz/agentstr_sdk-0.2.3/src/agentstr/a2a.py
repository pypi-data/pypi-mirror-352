import json
from typing import Any, Tuple, Optional
from pydantic import BaseModel
from agentstr.logger import get_logger

logger = get_logger(__name__)


class Skill(BaseModel):
    """Represents a specific capability or service that an agent can perform.

    A Skill defines a discrete unit of functionality that an agent can provide to other
    agents or users. Skills are the building blocks of an agent's service offerings and
    can be priced individually to create a market for agent capabilities.

    Attributes:
        name (str): A unique identifier for the skill that should be descriptive and
            concise. This name is used for referencing the skill in agent interactions.
        description (str): A detailed explanation of what the skill does, including:
            - The specific functionality provided
            - How to use the skill
            - Any limitations or prerequisites
            - Expected inputs and outputs
        satoshis (int, optional): The price in satoshis for using this skill. This allows
            agents to:
            - Set different prices for different capabilities
            - Create premium services
            - Implement usage-based pricing
            If None, the skill is either free or priced at the agent's base rate.
    """

    name: str
    description: str
    satoshis: int | None = None


class AgentCard(BaseModel):
    """Represents an agent's profile and capabilities in the Nostr network.

    An AgentCard is the public identity and capabilities card for an agent in the Nostr
    network. It contains essential information about the agent's services, pricing,
    and communication endpoints.

    Attributes:
        name (str): A human-readable name for the agent. This is the agent's display name.
        description (str): A detailed description of the agent's purpose, capabilities,
            and intended use cases.
        skills (list[Skill]): A list of specific skills or services that the agent can perform.
            Each skill is represented by a Skill model.
        satoshis (int, optional): The base price in satoshis for interacting with the agent.
            If None, the agent may have free services or use skill-specific pricing.
        nostr_pubkey (str): The agent's Nostr public key. This is used for identifying
            and communicating with the agent on the Nostr network.
        nostr_relays (list[str]): A list of Nostr relay URLs that the agent uses for
            communication. These relays are where the agent publishes and receives messages.
    """

    name: str
    description: str
    skills: list[Skill] = []
    satoshis: int | None = None
    nostr_pubkey: str
    nostr_relays: list[str] = []


class ChatInput(BaseModel):
    """Represents input data for an agent-to-agent chat interaction.

    Attributes:
        messages (list[str]): A list of messages in the conversation.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        extra_inputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """

    messages: list[str]
    thread_id: str | None = None
    extra_inputs: dict[str, Any] = {}


class RouterResponse(BaseModel):
    """Response model for the agent router.
    
    Attributes:
        can_handle: Whether the agent can handle the request
        cost_sats: Total cost in satoshis (0 if free or not applicable)
        user_message: Friendly message to show the user about the action to be taken
        skills_used: List of skills that would be used, if any
    """
    can_handle: bool
    cost_sats: int = 0
    user_message: str = ""
    skills_used: list[str] = []


CHAT_HISTORY = {}  # Thread id -> [str]


async def agent_router(user_message: str, agent_card: AgentCard, llm_callable: callable, thread_id: str | None = None) -> Tuple[bool, int, Optional[str]]:
    """Determine if an agent can handle a user's request and calculate the cost.
    
    This function uses an LLM to analyze whether the agent's skills match the user's request
    and returns the cost in satoshis if the agent can handle it.
    
    Args:
        user_message: The user's request message.
        agent_card: The AgentCard containing the agent's skills and pricing.
        llm_callable: A callable that takes a prompt and returns an LLM response.
        
    Returns:
        Tuple[bool, int, Optional[str]]: 
            - bool: Whether the agent can handle the request
            - int: Cost in satoshis (0 if free or not applicable)
            - Optional[str]: Explanation or reasoning for the decision
    """

    # check history
    if thread_id and thread_id in CHAT_HISTORY:
        user_message = f"{CHAT_HISTORY[thread_id]}\n\n{user_message}"
    if thread_id:
        CHAT_HISTORY[thread_id] = user_message

    logger.debug(f"Agent router: {user_message}")
    logger.debug(f"Agent card: {agent_card.model_dump()}")

    # Prepare the prompt for the LLM
    prompt = f"""You are an agent router that determines if an agent can handle a user's request.

Agent Information:
Name: {agent_card.name}
Description: {agent_card.description}

Skills:"""
    
    for skill in agent_card.skills:
        prompt += f"\n- {skill.name}: {skill.description}"
    
    prompt += f"\n\nUser Request History: \n\n{user_message}\n\n"
    prompt += """
Analyze if the agent can handle this request based on their skills and description and chat history.
Consider both the agent's capabilities and whether the request matches their purpose.

The agent may need to use multiple skills to handle the request. If so, include all
relevant skills.

The user_message should be a friendly, conversational message that:
- Confirms the action to be taken
- Explains what will be done in simple terms
- Asks for confirmation to proceed
- Is concise (1-2 sentences max)

Respond with a JSON object with these fields:
{
    "can_handle": boolean,    # Whether the agent can handle this request
    "user_message": string,   # Friendly message to ask the user if they want to proceed
    "skills_used": [string]   # Names of skills being used, if any
}
    """
    logger.debug(f'Prompt: {prompt}')
    try:
        # Get the LLM response
        response = await llm_callable(prompt)
        
        # Seek to first { and last }
        response = response[response.find('{'):response.rfind('}')+1]
        logger.debug(f'LLM response: {response}')

        # Parse the response
        try:
            result = json.loads(response.strip())
            can_handle = result.get('can_handle', False)
            user_message = result.get('user_message', '')
            
            # Get skills used
            skills_used = result.get('skills_used', [])
                
            # Calculate total cost based on skills used
            cost = 0
            if can_handle:
                # If specific skills are used, sum their costs
                if skills_used:
                    skill_cost = 0
                    for skill_name in skills_used:
                        for skill in agent_card.skills:
                            if skill.name.lower() == skill_name.lower() and skill.satoshis is not None:
                                skill_cost += skill.satoshis
                                break
                    # Only use skill-based pricing if at least one skill has a price
                    if skill_cost > 0:
                        cost = skill_cost
                # Add base price to skill-based pricing
                if agent_card.satoshis is not None:
                    cost += agent_card.satoshis
                
            logger.debug(f'Router response: {can_handle}, {cost}, {user_message}, {skills_used}')
            return can_handle, cost, user_message, skills_used
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f'Error parsing LLM response: {str(e)}')
            return False, 0, f"Error parsing LLM response: {str(e)}", []
            
    except Exception as e:
        logger.error(f'Error in agent routing: {str(e)}')
        return False, 0, f"Error in agent routing: {str(e)}", []
        

async def agent_router_v2(user_message: str, agent_card: AgentCard, llm_callable: callable, thread_id: str | None = None) -> RouterResponse:
    """Improved version of agent_router with better structured response.
    
    Args:
        user_message: The user's request message.
        agent_card: The AgentCard containing the agent's skills and pricing.
        llm_callable: A callable that takes a prompt and returns an LLM response.
        thread_id: The ID of the conversation thread. Defaults to None.
        
    Returns:
        RouterResponse: Contains the routing decision and details.
    """
    can_handle, cost, user_message, skills_used = await agent_router(user_message, agent_card, llm_callable, thread_id)
    
    return RouterResponse(
        can_handle=can_handle,
        cost_sats=cost,
        user_message=user_message,
        skills_used=skills_used
    )
