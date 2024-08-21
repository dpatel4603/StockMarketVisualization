from dash import Dash, dcc, html, Input, Output, dash_table, State
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import requests

app = Dash(__name__, suppress_callback_exceptions=True, title="Stock Market Visualization")

today = dt.datetime.today().strftime('%Y-%m-%d')
last_month = dt.datetime.today() - dt.timedelta(days=30)
last_month = last_month.strftime('%Y-%m-%d')
years_until_2000 = [str(year) for year in range(2000, dt.datetime.today().year + 1)]
years_until_2000.append("ADD Specific Dates")

# Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='home', children=[
        dcc.Tab(label="Stock Prices", value='home'),
        dcc.Tab(label="Technical Indicators", value='tech-ind'),
        dcc.Tab(label="Predictive Analysis", value='pred-ind'),
        dcc.Tab(label="Company Financials", value='company-fin'),
        dcc.Tab(label="Current News and Stock Information", value='news'),
    ]),
    html.Div(id='tabs-content')
])


def get_quarter_dates(year, quarter_start):
    """ Helper function to get the start and end date of a quarter given the year and the start month of the quarter."""
    if quarter_start is None:
        return None, None  # Return None if quarter_start is not provided
    start_date = dt.datetime.strptime(f"{year}-{quarter_start}", "%Y-%m-%d")
    end_date = (start_date + dt.timedelta(days=90)).strftime('%Y-%m-%d')  # Approximate quarter end date
    start_date = start_date.strftime('%Y-%m-%d')
    return start_date, end_date


