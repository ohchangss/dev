from fastapi_router_controller import Controller
from fastapi import APIRouter
from pydantic import BaseModel



class PostRequestModel(BaseModel):
    text: str

router = APIRouter(prefix='/test')
controller = Controller(router, openapi_tag={ 'name': 'test-controller',})



@controller.use()
@controller.resource()
class TestController():
    def __init__(self) -> None:
        pass
    @controller.route.get('/get', tags=['test-controller'], summary="Api Get Test Contoller")
    def test_get_endpoint(self):
        try:
            return {"res": 'ok'}
        except:
            return {"res": 'error'}
    @controller.route.post('/post', tags=['test-controller'], summary="Api Post Test Contoller")
    def test_post_endpoint(self,requests:PostRequestModel):
        try:
            return {"res": requests.text}
        except:
            return {"res": 'error'}