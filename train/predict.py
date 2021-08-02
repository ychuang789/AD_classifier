import torch
from torch.nn import Softmax
from transformers import AlbertTokenizer

# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def get_predictions(model, data_loader, path, device):
    model.load_state_dict(torch.load(path))
    model = model.eval()
    review_texts = []
    predictions = []
    prediction_probability = []
    real_values = []
    with torch.no_grad():
        for d in data_loader:
            texts = d["review_text"]
            input_ids = d["input_ids"].to(device)
            attention_mask = d["attention_mask"].to(device)
            targets = d["targets"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs, dim=1)
            review_texts.extend(texts)
            predictions.extend(preds)
            prediction_probability.extend(outputs)
            real_values.extend(targets)
        predictions = torch.stack(predictions).cpu()
        prediction_probability = torch.stack(prediction_probability).cpu()
        real_values = torch.stack(real_values).cpu()
    return review_texts, predictions, prediction_probability, real_values


def single_prediction(model, sentence, path, max_len, device):
    tokenizer = AlbertTokenizer.from_pretrained('./model/tokenizer/')
    model.load_state_dict(torch.load(path))
    encoding = tokenizer.encode_plus(sentence,
          add_special_tokens=True,
          max_length=max_len,
          return_token_type_ids=False,
          padding='max_length',
          return_attention_mask=True,
          return_tensors='pt',
          truncation=True)

    ds = {'review_text': sentence,'input_ids': encoding['input_ids'],'attention_mask': encoding['attention_mask']}
    # texts = ds["review_text"]
    input_ids = ds["input_ids"].to(device)
    attention_mask = ds["attention_mask"].to(device)
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    softmax = Softmax(dim=1)
    probs,_ = torch.max(softmax(outputs), dim=1)
    _, preds = torch.max(outputs, dim=1)
    return round(float(probs.data[0]),4), int(preds.data[0])



