import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import httpx
from datetime import datetime
import requests
import json

class NexiraBot:
    def __init__(self, bot_token: str, api_url: str, db_url: str = ''):
        self.api_url = api_url
        self.db_url = db_url
        self.application = ApplicationBuilder().token(bot_token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("new_chat", self.new_chat))
        self.application.add_handler(CommandHandler("mini_mavia_chatbot", self.mini_mavia_chatbot))
        self.application.add_handler(CommandHandler("block_clans_chatbot", self.block_clans_chatbot))
        self.application.add_handler(CommandHandler("standard_chatbot", self.standard_chatbot))
        self.application.add_handler(CommandHandler("list_all_agents", self.list_all_agents))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document_upload))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_upload))
        self.application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, self.handle_audio_upload))
        self.chatbot_agent = 'standard_agent'
        self.http_client = httpx.AsyncClient(timeout=20.0)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Hello! I'm your LLM chatbot. Send me a message!")

    async def standard_chatbot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Hello! I'm your standard chatbot. Send me a message!")
        self.chatbot_agent = 'standard_agent'

    async def mini_mavia_chatbot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Hello! I'm your Mini Mavia chatbot. Send me a message!")
        self.chatbot_agent = 'mini_mavia_agent'

    async def block_clans_chatbot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Hello! I'm your Block Clans chatbot. Send me a message!")
        self.chatbot_agent = 'block_clans_agent'

    async def list_all_agents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Currently, there are 3 agents available: \n1. /mini_mavia_chatbot \n2. /block_clans_chatbot \n3. /standard_chatbot")

    async def new_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.db_url:
            requests.post(self.db_url + "/llm_model/clear_chat", json={
                "user_id": update.effective_user.id,
                "chat_id": update.effective_chat.id,
                "agent_name": ""
            })
        await update.message.reply_text("🤖 New chat started!")

    async def store_message_mongodb(self, user_id: int, chat_id: int, bot_name: str, messages: list):
        if self.db_url:
            await self.http_client.post(self.db_url + "/llm_model/save_message", json={
                "user_thread": {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "agent_name": bot_name
                },
                "messages": messages
            })
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        messages = []
        text = update.effective_message.text
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        is_bot = update.effective_user.is_bot
        message_id = update.effective_message.message_id
        timestamp = update.effective_message.date
        messages.append({"role": "user" if not is_bot else "assistant", "content": text, "timestamp": timestamp.isoformat(), "message_id": message_id})

        try:
            url = self.api_url + "/llm_model/ask"
            response = await self.http_client.post(url, json={'question': text, 'agent_name': self.chatbot_agent})
            bot_text = response.json()['response']
            message_obj = await update.message.reply_text(bot_text)
            bot_text = message_obj.text
            bot_id = str(message_obj.from_user.id)
            chat_id = str(message_obj.chat.id)
            is_bot = message_obj.from_user.is_bot
            message_id = message_obj.message_id
            timestamp = message_obj.date
            messages.append({"role": "assistant" if is_bot else "user", "content": bot_text, "timestamp": timestamp.isoformat(), "message_id": message_id})
            await self.store_message_mongodb(user_id, chat_id, self.chatbot_agent, messages)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def handle_document_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Document upload")
        #print(update)
        document = update.effective_message.document
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        is_bot = update.effective_user.is_bot
        message_id = update.effective_message.message_id
        timestamp = update.effective_message.date
        file_id = document.file_id
        unique_id = document.file_unique_id
        file_size = document.file_size
        file_name = document.file_name

        file = await context.bot.get_file(file_id)
        file_bytes = await file.download_as_bytearray()

        files = {"file": (file_name, file_bytes)}
        data = {
            "file_name": file_name,
            "metadata": json.dumps({
                "user_id": user_id,
                "chat_id": chat_id,
                "is_bot": is_bot,
                "message_id": message_id,
                "timestamp": timestamp.isoformat(),
                "file_size": file_size,
                "file_unique_id": unique_id,
                "file_id": file_id
            })
        }

        response = requests.post(
            self.db_url + "/vector_db/insert_document",
            files=files,
            data=data
        )



    async def handle_photo_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Photo upload")
        print(update)

    async def handle_audio_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Audio upload")
        print(update)

    def run(self):
        print("🤖 Bot is running...")
        self.application.run_polling()
