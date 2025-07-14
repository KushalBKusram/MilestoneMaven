import asyncio
import os
import time
import requests
import threading
from datetime import datetime
from loguru import logger

from repositories.todoist import Todoist


class TrmnlService:
    def __init__(self, countdown_service):
        self.countdown_service = countdown_service
        self.todoist = Todoist()
        self.todoist_endpoint = os.environ.get('TODOIST_ENDPOINT', 'https://usetrmnl.com/api/custom_plugins/todoist_endpoint')
        self.countdown_endpoint = os.environ.get('COUNTDOWN_ENDPOINT', 'https://usetrmnl.com/api/custom_plugins/countdown_endpoint')
        # Get polling interval from environment (in minutes), default to 12 hours (720 minutes)
        polling_minutes = int(os.environ.get('TRMNL_POLLING_INTERVAL_MINUTES', '720'))
        self.interval = polling_minutes * 60  # Convert minutes to seconds
        self.running = False

    def start(self):
        """Start the TRMNL service"""
        self.running = True
        polling_minutes = self.interval // 60
        logger.info(f"TRMNL service started - will run every {polling_minutes} minutes")
        
        # Run immediately on startup
        self._run_cycle()
        
        # Then run at the configured interval
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self._run_cycle()

    def stop(self):
        """Stop the TRMNL service"""
        self.running = False
        logger.info("TRMNL service stopped")

    def _run_cycle(self):
        """Run one complete cycle of data collection and posting"""
        logger.info("Starting TRMNL service cycle...")
        
        try:
            # Post Todoist data
            self._post_todoist_data()
            
            # Post countdown data
            self._post_countdown_data()
            
            logger.info("TRMNL service cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in TRMNL service cycle: {e}")

    def _post_todoist_data(self):
        """Fetch Todoist data and post to endpoint"""
        try:
            logger.info("Fetching Todoist data...")
            
            # Run async function in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                task_objs = loop.run_until_complete(self.todoist.get_tracked_task_objs())
            finally:
                loop.close()
            
            if task_objs is None:
                logger.error("Failed to fetch Todoist tasks")
                return
            
            # Prepare payload with only title and progress
            tasks_data = []
            for task in task_objs:
                # Format progress as percentage (xx.xx%)
                progress_percentage = f"{task.progress*100:.2f}%"
                tasks_data.append({
                    "title": task.title,
                    "progress": progress_percentage
                })
            
            payload = {
                "merge_variables": {
                    "tasks": tasks_data,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "total_tasks": len(tasks_data)
                }
            }
            
            # Post to endpoint
            logger.info(f"Posting Todoist data to {self.todoist_endpoint}")
            response = requests.post(
                self.todoist_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Todoist data posted successfully")
            else:
                logger.error(f"Failed to post Todoist data. Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            logger.error(f"Error posting Todoist data: {e}")

    def _post_countdown_data(self):
        """Fetch countdown data and post to endpoint"""
        try:
            logger.info("Fetching countdown data...")
            
            countdowns = self.countdown_service.get_all_countdowns()
            
            # Prepare payload
            countdowns_data = []
            for countdown in countdowns:
                countdowns_data.append({
                    "title": countdown["title"],
                    "days_remaining": countdown["days_remaining"]
                })
            
            payload = {
                "merge_variables": {
                    "countdowns": countdowns_data,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "total_countdowns": len(countdowns_data)
                }
            }
            
            # Post to endpoint
            logger.info(f"Posting countdown data to {self.countdown_endpoint}")
            response = requests.post(
                self.countdown_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Countdown data posted successfully")
            else:
                logger.error(f"Failed to post countdown data. Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            logger.error(f"Error posting countdown data: {e}")
