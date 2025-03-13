from fastapi_router_controller import Controller
from fastapi import APIRouter

router = APIRouter(prefix='/triton')
controller = Controller(router, openapi_tag={ 'name': 'triton-controller',})

@controller.use()

@controller.resource()
class TritonController():
    def __init__(self) -> None:
        pass
    @controller.route.post('/inference', tags=['test-controller'], summary="Api Post Test Contoller")
    def test_post_endpoint(self, text):
        try:
            return {"res": text}
        except:
            return {"res": 'error'}
