# 라이브러리를 불러온다.
import tempfile
from tokenizers import ByteLevelBPETokenizer
# 텍스트를 불러온다. -> 임시 폴더에 다운받고 저장한뒤 넘겨줌

# BPE토크나이저로 토크나이징 한다.
# 결과를 반환한다.