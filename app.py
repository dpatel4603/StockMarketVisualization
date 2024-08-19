from dash import Dash, dcc, html, Input, Output
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

app = Dash(__name__, suppress_callback_exceptions=True, title="Stock Market Visualization")

today = dt.datetime.today().strftime('%Y-%m-%d')
last_month = dt.datetime.today() - dt.timedelta(days=30)
last_month = last_month.strftime('%Y-%m-%d')

# Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='home', children=[
        dcc.Tab(label="Stock Prices", value='home'),
        dcc.Tab(label="Technical Indicators", value='tech-ind'),
        dcc.Tab(label="Predictive Analysis", value='pred-ind'),
        dcc.Tab(label="Current News and Stock Information", value='news'),
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'home':
        return html.Div([
            html.H3('Stock Prices Over Time'),
            html.Div([
                html.P("Enter stock ticker:"),
                dcc.Input(id="ticker", type="text", placeholder="Enter ticker like AAPL", debounce=True, value="AAPL"),
                html.Br(),
                html.P("Enter another optional ticker: "),
                dcc.Input(id="ticker-2", type="text", placeholder="Optional enter a ticker here", debounce=True,
                          required=False),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
            html.Div([
                html.P("Select Beginning Time: "),
                dcc.Input(id="beg-time", type="text", placeholder="YYYY-MM-DD", debounce=True, value=last_month),
                html.P("Select Ending Time: "),
                dcc.Input(id="end-time", type="text", placeholder="YYYY-MM-DD", debounce=True, value=today),
                ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
            html.Div([
               html.P("Select Metric"),
               dcc.Dropdown(['Open', 'Close', 'Volume', 'Dividends', 'Stock Splits'], 'Close', id="metric")
            ], style={'display': '20px', 'alignItems': 'center', 'gap': '20px'}),
            dcc.Graph(id="time-series-chart"),
            dcc.Graph(id="candlestick-chart")

        ])
    elif tab == 'tech-ind':
        return html.Div([
            html.H3('Technical Indicators'),
            dcc.Graph(id='graph-2'),
            # More components can be added here
        ])
    elif tab == 'pred-ind':
        return html.Div([
            html.H3('Predictive Analysis'),
            dcc.Graph(id='graph-3'),
            # More components can be added here
        ])


# Callback to update the graph based on user inputs
@app.callback(
    Output("time-series-chart", "figure"),
    [Input("ticker", "value"),
     Input("ticker-2", "value"),
     Input("beg-time", "value"),
     Input("end-time", "value"),
     Input("metric", "value"),])
def display_time_series(ticker, ticker2, start_date, end_date, metric):
    if ticker and start_date and end_date and metric:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            fig = go.Figure()
            fig.add_scatter(x=df.index, y=df[metric], mode='lines', name=f'{ticker}')
            fig.update_layout(xaxis_title='Dates', yaxis_title=f'{metric}',
                              legend_title='Company Names', title=f'{ticker} from {start_date} - {end_date}')

            if ticker2:  # Check if there's a second ticker provided
                stock2 = yf.Ticker(ticker2)
                df2 = stock2.history(start=start_date, end=end_date)
                if not df2.empty:
                    fig.add_scatter(x=df2.index, y=df2[metric], mode='lines', name=f'{ticker2}')
                    fig.update_layout(title=f"{ticker} and {ticker2} from {start_date} - {end_date}")

            return fig
        except Exception as e:
            return px.line(title=f"An error occurred: {str(e)}")
    else:
        return px.line(title="Please provide ticker, start date, end date, and metric")


@app.callback(
    Output("candlestick-chart", "figure"),
    [Input("ticker", "value"),
     Input("beg-time", "value"),
     Input("end-time", "value")])
def display_candlestick_graph(ticker, start_date, end_date):
    if ticker and start_date and end_date:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            # Ensuring there is data to plot
            if not df.empty:
                fig = go.Figure(data=[
                    go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(xaxis_title='Date', yaxis_title='Candlestick',
                                  title=f'{ticker} Candlestick Chart from {start_date} - {end_date}')
                return fig
            else:
                return go.Figure()  # Returning an empty figure if no data is available
        except Exception as e:
            return px.line(title=f"An error occurred: {str(e)}")  # Handling possible errors gracefully
    else:
        return px.line(title="Please provide ticker, start date, and end date")  # Prompting user for missing inputs


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
