from flask import Flask, render_template, request, url_for
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update_plot', methods=['POST'])
def update_plot():
    ticker = request.form['ticker']
    start_date = request.form['beg-time']
    end_date = request.form['end-time']

    # Fetch stock data using yfinance
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    # Generate plot
    img = BytesIO()
    plt.figure()
    data['Close'].plot(title=f'{ticker} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()

    # Encode plot to base64
    plot_url = base64.b64encode(img.getvalue()).decode()
    img_data = f"data:image/png;base64,{plot_url}"

    return render_template('index.html', img_data=img_data)


if __name__ == '__main__':
    app.run(debug=True)
