from playwright.async_api import async_playwright
from termcolor import colored
import pandas as pd
import re
import ast
import time

import os
import logging

start_time = time.time()



class BlackboardScraper:
    start_time = time.time()
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_dir = os.path.join('media', 'blackboard')
        os.makedirs(self.base_dir, exist_ok=True)

    async def scrape(self):
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                #Login
                await page.goto('https://blackboard.hcmiu.edu.vn/')
                await page.fill('input#user_id', self.username)
                await page.fill('input#password', self.password)
                await page.click('input#entry-login')
                print(colored('Logged in ' + self.username, 'cyan', attrs=['bold']))
                await page.wait_for_selector('button#global-nav-link.nav-link.u_floatThis-right')
                await page.goto('https://blackboard.hcmiu.edu.vn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_2_1')
                await page.wait_for_selector('button#global-nav-link.nav-link.u_floatThis-right')
                
                print(colored('Begin to scrape' , 'cyan', attrs=['bold']))
                await page.wait_for_timeout(500)
                
                course_container = await page.query_selector('div#div_22_1 > div#_22_1termCourses_noterm')
                course_elements = await course_container.query_selector_all('ul.portletList-img.courseListing.coursefakeclass > li')
                
                output = []
                course_ids = []
                tab_ids = []
                content_ids = []
                content_list_items = []  # New list for content items
                
                for element in course_elements:
                    text = await element.inner_text()
                    output.append(text)
                    
                    link = await element.query_selector('a')
                    if link:
                        href = await link.get_attribute('href')
                        id_match = re.search(r'id=(_\d+_\d+)', href)
                        course_id = id_match.group(1) if id_match else None
                        course_ids.append(course_id)
                        
                        if course_id:
                            try:
                                course_page = await browser.new_page()
                                
                                # Login for course page
                                await course_page.goto('https://blackboard.hcmiu.edu.vn/')
                                await course_page.fill('input#user_id', self.username)
                                await course_page.fill('input#password', self.password)
                                await course_page.click('input#entry-login')
                                await course_page.wait_for_selector('button#global-nav-link.nav-link.u_floatThis-right')
                                
                                # Get to course page
                                initial_url = f'https://blackboard.hcmiu.edu.vn/webapps/blackboard/execute/launcher?type=Course&id={course_id}&url='
                                await course_page.goto(initial_url)
                                await course_page.wait_for_timeout(1000)
                                
                                current_url = course_page.url
                                
                                # Get tab_id
                                tab_match = re.search(r'cmp_tab_id=([^&]+)', current_url)
                                tab_id = tab_match.group(1) if tab_match else None
                                tab_ids.append(tab_id)
                                
                                # Find and get content_id from Assignments link
                                assignment_link = await course_page.query_selector_all('div.menuWrap-inner > div#courseMenuPalette.navPalette.listCm.navPaletteExpCol > div.navPaletteContent > ul#courseMenuPalette_contents > li')
                                assignments_link = None
                                for e in assignment_link:
                                    text = await e.inner_text()
                                    if 'Assignments' in text:
                                        assignments_link = e
                                        break
                                
                                content_id = None
                                if assignments_link:
                                    anchor = await assignments_link.query_selector('a')
                                    if anchor:
                                        href = await anchor.get_attribute('href')
                                        content_match = re.search(r'content_id=(_\d+_\d+)', href)
                                        content_id = content_match.group(1) if content_match else None
                                        content_ids.append(content_id)
                                        print(colored(f'Found content ID: {content_id}', 'green'))
                                        
                                        # Get content list items if we have content_id
                                        if content_id:
                                            try:
                                                content_url = f"https://blackboard.hcmiu.edu.vn/webapps/blackboard/content/listContent.jsp?course_id={course_id}&content_id={content_id}&mode=reset"
                                                await course_page.goto(content_url)
                                                await course_page.wait_for_load_state('networkidle')
                                                
                                                await course_page.wait_for_selector('#content_listContainer', timeout=500)
                                                items = await course_page.query_selector_all('li[id^="contentListItem:"]')
                                                
                                                items_list = []
                                                for item in items:
                                                    item_id = await item.get_attribute('id')
                                                    if item_id:
                                                        item_number = item_id.split(':')[1]
                                                        items_list.append(item_number)
                                                
                                                content_list_items.append(items_list)
                                                print(colored(f'Found {len(items_list)} content items', 'green'))
                                            except Exception as e:
                                                print(colored(f'Error getting content items: {str(e)}', 'yellow'))
                                                content_list_items.append(None)
                                        else:
                                            content_list_items.append(None)
                                    else:
                                        content_ids.append(None)
                                        content_list_items.append(None)
                                else:
                                    content_ids.append(None)
                                    content_list_items.append(None)
                                
                                await course_page.close()
                                print(colored(f'Extracted IDs for course {course_id}', 'green'))
                                
                            except Exception as e:
                                print(colored(f'Error accessing course {course_id}: {str(e)}', 'red'))
                                if len(tab_ids) < len(course_ids): tab_ids.append(None)
                                if len(content_ids) < len(course_ids): content_ids.append(None)
                                if len(content_list_items) < len(course_ids): content_list_items.append([])
                        else:
                            tab_ids.append(None)
                            content_ids.append(None)
                            content_list_items.append([])
                    else:
                        course_ids.append(None)
                        tab_ids.append(None)
                        content_ids.append(None)
                        content_list_items.append([])
                
                get_output = "".join(output)
                get_output = get_output.split(";")
                parsed_courses = parse_courses(get_output, course_ids, tab_ids, content_ids, content_list_items)

                # Create DataFrame
                assignment = pd.DataFrame({})
                for course in parsed_courses:
                    df = pd.DataFrame([course])
                    if df is not None:
                        assignment = assignment._append(df)
                assignments = explode_content_items(assignment)
                
                # Add new columns for deadlines
                assignments['due_date'] = pd.Series(dtype=str)
                assignments['due_time'] = pd.Series(dtype=str)
                
                # Get deadlines for each assignment
                print(colored('Begin extracting deadlines...', 'cyan', attrs=['bold']))
                
                due_dates = []
                due_times = []
                task_names = []

                for index, row in assignments.iterrows():
                    content_id = row['content_items']
                    course_id = row['course_id']
                    
                    if pd.notna(content_id) and pd.notna(course_id):
                        due_date, due_time, title = await get_assignment_deadlines(page, course_id, content_id)
                        # assignments.at[index, 'due_date'] = str(due_date)
                        # assignments.at[index, 'due_time'] = due_time
                        due_dates.append(due_date)
                        due_times.append(due_time)
                        task_names.append(title)


                        # assignments.at[index, 'due_time'] = str(due_time)
                        
                        if due_date or due_time:
                            print(colored(f'Found deadline for {title} {content_id}: {due_date} {due_time}', 'green'))
                    else:
                        due_dates.append(None)
                        due_times.append(None)                    
                        task_names.append(None)
                    await page.wait_for_timeout(500)  # Small delay between requests

                assignments['due_date'] = due_dates
                assignments['due_time'] = due_times
                assignments['task_name'] = task_names
                print(colored('Finished extracting deadlines', 'cyan', attrs=['bold']))
                blackboard_dir = os.path.join(self.base_dir, self.username)
                os.makedirs(blackboard_dir, exist_ok=True)
                path = os.path.join(blackboard_dir, f"{self.username}_bb.csv")
                assignments.to_csv(path, index=False, encoding='utf-8-sig')
                await browser.close()
                
                processing_time = time.time() - start_time
                print("--- %s seconds ---" % processing_time)
                
                assignments.to_csv(path, index=False, encoding='utf-8-sig')
                return path

        except Exception as e:
            logging.error(f"Blackboard scraping error: {str(e)}")
            raise
