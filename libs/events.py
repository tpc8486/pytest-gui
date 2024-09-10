class EventSource:
    """Generate and handle GUI events."""

    _events = {}

    @classmethod
    def bind(cls, event: str, handler):
        """
        Bind an event to a handler function.

        Args:
            event (str): The name of the event.
            handler (callable): The function to call when the event is emitted.
        """
        if cls not in cls._events:
            cls._events[cls] = {}
        if event not in cls._events[cls]:
            cls._events[cls][event] = []
        cls._events[cls][event].append(handler)

    def emit(self, event: str, **data):
        """
        Emit an event, triggering all registered handlers.

        Args:
            event (str): The name of the event to emit.
            **data: Additional data to pass to the handler functions.
        """
        handlers = self._events.get(self.__class__, {}).get(event, [])
        for handler in handlers:
            handler(self, **data)
