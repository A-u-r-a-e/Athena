from rag_manager import RAG
from channel_manager import ChannelsManager
import os

TOP_N = 10

Channels = ChannelsManager()

Athena = RAG(private_path = os.path.join(os.getcwd(),"private"),)
Athena.chroma_update()

Channels.create_and_use_new_channel()
channel = Channels.current_channel

while True:
    query = input("Enter your question: ")
    chat_history = Channels.get_channel_messages_context(channel)
    Channels.add_message(query, "user")
    response = Athena.process_query(chat_history, query, TOP_N)
    print(response)