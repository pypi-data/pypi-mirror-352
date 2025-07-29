from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional, cast
from datetime import datetime
import logging
import uuid
import os

import dspy
from mindbank_poc.core.agent.react_agent import ReActAgent, SearchDocsTool, EchoTool
from mindbank_poc.core.retrieval.service import get_retrieval_service
from mindbank_poc.core.agent.retrieval_wrapper import RetrievalWrapper
from mindbank_poc.core.agent.summarizer import generate_title

# Import the provider service
from mindbank_poc.core.services.provider_service import get_provider_service
from mindbank_poc.core.models.provider import ProviderModel
from mindbank_poc.core.common.types import ProviderType
from mindbank_poc.core.providers.selector import ProviderSelector

logger = logging.getLogger(__name__)

# --- Provider Instances Definition ---
# Define instances at the module level to ensure they are singletons
openai_provider_instance = None
offline_fallback_provider_instance = None

def select_llm_chat_provider(
    archetype: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Select the best LLMChatProvider instance for the given context using ProviderSelector.
    Falls back to offline provider if needed.
    """
    from mindbank_poc.core.providers.selector import ProviderSelector
    
    # Get provider service
    provider_service = get_provider_service()
    
    # Get providers of LLM_CHAT type using the enum 
    all_providers = provider_service.get_all_providers()
    providers = [p for p in all_providers if p.provider_type == ProviderType.LLM_CHAT]
    
    # Convert to format expected by ProviderSelector
    provider_infos = [p.dict(exclude={"instance"}) for p in providers]
    provider_map = {p.id: p for p in providers}

    selected_info = ProviderSelector.select_provider(
        provider_infos,
        ProviderType.LLM_CHAT.value,
        archetype=archetype,
        source=source,
        metadata=metadata
    )
    if not selected_info:
        # Fallback to offline
        for p in providers:
            if p.provider_type == ProviderType.LLM_CHAT and "offline" in p.id:
                return p
        return None
    return provider_map.get(selected_info["id"])

class Message:
    """
    Minimal message model for LLM chat context.
    """
    def __init__(self, message_id: str, chat_id: str, author: str, content: str, timestamp: datetime, metadata: Dict[str, Any] = None):
        self.message_id = message_id
        self.chat_id = chat_id
        self.author = author
        self.content = content
        self.timestamp = timestamp
        self.metadata = metadata or {}

# ---------------------------------------------------------------------------
#  Base abstract provider
# ---------------------------------------------------------------------------

class LLMChatProvider(ABC):
    """
    Abstract base class for LLM chat providers.
    """

    # Concrete subclasses should list provider IDs they implement (from providers.json)
    SUPPORTED_IDS: List[str] = []

    @abstractmethod
    async def generate_chat_response(
        self,
        messages: List[Message],
        config: Dict[str, Any]
    ) -> Message:
        """
        Generate a chat response given the message history and config.
        """
        pass

class OpenAILLMChatProvider(LLMChatProvider):
    """
    OpenAI-based LLM chat provider (gpt-3.5-turbo, gpt-4, etc).
    """

    SUPPORTED_IDS = ["openai-llm-chat"]

    async def generate_chat_response(
        self,
        messages: List[Message],
        config: Dict[str, Any]
    ) -> Message:
        """
        Call ReActAgent to generate a chat response using OpenAI.
        """
        logger.info(f"OpenAILLMChatProvider (ReAct) generating response with config: {config}")

        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        
        # Determine the model name for dspy.OpenAI
        # Priority: 1. Explicit model in request, 2. First model from provider's current_config, 3. Default
        model_name_to_use = config.get("model") # From SendMessageRequest.model or chat.metadata.selectedModelId
        
        if not model_name_to_use:
            provider_service = get_provider_service()
            provider_model = provider_service.get_provider("openai-llm-chat") 
            if provider_model and provider_model.current_config.get("model"):
                model_name_to_use = provider_model.current_config.get("model")
            elif provider_model and isinstance(provider_model.current_config.get("models"), list) and provider_model.current_config["models"]:
                model_name_to_use = provider_model.current_config["models"][0] 
            else:
                model_name_to_use = "gpt-3.5-turbo" 

        logger.info(f"OpenAILLMChatProvider: Using OpenAI model for agent: {model_name_to_use}")

        if not api_key:
            logger.error("OpenAI API key not found in config or environment for OpenAILLMChatProvider.")
            return Message(
                message_id=f"openai-error-{uuid.uuid4()}",
                chat_id=messages[-1].chat_id if messages else "unknown-chat",
                author="openai-react-error",
                content="OpenAI API key is not configured. Cannot generate response.",
                timestamp=datetime.utcnow(),
                metadata={"provider": "openai-react", "error": "API key missing"}
            )
        
        try:
            current_llm = dspy.LM(model=f"openai/{model_name_to_use}", api_key=api_key, max_tokens=config.get("max_tokens", 1500))
            dspy.settings.configure(lm=current_llm)
            logger.info(f"DSPy LLM configured with {model_name_to_use} (via dspy.LM) for OpenAILLMChatProvider.")
        except Exception as e:
            logger.error(f"Failed to configure DSPy LLM for OpenAILLMChatProvider: {e}", exc_info=True)
            return Message(
                message_id=f"openai-dspy-config-error-{uuid.uuid4()}",
                chat_id=messages[-1].chat_id if messages else "unknown-chat",
                author="openai-react-error",
                content=f"Failed to configure DSPy LLM: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={"provider": "openai-react", "error": "DSPy LLM config failed"}
            )

        chat_history_for_agent: List[Dict[str, Any]] = []
        for msg in messages[:-1]:
            role = "user" if msg.author == "user" else "assistant"
            chat_history_for_agent.append({"role": role, "content": msg.content})
        
        last_user_message_content = messages[-1].content if messages and messages[-1].author == "user" else ""
        if not last_user_message_content:
             logger.warning("OpenAILLMChatProvider: No last user message content found for agent input.")

        active_sources = config.get("sources")
        pre_fetched_context_str = "No pre-fetched context available."

        if active_sources and last_user_message_content: # Only search if there's a query and sources
            logger.info(f"OpenAILLMChatProvider: Active sources: {active_sources}. Performing initial retrieval.")
            try:
                retrieval_service = await get_retrieval_service()
                retrieval_wrapper = RetrievalWrapper(retrieval_service)

                # Fetch top-30 results filtered by provided connector IDs (active_sources)
                filters_for_wrapper = {"source_ids": active_sources} if active_sources else None
                print(f"OpenAILLMChatProvider: Filters for wrapper: {filters_for_wrapper}")
                # Use the new search_context method that returns both raw results and summarized context
                raw_results, summarized_context = await retrieval_wrapper.search_context(
                    query=last_user_message_content,
                    filters=filters_for_wrapper,
                    limit=30,
                    max_total_chars=8000,  # Allow more tokens for context
                    use_summarizer=True    # Use map-reduce summarization
                )
                print(f"OpenAILLMChatProvider: Raw results: {raw_results}")
                if raw_results and summarized_context:
                    pre_fetched_context_str = summarized_context
                    logger.info(
                        f"OpenAILLMChatProvider: Pre-fetched and summarized context chars={len(pre_fetched_context_str)} from {len(raw_results)} raw docs"
                    )
                else:
                    pre_fetched_context_str = "Initial search returned no relevant documents."
            except Exception as e:
                logger.error(f"OpenAILLMChatProvider: Error during initial retrieval: {e}", exc_info=True)
                pre_fetched_context_str = "Error occurred during context retrieval."
        elif not active_sources:
            logger.info("OpenAILLMChatProvider: No active sources, skipping initial retrieval.")
            # pre_fetched_context_str remains "No pre-fetched context available."
        elif not last_user_message_content:
            logger.info("OpenAILLMChatProvider: No user query for initial retrieval.")
            pre_fetched_context_str = "No user query was provided for initial context retrieval."

        # Now, decide whether to use ReAct or a simpler Predict/ChainOfThought
        # The logic is: if active_sources, we *could* use ReAct with tools.
        # If no active_sources, we use direct LLM.
        
        use_react_agent = bool(active_sources) 
        # Even if pre_fetched_context_str is empty/error, if sources were active, we might still want ReAct to try its tools.

        logger.info(f"OpenAILLMChatProvider: Use ReAct: {use_react_agent} (based on active_sources: {active_sources})")

        if use_react_agent:
            agent_tools = [SearchDocsTool, EchoTool]
            react_agent = ReActAgent(tools=agent_tools, max_steps=3)
            try:
                agent_response_dict = await react_agent.run(
                    user_input=last_user_message_content,
                    chat_history=chat_history_for_agent,
                    pre_fetched_context=pre_fetched_context_str 
                )
                final_answer = agent_response_dict.get("answer", "Sorry, I could not find an answer using ReAct.")
                trace = agent_response_dict.get("trace", [])
            except Exception as e:
                logger.error(f"Error during ReAct agent execution in OpenAILLMChatProvider: {e}", exc_info=True)
                final_answer = "An error occurred while processing your request with the ReAct agent."
                trace = [{"error": str(e), "agent_type": "ReAct"}]
        else: # No active_sources, use direct LLM call
            logger.info("No active sources, using dspy.Predict for direct LLM response.")
            try:
                class DirectAnswerWithHistory(dspy.Signature):
                    """Answer the question directly, based on chat history and the user's question."""
                    # pre_fetched_context: str = dspy.InputField(desc="Pre-fetched context from knowledge base. May be empty or indicate no results.")
                    chat_history_str: str = dspy.InputField(desc="Formatted chat history.")
                    user_question: str = dspy.InputField(desc="The user's current question.")
                    answer: str = dspy.OutputField(desc="The AI's direct answer.")
                
                history_str = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in chat_history_for_agent])
                
                predictor = dspy.Predict(DirectAnswerWithHistory)
                response = await predictor.acall(
                    # pre_fetched_context=pre_fetched_context_str, # Pass even if it's "No context..."
                    chat_history_str=history_str,
                    user_question=last_user_message_content
                )
                final_answer = response.answer
                # Include pre_fetched_context in trace for direct calls too, for transparency
                trace = [{    "info": "Direct LLM call (Predict) used as no sources were specified.", 
                            "pre_fetched_context_summary": pre_fetched_context_str[:200] + ("..." if len(pre_fetched_context_str) > 200 else "")
                        }]
            except Exception as e:
                logger.error(f"Error during dspy.Predict execution (no sources): {e}", exc_info=True)
                final_answer = "An error occurred while processing your request with the AI."
                trace = [{"error": str(e), "agent_type": "Predict_Direct"}]

        return Message(
            message_id=f"openai-response-{uuid.uuid4()}",
            chat_id=messages[-1].chat_id if messages else "unknown-chat",
            author="openai-react",
            content=final_answer,
            timestamp=datetime.utcnow(),
            metadata={"provider": "openai-react", "model_used": model_name_to_use, "trace": trace}
        )

