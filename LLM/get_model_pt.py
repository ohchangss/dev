# import transformers
import huggingface_hub
from transformers import AutoModel, AutoTokenizer

# 로그인
huggingface_hub.login()

# 모델 이름 설정
model_name = "bert-base-uncased"

# 토크나이저와 모델 다운로드 및 로드
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 모델과 토크나이저를 저장할 경로 설정
save_directory = "./model"

# 모델과 토크나이저 저장
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print(f"Model and tokenizer saved to {save_directory}")