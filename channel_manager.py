from dataclasses import dataclass
from uuid import *
from time import *

@dataclass
class Message:
    role: str
    content: str
    timestamp: int

class ChannelManager:
    def __init__(self):
        self.channels = {}
        self.channel_ids = []
        self.current_channel: int
    def sort_and_list_channels(self):
        self.channel_ids.sort(key=lambda x: self.channels[x][last_updated], reverse=True)
    def switch_or_make_channel(self, channel_id):
        new_channel = {
            "messages": [],
            "created_at": round(time.time(),2),
            "last_updated": round(time.time(),2)
        }
        self.channels[channel_id] = new_channel if channel_id not in self.channels
        self.current_channel = channel_id
    def create_and_use_new_channel(self):
        new_id = int(uuid4())
        self.switch_or_make_channel(new_id)
        self.channel_ids.append(new_id)
    def sort_channel_messages(self, channel_id):
        self.channels[channel_id]["messages"].sort(key=lambda x: x.timestamp, reverse=True)
    def add_message(self, text: str, role: str):
        new_message = Message(text=text, role=role, timestamp=round(time.time(),2))
        self.channels[self.current_channel]["messages"].append(new_message)
        self.channels[self.current_channel]["last_updated"] = round(time.time(),2)
        self.sort_channel_messages(self.current_channel)
    def get_channel_messages_context(self, channel_id):
        context = ""
        self.sort_channel_messages(channel_id)
        for message in self.channels[channel_id]["messages"]:
            context += f"{message.role}: {message.text}\n"
        return context