# ---------------------------------------------------------------------------
#  Offline / fallback provider
# ---------------------------------------------------------------------------

class OfflineFallbackLLMChatProvider(LLMChatProvider):
    """
    Offline fallback LLM chat provider.
    Returns a simple echo or retrieval-based response based on mode.
    Modes: "echo", "semantic-search", "fulltext-search"
    """

    # This provider is used when online providers fail or when explicitly selected.
    SUPPORTED_IDS = ["offline-fallback-llm-chat"]

    async def generate_chat_response(
        self,
        messages: List[Message],
        config: Dict[str, Any]
    ) -> Message:
        """
        Return a fallback response based on the configured mode.
        """
        mode = config.get("mode", "echo") # Default to echo mode
        logger.info(f"OfflineFallbackLLMChatProvider generating response with config: {config}, mode: {mode}")
        
        last_user_msg = next((m for m in reversed(messages) if m.author == "user"), None)
        
        content = f"(Offline fallback: No user message found for mode '{mode}')"
        metadata = {"provider": "offline-fallback", "mode": mode}

        if last_user_msg:
            if mode == "echo":
                content = f"Echo: {last_user_msg.content}"
            elif mode in ["semantic-search", "fulltext-search"]:
                try:
                    retrieval_service = await get_retrieval_service()
                    wrapper = RetrievalWrapper(retrieval_service)
                    
                    raw_results = []
                    summarized_context = None
                    
                    if mode == "semantic-search":
                        # Use default search_mode ('hybrid' or 'semantic')
                        raw_results, summarized_context = await wrapper.search_context(
                            query=last_user_msg.content, 
                            limit=5,
                            use_summarizer=False  # Just use simple formatting for offline mode
                        )
                    elif mode == "fulltext-search":
                        # Explicitly set search_mode for full-text
                        raw_results, summarized_context = await wrapper.search_context(
                            query=last_user_msg.content,
                            filters={"search_mode": "fulltext"},
                            limit=5,
                            use_summarizer=False
                        )

                    if raw_results:
                        # Format results in a markdown-friendly way
                        results_formatted = []
                        for i, result in enumerate(raw_results[:5], 1):  # Limit to 5 results
                            # Extract first 200 chars for preview
                            preview = result[:200] + ("..." if len(result) > 200 else "")
                            results_formatted.append(f"**Result {i}**\n\n{preview}\n")
                        
                        formatted_results = "\n---\n\n".join(results_formatted)
                        content = f"# Search Results ({mode})\n\nQuery: \"{last_user_msg.content}\"\n\n{formatted_results}"
                        
                        # Add suggestion for follow-up
                        content += "\n\n**Note**: You can ask follow-up questions about these results."
                    else:
                        content = f"Sorry, I couldn't find anything relevant to '{last_user_msg.content}' using {mode}."
                    
                    metadata["search_query"] = last_user_msg.content
                    metadata["results_count"] = len(raw_results)
                except Exception as e:
                    logger.error(f"Error during offline {mode} retrieval: {e}", exc_info=True)
                    content = f"An error occurred while trying to perform {mode} for your query: {str(e)}"
                    metadata["error"] = str(e)
            else:
                content = f"Unknown mode '{mode}' for offline fallback. Defaulting to echo: {last_user_msg.content}"
                metadata["error"] = f"Unknown mode: {mode}"
        
        return Message(
            message_id=f"offline-fallback-response-{uuid.uuid4()}",
            chat_id=messages[-1].chat_id if messages else "unknown-chat",
            author="offline-fallback",
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )

