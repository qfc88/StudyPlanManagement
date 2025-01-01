from .file_processor import FileProcessor
from django.core.exceptions import ValidationError
from .scrapers import EdusoftScraper
from .scrapers import BlackboardScraper
import os

class SyncService:
    @staticmethod
    async def sync_edusoft_schedule(user, username, password):
        """
        Sync Edusoft schedule with calendar events
        
        Args:
            user: Django user object
            username: Edusoft username
            password: Edusoft password
            
        Returns:
            dict: Status and results of the sync operation
        """
        try:
            # First, scrape the data
            scraper = EdusoftScraper(username, password)
            scrape_result = await scraper.scrape()
            
            if scrape_result['status'] != 'success':
                raise ValidationError(scrape_result['message'])

            # Process the scraped files
            processor = FileProcessor(user)
            process_result = await processor.process_edusoft_timetable(username)
            
            if process_result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': process_result['message'],
                    'data': {
                        'events_created': process_result['events_created'],
                        'files_processed': process_result['files_processed']
                    }
                }
            else:
                raise ValidationError(process_result['message'])

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to sync Edusoft schedule: {str(e)}'
            }

    @staticmethod
    async def sync_blackboard_tasks(user, username, password):
        """Sync Blackboard assignments with tasks"""
        try:
            # Initialize processor
            processor = FileProcessor(user)
            
            # First scrape the data
            scraper = BlackboardScraper(username, password)
            result = await scraper.scrape()
            
            if not result or not os.path.exists(result):
                raise ValidationError("Failed to fetch Blackboard data")

            # Now process the scraped file
            process_result = await processor.process_blackboard_csv(username, result)
            
            if process_result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': process_result['message'],
                    'data': {
                        'tasks_created': process_result.get('tasks_created', 0)
                    }
                }
            else:
                raise ValidationError(process_result['message'])

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to sync Blackboard tasks: {str(e)}'
            }