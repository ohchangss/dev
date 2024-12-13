from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from typing import List, Dict, Union
from types import SimpleNamespace
import torch.nn as nn
import torch
import random
import os

config = {
    "WINDOW_GIVEN"      : 10080,   # 1 week 
    "BATCH_SIZE"        : 64,
    "HIDDEN_DIM_LSTM"   : 1024,
    "NUM_LAYERS"        : 1,
    "EPOCHS"            : 3,
    "LEARNING_RATE"     : 1e-3,
    "DEVICE"            : "cuda",
    "DROPOUT"           : 0.2,
    "FEATURE"           : '^P\\d+$',
    "MAX_SEQ_LENGTH"    : 256,
    "EMBEDDING_DIM"     : 512
}

CFG = SimpleNamespace(**config)

class MLM(Dataset):
    def __init__(self,df:pd.DataFrame, inference:bool=False):
        """
        Args:
            df: 입력 데이터프레임
            inference: 추론 모드 여부
        """
        self.set_seed()

        self.inference = inference
        self.selected_features,self.file_ids = self._get_feature_name(df)
        self.all_columns = df.columns.tolist()
        
        if inference:
            self.values = df[self.selected_features].values.astype(np.float32)
            self._prepare_inference_data()
        else:
            self._prepare_training_data(df)
    def set_seed(self, seed_value=42):
        """Set seed for reproducibility."""
        np.random.seed(seed_value)
        torch.manual_seed(seed_value)
        torch.cuda.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)  # if you are using multi-GPU.
        random.seed(seed_value)
        os.environ['PYTHONHASHSEED'] = str(seed_value)

        # The below two lines are for deterministic algorithm behavior in CUDA
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def _get_feature_name(self, df:pd.DataFrame):
        
        selected_features = df.filter(regex=CFG.FEATURE).columns.tolist()
        ### 
        file_ids = df['file_id'].values if 'file_id' in df.columns else None
        ###
        return (selected_features, file_ids)

    def _normalize_columns(self, data: np.ndarray) -> np.ndarray:
        """벡터화된 열 정규화"""
        mins = data.min(axis=0, keepdims=True)
        maxs = data.max(axis=0, keepdims=True)
        
        # mins와 maxs가 같으면 전체를 0으로 반환
        is_constant = (maxs == mins)
        if np.any(is_constant):
            normalized_data = np.zeros_like(data)
            normalized_data[:, is_constant.squeeze()] = 0
            return normalized_data
        
        # 정규화 수행
        return (data - mins) / (maxs - mins)
    
    def _get_embedding(self,df):
        ebd_layer = nn.Embedding(
            num_embeddings=CFG.MAX_SEQ_LENGTH,
            embedding_dim=CFG.EMBEDDING_DIM,
            padding_idx= 1

        )
        return ebd_layer
    
    def _prepare_inference_data(self) -> None:
        """추론 데이터 준비 - 단일 시퀀스"""                                                                                                                     
        self.normalized_values = self._normalize_columns(self.values)

    def _prepare_training_data(self, df: pd.DataFrame, stride: int) -> None:
        """학습 데이터 준비 - 윈도우 단위"""
        self.values = df[self.selected_features].values.astype(np.float32)
        
        # 시작 인덱스 계산 (stride 적용)
        potential_starts = np.arange(0, len(df) - CFG.WINDOW_GIVEN, stride)
        
        # 각 윈도우의 마지막 다음 지점(window_size + 1)이 사고가 없는(0) 경우만 필터링
        accident_labels = df['anomaly'].values
        valid_starts = [
            idx for idx in potential_starts 
            if idx + CFG.WINDOW_GIVEN < len(df) and  # 범위 체크
            accident_labels[idx + CFG.WINDOW_GIVEN] == 0  # 윈도우 다음 지점 체크
        ]
        self.start_idx = np.array(valid_starts)
        
        # 유효한 윈도우들만 추출하여 정규화
        windows = np.array([
            self.values[i:i + CFG.WINDOW_GIVEN] 
            for i in self.start_idx
        ])
        
        # (윈도우 수, 윈도우 크기, 특성 수)로 한번에 정규화
        self.input_data = np.stack([
            self._normalize_columns(window) for window in windows
        ])
        
    def __len__(self) -> int:
        if self.inference:
            return len(self.selected_features)
        return len(self.start_idx) * len(self.selected_features)
    
    def __getitem__(self, idx: int) -> Dict[str, Union[str, torch.Tensor]]:
        if self.inference:
            col_idx = idx
            col_name = self.selected_features[col_idx]
            col_data = self.normalized_values[:, col_idx]
            file_id = self.file_ids[idx] if self.file_ids is not None else None
            return {
                "column_name": col_name,
                "input": torch.from_numpy(col_data).unsqueeze(-1),  # (time_steps, 1)
                "file_id": file_id
            }
        window_idx = idx // len(self.selected_features)
        col_idx = idx % len(self.selected_features)
        
        return {
            "column_name": self.selected_features[col_idx],
            "input": torch.from_numpy(self.input_data[window_idx, :, col_idx]).unsqueeze(-1)
        }
    
    def _mask_sentence(self, rows):
        masked_numericalized_s= []  
        mask = []
        for row in rows:
            prob = random.random()