import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import tempfile
from dotenv import load_dotenv
import os
load_dotenv()

EMAIL = os.getenv("TSTORY_ID")
PASSWORD = os.getenv("TSTORY_SECRET")

def make_tistory_post(title: str, content: str, tag: str ):
    """
    Function to make a post request to Tistory API.
    """
    # Define the URL, headers, and data for the request
    cookie_dict = get_session_info()
    TSSESSION = cookie_dict['TSSESSION']
    _T_ANO = cookie_dict['_T_ANO']
    url = "https://respecttt.tistory.com/manage/post.json"
    # TSSESSION = "2997525b5c40234a380e95182b230116a5dd98a3"
    # _T_ANO = "VFYGgAhO7Z/HjKgq9PGKRujMbfa4QFyGI/1hluzmq8gQ2X1LoOx740MT0nfEkp3+BOEhLJdeTiwmVvRzecrspMKy+L5UoFbjq9lMDjQLPLsScvBMxuqIE8/O9f1EMqQaQDezzQjzr/poiSU3vIGonD7XKkvqgzFPRumITbSrPYqpg8HFvXxBcS+avELKN1xQKBSEKgILVKYKj4T9/a+apBfHJbhCAKWZcTK1ysmqIFMTwi6ujhdppAJL8e3iQDmStAid0oEJgdQDTU9uoQ6rCtCUe67/GVUnRtwHYPq9UOGWvIwEUr9zjwLSI6raGU5wAwwjgUsGLRV5KHKb3OEhzg=="
    Cookie = "__T_=1; __T_SECURE=1; IS_TC=0; "+f"TSSESSION={TSSESSION}; "+ f"_T_ANO={_T_ANO};"
    headers = {
        "Host": "respecttt.tistory.com",
        "Cookie": Cookie,
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\"",
        "Content-Type": "application/json",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Origin": "https://respecttt.tistory.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://respecttt.tistory.com/manage/newpost/?type=post&returnURL=%2Fmanage%2Fposts%2F",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=4, i"
    }

    data = {
        "id": "0",
        "title": title,
        "content": content,
        "slogan": title,
        "visibility": 20,
        "category": 1225896,
        "tag": tag,
        "published": 1,
        "password": "41MDI1Mj",
        "uselessMarginForEntry": 1,
        "daumLike": "401",
        "cclCommercial": 0,
        "cclDerive": 0,
        "type": "post",
        "attachments": [],
        "recaptchaValue": "",
        "draftSequence": None,
        "challengeCode": ""
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("블로그 글 작성 완료")
    else:
        print(f"블로그 글 작성 실패: {response.status_code}, {response.text}")
    return response

def get_session_info():

    user_data_dir = tempfile.mkdtemp()  # 임시 폴더 생성

    # 크롬 옵션 설정 (headless는 필요에 따라 꺼도 됨)
    options = Options()
    options.add_argument("--headless")  # 브라우저 숨김
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    # 웹드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.tistory.com/auth/login")
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div/div/a[2]").click()
    time.sleep(3)
    # 아이디와 비밀번호 입력

    driver.find_element(By.NAME, "loginId").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 로그인 완료까지 대기
    time.sleep(5)

    # # 쿠키 저장
    cookies = driver.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}


    # 원하는 쿠키 값을 개별 접근 가능
    # 예: print(cookie_dict.get('TSSESSION'))

    # 종료
    driver.quit()

    return cookie_dict