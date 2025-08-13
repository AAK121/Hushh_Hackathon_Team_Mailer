"""
Windows-compatible scheduler using APScheduler with database backend
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import create_engine
import os

from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from .models import Reminder
from .db import get_session

logger = logging.getLogger(__name__)

class ReminderEngine:
    """Manages reminder scheduling and execution using APScheduler"""
    
    def __init__(self):
        # Initialize scheduler with PostgreSQL job store
        jobstores = {
            'default': SQLAlchemyJobStore(url=os.getenv('DATABASE_URL'))
        }
        
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()
        logger.info("APScheduler started successfully")
    
    def schedule_reminder(self, reminder: Reminder) -> str:
        """Schedule a new reminder"""
        try:
            # Create the job ID
            job_id = f"reminder_{reminder.id}_{reminder.user_id}"
            
            # Schedule one-time or recurring reminder
            if reminder.recurrence:
                # Convert recurrence string to cron trigger
                cron_trigger = self._get_cron_trigger(reminder.recurrence, reminder.scheduled_at)
                self.scheduler.add_job(
                    self._send_reminder_notification,
                    trigger=cron_trigger,
                    args=[reminder.id],
                    id=job_id,
                    replace_existing=True
                )
            else:
                # One-time reminder
                self.scheduler.add_job(
                    self._send_reminder_notification,
                    trigger=DateTrigger(run_date=reminder.scheduled_at),
                    args=[reminder.id],
                    id=job_id,
                    replace_existing=True
                )
            
            logger.info(f"Scheduled reminder {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {str(e)}")
            raise
    
    def cancel_reminder(self, reminder_id: int) -> None:
        """Cancel a scheduled reminder"""
        try:
            session = get_session()
            reminder = session.query(Reminder).get(reminder_id)
            
            if reminder:
                job_id = f"reminder_{reminder.id}_{reminder.user_id}"
                self.scheduler.remove_job(job_id)
                
                reminder.status = "cancelled"
                session.commit()
                
                logger.info(f"Cancelled reminder {reminder_id}")
            
        except Exception as e:
            logger.error(f"Error cancelling reminder: {str(e)}")
            raise
    
    def _send_reminder_notification(self, reminder_id: int) -> None:
        """Send a reminder notification"""
        try:
            session = get_session()
            reminder = session.query(Reminder).get(reminder_id)
            
            if not reminder:
                logger.error(f"Reminder {reminder_id} not found")
                return
            
            # TODO: Implement notification sending logic
            # This could involve:
            # 1. Sending email
            # 2. Push notification
            # 3. Webhook to frontend
            # 4. Integration with messaging platforms
            
            # Update reminder status
            reminder.status = "sent"
            session.commit()
            
            logger.info(f"Sent reminder notification for {reminder_id}")
            
        except Exception as e:
            logger.error(f"Error sending reminder notification: {str(e)}")
            raise
    
    def _get_cron_trigger(self, recurrence: str, scheduled_at: datetime) -> CronTrigger:
        """Convert recurrence string to cron trigger"""
        # Parse recurrence string and create appropriate cron trigger
        if recurrence == "daily":
            return CronTrigger(
                hour=scheduled_at.hour,
                minute=scheduled_at.minute
            )
        elif recurrence == "weekly":
            return CronTrigger(
                day_of_week=scheduled_at.weekday(),
                hour=scheduled_at.hour,
                minute=scheduled_at.minute
            )
        elif recurrence == "monthly":
            return CronTrigger(
                day=scheduled_at.day,
                hour=scheduled_at.hour,
                minute=scheduled_at.minute
            )
        elif recurrence == "yearly":
            return CronTrigger(
                month=scheduled_at.month,
                day=scheduled_at.day,
                hour=scheduled_at.hour,
                minute=scheduled_at.minute
            )
        else:
            raise ValueError(f"Unsupported recurrence pattern: {recurrence}")
