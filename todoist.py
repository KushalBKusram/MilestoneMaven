import os
import requests
from typing import Union, List

from loguru import logger
from pydantic import BaseModel
from todoist_api_python.api import TodoistAPI

class Task(BaseModel):
    title: str
    id: str
    due: Union[str, None]
    progress: float


class Todoist:
    def __init__(self):
        self.api = TodoistAPI(os.environ.get('API_KEY'))
        self.label = os.environ.get('LABEL')
        logger.info("Todoist API initialized successfully.")

    def get_tracked_task_objs(self) -> List[Task]:
        task_objs = []
        try:
            logger.info("Getting tracked tasks... ")
            tasks = self.api.get_tasks()
            for task in tasks:
                if self.label in task.labels:
                    logger.info(f"Working on Task ID: {task.id} Task Title: {task.content}")
                    task_obj = Task(title=task.content,
                                    id=task.id,
                                    due=task.due.string if task.due else None,
                                    progress=self.get_task_progress(task.id))
                    logger.info(f"Following Task ID: {task.id} Task Title: {task.content} is prepared.")
                    task_objs.append(task_obj)
            logger.info("Received tracked tasks!")
            return task_objs
        except Exception as error:
            logger.error(error)
            return None
        
    def get_all_completed_tasks(self) -> dict:
        url = "https://api.todoist.com/sync/v9/completed/get_all"
        headers = {
            'Authorization': f'Bearer {os.environ.get("API_KEY")}'
        }
        logger.info("Requesting completed tasks list... ")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            logger.info("Received completed tasks list!")
            return data['items']
        else:
            logger.error("Unable to retrieve completed tasks data!")
            logger.error(f"{response}")

    def get_task_progress(self, task_id: str) -> float:
        total_progress = 0.0
        completed_tasks_count = 0
        pending_tasks_count = 0

        logger.info(f"Computing task progress for Task ID: {task_id}")
        completed_tasks = self.get_all_completed_tasks()
        for completed_task in completed_tasks:
            task = self.api.get_task(completed_task['task_id'])
            if task.parent_id == task_id:
                completed_tasks_count += 1

        tasks = self.api.get_tasks()
        for task in tasks:
            if task.parent_id == task_id:
                pending_tasks_count += 1

        if pending_tasks_count > 0:
            total_progress = completed_tasks_count / pending_tasks_count
        logger.info(f"Computed total progress for Task ID: {task_id}")

        return total_progress
