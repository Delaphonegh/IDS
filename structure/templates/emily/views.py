import atexit
import csv
import os
from os import environ
from uuid import uuid4
import secrets
import random
import string
import requests
from requests.auth import HTTPBasicAuth
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, Blueprint, session, redirect, url_for, jsonify, current_app, request
from flask_login import login_required
from sqlalchemy import and_, or_, desc
from flask_mail import Mail, Message
from datetime import date,datetime
from structure import db,mail ,photos,app
from structure.core.forms import ChatbotForm
from structure.about.forms import AboutForm
from werkzeug.utils import secure_filename
from PIL import Image
from structure.models import Chatbot,KnowledgeBase , Chat , ConversationHistory ,ChatMessage
# import pytesseract 
# from io import BytesIO
# import base64

core = Blueprint('core', __name__)






@app.route('/new_chatbot', methods=['GET', 'POST'])
def create_chatbot():
    form =ChatbotForm()
    if request.method == 'POST':
        name = request.form['name']
        primary_knowledge_base = request.form['primary_kb']
        url = request.form['url']
        if request.files.get('kb_image'):
            image = photos.save(request.files['image'], name=secrets.token_hex(10) + ".")
            image= "static/images/packages/"+image
        else:
            image = None
        if request.files.get('kb_file'):
            file = photos.save(request.files['file'], name=secrets.token_hex(10) + ".")
            file= "static/images/packages/"+file
        else:
            file = None
        chatbot = Chatbot(name=name,user_id=session['id'])
        db.session.add(chatbot)
        db.session.commit()
        knowledgebase = KnowledgeBase(primary_kb=primary_knowledge_base,image_location=image,file=file,url=url,chatbot_id=chatbot.id)
        db.session.add(knowledgebase)
        db.session.commit()
        # flash('Chatbot created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('emily/newchatbot.html',form=form)



# @app.route('/chat/<int:chatbot_id>', methods=['GET', 'POST'])
# def chat(chatbot_id):
#     chatbot = Chatbot.query.get_or_404(chatbot_id)
#     knowledge_bases = KnowledgeBase.query.filter_by(chatbot_id=chatbot_id).all()

#     if request.method == 'POST':
#         print('chatting')
#         user_input = request.get_json().get('user_input')
#         if user_input:
#             prompt = construct_prompt(chatbot, knowledge_bases, user_input)
#             response = openai_completion(chatbot, knowledge_bases, user_input)
#             return jsonify({'response': response})
#         else:
#             return jsonify({'error': 'Invalid request. No user Input'}), 400

#     return render_template('emily/chat.html', chatbot=chatbot)
# OpenAI API Integration
# def openai_completion(chatbot, knowledge_bases, user_input):
#     openai_api_key = os.environ.get('OPENAI_API_KEY')
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {openai_api_key}',
#     }

#     messages = [
#         {"role": "system", "content": "You are an AI assistant for finding information in company knowledgebases."}
#     ]

#     prompt = construct_prompt(chatbot, knowledge_bases, user_input)
#     messages.append({"role": "user", "content": prompt})
#     print("messages:",messages)

#     data = {
#         "model": "gpt-3.5-turbo",
#         "messages": messages,
#         "temperature": 0.5,
#     }

#     try:
#         response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
#         response.raise_for_status()
#         ai_response = response.json()['choices'][0]['message']['content']
#         return ai_response
#     except requests.exceptions.RequestException as e:
#         return f"Error: {e}"

# Helper function to construct the prompt (unchanged)
# def construct_prompt(chatbot, knowledge_bases, user_input):
#     prompt = ""
#     print("kb:",knowledge_bases)
#     for kb in knowledge_bases:
#         if kb.primary_kb:
#             prompt += f"{kb.primary_kb}\n"
#         if kb.file:
#             prompt += f"File: {kb.file}\n"
#         if kb.image_location:
#             prompt += f"Image: {kb.image_location}\n"
#         if kb.url:
#             prompt += f"URL: {kb.url}\n"
#     prompt += f"\nHuman: {user_input}\nAI:"
#     print("prompt:", prompt)
#     return prompt


def construct_prompt(chatbot, knowledge_bases, user_input):
    prompt = ""
    for kb in knowledge_bases:
        if kb.primary_kb:
            prompt += f"{kb.primary_kb}\n"
        if kb.file:
            prompt += f"File: {kb.file}\n"
        if kb.image_location:
            prompt += f"Image: {kb.image_location}\n"
        if kb.url:
            prompt += f"URL: {kb.url}\n"
    prompt += f"\nHuman: {user_input}\nAI:"
    return prompt
# Index route
@app.route('/')
def index():
    chatbots = Chatbot.query.all()
    return render_template('index.html', chatbots=chatbots)


