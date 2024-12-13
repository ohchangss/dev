from datasets import load_dataset, DatasetDict, get_dataset_config_names
from collections import defaultdict

class LoadDatasets:
    def __init__(self, DATALIST):
        self.DATALIST = DATALIST

    def get_dataset(name):

        datasets=load_dataset(name, trust_remote_code=True)

        return datasets



class EDADataset:
    def __init__(self, DATALIST, datasets):

        self.DATALIST = DATALIST
        self.datasets = datasets

    def search_sub_data(self):
        sub =[]
        non_sub = []
        for name in self.DATALIST:
            if len(get_dataset_config_names(name)) == 1:
                non_sub.append(name)
            else:
                sub.append(name)
        print(f"sub dataset 데이터 셋 수 : {len(sub)}")
        print(f"non_sub dataset 데이터 셋 수 : {len(non_sub)}")

    def get_datset_eda(datasets):

        return 