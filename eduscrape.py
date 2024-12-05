import requests
from bs4 import BeautifulSoup
from flask import Flask, abort
from markupsafe import escape
import pandas as pd 
import datetime

def eduscrape(username, password):
    session = requests.Session()
    login_url = 'https://edusoftweb.hcmiu.edu.vn/default.aspx?page=dangnhap'
    session.get(login_url)
    session.post(login_url, data={

        'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtTaiKhoa': username,
        'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtMatKhau': password,
        'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$btnDangNhap': 'Đăng nhập',
    })
    response = session.get('https://edusoftweb.hcmiu.edu.vn/default.aspx?page=thoikhoabieu&sta=1')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'gridView'})
    rows = table.find_all('tr')
    print(rows)

    # @app.route('/')
# def hello():
#     return '<h1>Hello, World!</h1>'


# @app.route('/about/')
# def about():
#     return '<h3>This is a Flask web application.</h3>'

# @app.route('/capitalize/<word>/')
# def capitalize(word):
#     return '<h1>{}</h1>'.format(escape(word.capitalize()))

# @app.route('/add/<int:n1>/<int:n2>/')
# def add(n1, n2):
#     return '<h1>{}</h1>'.format(n1 + n2)

# @app.route('/users/<int:user_id>/')
# def greet_user(user_id):
#     users = ['Bob', 'Jane', 'Adam']
#     try:
#         return '<h2>Hi {}</h2>'.format(users[user_id])
#     except IndexError:
#         abort(404)
# @app.route('/edusoft/<username>/<password>/')
# def edusoft(username, password):
#     login_url = 'https://edusoftweb.hcmiu.edu.vn/default.aspx?page=dangnhap'
#     enter_url = 'https://edusoftweb.hcmiu.edu.vn/default.aspx?page=thoikhoabieu&sta=1'
#     payload = {
#         'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtTaiKhoa': username,
#         'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtMatKhau': password,
#         'ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$btnDangNhap': 'Đăng nhập',
#     }
#     with requests.Session() as session:
#         session.get(login_url)
#         session.post(login_url, data=payload)
#         response = session.get(enter_url)
#         return response.text

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
        # print('Logged in ' + username)
        #Enter the main page
        await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')
        #Turn into timetable page
        await page.goto('https://edusoftweb.hcmiu.edu.vn/default.aspx?page=thoikhoabieu&sta=1')
        await page.click('input[type=radio]#ContentPlaceHolder1_ctl00_rad_ThuTiet')
        await page.wait_for_selector('span#Header1_Logout1_lblNguoiDung')
        await page.get_by_role('input[type=radio]#ContentPlaceHolder1_ctl00_rad_ThuTiet').check()
        print('\nEntered the timetable page')
        await page.goto('https://edusoftweb.hcmiu.edu.vn/Report/TKBReportView.aspx')
        await page.click('label#ContentPlaceHolder1_ctl00_rad_ThuTiet')
        html = await page.content()


        soup = BeautifulSoup(html, 'html.parser')
        result = soup.text
        await browser.close()
        return result