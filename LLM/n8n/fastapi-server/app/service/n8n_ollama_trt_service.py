"""
✅ InferenceServerClient 주요 메서드 정리

메서드	설명	비고
1.infer()	모델에 입력 데이터를 넣고 추론 실행	주요 추론 함수
2.is_server_live()	Triton 서버가 현재 살아 있는지 확인	health check
3.is_server_ready()	Triton 서버가 준비되었는지 확인	서버 준비 여부
4.is_model_ready(model_name)	특정 모델이 Triton에서 준비되었는지 확인	모델 상태 체크
5. get_model_metadata(model_name)	특정 모델의 메타데이터(입출력 정보 등)를 조회	I/O 포맷 확인 가능
6.get_model_config(model_name)	모델의 config.pbtxt 정보를 가져옴	구조/옵션 확인
7.get_model_repository_index()	model_repository에 등록된 모든 모델 리스트를 가져옴	모델 목록 보기
8.load_model(model_name)	model_repository에 있는 모델을 메모리로 로드	동적 모델 로딩
9.unload_model(model_name)	메모리에 로드된 모델을 언로드 (메모리 해제)	자원 절약용
10.close()	gRPC 클라이언트 연결 종료 (비동기 클린업)	async with 사용 시 생략 가능

사용할 메서드

1. 서버 상태 확인 : is_server_live()
[http:address/ollama/]

2. 모델 네임 파싱 : get_model_name()
[http:address/ollama/api/tags]
* 지금은 수동 처리(모델이 하나뿐이므로.....ㅠ "llama3.2-1B-Instruct")// 
    모델이 많아지면 ready완료된 모델의 목록을 get_model_repository_index()를 통해 가져옴-

3. 모델 상태 확인 : is_model_ready(model_name) 
4. 모델 로드 : load_model(model_name)

"""

from pyexpat.errors import messages
import tritonclient.grpc.aio as grpcclient  # ✅ 비동기 gRPC 클라이언트
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
import asyncio

class TritonService:
    def __init__(self, triton_url: str):
        """Triton Service 초기화 (gRPC 클라이언트 생성)"""
        self.triton_url = triton_url
        self.client = grpcclient.InferenceServerClient(url=triton_url)  # ✅ gRPC 클라이언트 생성

    async def close(self):
        """서비스 종료 시 gRPC 클라이언트 해제"""
        await self.client.close()
    async def get_model_name(self):
        """모델 네임 파싱"""
        try:
            model_name = "llama3.2-1B-Instruct"  # 현재는 고정된 모델 이름 사용
            return {"model_name":model_name, "status":200}

        except Exception as e:
            return {"error": str(e), "status":400}
        
    async def load_and_check_model(self, model_name: str):
        """모델을 Triton에 로드하고 준비 완료 여부 확인"""
        try:
            # 1. 모델 로드 요청
            await self.client.load_model(model_name=model_name)
            print(f"✅ 모델 '{model_name}' 로드 요청 완료")

            # 2. 준비될 때까지 확인
            for i in range(10):  # 최대 10회 재시도
                is_ready = await self.client.is_model_ready(model_name=model_name)
                if is_ready:
                    return {"status": f"✅ 모델 '{model_name}' 가 성공적으로 로드되었습니다."}
                await asyncio.sleep(0.5)  # 0.5초 대기 후 재시도

            return {"error": f"⏱ 모델 '{model_name}' 가 일정 시간 내에 준비되지 않았습니다."}

        except Exception as e:
            return {"error": str(e)}

    async def is_server_live(self):
        """Triton 서버 상태 확인 (비동기)"""
        try:
            return await self.client.is_server_live()
        except Exception as e:
            return {"error": str(e)}

    async def is_server_ready(self):
        """Triton 서버 상태 확인 (비동기)"""
        try:
            return await self.client.is_server_ready()
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