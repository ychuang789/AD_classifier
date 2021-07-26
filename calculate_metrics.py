import torch
from torch import nn
from tqdm import tqdm
from transformers import  AdamW, get_linear_schedule_with_warmup
from train.build import build_dataset_object
from train.evaluate import eval_model
from train.metrics import evalute_metrics
from train.model import ADClassifier
from train.train import train_epoch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = ADClassifier(len(['0', '1'])).to(device)

train_df, test_df, train_data_loader, test_data_loader = build_dataset_object('data.pkl', MAX_LEN = 300, BATCH_SIZE = 16)

evalute_metrics(model, test_data_loader)
