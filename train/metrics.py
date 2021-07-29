import pandas as pd
from datetime import datetime
from sklearn import metrics
from sklearn.metrics import classification_report
from train.predict import get_predictions

def evalute_metrics(model, test_data_loader, path, device):
    y_review_texts, y_pred, y_pred_probability, y_test = get_predictions(model, test_data_loader, path, device)
    # macro_average = "Macro_average: {0}".format(metrics.f1_score(y_test, y_pred, average="macro"))
    report = classification_report(y_test, y_pred, target_names=['0', '1'], output_dict=True)
    return report

