import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import joblib

print("Step 1: Downloading Data...")
data = yf.download("AAPL", start="2019-01-01", end="2026-04-01")
dataset = data[['Close']].values

print("Step 2: Scaling Data (0 to 1)...")
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

print("Step 3: Creating 60-Days Sequences...")
# Hum AI ko 60 din ka data denge, aur wo 61st day predict karega
X_train, y_train = [], []
for i in range(60, len(scaled_data)):
    X_train.append(scaled_data[i-60:i, 0])
    y_train.append(scaled_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
# LSTM ko 3D data chahiye hota hai: (Samples, Time Steps, Features)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

print("Step 4: Building the Deep Learning LSTM Model...")
model = Sequential()
# Pehli LSTM layer
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2)) # Overfitting rokne ke liye
# Dusri LSTM layer
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
# Final prediction layer
model.add(Dense(units=25))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

print("Step 5: Training the AI (This might take 1-2 minutes)...")
model.fit(X_train, y_train, batch_size=32, epochs=10)

print("Step 6: Saving Model & Scaler...")
model.save('marketmind_model.keras')
joblib.dump(scaler, 'scaler.pkl')

print("BOOM! 💥 Model trained and saved successfully!")