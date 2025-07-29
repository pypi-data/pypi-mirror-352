from typing import Any, Dict, Callable, Optional, Awaitable

class DspySignature:
    """
    Declarative signature for agent actions/tools.
    Describes the action name, input/output schema, and handler.
    The handler is expected to be an async function.
    """
    def __init__(
        self,
        name: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        handler: Optional[Callable[..., Awaitable[Any]]] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.handler = handler
        self.description = description

    async def __call__(self, *args, **kwargs) -> Any:
        if self.handler is None:
            raise NotImplementedError("No handler assigned for this signature.")
        return await self.handler(*args, **kwargs)
