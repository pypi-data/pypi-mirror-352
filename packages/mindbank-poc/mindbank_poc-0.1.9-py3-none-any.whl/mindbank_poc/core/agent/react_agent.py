import dspy
from typing import List, Any, Dict, Optional, cast

from mindbank_poc.core.agent.dspy_signature import DspySignature
from mindbank_poc.core.agent.retrieval_wrapper import RetrievalWrapper
from mindbank_poc.core.retrieval.service import get_retrieval_service

# Define Tools (DspySignatures)

class SearchDocsSignature(dspy.Signature):
    """Searches documents for a given query and optional filters."""
    query: str = dspy.InputField(desc="Natural language query to search for in documents.")
    # filters_json: Optional[str] = dspy.InputField(default=None, desc="Optional JSON string of filters (e.g., {\"archetype\": \"email\"}).")
    # Simplification: using only query for now, filters can be added later if complex logic is needed for LLM to generate them
    relevant_context: List[str] = dspy.OutputField(desc="List of relevant text snippets from documents.")

async def search_docs_tool(query: str) -> List[str]:
    """Tool to search documents using RetrievalWrapper."""
    retrieval_service = await get_retrieval_service() # Corrected: await the async factory
    wrapper = RetrievalWrapper(retrieval_service)
    # For simplicity, not exposing filters to the LLM directly yet.
    # If filters are needed, the ReAct agent might need to be taught to generate a filter dict.
    # Or the DspySignature could take individual filter fields.
    results = await wrapper.search_context(query=query, limit=3) # Limit results to 3 for now
    return results

# It's better to define tools as instances of a class that dspy.Predict can use,
# or ensure the function can be directly used by dspy.react's `actions` parameter.
# For dspy.ReAct, we typically provide it with dspy.Tool subclasses or callables.

# Let's prepare the tools in a way dspy.ReAct expects, often as callables or dspy.Tool instances.
# We'll use DspySignature to wrap them for clarity and potential future use with dspy.Predict, 
# but for ReAct, the handler callable is key.

SearchDocsTool = DspySignature(
    name="SearchDocs",
    input_schema=cast(Dict[str, Any], {"query": str}), # Cast for type checker
    output_schema=cast(Dict[str, Any], {"relevant_context": List[str]}),
    handler=search_docs_tool, # type: ignore # dspy might expect specific type here, ignore for now
    description="Searches documents for a given query. Input is a single string 'query'."
)

class EchoSignature(dspy.Signature):
    """Echoes a fixed message, useful for testing agent's ability to select a tool."""
    # input_text: str = dspy.InputField(desc="Any input text, will be ignored.") # Not needed if it always says the same
    echo_response: str = dspy.OutputField(desc="A fixed echo response.")

async def echo_tool() -> str:
    return "I don't know the answer to that yet."

EchoTool = DspySignature(
    name="EchoTool",
    input_schema={}, # No specific input needed
    output_schema=cast(Dict[str, Any], {"echo_response": str}),
    handler=echo_tool, # type: ignore
    description="Responds with a standard message indicating it doesn't know the answer."
)


