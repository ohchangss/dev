from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "meta-llama/LLaMA-7B"  # 실제로 사용할 모델 이름으로 대체해야 합니다.
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 입력 텍스트
input_text = "Once upon a time"

# 입력 텍스트를 토큰화
inputs = tokenizer(input_text, return_tensors="pt")

# GPU가 사용 가능한 경우 GPU로 이동
if torch.cuda.is_available():
    model.to("cuda")
    inputs = {key: value.to("cuda") for key, value in inputs.items()}

# 모델 예측
with torch.no_grad():
    outputs = model(**inputs)


predictions = outputs.logits.argmax(dim=-1)


predicted_text = tokenizer.decode(predictions[0])


print(predicted_text)