@app.route('/chats')
def chats():
    chatbots = Chatbot.query.all()
    chats = Chat.query.filter_by(user_id=session['id']).all()

    return render_template('emily/chats.html', chatbots=chatbots,chats=chats)

# @app.route('/chat/<int:chatbot_id>/<int:history_id>', methods=['GET', 'POST'])
# def chat(chatbot_id,history_id):
#     chatbot = Chatbot.query.get_or_404(chatbot_id)
#     knowledge_bases = KnowledgeBase.query.filter_by(chatbot_id=chatbot_id).all()
#     # chat = Chat.query.filter_by(chatbot_id=chatbot_id,conversation_history_id=history_id).first()
#     conversation_history = ConversationHistory.query.get_or_404(history_id)
#     print("history:",conversation_history.messages)
#     chat = Chat.query.filter_by(chatbot_id=chatbot_id, conversation_history=conversation_history).first()


#     if not chat:
#         unique_id='11111' #TODO generate 
#         conversation_history = ConversationHistory(user_id =session['id'],chatbot_id = chatbot_id,unique_id=unique_id)
#         db.session.add(conversation_history)
#         db.session.commit()
#         chat = Chat(chatbot_id=chatbot_id, conversation_history=conversation_history,user_id=session['id'])
#         db.session.add(chat)
#         db.session.commit()

#     if request.method == 'POST':
#         print('chatting')
#         user_input = request.get_json().get('user_input')
#         if user_input:
#             chat.conversation_history.messages.append({"role": "user", "content": user_input})
#             db.session.commit()
#             response = openai_completion(chatbot, knowledge_bases, chat.conversation_history)
#             # db.session.commit()
#             return jsonify({'response': response})
#         else:
#             return jsonify({'error': 'Invalid request. No user Input'}), 400

#     return render_template('emily/chat.html', chatbot=chatbot, chat=chat ,history_id=history_id)



# def openai_completion(chatbot, knowledge_bases, conversation_history):
#     openai_api_key = os.environ.get('OPENAI_API_KEY')
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {openai_api_key}',
#     }
#     messages = [
#         {"role": "system", "content": "You are an AI assistant for finding information in company knowledgebases."}
#     ]

#     if conversation_history.messages:
#         messages.extend(conversation_history.messages)
#         user_input = conversation_history.messages[-1]["content"]
#     else:
#         user_input = ""

#     prompt = construct_prompt(chatbot, knowledge_bases, user_input)
#     messages.append({"role": "user", "content": prompt})
#     print("messages:", messages)

#     data = {
#         "model": "gpt-3.5-turbo",
#         "messages": messages,
#         "temperature": 0.5,
#     }

#     try:
#         response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
#         response.raise_for_status()
#         ai_response = response.json()['choices'][0]['message']['content']
#         conversation_history.messages.append({"role": "assistant", "content": ai_response})
#         return ai_response
#     except requests.exceptions.RequestException as e:
#         return f"Error: {e}"





@app.route('/chat/<int:chatbot_id>/<int:chat_id>', methods=['GET', 'POST'])
def chat(chatbot_id, chat_id):
    chatbot = Chatbot.query.get_or_404(chatbot_id)
    knowledge_bases = KnowledgeBase.query.filter_by(chatbot_id=chatbot_id).all()
    chat = Chat.query.get_or_404(chat_id)

    if request.method == 'POST':
        print('chatting')
        user_input = request.get_json().get('user_input')
        if user_input:
            message = ChatMessage(chat=chat, role='user', content=user_input)
            db.session.add(message)
            db.session.commit()

            conversation_history = [
                {'role': msg.role, 'content': msg.content}
                for msg in chat.messages
            ]
            response = openai_completion(chatbot, knowledge_bases, conversation_history)

            ai_message = ChatMessage(chat=chat, role='assistant', content=response)
            db.session.add(ai_message)
            db.session.commit()

            return jsonify({'response': response})
        else:
            return jsonify({'error': 'Invalid request. No user Input'}), 400

    conversation_history = [
        {'role': msg.role, 'content': msg.content}
        for msg in chat.messages
    ]
    return render_template('emily/chat.html', chatbot=chatbot, chat=chat, conversation_history=conversation_history,chat_id=chat_id)




def openai_completion(chatbot, knowledge_bases, conversation_history):
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    }

    messages = [{"role": "system", "content": "You are an AI assistant for finding information in company knowledgebases."}]
    messages.extend(conversation_history)

    user_input = conversation_history[-1]["content"] if conversation_history else ""
    prompt = construct_prompt(chatbot, knowledge_bases, user_input)
    messages.append({"role": "user", "content": prompt})

    print("messages:", messages)
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.5,
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        ai_response = response.json()['choices'][0]['message']['content']
        return ai_response
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"