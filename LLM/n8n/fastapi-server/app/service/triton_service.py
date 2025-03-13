import numpy as np
import tritonclient.http as httpclient
from pydantic import BaseModel  # ✅ Pydantic v2 호환
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from tritonclient.grpc import InferenceServerClient
from langchain_core.runnables import RunnableLambda
import tritonclient.grpc as grpcclient





# ✅ Triton 서버 정보
TRITON_SERVER_URL = "llm-triton-1:8001"
MODEL_NAME = "llama3.2-1B-Instruct"
# client = grpcclient.InferenceServerClient(url=TRITON_SERVER_URL)

# ✅ 프롬프트 템플릿 정의
prompt = PromptTemplate.from_template("Question: {question}\nAnswer:")

class TritonLLM:
    def __init__(self, TRITON_SERVER_URL):
        self.client =  grpcclient.InferenceServerClient(url=TRITON_SERVER_URL)
        
    def stream_response(self, question):
        # input_data=np.array([question], dtype=object)
        
        inputs = grpcclient.InferInput("text_input", [1], "BYTES", shape=[1])
        inputs.set_data_from_numpy(np.array([question.encode("utf-8")], dtype=object))

        outputs = grpcclient.InferRequestedOutput("text_output")

        response = self.client.infer(model_name=MODEL_NAME, inputs=[inputs], outputs=[outputs])
        return response.as_numpy("text_output").item().decode("utf-8")
        
    def invoke(self, user_input):
        input_data=np.array([user_input], dtype=object)
        inputs = grpcclient.InferInput(
                                    name="text_input",
                                    datatype="BYTES",
                                    shape = [1]    
                                )
        inputs.set_data_from_numpy(input_data)
        outputs = grpcclient.InferRequestedOutput("text_output")
        response = self.client.infer(model_name=MODEL_NAME, inputs=[inputs], outputs=[outputs])
        output_text = response.as_numpy("text_output")
        return eval(output_text[0][-1].decode("utf-8"))['content']

# custom_postprocessor = RunnableLambda(postprocess_output)
trt = TritonLLM(TRITON_SERVER_URL)

# ✅ 🔹 (3) 전체 LangChain 체인 구성 (프롬프트 → 전처리 → Triton → 후처리)
chain = prompt | trt.invoke 

# ✅ 🚀 모델 실행 (예제)
response = chain.invoke({"question": "what is langchain?  한글로 대답해줘"})

# ✅ 결과 출력
print(response)