from fastapi_router_controller import Controller
from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from app import TRITON_SERVER_URL,CLIENT
# import tritonclient.grpc as grpcclient

class PostRequestModel(BaseModel):
    text: str

router = APIRouter(prefix='/ollama')
controller = Controller(router, openapi_tag={ 'name': 'n8n ollama-controller',})


@controller.use()
@controller.resource()
class OllamaTritonController():
    def __init__(self) -> None:
            res = CLIENT.get_model_repository_index()
            self.loaded_model_name=res.models[res.MODELS_FIELD_NUMBER].name
            # pass
    @controller.route.get('/', tags=['ollama-controller'], summary="Api Get ollama Contoller")
    def ollama_get_endpoint(self):
        try:
            res=CLIENT.is_server_live()

            return res
        except Exception as e:
            return {"res": "error", "detail": str(e)}

    @controller.route.get('/api/tags', tags=['ollama-controller'], summary="Get Installed Ollama Models (Dummy Response)")
    async def get_ollama_models_dummy(self):
        """
        Ollama에서 설치된 모델 리스트를 가져오는 더미 응답
        """
        try:
            # 테스트용 더미 JSON 데이터 반환

            # do : 지금은 모델 정보만 정확하게 받음 추후 config.pbtxt에서 정보 파싱해서 사용가능하게 바꿔야함 // onnx 변환 및 triton변경 필요함 
            dummy_response = {
                "models": [
                    {
                        "name": self.loaded_model_name,
                        "modified_at": "2025-03-11T12:34:56Z",
                        "size": 1
                    }

                ]
            }
            return dummy_response
        except Exception as e:
            return {"error": "Failed to fetch models", "detail": str(e)}



    @controller.route.get('/get', tags=['ollama-controller'], summary="Api Get ollama Contoller")
    def ollama_get_endpoint(self):
        try:
            return {"res": 'ok'}
        except:
            return {"res": 'error'}
    @controller.route.post('/generate', tags=['ollama-controller'], summary="API POST Ollama Controller")
    async def ollama_generate(self, request: PostRequestModel):
        """
        Ollama API와 연동하여 텍스트 생성 수행
        """
        try:
            # async with httpx.AsyncClient() as client:
                # response = await client.post(OLLAMA_URL, json={
                #     "model": "llama3",
                #     "prompt": request.text,
                #     "stream": False
                # })
                # return response.json()
            dummy_response = {
            "model": "llama3",
            "created_at": "2025-03-11T14:00:00Z",
            "response": f"Test response for: {request.text}",
            "done": True,
            "total_duration": 123456789
                }
            return dummy_response
        except Exception as e:
            return {"res": "error", "detail": str(e)}
        
    @controller.route.post('/chat', tags=['ollama-controller'], summary="API POST Ollama Controller")
    async def ollama_chat(self, request: PostRequestModel):
        """
        Ollama API와 연동하여 텍스트 생성 수행
        """
        try:
            # async with httpx.AsyncClient() as client:
                # response = await client.post(OLLAMA_URL, json={
                #     "model": "llama3",
                #     "prompt": request.text,
                #     "stream": False
                # })
                # return response.json()
            dummy_response = {
            "model": "llama3",
            "created_at": "2025-03-11T14:00:00Z",
            "response": f"Test response for: {request.text}",
            "done": True,
            "total_duration": 123456789
                }
            return dummy_response
        except Exception as e:
            return {"res": "error", "detail": str(e)}
        



    @controller.route.get('/model', tags=['ollama-controller'], summary="Get Installed Ollama Models (Dummy Response)")
    async def get_ollama_models_(self):
        """
        Ollama에서 설치된 모델 리스트를 가져오는 더미 응답
        """
        try:
            # 테스트용 더미 JSON 데이터 반환
            res=CLIENT.get_model_repository_index()
            loaded_model_name=res.models[res.MODELS_FIELD_NUMBER].name
            print(loaded_model_name)
            # do : 지금은 모델 정보만 정확하게 받음 추후 config.pbtxt에서 정보 파싱해서 사용가능하게 바꿔야함 // onnx 변환 및 triton변경 필요함 
            dummy_response = {
                "models": [
                    {
                        "name": loaded_model_name,
                        "modified_at": "2025-03-11T12:34:56Z",
                        "size": 1
                    }

                ]
            }
            return dummy_response
        except Exception as e:
            return {"error": "Failed to fetch models", "detail": str(e)}