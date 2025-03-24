from pyexpat.errors import messages
import tritonclient.grpc.aio as grpcclient  # ✅ 비동기 gRPC 클라이언트
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel

class TritonService:
    def __init__(self, triton_url: str):
        """Triton Service 초기화 (gRPC 클라이언트 생성)"""
        self.triton_url = triton_url
        self.client = grpcclient.InferenceServerClient(url=triton_url)  # ✅ gRPC 클라이언트 생성

    async def close(self):
        """서비스 종료 시 gRPC 클라이언트 해제"""
        await self.client.close()

    async def get_model_name(self):
        """Triton에서 로드된 모델 이름 가져오기 (비동기)"""
        try:
            res = await self.client.get_model_repository_index()
            return res.models[res.MODELS_FIELD_NUMBER].name
        except Exception as e:
            print(f"⚠️ Failed to get model name: {str(e)}")
            return "Unknown Model"

    async def is_server_live(self):
        """Triton 서버 상태 확인 (비동기)"""
        try:
            return await self.client.is_server_live()
        except Exception as e:
            return {"error": str(e)}
        
    async def model(self, user_input, model_name):
        try:
            input_data=np.array([user_input], dtype=object)
            inputs = grpcclient.InferInput(
                                        name="text_input",
                                        datatype="BYTES",
                                        shape = [1]    
                                    )
            inputs.set_data_from_numpy(input_data)
            outputs = grpcclient.InferRequestedOutput("text_output")
            response = await self.client.infer(model_name=model_name, inputs=[inputs], outputs=[outputs])
            output_text = response.as_numpy("text_output")
            return eval(output_text[0][-1].decode("utf-8"))['content']
    
        except Exception as e:
            return {"error": str(e)}
        
    async def infer_text_python(self, model_name: str, messages: str):
        try:
            prompt=ChatPromptTemplate.from_messages(messages)            
            # 모델 실행
            response = await self.invoke(langchain_messages,model_name)
            print(response)
            return             {
                                "model": "llama3.2-1B-Instruct",
                                "created_at": "2025-03-11T14:00:00Z",
                                "response": response,
                                "done": True,
                                "total_duration": 123456789
                                }    

        except Exception as e:
            return {"error": str(e)}


class TritonLLM(BaseChatModel):
    def _call(self, messages, stop=None, run_manager=None):
        user_message = messages[-1].content  # 마지막 user 메시지
        triton_payload = {
            "inputs": [{"name": "input_text", "shape": [1], "datatype": "BYTES", "data": [user_message]}]
        }

        response = requests.post(TRITON_URL, json=triton_payload)
        result = response.json()
        model_response = result.get("outputs", [{}])[0].get("data", [""])[0]
        
        return model_response

    def _identifying_params(self):
        return {}

    def _llm_type(self):
        return "triton_llm"