# Initialize instances after class definitions
openai_provider_instance = OpenAILLMChatProvider()
offline_fallback_provider_instance = OfflineFallbackLLMChatProvider()

# Map of provider IDs to their singleton instances
_LLM_PROVIDER_INSTANCES: Dict[str, LLMChatProvider] = {}

def _create_llm_provider_instance(provider_model: ProviderModel) -> LLMChatProvider:
    """Instantiate concrete LLMChatProvider based on SUPPORTED_IDS registry.

    The mechanism avoids string-matching эвристик: каждый класс сам объявляет,
    какие provider_id он поддерживает через атрибут SUPPORTED_IDS.
    При добавлении нового провайдера достаточно создать класс-наследник и
    указать нужные ID в SUPPORTED_IDS – основная фабрика ничего не меняет.
    """

    for subclass in LLMChatProvider.__subclasses__():
        if provider_model.id in getattr(subclass, "SUPPORTED_IDS", []):
            logger.debug(f"Matched provider_id '{provider_model.id}' → {subclass.__name__}")
            return subclass()  # type: ignore[call-arg]

    # Fallback: offline provider
    logger.warning(
        f"No LLMChatProvider subclass declared support for id '{provider_model.id}'. "
        "Using OfflineFallbackLLMChatProvider."
    )
    return OfflineFallbackLLMChatProvider()

