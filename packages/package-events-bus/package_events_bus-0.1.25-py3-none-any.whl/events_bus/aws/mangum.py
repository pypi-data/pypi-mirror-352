from mangum import Mangum
from mangum.types import (
    LambdaEvent,
    LambdaContext,
    LambdaConfig,
    LambdaHandler,
    ASGI,
    LifespanMode,
)

from ..core.infrastructure.event_deserializer import EventDeserializer
from ..core.runtime.event_register import EventHandlerRegistry


class SQSEventBridgeHandler:
    """Handler for processing events from AWS SQS or EventBridge.
    This handler is designed to process events that are either received from
    an SQS queue or from an EventBridge event. It determines the type of event
    based on the structure of the incoming event and executes the appropriate
    handler registered in the `EventHandlerRegistry`.
    Args:
        event (LambdaEvent): The event data received from AWS Lambda.
        context (LambdaContext): The context object provided by AWS Lambda.
        config (LambdaConfig): Configuration settings for the handler.
    Raises:
        ValueError: If the event type is not recognized or if required fields are missing.
    """  # noqa: E501

    def __init__(
        self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ):
        self.event = event
        self.context = context
        self.config = config

    @classmethod
    def infer(
        cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ) -> bool:
        return "Records" in event or "detail" in event

    def __get_handler_by_event_name(self, event_name: str):
        handler = EventHandlerRegistry.get_handlers_by_event().get(
            event_name, None
        )  # noqa: E501
        if handler is None:
            raise ValueError(f"No handler found for event type: {event_name}")
        return handler

    def __execute_handler_from_sqs(self):
        event_name = EventDeserializer.get_event_type_json(
            self.event["Records"][0]["body"]
        )
        handler = self.__get_handler_by_event_name(event_name)
        event = EventDeserializer.json_deserializer(
            self.event["Records"][0]["body"], handler=handler
        )
        handler.handle(event)

    def __execute_handler_from_event(self, event_name: str):
        handler = self.__get_handler_by_event_name(event_name)
        event = EventDeserializer.dict_deserializer(
            self.event.get("detail"), handler=handler
        )  # noqa: E501
        handler.handle(event)

    def execute(self):
        """Execute the handler based on the event type."""
        if "Records" in self.event:
            self.__execute_handler_from_sqs()
        elif "detail" in self.event:
            if "type" not in self.event:
                raise ValueError("Event detail must contain 'type' field.")
            event_name = self.event.get("detail", {}).get("type")
            self.__execute_handler_from_event(event_name)


class MangumExtended(Mangum):
    def __init__(
        self,
        app: ASGI,
        lifespan: LifespanMode = "auto",
        api_gateway_base_path: str = "/",
        custom_handlers: list[type[LambdaHandler]] | None = None,
        text_mime_types: list[str] | None = None,
        exclude_headers: list[str] | None = None,
    ) -> None:
        handlers = list(custom_handlers) if custom_handlers else []
        if SQSEventBridgeHandler not in handlers:
            handlers.append(SQSEventBridgeHandler)
        super().__init__(
            app,
            lifespan,
            api_gateway_base_path,
            handlers,
            text_mime_types,
            exclude_headers,
        )

    def __call__(self, event, context):
        handler = self.infer(event, context)
        if isinstance(handler, SQSEventBridgeHandler):
            return handler.execute()
        return super().__call__(event, context)