async def get_assignment_deadlines(page, course_id, content_id):
    """Get due date and time for an assignment"""
    try:
        url = f"https://blackboard.hcmiu.edu.vn/webapps/assignment/uploadAssignment?content_id={content_id}&course_id={course_id}&group_id=&mode=view"
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        
        # Look for due date 
        container = await page.query_selector('div.metaWrapper.clearfix')
        due_date_container = await page.query_selector('div.metaSection:has(div.metaLabel:text-is("Due Date"))')
        title = await page.locator("#pageTitleText").text_content()
        if container:
            if due_date_container:
                date_field = await due_date_container.query_selector('div.metaField')
                if date_field:
                    full_text = await date_field.inner_text()
                    parts = full_text.split('\n')
                    
                    date_str = parts[0].strip() if parts else None
                    time_str = None
                    
                    if len(parts) > 1:
                        time_match = re.search(r'\d{1,2}:\d{2}\s*[APM]{2}', parts[1])
                        if time_match:
                            time_str = time_match.group()
                    
                    return date_str, time_str, title
            else:
                return "No due date", "No due time", title
        else:
            return None, None, title
    except Exception as e:
        print(colored(f'Error getting deadline for content {content_id}: {str(e)}', 'yellow'))
    
    return None, None

def parse_courses(course_list, course_ids, tab_ids, content_ids, content_list_items):
    courses = []
    current_course = None
    id_index = 0
    
    for entry in course_list:
        if entry.strip() == "":
            continue
        
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        
        for line in lines:
            if line.startswith('Tasks:') or line.startswith('Announcements:'):
                continue
            
            if '_' in line and (':' in line or 'Lab' in line):
                if current_course:
                    courses.append(current_course)
                    id_index += 1
                
                parts = line.split(':', 1)
                course_code = parts[0].strip()
                course_name = parts[1].strip() if len(parts) > 1 else ''
                
                current_course = {
                    'code': course_code,
                    'name': course_name,
                    'instructor': None,
                    'is_lab': 'Lab' in line,
                    'semester': extract_semester(line),
                    'group': extract_group(line),
                    'course_id': course_ids[id_index] if id_index < len(course_ids) else None,
                    'tab_id': tab_ids[id_index] if id_index < len(tab_ids) else None,
                    'content_id': content_ids[id_index] if id_index < len(content_ids) else None,
                    'content_items': content_list_items[id_index] if id_index < len(content_list_items) else None
                }
            
            elif line.startswith('Instructor:'):
                if current_course:
                    current_course['instructor'] = line.replace('Instructor:', '').strip()
    
    if current_course:
        courses.append(current_course)
    
    return courses

def explode_content_items(df: pd.DataFrame, column: str = 'content_items') -> pd.DataFrame:
    df_copy = df.copy()

    df_copy[column] = df_copy[column].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x
    )

    result_df = df_copy.explode(column)
    
    return result_df

def generate_assignment_url(course_id, content_id):
    """Generate assignment URL from course_id and content_id"""
    if course_id and content_id:
        return f"https://blackboard.hcmiu.edu.vn/webapps/blackboard/content/listContent.jsp?course_id={course_id}&content_id={content_id}&mode=reset"
    return None
def extract_semester(course_string):
    """Extract semester information from course string."""
    if 'S1' in course_string:
        return 'Semester 1'
    elif 'S2' in course_string:
        return 'Semester 2'
    elif 'S3' in course_string:
        return 'Semester 3'
    return None

def extract_group(course_string):
    """Extract group information from course string."""
    import re
    group_match = re.search(r'Group(\d+)|G(\d+)', course_string)
    if group_match:
        return group_match.group(0)
    return None

