"""
MongoDB User & Authentication Repository.
Encapsulates CRUD operations, password reset tokens, and preference provisioning.
"""
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from ..mongodb.connection import get_async_db

logger = logging.getLogger("raahi.auth.repository")


class UserRepository:
    @property
    def coll(self):
        return get_async_db().users

    @property
    def reset_coll(self):
        return get_async_db().password_resets

    @property
    def pref_coll(self):
        return get_async_db().user_preferences

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user document by unique identifier."""
        return await self.coll.find_one({"_id": user_id})

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user document by normalized email address."""
        email_norm = email.strip().lower()
        return await self.coll.find_one({
            "$or": [
                {"email_normalized": email_norm},
                {"email": email_norm}
            ]
        })

    async def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "commuter",
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user with secure password hash and default commuter preferences."""
        email_norm = email.strip().lower()
        user_id = f"user-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        doc = {
            "_id": user_id,
            "name": name.strip(),
            "email": email.strip(),
            "email_normalized": email_norm,
            "password_hash": password_hash,
            "role": role,
            "avatar_url": avatar_url,
            "email_verified": True,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "last_login_at": now
        }

        await self.coll.insert_one(doc)

        # Provision initial personalized preferences for this commuter
        try:
            pref_doc = {
                "_id": f"pref-{user_id}",
                "user_id": user_id,
                "preferred_language": "en",
                "travel_preferences": {
                    "fastest": True,
                    "cheapest": False,
                    "less_crowded": False,
                    "fewer_transfers": False,
                    "accessible": False,
                    "prefer_ebus": False,
                    "pink_pass": False,
                    "prefer_rail": False
                },
                "updated_at": now
            }
            await self.pref_coll.insert_one(pref_doc)
        except Exception as e:
            logger.warning(f"Could not provision default preferences for {user_id}: {e}")

        return doc

    async def update_last_login(self, user_id: str) -> None:
        """Record the latest successful authentication timestamp."""
        now = datetime.now(timezone.utc)
        await self.coll.update_one(
            {"_id": user_id},
            {"$set": {"last_login_at": now, "updated_at": now}}
        )

    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update commuter profile attributes."""
        safe_updates = {}
        for k in ["name", "avatar_url"]:
            if k in updates and updates[k] is not None:
                safe_updates[k] = updates[k]
        
        if safe_updates:
            safe_updates["updated_at"] = datetime.now(timezone.utc)
            await self.coll.update_one({"_id": user_id}, {"$set": safe_updates})
        
        return await self.get_by_id(user_id)

    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update password hash upon verified reset or credential change."""
        now = datetime.now(timezone.utc)
        res = await self.coll.update_one(
            {"_id": user_id},
            {"$set": {"password_hash": new_password_hash, "updated_at": now}}
        )
        return res.modified_count > 0

    async def create_password_reset(self, user_id: str, token_hash: str, expires_in_hours: int = 1) -> None:
        """Store hashed password reset token with expiration."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expires_in_hours)
        # Invalidate any prior active tokens for this user
        await self.reset_coll.update_many(
            {"user_id": user_id, "used": False},
            {"$set": {"used": True}}
        )
        await self.reset_coll.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "used": False,
            "created_at": now
        })

    async def verify_and_consume_password_reset(self, token_hash: str) -> Optional[str]:
        """Verify that token hash is valid, not expired, and not already consumed."""
        now = datetime.now(timezone.utc)
        record = await self.reset_coll.find_one({
            "token_hash": token_hash,
            "used": False,
            "expires_at": {"$gt": now}
        })
        if not record:
            return None
        # Mark consumed
        await self.reset_coll.update_one(
            {"_id": record["_id"]},
            {"$set": {"used": True}}
        )
        return record["user_id"]


user_repository = UserRepository()

