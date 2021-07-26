import pandas as pd
from datetime import datetime
from sklearn import metrics
from sklearn.metrics import classification_report
from train.predict import get_predictions

def evalute_metrics(model, test_data_loader):
    y_review_texts, y_pred, y_pred_probability, y_test = get_predictions(model, test_data_loader)
    # print("Macro_average: {0}".format(metrics.f1_score(y_test, y_pred, average="macro")))
    report = classification_report(y_test, y_pred, target_names=['0', '1'], output_dict=True)
    now = datetime.now()
    df = pd.DataFrame(report).transpose()
    date_time = now.strftime("%m%d%Y_%H%M%S")
    # df.to_csv('report'+'_'+date_time+'.csv')

