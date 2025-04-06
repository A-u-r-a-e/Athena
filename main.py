from rag_manager import RAG
from channel_manager import ChannelManager
import os
import sys
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder='static', static_url_path='/static')

TOP_N = 10

Channels = ChannelManager(private_path = os.path.join(os.getcwd(),"private"))
Athena = RAG(private_path = os.path.join(os.getcwd(),"private"))

# Athena.chroma_update()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-channel', methods=['POST'])
def new_channel():
    Channels.create_and_use_new_channel()
    return jsonify({
        'channel_id': Channels.current_channel
    })

@app.route('/api/messages/<channel_id>')
def get_channel_messages(channel_id):
    Channels.switch_or_make_channel(channel_id)
    messages = Channels.get_channel_messages_context(channel_id)
    return jsonify({
        'messages': [{'content': msg.content, 'role': msg.role} for msg in messages]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    channel_id = data.get('channel_id')
    
    if not message or not channel_id:
        return jsonify({'error': 'Missing message or channel_id'}), 400
    
    Channels.switch_or_make_channel(channel_id)
    chat_history = Channels.get_channel_messages_context(channel_id)
    
    # Add user message and get response
    Channels.add_message(message, "User")
    response = Athena.process_query(chat_history, message, TOP_N)
    Channels.add_message(response, "Athena")
    
    return jsonify({
        'response': response
    })

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    app.run(debug=True, port=port)