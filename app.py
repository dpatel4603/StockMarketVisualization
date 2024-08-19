from dash import Dash, dcc, html, Input, Output
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

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
    """ Helper function to get the start and end date of a quarter given the year and the start month of the quarter. """
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
            dcc.Graph(id='graph-2'),
        ])
    elif tab == 'pred-ind':
        return html.Div([
            html.H3('Predictive Analysis'),
            dcc.Graph(id='graph-3'),
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


if __name__ == '__main__':
    app.run_server(debug=True)
