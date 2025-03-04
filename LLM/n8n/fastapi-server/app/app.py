from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
from trafilatura import extract

app = FastAPI()

class QuestionRequest(BaseModel):
    """POST 요청에서 HTML 데이터를 받기 위한 모델"""
    data: str

def process_questions(html_data):
    """HTML을 파싱하여 질문 제목을 추출하는 함수"""
    soup = BeautifulSoup(html_data, "html.parser")
    questions = soup.select(".s-post-summary--content-title a")

    # 질문 제목만 추출하여 JSON 형태로 반환
    extracted_texts = [{"id": i + 1, "title": q.get_text(strip=True)} for i, q in enumerate(questions)]
    
    return extracted_texts

@app.post("/process")
def process_questions_endpoint(request: QuestionRequest):
    """POST로 HTML을 받아 질문 목록을 JSON으로 반환"""
    soup = BeautifulSoup(request.data, "html.parser")
    x=extract(request.data)
    # HTML에서 텍스트만 추출
    # text_content = soup.get_text()
    # print(text_content.join())
    # print(type(text_content))
    # processed_data = process_questions(request.html)  # HTML 전처리 실행
    return {"questions": 'processed_data','data':x}


@app.get("/test")
def test_endpoint():
    return {"res": 'ok'}