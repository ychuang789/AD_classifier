import torch
import pandas as pd
from pandas.core.frame import DataFrame
from torch.utils.data import Dataset, DataLoader
from transformers import AlbertTokenizer
from sklearn.model_selection import train_test_split

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def read_data(filename):
    data = pd.read_pickle(filename)
    text = list(data.text)
    label = list(data.label)
    train_texts, test_texts, train_labels, test_labels = train_test_split(text, label, test_size=.2)

    train = {'text': train_texts, 'label': train_labels}
    test = {'text': test_texts, 'label': test_labels}

    train_df = DataFrame(train)
    test_df = DataFrame(test)

    return train_df, test_df




class ADDataset(Dataset):
    def __init__(self, reviews, targets, tokenizer, max_len):
        self.reviews = reviews
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_len = max_len
    def __len__(self):
        return len(self.reviews)
    def __getitem__(self, item):
        review = str(self.reviews[item])
        target = self.targets[item]
        encoding = self.tokenizer.encode_plus(
          review,
          add_special_tokens=True,
          max_length=self.max_len,
          return_token_type_ids=False,
          padding='max_length',
          return_attention_mask=True,
          return_tensors='pt',
          truncation=True
        )
        return {
          'review_text': review,
          'input_ids': encoding['input_ids'].flatten(),
          'attention_mask': encoding['attention_mask'].flatten(),
          'targets': torch.tensor(target, dtype=torch.long)
        }

def create_data_loader(df, tokenizer, max_len, batch_size):
    ds = ADDataset(
        reviews=df.text.to_numpy(),
        targets=df.label.to_numpy(),
        tokenizer=tokenizer,
        max_len=max_len
        )
    return DataLoader(
        ds,
        batch_size=batch_size,
        num_workers=0,
        shuffle= True,
        )


def build_dataset_object(filename, MAX_LEN, BATCH_SIZE):
    train_df, test_df = read_data(filename)
    tokenizer = AlbertTokenizer.from_pretrained('albert-base-v2')
    train_data_loader = create_data_loader(train_df, tokenizer, MAX_LEN, BATCH_SIZE)
    test_data_loader = create_data_loader(test_df, tokenizer, MAX_LEN, BATCH_SIZE)
    tokenizer.save_pretrained("./model/tokenizer/")
    return train_df, test_df, train_data_loader, test_data_loader