class ReActAgent:
    """
    Reasoning + Acting (ReAct) agent.
    Accepts user input, chat history, and a set of tools (DspySignature).
    Executes a reasoning loop to select and apply actions/tools.
    """

    def __init__(
        self,
        tools: List[DspySignature], # Expects our DspySignature wrappers
        max_steps: int = 3, # Reduced max_steps for initial PoC
        trace: bool = True,
        # llm: Optional[dspy.LanguageModel] = None, # LLM can be configured globally or passed
    ):
        # self.tools = {tool.name: tool for tool in tools} # dspy.ReAct takes a list of tools
        self.tool_definitions = tools # Keep the DspySignature instances
        # dspy.ReAct will use the .name and the handler from DspySignature
        # The dspy.Signature part (SearchDocsSignature) is for dspy.Predict/TypedPredictor primarily.
        # For ReAct, it needs callables or dspy.Tool instances.
        # We are providing callables via DspySignature.handler
        
        # Convert DspySignature handlers to a format ReAct might use directly if needed
        # This step might be redundant if ReAct can directly use DspySignature.handler with its name
        self.react_tools = []
        for ds_tool in tools:
            # dspy.ReAct can often take a list of dspy.Tool instances or callables directly
            # Let's assume for now it can use the DspySignature objects if they have a __call__ method pointing to handler,
            # or we directly pass the handlers with their descriptions.
            # Creating simple dspy.Tool instances for ReAct:
            # Note: dspy.Tool has specific requirements for its constructor. 
            # We might need to adapt DspySignature or create wrappers if direct use is problematic.
            # For now, we'll assume dspy.ReAct can use the DspySignature list directly if their handlers are correctly defined.
            # Or, more simply, dspy.ReAct can take a list of callables with descriptions.
            # The DspySignature class itself has a __call__ method.
            self.react_tools.append(ds_tool) 

        self.max_steps = max_steps
        self.trace_enabled = trace # Renamed to avoid conflict with dspy's trace
        self.reasoning_trace: List[Dict[str, Any]] = [] 

        # Configure LLM for DSPy - this should ideally be done globally or passed in
        # if llm:
        #     dspy.settings.configure(lm=llm)
        # elif not dspy.settings.lm:
        #     # Configure a default if none is set - this is crucial
        #     # Requires OPENAI_API_KEY to be in env
        #     try:
        #         default_llm = dspy.OpenAI(model='gpt-3.5-turbo-instruct', max_tokens=250)
        #         dspy.settings.configure(lm=default_llm)
        #         print("DSPy configured with default OpenAI LLM (gpt-3.5-turbo-instruct)")
        #     except Exception as e:
        #         print(f"Warning: Could not configure default DSPy LLM. Set OPENAI_API_KEY. Error: {e}")
        #         # The agent might fail if no LLM is configured.

    def reset_trace(self):
        self.reasoning_trace = []

    async def run(
        self,
        user_input: str,
        chat_history: List[Dict[str, Any]],
        pre_fetched_context: Optional[str] = None # New parameter
    ) -> Dict[str, Any]:
        """
        Main reasoning loop using dspy.ReAct.
        - Accepts user_input, chat_history, and optional pre_fetched_context.
        - Uses dspy.ReAct to select and apply tools.
        - Returns the final agent response and reasoning trace.
        """
        self.reset_trace()

        if not dspy.settings.lm:
            print("Warning: DSPy LLM not configured. ReAct agent may fail or use a default if available.")

        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        
        # Construct the main query/prompt for the ReAct agent
        context_section = f"Pre-fetched Context:\n{pre_fetched_context}\n\n" if pre_fetched_context and pre_fetched_context != "No pre-fetched context available." else ""
        
        full_query = (
            f"{context_section}"
            f"Chat History:\n{history_str}\n\n"
            f"User Query: {user_input}\n\n"
            f"Assistant, considering the pre-fetched context (if any) and the chat history, "
            f"please respond to the user's query. You can use available tools to find more information or perform actions if needed."
        )

        # The DspySignature instances themselves can act as tools if they are callable
        # and have a 'name' and 'description'.
        # dspy.ReAct expects a list of tools (actions).
        # Our DspySignature instances have a __call__ method and name/description.
        
        # Define a simple signature for the ReAct module itself
        class AgentSignature(dspy.Signature):
            """Takes a question and returns an answer, potentially using tools."""
            question: str = dspy.InputField()
            answer: str = dspy.OutputField()

        # Pass the signature as the first argument, then tools
        agent_instance = dspy.ReAct(AgentSignature, self.react_tools, max_iters=self.max_steps)
        
        # Store trace if enabled
        # dspy.ReAct has its own tracing mechanism. We can inspect dspy.settings.lm.history
        # For a more structured trace, we might need to wrap tool calls or inspect ReAct's internals.
        
        final_answer = ""
        reasoning_steps = []

        try:
            # dspy.ReAct is a Predict module, so it's called with keyword arguments matching its signature's InputFields
            # The default ReAct signature is often just `question: str -> answer: str`
            # It uses the 'question' to then internally decide on thoughts, actions, observations.
            # We need to ensure our `full_query` is passed to the correct InputField of ReAct.
            # Let's assume ReAct's default InputField is 'question' or 'query'.
            # We might need to define a custom ReAct module if we need more complex input fields for ReAct itself.
            
            # The `actions` parameter in ReAct constructor is for the tools.
            # The call to the ReAct instance is for the main input.
            # Example from DSPy docs: `react_module(question=user_query)`
            
            # We need to ensure our tools' handlers (like search_docs_tool) are async-compatible
            # if dspy.ReAct or the underlying LLM calls are async.
            # The DspySignature.__call__ is sync, but it calls an async handler.
            # This can be problematic. dspy's ReAct might not handle async tool calls out of the box
            # or might require specific async setup for the LLM.
            
            # For now, let's assume a synchronous call pattern for ReAct for simplicity, 
            # and tool handlers will be called in a way that works.
            # If tools are async, dspy.ReAct itself needs to be run in an async context
            # and handle awaitables from tools.
            # This is a complex area in dspy. For now, we aim for a conceptual implementation.
            
            # Let's try to run it. This part is tricky due to async handlers.
            # dspy.ReAct typically uses the LLM to generate thought/action steps.
            # If the LLM is synchronous, and tools are async, it's a problem.
            # We will assume for now that this will be handled, or simplify to sync tools for PoC.

            # ---- SIMPLIFICATION FOR ASYNC HANDLERS IN DSPY REACT ----
            # DSPy's ReAct and other modules primarily work synchronously with the LLM.
            # If tool handlers are async, they cannot be directly awaited inside the LLM's synchronous generation loop.
            # Option 1: Make tool handlers synchronous (bad for IO-bound tasks like API calls).
            # Option 2: Use an async-capable ReAct variant if DSPy offers one (not standard).
            # Option 3: Run async tool handlers in a separate event loop and block (tricky).
            # Option 4: DSPy might have mechanisms for this (e.g. `dspy.async_context`).

            # For this PoC, we will proceed as if DSPy's ReAct can handle this, 
            # or acknowledge this as a point needing further investigation for robust async tool use.
            # The `DspySignature.__call__` is synchronous. This will block if `handler` is async and awaited directly.
            # We should make the DspySignature.__call__ async if its handler is async.
            
            # Given DspySignature.__call__ is sync, and our handlers are async, we have a mismatch.
            # Let's adjust DspySignature to be async-aware or simplify tool handlers to be sync for now.
            # For this iteration, we will MARK THIS AS A KNOWN ISSUE / TODO for proper async handling with DSPy.
            # We'll proceed with the structure, assuming it conceptually works or will be refined.

            # According to DSPy docs, if ReAct is called with acall(), it will acall() tools.
            # Our DspySignature tools have async __call__ methods.
            response = await agent_instance.acall(question=full_query) # Use acall for async execution
            final_answer = response.answer

            # Extracting trace from dspy.ReAct
            # The trace is usually in `dspy.settings.lm.history` if the LLM is traced.
            # ReAct module itself might store some trajectory.
            if self.trace_enabled and dspy.settings.lm and hasattr(dspy.settings.lm, 'history'):
                # This is a raw LLM call history, not a structured ReAct trace.
                # For a structured ReAct trace (Thought, Action, Observation), it's more involved.
                # We may need to parse the final `answer` if it contains the trace, or inspect agent_instance internals.
                # For now, we'll use the raw LLM history as a proxy for trace.
                # Let's assume `response` object might have more details or the agent instance.
                # react_module.trajectory might exist in some dspy versions/customizations.

                # Simplified trace based on LLM history for now
                # Each element in lm.history is often a dict with 'prompt', 'response', 'kwargs', etc.
                # This might be too verbose or not structured enough for a ReAct trace.
                # For now, we'll create a placeholder trace.
                if hasattr(agent_instance, 'trajectory') and agent_instance.trajectory:
                    # If ReAct module stores a trajectory (some versions might)
                    # This is hypothetical, dspy.ReAct's tracing can be complex.
                    for i, step in enumerate(agent_instance.trajectory):
                        # Structure of 'step' depends on dspy.ReAct implementation
                        # Typically includes thought, action, observation
                        reasoning_steps.append({
                            "step": i + 1,
                            "thought": step.get("thought", "N/A"),
                            "action": step.get("action_name", "N/A"),
                            "action_input": step.get("action_input", "N/A"),
                            "observation": step.get("observation", "N/A")
                        })
                elif dspy.settings.lm and dspy.settings.lm.history:
                     # Fallback to raw LLM trace if specific trajectory is not available
                    for entry in dspy.settings.lm.history:
                        reasoning_steps.append({
                            "prompt": entry.get('prompt'),
                            "response": entry.get('response'),
                            # "kwargs": entry.get('kwargs') # Potentially too verbose
                        })                   
                else:
                    reasoning_steps.append({"note": "No detailed trace available from ReAct or LLM history."}) 
        except Exception as e:
            print(f"Error during ReAct agent execution: {e}")
            final_answer = "I encountered an error trying to process your request."
            reasoning_steps.append({"error": str(e)})
            # Potentially re-raise or handle more gracefully

        self.reasoning_trace = reasoning_steps

        return {
            "answer": final_answer,
            "trace": self.reasoning_trace
        }
