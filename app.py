from markupsafe import escape
from flask import Flask, abort, render_template, send_file
import requests 
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from termcolor import colored
import pandas as pd
from io import StringIO

app = Flask(__name__)
@app.route('/<username>/<password>/')
async def edusoftlogin(username, password):
    async with async_playwright() as pw:
    # browser = await launch(ignoreHTTPSErrors=True, headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        #Login
        await page.goto('https://edusoftweb.hcmiu.edu.vn/')
        # await page.wait_for_timeout(1000)
        await page.fill('input#ContentPlaceHolder1_ctl00_ucDangNhap_txtTaiKhoa', username)
        await page.fill('input#ContentPlaceHolder1_ctl00_ucDangNhap_txtMatKhau', password)
        await page.click('input#ContentPlaceHolder1_ctl00_ucDangNhap_btnDangNhap')
        print(colored('Logged in ' + username, 'cyan', attrs=['bold']))
        #Enter the main page
        await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')
        #Turn into timetable page
        await page.goto('https://edusoftweb.hcmiu.edu.vn/default.aspx?page=thoikhoabieu&sta=1')
        await page.click('input#ContentPlaceHolder1_ctl00_rad_ThuTiet')
        await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')
        # await page.wait_for_response('https://edusoftweb.hcmiu.edu.vn/ajaxpro/EduSoft.Web.UC.ThoiKhoaBieu,EduSoft.Web.ashx')
        print(colored('Entered the timetable page as user ' + username, 'cyan', attrs=['bold']))
        #Scrape the timetable
        print(colored('Begin to scrape' , 'cyan', attrs=['bold']))

        timetableRows = await page.query_selector_all('div#ContentPlaceHolder1_ctl00_pnlHeader > table > tbody > tr > td > div.grid-roll2')
        response = await page.content()
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find_all('table', {'class': 'body-table'})
        
        # Append all the tables into one
        timetable = pd.DataFrame({})
        for i in range(0, len(table)):
            df = pd.read_html(StringIO(str(table)))[i]
            if df is not None:
                timetable = timetable._append(df)
        # Export the timetable to a csv file
        path = username + ".csv"
        timetable.to_csv(path, index=False)             
        await browser.close()
        return send_file(path, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="80")