def _build_llm_provider_instances():
    """Builds the _LLM_PROVIDER_INSTANCES registry from ProviderService models.
    It is safe to call multiple times – results are cached in-memory.
    """
    global _LLM_PROVIDER_INSTANCES

    if _LLM_PROVIDER_INSTANCES:
        # Already built – no-op
        return

    provider_service = get_provider_service()
    llm_provider_models = provider_service.get_providers_by_type(ProviderType.LLM_CHAT)

    if not llm_provider_models:
        # Ensure we always have at least offline fallback available
        logger.warning("No LLM_CHAT providers registered in ProviderService – using OfflineFallback only.")
        _LLM_PROVIDER_INSTANCES["offline-fallback-llm-chat"] = OfflineFallbackLLMChatProvider()
        return

    for p_model in llm_provider_models:
        try:
            instance = _create_llm_provider_instance(p_model)
            _LLM_PROVIDER_INSTANCES[p_model.id] = instance
        except Exception as e:
            logger.error(f"Could not create provider instance for {p_model.id}: {e}", exc_info=True)

    # Always guarantee offline fallback exists in the registry
    if "offline-fallback-llm-chat" not in _LLM_PROVIDER_INSTANCES:
        _LLM_PROVIDER_INSTANCES["offline-fallback-llm-chat"] = OfflineFallbackLLMChatProvider()

