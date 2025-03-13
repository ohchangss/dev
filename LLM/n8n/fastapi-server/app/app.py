import controller as c
from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
from trafilatura import extract
import uvicorn
import tritonclient.grpc as grpcclient

from fastapi_router_controller import Controller, ControllersTags

TRITON_SERVER_URL = "llm-triton-1.llm_default:8001"
CLIENT =  grpcclient.InferenceServerClient(url=TRITON_SERVER_URL)

app = FastAPI(
    title='{}'.format('fast api LLM'),
    description='LLM 관리 API',
    version='0.0.1',
    docs_url="/docs",
    openapi_tags=ControllersTags)

for router in Controller.routers():
    app.include_router(router)


if __name__ == '__main__':
    status = True
    # uvicorn.run("__main__:app", host='localhost', port=5556, reload=True) #5554
    uvicorn.run("__main__:app", host='0.0.0.0', port=9999, reload=True) #5554


# class QuestionRequest(BaseModel):
#     """POST 요청에서 HTML 데이터를 받기 위한 모델"""
#     data: str

# def process_questions(html_data):
#     """HTML을 파싱하여 질문 제목을 추출하는 함수"""
#     soup = BeautifulSoup(html_data, "html.parser")
#     questions = soup.select(".s-post-summary--content-title a")

#     # 질문 제목만 추출하여 JSON 형태로 반환
#     extracted_texts = [{"id": i + 1, "title": q.get_text(strip=True)} for i, q in enumerate(questions)]
    
#     return extracted_texts

# @app.post("/process")
# def process_questions_endpoint(request: QuestionRequest):
#     """POST로 HTML을 받아 질문 목록을 JSON으로 반환"""
#     soup = BeautifulSoup(request.data, "html.parser")
#     x=extract(request.data)
#     # HTML에서 텍스트만 추출
#     # text_content = soup.get_text()
#     # print(text_content.join())
#     # print(type(text_content))
#     # processed_data = process_questions(request.html)  # HTML 전처리 실행
#     return {"questions": 'processed_data','data':x}


# @app.get("/test")
# def test_endpoint():
#     return {"res": 'ok'}