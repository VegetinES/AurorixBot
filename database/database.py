from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connection_string = "mongodb://localhost:27017" # Conexión a MongoDB
        self.database_name = "database" # Nombre de la base de datos
    
    async def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
    
    async def ensure_tables(self):
        await self.connect()
        
        collections = await self.db.list_collection_names()
        
        required_collections = [
            "suggestion_votes",
            "suggestion_threads", 
            "tickets",
            "ticket_counters",
            "sanctions",
            "sanction_counters"
        ]
        
        for collection_name in required_collections:
            if collection_name not in collections:
                await self.db.create_collection(collection_name)
        
        await self.db.suggestion_votes.create_index([("message_id", 1), ("user_id", 1)], unique=True)
        await self.db.suggestion_threads.create_index("message_id", unique=True)
        await self.db.tickets.create_index("channel_id", unique=True)
        await self.db.ticket_counters.create_index("category", unique=True)
        await self.db.sanctions.create_index("sanction_id", unique=True)
        await self.db.sanctions.create_index("user_id")
        await self.db.sanctions.create_index("expires_at")
    
    async def add_vote(self, message_id, user_id, vote_type):
        await self.connect()
        await self.db.suggestion_votes.update_one(
            {"message_id": message_id, "user_id": user_id},
            {
                "$set": {
                    "vote_type": vote_type,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
    
    async def remove_vote(self, message_id, user_id):
        await self.connect()
        await self.db.suggestion_votes.delete_one({
            "message_id": message_id,
            "user_id": user_id
        })
    
    async def get_votes(self, message_id):
        await self.connect()
        cursor = self.db.suggestion_votes.find({"message_id": message_id})
        results = await cursor.to_list(length=None)
        
        votes = {"yes": set(), "no": set()}
        for result in results:
            votes[result["vote_type"]].add(result["user_id"])
        
        return votes
    
    async def clear_suggestion_votes(self, message_id):
        await self.clear_suggestion_data(message_id)
    
    async def has_voted(self, message_id, user_id):
        await self.connect()
        result = await self.db.suggestion_votes.find_one({
            "message_id": message_id,
            "user_id": user_id
        })
        return result["vote_type"] if result else None
    
    async def save_thread_url(self, message_id, thread_url):
        await self.connect()
        await self.db.suggestion_threads.update_one(
            {"message_id": message_id},
            {
                "$set": {
                    "thread_url": thread_url,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
    
    async def get_thread_url(self, message_id):
        await self.connect()
        result = await self.db.suggestion_threads.find_one({"message_id": message_id})
        return result["thread_url"] if result else None
    
    async def clear_suggestion_data(self, message_id):
        await self.connect()
        await self.db.suggestion_votes.delete_many({"message_id": message_id})
        await self.db.suggestion_threads.delete_one({"message_id": message_id})

    async def get_next_ticket_counter(self, category):
        await self.connect()
        result = await self.db.ticket_counters.find_one_and_update(
            {"category": category},
            {"$inc": {"counter": 1}},
            upsert=True,
            return_document=True
        )
        return result["counter"]

    async def create_ticket(self, channel_id, creator_id, category, counter, form_data):
        await self.connect()
        ticket_doc = {
            "channel_id": channel_id,
            "creator_id": creator_id,
            "category": category,
            "counter": counter,
            "status": "open",
            "form_data": form_data,
            "users": [creator_id],
            "transcript_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await self.db.tickets.insert_one(ticket_doc)
        return str(result.inserted_id)

    async def get_user_active_ticket(self, user_id, category):
        await self.connect()
        result = await self.db.tickets.find_one({
            "creator_id": user_id,
            "category": category,
            "status": "open"
        })
        return result["channel_id"] if result else None

    async def get_ticket_by_channel(self, channel_id):
        await self.connect()
        result = await self.db.tickets.find_one({"channel_id": channel_id})
        if result:
            return result["creator_id"], result["category"], result.get("users", [])
        return None

    async def update_ticket_status(self, channel_id, status, transcript_id=None):
        await self.connect()
        update_data = {
            "status": status,
            "updated_at": datetime.now()
        }
        if transcript_id:
            update_data["transcript_id"] = transcript_id
        
        await self.db.tickets.update_one(
            {"channel_id": channel_id},
            {"$set": update_data}
        )

    async def get_ticket_transcript_id(self, channel_id):
        await self.connect()
        result = await self.db.tickets.find_one({"channel_id": channel_id})
        return result.get("transcript_id") if result else None

    async def delete_ticket(self, channel_id):
        await self.connect()
        await self.db.tickets.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "status": "deleted",
                    "updated_at": datetime.now()
                }
            }
        )

    async def add_user_to_ticket(self, channel_id, user_id):
        await self.connect()
        await self.db.tickets.update_one(
            {"channel_id": channel_id},
            {
                "$addToSet": {"users": user_id},
                "$set": {"updated_at": datetime.now()}
            }
        )

    async def remove_user_from_ticket(self, channel_id, user_id):
        await self.connect()
        await self.db.tickets.update_one(
            {"channel_id": channel_id},
            {
                "$pull": {"users": user_id},
                "$set": {"updated_at": datetime.now()}
            }
        )

    async def get_ticket_form_data(self, channel_id):
        await self.connect()
        result = await self.db.tickets.find_one({"channel_id": channel_id})
        return result.get("form_data", {}) if result else {}

    async def get_tickets_by_user(self, user_id, limit=10):
        await self.connect()
        cursor = self.db.tickets.find(
            {"creator_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        results = await cursor.to_list(length=None)
        return [(doc["channel_id"], doc["category"], doc["status"], doc["created_at"]) for doc in results]

    async def get_tickets_stats(self):
        await self.connect()
        pipeline = [
            {
                "$group": {
                    "_id": {"category": "$category", "status": "$status"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = self.db.tickets.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        stats = {}
        for result in results:
            category = result["_id"]["category"]
            status = result["_id"]["status"]
            count = result["count"]
            
            if category not in stats:
                stats[category] = {}
            stats[category][status] = count
        
        return stats

    async def get_next_sanction_id(self):
        await self.connect()
        result = await self.db.sanction_counters.find_one_and_update(
            {"_id": "sanction_counter"},
            {"$inc": {"counter": 1}},
            upsert=True,
            return_document=True
        )
        return result["counter"]

    async def create_sanction(self, user_id, moderator_id, sanction_type, reason, duration=None):
        await self.connect()
        sanction_id = await self.get_next_sanction_id()
        
        sanction_doc = {
            "sanction_id": sanction_id,
            "user_id": user_id,
            "moderator_id": moderator_id,
            "sanction_type": sanction_type,
            "reason": reason,
            "created_at": datetime.now(),
            "expires_at": duration,
            "is_active": True
        }
        
        await self.db.sanctions.insert_one(sanction_doc)
        return sanction_id

    async def get_user_sanctions(self, user_id, limit=None, skip=0):
        await self.connect()
        cursor = self.db.sanctions.find(
            {"user_id": user_id}
        ).sort("created_at", -1)
        
        if limit:
            cursor = cursor.skip(skip).limit(limit)
            
        results = await cursor.to_list(length=None)
        return results

    async def count_user_sanctions(self, user_id):
        await self.connect()
        return await self.db.sanctions.count_documents({"user_id": user_id})

    async def remove_sanction(self, sanction_id):
        await self.connect()
        await self.db.sanctions.update_one(
            {"sanction_id": sanction_id},
            {"$set": {"is_active": False}}
        )

    async def get_expired_sanctions(self, sanction_types):
        await self.connect()
        cursor = self.db.sanctions.find({
            "sanction_type": {"$in": sanction_types},
            "expires_at": {"$lte": datetime.now()},
            "is_active": True
        })
        
        results = await cursor.to_list(length=None)
        return results

    async def deactivate_sanction(self, sanction_id):
        await self.connect()
        await self.db.sanctions.update_one(
            {"sanction_id": sanction_id},
            {"$set": {"is_active": False}}
        )

db = Database()