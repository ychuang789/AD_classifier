import argparse
import torch
import logging
from torch import nn
from transformers import logging as hf_logging
from transformers import  AdamW, get_linear_schedule_with_warmup
from train.build import build_dataset_object
from train.evaluate import eval_model
from train.metrics import evalute_metrics
from train.model import ADClassifier
from train.train import train_epoch

parser = argparse.ArgumentParser()
parser.add_argument('run_number', type=int, help= 'run number')
parser.add_argument('--device',default= torch.device("cuda:0" if torch.cuda.is_available() else "cpu"),
                    help= 'gpu number or cpu')
parser.add_argument('--n_classes', default= 2, help= 'number of class')
parser.add_argument('--max_len', type= int, default= 1000, help= 'max length')
parser.add_argument('--batch_size', type= int, default= 16, help= 'batch size')
parser.add_argument('--epochs', type= int, default= 10, help= 'Number of epochs')
parser.add_argument('--learning_rate', type= int ,default= 1e-5)
parser.add_argument('--num_warmup_steps', type= int, default= 0)
parser.add_argument('--loss_func', default= nn.CrossEntropyLoss())


args = parser.parse_args()

hf_logging.set_verbosity_error()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

device = args.device
model = ADClassifier(args.n_classes).to(device)

train_df, test_df, train_data_loader, test_data_loader = build_dataset_object('data.pkl', )

EPOCHS = 10
optimizer = AdamW(model.parameters(), lr=1e-5, correct_bias=False)
total_steps = len(train_data_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
  optimizer,
  num_warmup_steps=0,
  num_training_steps=total_steps
)
loss_fn = nn.CrossEntropyLoss().to(device)


from collections import defaultdict
history = defaultdict(list)
best_accuracy = 0
for epoch in range(EPOCHS):
    logging.info(f'Epoch {epoch + 1}/{EPOCHS}')
    logging.info('-' * 10)
    # print(f'Epoch {epoch + 1}/{EPOCHS}')
    # print('-' * 10)
    train_acc, train_loss = train_epoch(model, train_data_loader, loss_fn, optimizer, device, scheduler, len(train_df))

    logging.info(f'Train loss {train_loss} accuracy {train_acc}')
    # print(f'Train loss {train_loss} accuracy {train_acc}')

    val_acc, val_loss = eval_model(model, test_data_loader, loss_fn, device, len(test_df))

    logging.info(f'Val loss {val_loss} accuracy {val_acc}')
    # print(f'Val loss {val_loss} accuracy {val_acc}')

    history['train_acc'].append(train_acc)
    history['train_loss'].append(train_loss)
    history['val_acc'].append(val_acc)
    history['val_loss'].append(val_loss)
    if val_acc > best_accuracy:
        torch.save(model.state_dict(), './model/best_model_state.bin')
        best_accuracy = val_acc


    evalute_metrics(model, test_data_loader)
