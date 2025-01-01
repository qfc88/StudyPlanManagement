from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
import time
import logging

class EdusoftScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_dir = os.path.join('media', 'edusoftweb')
        os.makedirs(self.base_dir, exist_ok=True)
        self.start_time = time.time()

    async def scrape(self):
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Login
                await page.goto('https://edusoftweb.hcmiu.edu.vn/')
                if await page.is_visible('input#ContentPlaceHolder1_ctl00_txtCaptcha'):
                    print('Captcha detected')
                    captcha_text = await page.inner_text("span#ContentPlaceHolder1_ctl00_lblCapcha")
                    print('Captcha text: ' + captcha_text)
                    await page.fill('input#ContentPlaceHolder1_ctl00_txtCaptcha', captcha_text)
                    await page.click('input#ContentPlaceHolder1_ctl00_btnXacNhan')
                    
                await page.fill('input#ContentPlaceHolder1_ctl00_ucDangNhap_txtTaiKhoa', self.username)
                await page.fill('input#ContentPlaceHolder1_ctl00_ucDangNhap_txtMatKhau', self.password)
                await page.click('input#ContentPlaceHolder1_ctl00_ucDangNhap_btnDangNhap')

                print(f'Logged in {self.username}')
                
                # Check login success
                try:
                    await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung', timeout=5000)
                except:
                    return {
                        'status': 'error',
                        'message': 'Login failed - Invalid credentials or connection error'
                    }

                await page.goto('https://edusoftweb.hcmiu.edu.vn/default.aspx?page=thoikhoabieu&sta=1')
                await page.click('input#ContentPlaceHolder1_ctl00_rad_ThuTiet')
                await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')

                select_locator = page.locator("#ContentPlaceHolder1_ctl00_ddlChonNHHK")
                semester_options = await select_locator.evaluate("""el => 
                    Array.from(el.options).map(option => ({
                        value: option.value,
                        text: option.text
                    }))
                """)
                
                SemesterOptions = [option['value'] for option in semester_options]
                print(f'Found {len(SemesterOptions)} semesters')

                semester_files = []
                for semester in SemesterOptions:
                    print(f'Processing semester {semester}')
                    await select_locator.select_option(value=semester)
                    await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')

                    response = await page.content()
                    soup = BeautifulSoup(response, 'html.parser')
                    table = soup.find_all('table', {'class': 'body-table'})
                    
                    timetable = pd.DataFrame()
                    for i in range(0, len(table)):
                        df = pd.read_html(StringIO(str(table)))[i]
                        if df is not None:
                            timetable = pd.concat([timetable, df], ignore_index=True)

                    if not timetable.empty:
                        # Create directory structure
                        semester_dir = os.path.join(self.base_dir, self.username)
                        os.makedirs(semester_dir, exist_ok=True)
                        
                        # Save individual CSV file for each semester
                        file_path = os.path.join(semester_dir, f"{self.username}_{semester}_timetable.csv")
                        timetable.to_csv(file_path, index=False, encoding='utf-8-sig')
                        semester_files.append(file_path)
                        logging.info(f'Saved timetable for semester {semester} to {file_path}')

                await browser.close()
                
                return {
                    'status': 'success',
                    'files': semester_files,
                    'semesters_processed': len(semester_files)
                }

        except Exception as e:
            logging.error(f"Edusoft scraping error: {str(e)}")
            raise