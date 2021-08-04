import pandas as pd
from sklearn.metrics import classification_report
from train.predict import get_predictions

def evalute_metrics(model, test_data_loader, path, device):
    y_review_texts, y_pred, y_pred_probability, y_test = get_predictions(model, test_data_loader, path, device)
    report = classification_report(y_test, y_pred, target_names=['0', '1'], output_dict=True)
    false_prediction = [['text', 'label', 'predict']]
    for i in range(len(y_pred)):
        if y_pred[i] != y_test[i]:
            false_prediction.append([y_review_texts[i], int(y_test[i]), int(y_pred[i])])
        else:
            continue

    false_prediction_df = pd.DataFrame(false_prediction[1:],columns=false_prediction[0])

    return report, false_prediction_df

