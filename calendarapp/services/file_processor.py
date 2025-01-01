# calendarapp/services/file_processor.py

import pandas as pd
import os
from django.conf import settings
from datetime import datetime, timedelta
import logging
from ..models import Event, Task
from .scrapers import BlackboardScraper, EdusoftScraper
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class FileProcessor:
    """Process educational timetable files and sync to calendar"""
    async def process_blackboard(self, username, password):
        try:
            scraper = BlackboardScraper(username, password)
            bb_dir = os.path.join(self.base_dir, 'blackboard')
            os.makedirs(bb_dir, exist_ok=True)

            file_path = os.path.join(bb_dir, f'{username}_bb.csv')
            scraper.scrape(file_path)
            return self.process_blackboard_csv(username, file_path)
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def process_edusoft(self, username, password):
        try:
            # Create directories
            edusoft_dir = os.path.join(self.base_dir, 'edusoftweb', username)
            os.makedirs(edusoft_dir, exist_ok=True)
            files_dir = os.path.join(edusoft_dir, 'files')
            os.makedirs(files_dir, exist_ok=True)

            scraper = EdusoftScraper(username, password)
            zip_path = os.path.join(edusoft_dir, f'{username}_timetable.zip')
            scraper.scrape(zip_path)
            return self.process_edusoft_zip(username, zip_path)
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def __init__(self, user):
        self.user = user
        self.base_dir = settings.MEDIA_ROOT
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, 'blackboard'), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, 'edusoftweb'), exist_ok=True)

    # @sync_to_async
    # def clear_user_data(self):
    #     """Clear all user's events and tasks before syncing"""
    #     try:
    #         events_deleted = Event.objects.filter(user=self.user).delete()[0]
    #         tasks_deleted = Task.objects.filter(user=self.user).delete()[0]
            
    #         logger.info(f"Cleared {events_deleted} events and {tasks_deleted} tasks for user {self.user.email}")
            
    #         return {
    #             'status': 'success',
    #             'events_deleted': events_deleted,
    #             'tasks_deleted': tasks_deleted,
    #             'message': f'Cleared {events_deleted} events and {tasks_deleted} tasks'
    #         }
    #     except Exception as e:
    #         logger.error(f"Error clearing user data: {str(e)}")
    #         return {
    #             'status': 'error',
    #             'message': f'Error clearing data: {str(e)}'
    #         }
    @sync_to_async
    def clear_event_data(self):
        try:
            events_deleted = Event.objects.filter(user=self.user).delete()[0]
            
            logger.info(f"Cleared {events_deleted} events for user {self.user.email}")
            
            return {
                'status': 'success',
                'events_deleted': events_deleted,
                'message': f'Cleared {events_deleted} events'
            }
        except Exception as e:
            logger.error(f"Error clearing event data: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error clearing data: {str(e)}'
            }
    @sync_to_async
    def clear_task_data(self):
        try:
            tasks_deleted = Task.objects.filter(user=self.user).delete()[0]
            
            logger.info(f"Cleared {tasks_deleted} tasks for user {self.user.email}")
            
            return {
                'status': 'success',
                'tasks_deleted': tasks_deleted,
                'message': f'Cleared {tasks_deleted} tasks'
            }
        except Exception as e:
            logger.error(f"Error clearing task data: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error clearing data: {str(e)}'
            }

    def process_edusoft_zip(self, username):
        """Process Edusoft schedule files from zip"""
        try:
            # Clear existing data first
            clear_result = self.clear_event_data()
            if clear_result['status'] != 'success':
                raise Exception(clear_result['message'])
            
            directory = os.path.join(self.base_dir, f"{username}_edusoftweb")
            if not os.path.exists(directory):
                logger.error(f"Directory not found: {directory}")
                raise Exception("Directory not found")

            csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
            if not csv_files:
                logger.error("No CSV files found in directory")
                raise Exception("No CSV files found")

            total_events = 0
            processed_data = []

            for csv_file in csv_files:
                try:
                    file_path = os.path.join(directory, csv_file)
                    logger.info(f"Processing file: {csv_file}")
                    
                    df = pd.read_csv(file_path)
                    semester_data = self._process_timetable(df)
                    processed_data.extend(semester_data)
                    
                except Exception as e:
                    logger.error(f"Error processing {csv_file}: {str(e)}")
                    continue

            for course in processed_data:
                try:
                    events_created = self._create_recurring_events(course)
                    total_events += events_created
                except Exception as e:
                    logger.error(f"Error creating events for course: {str(e)}")
                    continue

            return {
                'status': 'success',
                'message': f'Successfully processed {len(csv_files)} files and created {total_events} events',
                'files_processed': len(csv_files),
                'events_created': total_events,
                'items_cleared': clear_result['events_deleted']
            }

        except Exception as e:
            logger.error(f"Error in process_edusoft_zip: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def process_blackboard_file(self, username):
        """Process Blackboard assignments file"""
        try:
            # Clear existing data first
            clear_result = self.clear_task_data()
            if clear_result['status'] != 'success':
                raise Exception(clear_result['message'])
            
            file_path = os.path.join(self.base_dir, f"{username}_blackboard", f"{username}_bb.csv")
            if not os.path.exists(file_path):
                logger.error(f"Blackboard CSV file not found: {file_path}")
                raise Exception("Blackboard CSV file not found")

            result = self._process_blackboard_tasks(file_path)
            
            if result['status'] == 'success':
                tasks_created = 0
                for task_data in result['tasks']:
                    try:
                        task, created = Task.objects.get_or_create(
                            user=self.user,
                            title=task_data['title'],
                            deadline=task_data['deadline'],
                            defaults={
                                'description': task_data['description'],
                                'is_completed': False,
                                'is_active': True,
                                'is_deleted': False
                            }
                        )
                        if created:
                            tasks_created += 1
                    except Exception as e:
                        logger.error(f"Error creating task: {str(e)}")
                        continue

                return {
                    'status': 'success',
                    'message': f'Successfully created {tasks_created} tasks',
                    'tasks_created': tasks_created,
                    'items_cleared': clear_result['tasks_deleted']
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error processing Blackboard file: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    

    async def process_edusoft_timetable(self, username):
        """Process Edusoft schedule files"""
        try:
            # Clear existing data first
            clear_result = await self.clear_event_data()
            if clear_result['status'] != 'success':
                raise Exception(clear_result['message'])
            
            # Get the directory for this user's timetables
            user_dir = os.path.join(self.base_dir, 'edusoftweb', username)
            
            # Debug logging
            print(f"Looking for files in: {user_dir}")
            if os.path.exists(user_dir):
                print(f"Directory contents: {os.listdir(user_dir)}")
            else:
                print("Directory does not exist")
            
            if not os.path.exists(user_dir):
                raise Exception("No timetable files found for user")

            # Find all CSV files
            csv_files = [f for f in os.listdir(user_dir) if f.endswith('_timetable.csv')]
            if not csv_files:
                raise Exception("No timetable files found")

            total_events = 0
            processed_data = []

            for csv_file in csv_files:
                try:
                    file_path = os.path.join(user_dir, csv_file)
                    print(f"Processing file: {file_path}")
                    
                    df = pd.read_csv(file_path)
                    semester_data = await self._process_timetable(df)
                    processed_data.extend(semester_data)
                    
                except Exception as e:
                    print(f"Error processing {csv_file}: {str(e)}")
                    continue

            # Create events from processed data
            for course in processed_data:
                try:
                    events_created = await self._create_recurring_events(course)
                    total_events += events_created
                except Exception as e:
                    print(f"Error creating events for course: {str(e)}")
                    continue

            return {
                'status': 'success',
                'message': f'Successfully processed {len(csv_files)} files and created {total_events} events',
                'files_processed': len(csv_files),
                'events_created': total_events
            }

        except Exception as e:
            print(f"Error in process_edusoft_timetable: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    @sync_to_async
    def _process_timetable(self, df):
        """Process the Edusoft timetable dataframe into standardized format"""
        processed_courses = []
        
        for index, row in df.iterrows():
            try:
                # Use proper column names instead of indices
                column_map = {
                    'course_name': 1,  # Column 1: Course name
                    'lab_indicator': 7,  # Column 7: Lab indicator
                    'room': 11,  # Column 11: Room
                    'day': 8,  # Column 8: Day
                    'date_range': 13,  # Column 13: Date range
                    'start_period': 9,  # Column 9: Start period
                    'duration': 10  # Column 10: Duration
                }
                
                course_name = row.iloc[column_map['course_name']]  
                is_lab = not pd.isna(row.iloc[column_map['lab_indicator']])
                room = str(row.iloc[column_map['room']])
                day = self._convert_vietnamese_day(row.iloc[column_map['day']])
                date_range = row.iloc[column_map['date_range']]

                start_time, end_time = self._calculate_time(
                    start_period=row.iloc[column_map['start_period']],
                    duration=row.iloc[column_map['duration']]
                )

                if not start_time or not end_time:
                    logging.warning(f"Could not calculate times for row {index}")
                    continue

                title = f"{course_name}{' (Lab)' if is_lab else ''}"

                processed_courses.append({
                    'title': title,
                    'description': f"Room: {room}",
                    'start_time': start_time,
                    'end_time': end_time,
                    'day': day,
                    'date_range': date_range
                })

                logging.info(f"Processed course: {title}")

            except Exception as e:
                logging.error(f"Error processing row {index}: {str(e)}")
                continue

        return processed_courses

    def _process_blackboard_tasks(self, file_path):
        """Process Blackboard CSV into tasks"""
        try:
            df = pd.read_csv(file_path)
            processed_tasks = []
            
            for _, row in df.iterrows():
                try:
                    course_name = row['name']
                    is_lab = row['is_lab']
                    task_name = row['task_name']
                    
                    course_title = f"{course_name}{' (Lab)' if is_lab else ''}"
                    
                    if pd.notna(row['due_date']) and pd.notna(row['due_time']):
                        try:
                            date_str = row['due_date']
                            time_str = row['due_time']
                            deadline = self._parse_deadline(date_str, time_str)
                            
                            processed_tasks.append({
                                'title': task_name,
                                'description': f"Course: {course_title}",
                                'deadline': deadline
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing deadline: {str(e)}")
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing task row: {str(e)}")
                    continue

            return {
                'status': 'success',
                'message': f'Successfully processed {len(processed_tasks)} tasks',
                'tasks': processed_tasks
            }

        except Exception as e:
            logger.error(f"Error processing Blackboard CSV: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _convert_vietnamese_day(self, vn_day):
        """Convert Vietnamese day name to English"""
        day_mapping = {
            'Hai': 'Monday',
            'Ba': 'Tuesday',
            'Tư': 'Wednesday',
            'Năm': 'Thursday',
            'Sáu': 'Friday',
            'Bảy': 'Saturday',
            'Chủ Nhật': 'Sunday',
            # Add variations without diacritics
            'Tu': 'Wednesday',
            'Nam': 'Thursday',
            'Sau': 'Friday',
            'Bay': 'Saturday',
            'Chu Nhat': 'Sunday'
        }
        return day_mapping.get(vn_day.strip(), vn_day)

    def _calculate_time(self, start_period, duration):
        """Calculate actual start and end times based on period and duration"""
        shift_starts = {
            1: "08:00",  # First shift: 8:00 AM - 10:30 AM
            4: "10:35",  # Second shift: 10:35 AM - 1:00 PM
            7: "13:15",  # Third shift: 1:15 PM - 3:45 PM
            10: "15:50"  # Fourth shift: 3:50 PM - 6:30 PM
        }

        try:
            for shift_start_period, time in shift_starts.items():
                if start_period >= shift_start_period and start_period < shift_start_period + 3:
                    # Calculate start time
                    start_hour, start_minute = map(int, time.split(":"))
                    minutes_to_add = (start_period - shift_start_period) * 50
                    total_start_minutes = start_hour * 60 + start_minute + minutes_to_add
                    
                    # Calculate end time
                    total_end_minutes = total_start_minutes + (duration * 50)

                    # Format times
                    start_time = f"{total_start_minutes // 60:02d}:{total_start_minutes % 60:02d}"
                    end_time = f"{total_end_minutes // 60:02d}:{total_end_minutes % 60:02d}"

                    return start_time, end_time

        except Exception as e:
            logger.error(f"Error calculating time: {str(e)}")
            return None, None

        logger.warning(f"No valid shift found for period {start_period}")
        return None, None

    def _parse_deadline(self, date_str, time_str):
        """Parse deadline from date and time strings"""
        try:
            date_obj = datetime.strptime(date_str, '%m/%d/%Y').date()
            time_obj = datetime.strptime(time_str, '%I:%M %p').time()
            return datetime.combine(date_obj, time_obj)
        except Exception as e:
            raise Exception(f"Error parsing deadline: {str(e)}")
        
    @sync_to_async
    def _create_recurring_events(self, course_data):
        """Create recurring events for a course within its date range"""
        try:
            start_date, end_date = self._parse_date_range(course_data['date_range'])
            start_time = datetime.strptime(course_data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(course_data['end_time'], '%H:%M').time()

            events_created = 0
            current_date = start_date

            while current_date <= end_date:
                if self._get_day_name(current_date) == course_data['day']:
                    event_start = datetime.combine(current_date, start_time)
                    event_end = datetime.combine(current_date, end_time)

                    event, created = Event.objects.get_or_create(
                        user=self.user,
                        title=course_data['title'],
                        start_time=event_start,
                        end_time=event_end,
                        defaults={
                            'description': course_data['description'],
                            'is_active': True,
                            'is_deleted': False
                        }
                    )

                    if created:
                        events_created += 1
                        logger.info(f"Created event: {course_data['title']} on {current_date}")

                current_date += timedelta(days=1)

            return events_created

        except Exception as e:
            logger.error(f"Error creating recurring events: {str(e)}")
            raise

    def _parse_date_range(self, date_range_str):
        """Parse date range string into start and end dates"""
        try:
            # Remove any extra quotes and spaces
            date_range_str = date_range_str.strip("'\"").strip()
            
            # Split on double dash
            start_str, end_str = date_range_str.split('--')
            
            # Convert to datetime objects
            start_date = datetime.strptime(start_str.strip(), '%d/%m/%Y').date()
            end_date = datetime.strptime(end_str.strip(), '%d/%m/%Y').date()
            
            return start_date, end_date
        except Exception as e:
            logger.error(f"Error parsing date range '{date_range_str}': {str(e)}")
            raise Exception(f"Error parsing date range: {str(e)}")

    def _get_day_name(self, date):
        """Get day name from date object"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[date.weekday()]
    
    
    async def process_blackboard_csv(self, username, file_path):
        
        try:
            # Clear existing data first
            clear_result = await self.clear_task_data()
            if clear_result['status'] != 'success':
                raise Exception(clear_result['message'])
            
            if not os.path.exists(file_path):
                logger.error(f"Blackboard CSV file not found: {file_path}")
                raise Exception("Blackboard CSV file not found")

            try:
                df = pd.read_csv(file_path)
                tasks_created = 0
                
                for _, row in df.iterrows():
                    if pd.notna(row['due_date']) and pd.notna(row['due_time']):
                        try:
                            deadline = self._parse_deadline(row['due_date'], row['due_time'])
                            title = row['task_name']
                            course_name = f"{row['name']}{'(Lab)' if row['is_lab'] else ''}"
                            
                            task, created = await sync_to_async(Task.objects.get_or_create)(
                                user=self.user,
                                title=title,
                                description=f"Course: {course_name}",
                                deadline=deadline,
                                defaults={
                                    'is_completed': False,
                                    'is_active': True,
                                    'is_deleted': False
                                }
                            )
                            if created:
                                tasks_created += 1
                        except Exception as e:
                            logger.error(f"Error creating task: {str(e)}")
                            continue
                            
                return {
                    'status': 'success',
                    'tasks_created': tasks_created,
                    'message': f'Successfully created {tasks_created} tasks'
                }
                
            except pd.errors.EmptyDataError:
                return {
                    'status': 'error',
                    'message': 'The CSV file is empty'
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Error processing CSV: {str(e)}'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }