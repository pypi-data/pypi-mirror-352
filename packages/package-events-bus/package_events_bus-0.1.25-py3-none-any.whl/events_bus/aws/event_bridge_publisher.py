import boto3

from .. import CONFIG
from ..core import (EventBusPublisher, BaseEvent,
                    EventJsonSerializer)


class EventBridgePublisher(EventBusPublisher):
    def __init__(self, bus_name: str, source: str):
        self.client = boto3.client('events',
                                   region_name=CONFIG.AWS_REGION_NAME,
                                   endpoint_url=CONFIG.AWS_CLIENT_URL)
        self.bus_name = bus_name
        self.source = source

    def publish(self, event: BaseEvent):
        """Publish a single event to the EventBridge bus."""
        # TODO: Add try/except for publish
        self.client.put_events(
            Entries=[
                {
                    'Source': self.source,
                    'DetailType': event.event_name,
                    'Detail': EventJsonSerializer.serialize(event),
                    'EventBusName': self.bus_name,
                }
            ]
        )

    def publish_batch(self, events: list[BaseEvent]):
        """Publish a batch of events to the EventBridge bus."""
        # TODO: Add try/except for publish_batch
        entries = []
        for event in events:
            entries.append(
                {
                    'Source': self.source,
                    'DetailType': event.event_name,
                    'Detail': EventJsonSerializer.serialize(event),
                    'EventBusName': self.bus_name,
                }
            )
        self.client.put_events(Entries=entries)
