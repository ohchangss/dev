import re
from urllib import response
from fastapi_router_controller import Controller
from fastapi import APIRouter
from pydantic import BaseModel
from service.n8n_tistory import make_tistory_post


class PostRequestModel(BaseModel):
    title: str
    content: str
    tag: str
router = APIRouter(prefix='/tistory')
controller = Controller(router, openapi_tag={ 'name': 'tistory-controller',})



@controller.use()
@controller.resource()
class TistoryController():
    def __init__(self) -> None:
        pass
    @controller.route.get('/get', tags=['tistory-controller'], summary="Api Get Tistory Contoller")
    def tistory_get_endpoint(self):
        try:
            return {"res": 'ok'}
        except Exception as e:
            return {"res": "error", "error_message": str(e)}
    @controller.route.post('/post', tags=['tistory-controller'], summary="Api Post Tistory Contoller")
    def tistory_post_endpoint(self,requests:PostRequestModel):
        try:
            response = make_tistory_post(requests.title, requests.content, requests.tag)
            return {"status_code": response.status_code, "response_text": response.text}
        except Exception as e:
            return {"res": "error", "error_message": str(e)}