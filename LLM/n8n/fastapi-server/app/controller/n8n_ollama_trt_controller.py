"""



"""


from fastapi_router_controller import Controller
from fastapi import APIRouter
from pydantic import BaseModel
from app import TRITON_SERVER_URL
import asyncio
# import tritonclient.grpc as grpcclient
from fastapi import APIRouter, Request

class PostRequestModel(BaseModel):
    text: str

router = APIRouter(prefix='/ollama')
controller = Controller(router, openapi_tag={ 'name': 'n8n ollama-controller',})


@controller.use()
@controller.resource()
class OllamaTritonController():
    def __init__(self) -> None:
        self.loaded_model_name = None 

    async def get_service(self, request: Request):
        """FastAPI `app.state`에서 TritonService 객체 가져오기"""
        return request.app.state.triton_service

    @controller.route.get('/', tags=['ollama-controller'], summary="Check if Triton Server is Live")
    async def ollama_get_endpoint(self, request: Request):
        """Triton 서버 상태 확인"""
        service = await self.get_service(request)
        return await service.is_server_live()
    


    @controller.route.get('/api/tags', tags=['ollama-controller'], summary="Get Installed Ollama Models")
    async def get_ollama_models_dummy(self, request: Request):
        """설치된 모델 리스트 가져오기"""
        # do : 지금은 모델 정보만 정확하게 받음 추후 config.pbtxt에서 정보 파싱해서 사용가능하게 바꿔야함 // onnx 변환 및 triton변경 필요함 

        service = await self.get_service(request)
        model=await service.get_model_name()
        self.loaded_model_name = dict(model)['model_name']
        # self.loaded_model_name = await service.get_model_name()
        return {"models": [{"name": self.loaded_model_name, "modified_at": "2025-03-11T12:34:56Z", "size": 1}]}

    @controller.route.post('/api/model_load', tags=['ollama-controller'], summary="Load Ollama Model")
    async def load_ollama_models(self, request: Request):
        """설치된 모델 로드 하기"""
        # service = await self.get_service(request)
        param=dict(request)
        model_name=param['model']
        try:
            # 1. 모델 로드 요청
            await self.client.load_model(model_name=model_name)
            print(f"✅ 모델 '{model_name}' 로드 요청 완료")

            # 2. 준비될 때까지 확인
            for i in range(10):  # 최대 10회 재시도
                is_ready = await self.client.is_model_ready(model_name=model_name)
                if is_ready:
                    return {"status": 200,
                           "msg":f"✅ 모델 '{model_name}' 가 성공적으로 로드되었습니다."}
                await asyncio.sleep(0.5)  # 0.5초 대기 후 재시도

            return {"status": 400,
                "error": f"⏱ 모델 '{model_name}' 가 일정 시간 내에 준비되지 않았습니다."}

        except Exception as e:
            return {"status":400,
                "error": str(e)}

    @controller.route.post('/api/chat', tags=['ollama-controller'], summary="API POST Ollama Controller")
    async def ollama_generate(self, request: Request):
        """
        {'model': 'llama3.2-1B-Instruct', 'options': {}, 
        'messages': [{'role': 'system', 'content': 'You are a helpful assistant'}, 
        {'role': 'user', 'content': 'asd'}], 'stream': True}
        
        """
        requests = dict(request.json())
        """Triton에 텍스트 생성 요청"""     
        service = await self.get_service(request)
        self.loaded_model_name = requests['model']
        messages = requests['messages']
        # if not self.loaded_model_name:
            # self.loaded_model_name = await service.get_model_name()
        return await service.infer_text_python(self.loaded_model_name, messages)