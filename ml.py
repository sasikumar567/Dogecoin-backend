# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
import yfinance as yf
from datetime import datetime
from sqlalchemy import create_engine
import os

# === Fetch environment variables (Render will store your secrets) ===
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "sasikumar23")
DB_HOST = os.getenv("DB_HOST", "db.zwcmmwdepxwdfdvxtamb.supabase.co")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Download DOGE price data
start_dt = "2018-12-01"
end_dt = datetime.today().strftime('%Y-%m-%d')

ticker = ["DOGE-USD"]
df = yf.download(ticker, start=start_dt, end=end_dt)
df.columns = df.columns.droplevel(1)

for _ in range(30):
    features = df[['Open', 'High', 'Low', 'Volume', 'Close']]
    target = df[['Open', 'High', 'Low', 'Volume', 'Close']]

    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)
    target_scaled = scaler.fit_transform(target)

    train_size = int(len(features_scaled) * 0.99)
    X_train, X_test = features_scaled[:train_size], features_scaled[train_size:]
    y_train, y_test = target_scaled[:train_size], target_scaled[train_size:]

    model = MultiOutputRegressor(
        XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.99)
    )
    model.fit(X_train, y_train)

    predictions_scaled = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions_scaled)
    y_test_original = scaler.inverse_transform(y_test)

    results = pd.DataFrame(predictions, columns=['Open', 'High', 'Low', 'Volume', 'Close'])
    results['Date'] = df.index[train_size:]
    results['Actual Open'] = y_test_original[:, 0]
    results['Actual High'] = y_test_original[:, 1]
    results['Actual Low'] = y_test_original[:, 2]
    results['Actual Volume'] = y_test_original[:, 3]
    results['Actual Close'] = y_test_original[:, 4]

    last_features = features_scaled[-1].reshape(1, -1)
    next_day_prediction_scaled = model.predict(last_features)
    next_day_prediction = scaler.inverse_transform(next_day_prediction_scaled)

    next_day = pd.DataFrame(next_day_prediction, columns=['Open', 'High', 'Low', 'Volume', 'Close'])
    next_day['Date'] = [df.index[-1] + pd.Timedelta(days=1)]
    next_day.set_index('Date', inplace=True)
    df = pd.concat([df, next_day])

# === Save to Supabase PostgreSQL ===
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

forecast_data = df.tail(30).copy()
forecast_data.reset_index(inplace=True)

forecast_data.to_sql(name='forecast_table', con=engine, if_exists='replace', index=False)

print("✅ Last 30 days forecast saved to Supabase table `forecast_table`")
