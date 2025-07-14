import json
import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional
from loguru import logger


class CountdownService:
    def __init__(self, data_file="/data/countdowns.json"):
        self.data_file = data_file
        self._ensure_data_directory()
        self._load_data()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.data_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")

    def _load_data(self):
        """Load countdown data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.countdowns = json.load(f)
                logger.info(f"Loaded {len(self.countdowns)} countdowns from {self.data_file}")
            else:
                self.countdowns = {}
                self._save_data()
                logger.info("Created new countdown data file")
        except Exception as e:
            logger.error(f"Error loading countdown data: {e}")
            self.countdowns = {}

    def _save_data(self):
        """Save countdown data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.countdowns, f, indent=2, default=str)
            logger.debug("Countdown data saved successfully")
        except Exception as e:
            logger.error(f"Error saving countdown data: {e}")

    def _calculate_days_remaining(self, target_date_str: str) -> int:
        """Calculate days remaining until target date"""
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            today = date.today()
            delta = target_date - today
            return delta.days
        except Exception as e:
            logger.error(f"Error calculating days remaining: {e}")
            return 0

    def add_countdown(self, title: str, target_date: str) -> str:
        """Add a new countdown item"""
        try:
            countdown_id = str(uuid.uuid4())
            countdown_data = {
                "id": countdown_id,
                "title": title,
                "target_date": target_date,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.countdowns[countdown_id] = countdown_data
            self._save_data()
            
            logger.info(f"Added countdown: {title} (ID: {countdown_id})")
            return countdown_id
            
        except Exception as e:
            logger.error(f"Error adding countdown: {e}")
            raise

    def update_countdown(self, countdown_id: str, title: str, target_date: str) -> bool:
        """Update an existing countdown item"""
        try:
            if countdown_id not in self.countdowns:
                return False
            
            self.countdowns[countdown_id]["title"] = title
            self.countdowns[countdown_id]["target_date"] = target_date
            self.countdowns[countdown_id]["updated_at"] = datetime.utcnow().isoformat()
            
            self._save_data()
            
            logger.info(f"Updated countdown: {title} (ID: {countdown_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating countdown: {e}")
            return False

    def delete_countdown(self, countdown_id: str) -> bool:
        """Delete a countdown item"""
        try:
            if countdown_id not in self.countdowns:
                return False
            
            title = self.countdowns[countdown_id]["title"]
            del self.countdowns[countdown_id]
            self._save_data()
            
            logger.info(f"Deleted countdown: {title} (ID: {countdown_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting countdown: {e}")
            return False

    def get_countdown(self, countdown_id: str) -> Optional[Dict]:
        """Get a specific countdown item"""
        if countdown_id not in self.countdowns:
            return None
        
        countdown = self.countdowns[countdown_id].copy()
        countdown["days_remaining"] = self._calculate_days_remaining(countdown["target_date"])
        return countdown

    def get_all_countdowns(self) -> List[Dict]:
        """Get all countdown items with calculated days remaining"""
        countdowns = []
        
        for countdown_id, countdown_data in self.countdowns.items():
            countdown = countdown_data.copy()
            countdown["days_remaining"] = self._calculate_days_remaining(countdown["target_date"])
            countdowns.append(countdown)
        
        # Sort by days remaining (ascending)
        countdowns.sort(key=lambda x: x["days_remaining"])
        
        return countdowns

    def get_active_countdowns(self) -> List[Dict]:
        """Get only countdowns that haven't passed yet"""
        all_countdowns = self.get_all_countdowns()
        return [c for c in all_countdowns if c["days_remaining"] >= 0]

    def cleanup_expired_countdowns(self, days_threshold: int = -30) -> int:
        """Remove countdowns that are older than threshold days"""
        expired_ids = []
        
        for countdown_id, countdown_data in self.countdowns.items():
            days_remaining = self._calculate_days_remaining(countdown_data["target_date"])
            if days_remaining < days_threshold:
                expired_ids.append(countdown_id)
        
        for countdown_id in expired_ids:
            del self.countdowns[countdown_id]
        
        if expired_ids:
            self._save_data()
            logger.info(f"Cleaned up {len(expired_ids)} expired countdowns")
        
        return len(expired_ids)
