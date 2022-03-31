import numpy as np
from keras.models import load_model
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from django.conf import settings
from peakdetect import peakdetect

def create_series(df, xcol, datecol):
    features_considered = [xcol]
    features = df[features_considered]
    features.index = df[datecol]
    return features


def get_prediction(file_path, state, time_type):
    try:
        models = {
            "ca": {"daily": "ca_daily.h5", "hourly": "ca_hourly.h5"},
            "tx": {"daily": "tx_daily.h5", "hourly": "tx_hourly.h5"},
            "mn": {"daily": "mn_daily.h5", "hourly": "mn_hourly.h5"},
            "ny": {"daily": "ny_daily.h5", "hourly": "ny_hourly.h5"}
        }

        df = pd.read_excel(file_path)

        features = create_series(df, 'D', 'localTime' if time_type == "hourly" else "localDate")
        features.dropna(axis = 0, inplace=True)
        
        date_time = list(map(lambda v:str(v) if time_type == "hourly" else str(v).replace(' 00:00:00', ''), features.index))

        scaler = MinMaxScaler(feature_range=(0, 1))
        dataset = scaler.fit_transform(features)
        X_test = np.reshape(dataset, (dataset.shape[0], dataset.shape[1], 1))
        y_test = np.reshape(dataset, (-1, 1))
        
        model = load_model(os.path.join(settings.BASE_DIR, "trained_data", "Models", models[state][time_type]))
        
        predictions = model.predict(X_test)
        predictions_unscaled = scaler.inverse_transform(predictions)
        actuals_unscaled = scaler.inverse_transform(y_test)
        predictions = np.reshape(predictions_unscaled, (predictions_unscaled.size,))
        y_test = np.reshape(actuals_unscaled, (actuals_unscaled.size,))

        comparison_df_train = {"d": list(y_test), "df": list(predictions), 't': date_time}
        return comparison_df_train

    except Exception as e:
        print(e)
        return False


def get_peaks(forecasting, time_format):

    df = forecasting.get('df')

    lookahead = (0.01 if time_format == "daily" else 0.001) * len(df)

    if lookahead < 1:
        lookahead = 1

    print(lookahead, len(forecasting['df']))

    peaks = peakdetect(df,lookahead = round(lookahead))
    higherPeaks = peaks[0]
    lowerPeaks = peaks[1]

    return {'hp': map(lambda p:p[0], higherPeaks), 'lp':  map(lambda p:p[0], lowerPeaks)}