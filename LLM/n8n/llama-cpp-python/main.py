from llama_cpp import Llama
from llama_cpp.server.app import create_app
import uvicorn
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

MODEL_PATH = os.getenv("CPP_MODEL_PATH")
N_CTX = int(os.getenv("N_CTX", 2048))
N_THREADS = int(os.getenv("N_THREADS", 8))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", -1))
HOST = os.getenv("CPP_HOST", "0.0.0.0")
PORT = int(os.getenv("CPP_PORT", 8000))

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=N_CTX,
    n_threads=N_THREADS,
    n_gpu_layers=N_GPU_LAYERS,
    use_mlock=True,
    verbose=True
)

app = create_app(llm)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