@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'home':
        return html.Div([
            html.H3('Stock Prices Over Time'),
            html.Div([
                html.P("Enter stock ticker:"),
                dcc.Input(id="ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True, value="AAPL"),
                html.Br(),
                html.P("Enter another optional ticker:"),
                dcc.Input(id="ticker-2", type="text", placeholder="Optional enter a ticker here", debounce=True),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
            html.Div([
                html.P("Select Year or Select Specific Date"),
                dcc.Dropdown(options=[{'label': year, 'value': year} for year in years_until_2000],
                             value=dt.datetime.today().year, id="year-dropdown", style={'flex': '1'}),
                dcc.Dropdown(options=[
                    {'label': "Q1", 'value': "01-01"},
                    {'label': "Q2", 'value': "04-01"},
                    {'label': "Q3", 'value': "07-01"},
                    {'label': "Q4", 'value': "10-01"},
                ], id="quarter-dropdown", style={'flex': '1'}),
                html.Div([
                    html.P("Select Beginning Time: "),
                    dcc.Input(id="beg-time", type="text", placeholder="YYYY-MM-DD", debounce=True),
                    html.P("Select Ending Time: "),
                    dcc.Input(id="end-time", type="text", placeholder="YYYY-MM-DD", debounce=True),
                ], id="specific-date-inputs", style={'display': 'none'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
            html.Div([
                html.P("Select Metric"),
                dcc.Dropdown(['Open', 'Close', 'Volume', 'Dividends', 'Stock Splits'], 'Close', id="metric",
                             style={'flex': '1'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '20px'}),
            dcc.Graph(id="time-series-chart"),
            dcc.Graph(id="candlestick-chart")
        ])
    elif tab == 'tech-ind':
        return html.Div([
            html.H3('Technical Indicators'),
            html.Div([
                html.P("Enter stock ticker:"),
                dcc.Input(id="tech-ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True, value="AAPL"),
                html.P("Select Technical Indicator"),
                dcc.Dropdown(options=[
                    {'label': 'Simple Moving Average (SMA)', 'value': 'SMA'},
                    {'label': 'Exponential Moving Average (EMA)', 'value': 'EMA'},
                    {'label': 'Relative Strength Index (RSI)', 'value': 'RSI'}
                ], value='SMA', id="tech-ind-dropdown"),
                dcc.Input(id="window-size", type="number", placeholder="Enter window size for SMA/EMA", value=14)
            ], style={'alignItems': 'center', 'gap': '20px'}),
            dcc.Graph(id="tech-indicator-chart")
        ])
    elif tab == 'pred-ind':
        return html.Div([
            html.H3('Predictive Analysis'),
            dcc.Input(id="pred-ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True, value="AAPL"),
            html.P("Enter number of days to predict:"),
            dcc.Input(id="days-ahead", type="number", placeholder="Days ahead", value=30),
            dcc.Graph(id='pred-indicator-chart'),
        ])
    elif tab == 'company-fin':
        return html.Div([
            html.H3('Company Financials'),
            dcc.Input(id="fin-ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True),
            dcc.Dropdown(
                options=[
                    {'label': '2020', 'value': 2020},
                    {'label': '2021', 'value': 2021},
                    {'label': '2022', 'value': 2022},
                    {'label': '2023', 'value': 2023}
                ],
                value=2020,
                id="fin-year-dropdown"
            ),
            dcc.Dropdown(
                options=[
                    {'label': "Balance Sheet", 'value': "balance_sheet"},
                    {'label': "Income Statement", 'value': "income_statement"},
                    {'label': "Cash Flow", 'value': "cash_flow"}
                ],
                id="fin-type-dropdown",
                value="balance_sheet"
            ),
            html.Button('Submit', id='fin-submit', n_clicks=0),
            html.Div(id='financial-output')
        ], style={'text-align': 'left', 'margin-left': '0px'})
    elif tab == 'news':
        return html.Div([
            html.H3('Recent News and Stock Information'),
            dcc.Input(id="news-ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True, value="AAPL"),
            html.Div(id="news-output")
        ])


@app.callback(
    Output("specific-date-inputs", "style"),
    Input("year-dropdown", "value")
)
def toggle_date_inputs(selected_year):
    return {'display': 'block'} if selected_year == "ADD Specific Dates" else {'display': 'none'}


# Callback to update the graph based on user inputs
@app.callback(
    Output("time-series-chart", "figure"),
    [Input("ticker", "value"), Input("ticker-2", "value"), Input("beg-time", "value"),
     Input("end-time", "value"), Input("year-dropdown", "value"), Input("quarter-dropdown", "value"),
     Input("metric", "value")])
def display_time_series(ticker, ticker2, start_date, end_date, year, quarter, metric):
    if year == "ADD Specific Dates" and not all([start_date, end_date]):
        return px.line(title="Please provide specific start and end dates.")
    if year != "ADD Specific Dates":
        start_date, end_date = get_quarter_dates(year, quarter)
        if start_date is None:
            return px.line(title="Please select a quarter.")
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            return px.line(title="No data available.")
        fig = go.Figure()
        fig.add_scatter(x=df.index, y=df[metric], mode="lines",
                        name=f"{ticker}")
        fig.update_layout(title=f"{ticker} {metric} from {start_date} to {end_date}")
        if ticker2:
            df2 = yf.download(ticker2, start=start_date, end=end_date)
            if not df2.empty:
                fig.add_scatter(x=df2.index, y=df2[metric], mode='lines', name=f'{ticker2}')
        return fig
    except Exception as e:
        return px.line(title=f"An error occurred: {str(e)}")


@app.callback(
    Output("candlestick-chart", "figure"),
    [Input("ticker", "value"), Input("beg-time", "value"),
     Input("end-time", "value"), Input("year-dropdown", "value"), Input("quarter-dropdown", "value")])
def display_candlestick_graph(ticker, start_date, end_date, year, quarter):
    if year == "ADD Specific Dates" and not all([start_date, end_date]):
        return px.line(title="Please provide specific start and end dates.")
    if year != "ADD Specific Dates":
        start_date, end_date = get_quarter_dates(year, quarter)
        if start_date is None:
            return px.line(title="Please select a quarter.")
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            return px.line(title="No data available.")
        fig = go.Figure(data=[
            go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])
        ])
        fig.update_layout(title=f"Candlestick Chart for {ticker} from {start_date} to {end_date}", xaxis_title='Date',
                          yaxis_title='Price')
        return fig
    except Exception as e:
        return px.line(title=f"An error occurred: {str(e)}")


@app.callback(
    Output("tech-indicator-chart", "figure"),
    [Input("tech-ticker", "value"), Input("tech-ind-dropdown", "value"), Input("window-size", "value")]
)
def update_tech_indicators(ticker, indicator, window_size):
    try:
        df = yf.download(ticker, period='1y')
        if df.empty:
            return px.line(title="No data available.")
        if indicator == 'SMA':
            df['SMA'] = df['Close'].rolling(window=window_size).mean()
            fig = px.line(df, x=df.index, y=['Close', 'SMA'], title=f'SMA for {ticker}')
        elif indicator == 'EMA':
            df['EMA'] = df['Close'].ewm(span=window_size, adjust=False).mean()
            fig = px.line(df, x=df.index, y=['Close', 'EMA'], title=f'EMA for {ticker}')
        elif indicator == 'RSI':
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window_size).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window_size).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            fig = px.line(df, x=df.index, y='RSI', title=f'RSI for {ticker}')
        else:
            return px.line(title="Invalid indicator selected.")
        return fig
    except Exception as e:
        return px.line(title=f"An error occurred: {str(e)}")


@app.callback(
    Output("pred-indicator-chart", "figure"),
    [Input("pred-ticker", "value"), Input("days-ahead", "value")]
)
def update_predictive_analysis(ticker, days_ahead):
    try:
        df = yf.download(ticker, period='1y')
        if df.empty:
            return px.line(title="No data available.")

        # Prepare data for modeling
        df['Date'] = df.index
        df['Days'] = (df['Date'] - df['Date'].min()).dt.days
        X = df[['Days']]
        y = df['Close']

        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict future values
        last_day = X['Days'].max()
        future_days = pd.DataFrame({'Days': np.arange(last_day + 1, last_day + 1 + days_ahead)})
        future_dates = df['Date'].max() + pd.to_timedelta(future_days['Days'] - last_day, unit='D')
        predictions = model.predict(future_days)

        # Construct future data for plotting
        future_df = pd.DataFrame({'Date': future_dates, 'Predicted Close': predictions})

        # Combine historical and predicted data for a seamless plot
        fig = go.Figure()
        fig.add_scatter(x=df['Date'], y=df['Close'], mode='lines', name='Historical Close')
        fig.add_scatter(x=future_df['Date'], y=future_df['Predicted Close'], mode='lines', name='Predicted Close',
                        line=dict(dash='dash'))

        # Improve layout
        fig.update_layout(
            title=f'{ticker} Predictive Analysis for Next {days_ahead} Days',
            xaxis_title='Date',
            yaxis_title='Price',
            showlegend=True
        )

        return fig
    except Exception as e:
        return px.line(title=f"An error occurred: {str(e)}")


@app.callback(
    Output("news-output", "children"),
    [Input("news-ticker", "value")]
)
def update_news(ticker):
    api_key = 'api-key'
    url = f'https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={api_key}'
    try:
        response = requests.get(url)
        news_data = response.json()

        if news_data['status'] != 'ok':
            return html.P(f"An error occurred: {news_data.get('message', 'Unknown error')}")

        articles = news_data['articles'][:5]  # Get the top 5 news articles
        news_items = []
        for article in articles:
            news_items.append(html.Div([
                html.H4(article['title']),
                html.P(article['description']),
                html.A("Read more", href=article['url'], target="_blank")
            ]))
        return html.Div(news_items)
    except Exception as e:
        return html.P(f"An error occurred: {str(e)}")


@app.callback(
    Output('financial-output', 'children'),
    [Input('fin-submit', 'n_clicks')],
    [State('fin-ticker', 'value'), State('fin-year-dropdown', 'value'), State('fin-type-dropdown', 'value')])
def update_financial_output(n_clicks, ticker, year, fin_type):
    if n_clicks > 0:
        if ticker and year and fin_type:
            company = yf.Ticker(ticker)
            if fin_type == "balance_sheet":
                financials = company.balance_sheet
            elif fin_type == "income_statement":
                financials = company.financials
            elif fin_type == "cash_flow":
                financials = company.cashflow

            if financials is not None and not financials.empty:
                try:
                    financials.columns = financials.columns.strftime('%Y')  # Convert DateTimeIndex to year string
                    if str(year) in financials.columns:
                        data = financials[str(year)]
                        return html.Div([
                            dash_table.DataTable(
                                data=data.reset_index().to_dict('records'),
                                columns=[{'name': i, 'id': i} for i in data.reset_index().columns]
                            )
                        ], style={'width': '100%', 'display': 'flex', 'justify-content': 'flex-start'})
                    else:
                        return html.P("No data available for this year.")
                except Exception as e:
                    return html.P(f"An error occurred: {str(e)}")
            else:
                return html.P("No financial data available.")
        else:
            return html.P("Please enter a ticker and select year and financial statement type.")
    return html.Div()


if __name__ == '__main__':
    app.run_server(debug=True)
