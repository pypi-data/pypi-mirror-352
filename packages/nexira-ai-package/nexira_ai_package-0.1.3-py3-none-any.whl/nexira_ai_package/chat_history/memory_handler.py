from nexira_ai_package.db_handler import DocumentDBHandler
from nexira_ai_package.chat_history.schema import UserThread, ConversationInfor
from datetime import datetime
from typing import Dict, Any, List

class MemoryHandler(DocumentDBHandler):
    def __init__(self, connection_string: str, username: str, password: str, db_name: str, collection_name: str):
        super().__init__(connection_string, username, password, db_name, collection_name)

    def clear_conversation(self, thread_infor: UserThread):
        """Clear a specific conversation."""
        self.collection.delete_one(
            {"user_id": thread_infor.user_id, "chat_id": thread_infor.chat_id}
        )

    def insert_or_update_conversation(self, conversation_infor: ConversationInfor):
        if not conversation_infor.messages:
            print("No messages provided. Skipping update.")
            return

        key = {
            "user_id": conversation_infor.user_thread.user_id,
            "chat_id": conversation_infor.user_thread.chat_id,
            "agent_name": conversation_infor.user_thread.agent_name
        }

        messages_as_dicts = [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp, "message_id": msg.message_id}
            for msg in conversation_infor.messages
        ]

        self.insert_document(key, messages_as_dicts)

    def retrieve_conversation(self, user_id: int, chat_id: int) -> Dict[str, Any]:
        conversations = self.collection.find(
            {
                "user_id": user_id,
                "chat_id": chat_id,
            }
        )
        results = []
        for convo in conversations:
            convo["_id"] = str(convo["_id"])
            results.append(convo)

        if not results:
            print(f"No conversations found for user_id '{user_id}' and chat_id '{chat_id}'.")
        return results

    def all_users(self) -> List[int]:
        try:
            user_ids = self.collection.distinct("user_id")
            return user_ids
        except Exception as e:
            print(f"❌ Error fetching user_ids: {e}")
            return []

    def all_chats(self, user_id: int) -> List[int]:
        try:
            chat_ids = self.collection.distinct("chat_id", {"user_id": user_id})
            return [int(cid) for cid in chat_ids]
        except Exception as e:
            print(f"❌ Error fetching chat_ids for user {user_id}: {e}")
            return []
