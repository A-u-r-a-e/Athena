from dataclasses import dataclass
from uuid import *

@dataclass
class Message:
    role: str
    content: str
    timestamp: str

@dataclass
class Channel:
    channel_id: int
    messages: List[Message]
    created_at: str
    last_updated: str


#fix this entire thing
class Channels:
    def __init__(self):
        self.channels: List[Channel] = []
        self.current_channel: int
    def create_channel(self, channel_id):
        for channel in self.channels:
            if channel.channel_id == channel_id:
                return channel
        new_channel = Channel(channel_id, [], "", "")
        self.channels.append(new_channel)
        return new_channel
    def switch_channel(self, channel_id):
        self.current_channel = channel_id