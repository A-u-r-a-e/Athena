from rag_manager import RAG
from channel_manager import ChannelManager
import os

TOP_N = 10
INPUT_PROMPT = "What can I help you with? "

Channels = ChannelManager()
Athena = RAG(private_path = os.path.join(os.getcwd(),"private"),)

Athena.chroma_update()

Channels.create_and_use_new_channel()
channel = Channels.current_channel

while True:
    query = input(INPUT_PROMPT)
    chat_history = Channels.get_channel_messages_context(channel)
    Channels.add_message(query, "User")
    response = Athena.process_query(chat_history, query, TOP_N)
    Channels.add_message(query, "Athena")
    print(response)