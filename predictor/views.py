from django.shortcuts import render
import numpy as np
import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from tensorflow.keras.models import load_model

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'marketmind_model.keras')

model = load_model(MODEL_PATH)

ALLOWED_STOCKS = {
    'TCS': 'Tata Consultancy Services',
    'INFY': 'Infosys',
    'RELIANCE': 'Reliance Industries',
    'TATAMOTORS': 'Tata Motors',
    'MARUTI': 'Maruti Suzuki',
    'HDFCBANK': 'HDFC Bank',
    'SBIN': 'State Bank of India',
    'ZOMATO': 'Zomato',
    'AAPL': 'Apple Inc.',
    'TSLA': 'Tesla',
    'NVDA': 'Nvidia',
    'BTC-USD': 'Bitcoin'
}

def dashboard(request):
    ticker_input = request.GET.get('ticker', '').strip().upper()
    exchange = request.GET.get('exchange', 'US')

    if not ticker_input:
        return render(request, 'dashboard.html', {
            'is_home': True,
            'available_stocks': ALLOWED_STOCKS
        })

    ticker = ticker_input
    if exchange == 'NSE' and not ticker_input.endswith('.NS'):
        ticker = f"{ticker_input}.NS"
    elif exchange == 'BSE' and not ticker_input.endswith('.BO'):
        ticker = f"{ticker_input}.BO"

    try:
        data = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
        data.dropna(inplace=True)
        
        if data.empty or len(data) < 60:
            return render(request, 'dashboard.html', {
                'error': f'Oops! We could not fetch data for "{ticker_input}" from the market server.',
                'ticker_display': ticker_input,
                'is_home': False,
                'available_stocks': ALLOWED_STOCKS
            })

        if isinstance(data.columns, pd.MultiIndex):
            close_prices = data['Close'][ticker].values
        else:
            close_prices = data['Close'].values

        last_60_days = close_prices[-60:].flatten()
        
        local_scaler = MinMaxScaler(feature_range=(0, 1))
        last_60_days_scaled = local_scaler.fit_transform(last_60_days.reshape(-1, 1))
        
        X_test = np.reshape(np.array([last_60_days_scaled]), (1, 60, 1))
        
        pred = model.predict(X_test, verbose=0)
        tomorrow_price = round(float(local_scaler.inverse_transform(pred).item()), 2)
        today_price = round(float(last_60_days[-1]), 2)

        # 🧠 NAYA: AI Confidence Calculator
        price_change_percent = abs(tomorrow_price - today_price) / today_price * 100
        confidence = round(max(45.0, min(98.0, 98.0 - (price_change_percent * 5))), 1)

        company_name = ALLOWED_STOCKS.get(ticker_input, ticker_input + " (Market Data)")

        context = {
            'ticker_display': ticker_input,
            'company_name': company_name,
            'exchange': exchange,
            'today_price': today_price,
            'tomorrow_price': tomorrow_price,
            'confidence': confidence, # <--- Added here
            'status': 'UP 🚀' if tomorrow_price > today_price else 'DOWN 🔻',
            'dates': data.index[-60:].strftime('%b %d').tolist(),
            'past_prices': [round(float(p), 2) for p in last_60_days],
            'currency': '₹' if exchange in ['NSE', 'BSE'] else '$',
            'is_home': False
        }
        return render(request, 'dashboard.html', context)

    except Exception as e:
        return render(request, 'dashboard.html', {
            'error': f"System Error: {str(e)}",
            'is_home': False,
            'available_stocks': ALLOWED_STOCKS
        })