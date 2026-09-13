from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import MONGO_URI, DB_NAME
import uuid

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
admins_col = db["admins"]
banned_col = db["banned"]
files_col = db["files"]
batches_col = db["batches"]
shorteners_col = db["shorteners"]
stats_col = db["stats"]


# ─── USER ───────────────────────────────────────────────
async def add_user(user_id: int, username: str = None, full_name: str = None):
    if not await users_col.find_one({"user_id": user_id}):
        await users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "joined_at": datetime.utcnow(),
        })

async def get_all_users():
    return await users_col.find({}, {"user_id": 1}).to_list(length=None)

async def total_users():
    return await users_col.count_documents({})


# ─── ADMIN ──────────────────────────────────────────────
async def add_admin(user_id: int):
    if not await admins_col.find_one({"user_id": user_id}):
        await admins_col.insert_one({"user_id": user_id, "added_at": datetime.utcnow()})
        return True
    return False

async def remove_admin(user_id: int):
    result = await admins_col.delete_one({"user_id": user_id})
    return result.deleted_count > 0

async def is_admin(user_id: int, owner_id: int) -> bool:
    if user_id == owner_id:
        return True
    return bool(await admins_col.find_one({"user_id": user_id}))

async def get_all_admins():
    return await admins_col.find({}).to_list(length=None)

async def total_admins():
    return await admins_col.count_documents({})


# ─── BAN ────────────────────────────────────────────────
async def ban_user(user_id: int, reason: str = "No reason"):
    if not await banned_col.find_one({"user_id": user_id}):
        await banned_col.insert_one({
            "user_id": user_id,
            "reason": reason,
            "banned_at": datetime.utcnow()
        })
        return True
    return False

async def unban_user(user_id: int):
    result = await banned_col.delete_one({"user_id": user_id})
    return result.deleted_count > 0

async def is_banned(user_id: int) -> bool:
    return bool(await banned_col.find_one({"user_id": user_id}))

async def total_banned():
    return await banned_col.count_documents({})

async def get_all_banned():
    return await banned_col.find({}).to_list(length=None)


# ─── FILES ──────────────────────────────────────────────
async def store_file(tg_file_id: str, file_name: str, file_size: int,
                     file_type: str, uploader_id: int, msg_id: int,
                     batch_id: str = None):
    file_uid = str(uuid.uuid4())[:8]
    doc = {
        "file_uid": file_uid,
        "tg_file_id": tg_file_id,
        "msg_id": msg_id,
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "uploader_id": uploader_id,
        "batch_id": batch_id,
        "download_count": 0,
        "uploaded_at": datetime.utcnow(),
    }
    await files_col.insert_one(doc)
    return file_uid

async def get_file(file_uid: str):
    return await files_col.find_one({"file_uid": file_uid})

async def increment_download(file_uid: str):
    await files_col.update_one({"file_uid": file_uid}, {"$inc": {"download_count": 1}})

async def total_files():
    return await files_col.count_documents({})


# ─── BATCH ──────────────────────────────────────────────
async def create_batch(admin_id: int):
    batch_id = str(uuid.uuid4())[:10]
    await batches_col.insert_one({
        "batch_id": batch_id,
        "admin_id": admin_id,
        "file_uids": [],
        "created_at": datetime.utcnow(),
    })
    return batch_id

async def add_file_to_batch(batch_id: str, file_uid: str):
    await batches_col.update_one(
        {"batch_id": batch_id},
        {"$push": {"file_uids": file_uid}}
    )

async def get_batch(batch_id: str):
    return await batches_col.find_one({"batch_id": batch_id})

async def total_batches():
    return await batches_col.count_documents({})


# ─── SHORTENER ──────────────────────────────────────────
async def add_shortener(name: str, api_key: str, domain: str,
                        note: str = "", duration_hours: int = 24):
    shortener_id = str(uuid.uuid4())[:6]
    await shorteners_col.insert_one({
        "shortener_id": shortener_id,
        "name": name,
        "api_key": api_key,
        "domain": domain,
        "note": note,
        "duration_hours": duration_hours,
        "enabled": True,
        "added_at": datetime.utcnow(),
    })
    return shortener_id

async def get_all_shorteners():
    return await shorteners_col.find({}).to_list(length=None)

async def get_shortener(shortener_id: str):
    return await shorteners_col.find_one({"shortener_id": shortener_id})

async def update_shortener(shortener_id: str, update_data: dict):
    await shorteners_col.update_one(
        {"shortener_id": shortener_id},
        {"$set": update_data}
    )

async def delete_shortener(shortener_id: str):
    await shorteners_col.delete_one({"shortener_id": shortener_id})

async def toggle_shortener(shortener_id: str, enabled: bool):
    await shorteners_col.update_one(
        {"shortener_id": shortener_id},
        {"$set": {"enabled": enabled}}
    )
