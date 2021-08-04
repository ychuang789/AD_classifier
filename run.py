import os
import argparse
import logging
import torch
import pandas as pd
from collections import defaultdict
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
parser.add_argument('--data', default= 'data.pkl', help= 'data path')
parser.add_argument('--device', default= "cpu",
                    help= 'default is cpu, input gpu number (cuda:number) or cpu')
parser.add_argument('--n_classes', default= 2, help= 'number of class')
parser.add_argument('--max_len', type= int, default= 300, help= 'max length')
parser.add_argument('--batch_size', type= int, default= 16, help= 'batch size')
parser.add_argument('--epochs', type= int, default= 10, help= 'Number of epochs')
parser.add_argument('--learning_rate', type= float, default= 2e-5)
parser.add_argument('--num_warmup_steps', type= int, default= 0)
parser.add_argument('--loss_func', default= nn.CrossEntropyLoss())

args = parser.parse_args()

def model_run(args):
    hf_logging.set_verbosity_error()
    logging.basicConfig(filename='./model/run.log',
                        format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
    logging.info('\n')
    logging.info(' *** This is run {} *** '.format(args.run_number))

    device = torch.device(args.device)

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument {0}: {1}".format(arg, value))

    model = ADClassifier(args.n_classes).to(device)

    logging.info(' >>> Tokenizing and building the data loader ... ')
    try:
        train_df, test_df, train_data_loader, test_data_loader = build_dataset_object(args.data,
                                                                                      args.max_len,
                                                                                      args.batch_size)
    except:
        logging.error('There is something wrong while building data loader!!')

    # parameters
    optimizer = AdamW(model.parameters(), lr= args.learning_rate, correct_bias= False)
    total_steps = len(train_data_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
      optimizer,
      num_warmup_steps= args.num_warmup_steps,
      num_training_steps=total_steps
    )
    loss_fn = args.loss_func.to(device)
    history = defaultdict(list)
    best_accuracy = 0

    for epoch in range(args.epochs):
        logging.info(f'Epoch {epoch + 1}/{ args.epochs}')
        logging.info('-' * 10)
        train_acc, train_loss = train_epoch(model, train_data_loader, loss_fn, optimizer, device, scheduler, len(train_df))
        logging.info(f'Train loss {train_loss} accuracy {train_acc}')
        val_acc, val_loss = eval_model(model, test_data_loader, loss_fn, device, len(test_df))
        logging.info(f'Val loss {val_loss} accuracy {val_acc}')

        history['train_acc'].append(train_acc)
        history['train_loss'].append(train_loss)
        history['val_acc'].append(val_acc)
        history['val_loss'].append(val_loss)

        # save best model
        if val_acc > best_accuracy:
            torch.save(model.state_dict(), './model/run/best_model_state_{}.bin'.format(args.run_number))
            best_accuracy = val_acc


    logging.info(' *** Well done, the training is over *** ')
    logging.info('\n')

    report, false_prediction_df = evalute_metrics(model, test_data_loader, './model/run/best_model_state_{}.bin'.format(args.run_number), device)
    return report, false_prediction_df

def write_result(report, args):
    df = pd.DataFrame(report).transpose()
    df.to_csv('./model/evaluate/classification_report_{}.csv'.format(args.run_number))

def output_false_pred(false_prediction_df, args):
    false_prediction_df.to_csv('./model/false_predict/false_predict_{}.csv'.format(args.run_number), index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    report, false_prediction_df = model_run(args)
    write_result(report, args)
    output_false_pred(false_prediction_df, args)