# Build provider instances on module import
_build_llm_provider_instances()

def get_llm_chat_provider_instance_by_id(provider_id: str) -> Optional[LLMChatProvider]:
    """Gets a specific LLM provider instance by its ID (after ensuring registry is built)."""
    _build_llm_provider_instances()
    return _LLM_PROVIDER_INSTANCES.get(provider_id)

def get_llm_chat_providers_info_and_instance() -> List[Dict[str, Any]]:
    """Return provider info and instances for every LLM_CHAT provider registered."""
    _build_llm_provider_instances()
    provider_service = get_provider_service()
    provider_models = provider_service.get_providers_by_type(ProviderType.LLM_CHAT)

    result: List[Dict[str, Any]] = []
    for p_model in provider_models:
        instance = _LLM_PROVIDER_INSTANCES.get(p_model.id)
        if not instance:
            # This should not happen, but build defensively
            instance = _create_llm_provider_instance(p_model)
            _LLM_PROVIDER_INSTANCES[p_model.id] = instance
        result.append({
            "info": p_model.dict(),
            "instance": instance,
        })
    return result

def select_llm_chat_provider_instance(
    archetype: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[LLMChatProvider]:
    """Selects an LLMChatProvider instance using ProviderSelector, then fetches it from the registry."""
    _build_llm_provider_instances()
    provider_service = get_provider_service()
    all_provider_models = provider_service.get_providers_by_type(ProviderType.LLM_CHAT)

    if not all_provider_models:
        logger.warning("No LLM chat provider models registered – returning offline fallback instance.")
        return _LLM_PROVIDER_INSTANCES.get("offline-fallback-llm-chat")

    provider_model_dicts = [p.dict() for p in all_provider_models]
    selected_info = ProviderSelector.select_provider(
        provider_model_dicts,
        ProviderType.LLM_CHAT.value,
        archetype=archetype,
        source=source,
        metadata=metadata
    )

    if selected_info and selected_info.get("id"):
        selected_instance = _LLM_PROVIDER_INSTANCES.get(selected_info["id"])
        if selected_instance:
            logger.info(f"ProviderSelector selected LLM provider: {selected_info['id']}")
            return selected_instance
        else:
            logger.warning(f"Instance for selected provider id '{selected_info['id']}' not found – falling back.")

    # Fallback to offline
    return _LLM_PROVIDER_INSTANCES.get("offline-fallback-llm-chat")
