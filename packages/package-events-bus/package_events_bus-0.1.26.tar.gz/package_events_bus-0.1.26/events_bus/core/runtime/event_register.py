from .. import BaseHandler


class EventHandlerRegistry:
    """Registry for event handlers.
    This class is responsible for registering event handlers and
    providing access to them.
    """
    _registry_queues: dict[str, BaseHandler] = {}
    _registry_handlers: dict[str, BaseHandler] = {}

    @classmethod
    def register_by_queue(cls, queue_url: str, handler: BaseHandler):
        """Register an event handler associated with a specific queue URL.
        Args:
            queue_url (str): The URL of the queue to which the handler is
            associated.
            handler (BaseHandler): The event handler to register.
        """
        cls._registry_queues[queue_url] = handler

    @classmethod
    def register_handler(cls, event_name: str, handler: BaseHandler):
        """Register an event handler without a specific queue URL.
        Args:
            handler (BaseHandler): The event handler to register.
        """
        if not isinstance(handler, BaseHandler):
            raise TypeError(f"Expected a BaseHandler, got {type(handler)}")
        cls._registry_handlers[event_name] = handler

    @classmethod
    def register_multiple_handlers(cls, handlers: dict[str, BaseHandler]):
        """Register multiple event handlers at once.
        Args:
            handlers (dict[str, BaseHandler]): A dictionary mapping event
            names to their associated event handlers.
        """
        for event_name, handler in handlers.items():
            cls.register_handler(event_name, handler)

    @classmethod
    def get_handlers_with_queues(cls) -> dict[str, BaseHandler]:
        """Get all registered event handlers.
        Returns:
            dict[str, BaseHandler]: A dictionary mapping queue URLs to
            their associated event handlers.
        """
        return cls._registry_queues

    @classmethod
    def get_handlers_by_event(cls) -> dict[str, BaseHandler]:
        """Get all registered event handlers.
        Returns:
            dict[str, BaseHandler]: A dictionary mapping event names to
            their associated event handlers.
        """
        return cls._registry_handlers
