from torch import nn
from transformers import AlbertModel

class ADClassifier(nn.Module):
    def __init__(self, n_classes):
        super(ADClassifier, self).__init__()
        self.bert = AlbertModel.from_pretrained('albert-base-v2')
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(input_ids=input_ids, attention_mask=attention_mask, return_dict=False)
        return self.out(pooled_output)
