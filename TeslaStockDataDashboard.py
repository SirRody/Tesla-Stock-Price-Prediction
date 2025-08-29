# import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Create a dash application
app = dash.Dash(__name__)

# Load your pre-processed DataFrame
df_clean = pd.read_csv('TSLA_wrangled_data.csv', index_col=0, parse_dates=True)

# Get min and max date for the slider
min_date = df_clean.index.min()
max_date = df_clean.index.max()

# Create an app layout - Define ALL components upfront
app.layout = html.Div(children=[
    html.H1('Tesla (TSLA) Stock Analysis Dashboard',
            style={'textAlign': 'center', 'color': '#2C3E50', 'font-size': 40, 'margin-bottom': '20px'}),
    
    # Date Range Selector
    html.Div([
        html.Label('Select Date Range:', style={'font-weight': 'bold'}),
        dcc.DatePickerRange(
            id='date-range-picker',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            start_date=min_date,
            end_date=max_date,
            display_format='YYYY-MM-DD'
        ),
    ], style={'width': '50%', 'margin': '20px auto'}),
    
    html.Br(),
    
    # Tabs for different sections
    dcc.Tabs(id='dashboard-tabs', value='tab-overview', children=[
        dcc.Tab(label='Price Overview', value='tab-overview'),
        dcc.Tab(label='Returns Analysis', value='tab-returns'),
        dcc.Tab(label='Technical Indicators', value='tab-technical'),
        dcc.Tab(label='Correlation Matrix', value='tab-correlation'),
    ]),
    
    # Container for tab content (titles and structure)
    html.Div(id='tabs-content'),
    
    # Define ALL graph components here (initially hidden)
    html.Div([
        # Tab 1: Overview Graphs
        dcc.Graph(id='price-chart', style={'display': 'none'}),
        dcc.Graph(id='volume-chart', style={'display': 'none'}),
        
        # Tab 2: Returns Analysis Graphs
        dcc.Graph(id='returns-histogram', style={'display': 'none'}),
        dcc.Graph(id='autocorrelation-plot', style={'display': 'none'}),
        
        # Tab 3: Technical Indicators Graphs
        dcc.Graph(id='volatility-chart', style={'display': 'none'}),
        dcc.Graph(id='range-chart', style={'display': 'none'}),
        
        # Tab 4: Correlation Graph
        dcc.Graph(id='correlation-heatmap', style={'display': 'none'})
    ])
])

# Callback 1: Render tab content structure
@app.callback(
    Output('tabs-content', 'children'),
    Input('dashboard-tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'tab-overview':
        return html.Div([
            html.H3('Price and Trend Analysis', style={'textAlign': 'center'}),
            html.Div('The price-chart graph will appear here.', id='price-chart-container'),
            html.H3('Trading Volume', style={'textAlign': 'center'}),
            html.Div('The volume-chart graph will appear here.', id='volume-chart-container')
        ])
    elif tab == 'tab-returns':
        return html.Div([
            html.H3('Distribution of Daily Returns', style={'textAlign': 'center'}),
            html.Div('The returns-histogram graph will appear here.', id='returns-histogram-container'),
            html.H3('Autocorrelation of Daily Returns', style={'textAlign': 'center'}),
            html.Div('The autocorrelation-plot graph will appear here.', id='autocorrelation-plot-container')
        ])
    elif tab == 'tab-technical':
        return html.Div([
            html.H3('Volatility Analysis (30-Day Rolling)', style={'textAlign': 'center'}),
            html.Div('The volatility-chart graph will appear here.', id='volatility-chart-container'),
            html.H3('Daily Price Range (%)', style={'textAlign': 'center'}),
            html.Div('The range-chart graph will appear here.', id='range-chart-container')
        ])
    elif tab == 'tab-correlation':
        return html.Div([
            html.H3('Feature Correlation Heatmap', style={'textAlign': 'center'}),
            html.Div('The correlation-heatmap graph will appear here.', id='correlation-heatmap-container')
        ])

# Callback 2: Show/hide graphs based on active tab
@app.callback(
    [Output('price-chart', 'style'),
     Output('volume-chart', 'style'),
     Output('returns-histogram', 'style'),
     Output('autocorrelation-plot', 'style'),
     Output('volatility-chart', 'style'),
     Output('range-chart', 'style'),
     Output('correlation-heatmap', 'style')],
    Input('dashboard-tabs', 'value')
)
def show_hide_graphs(tab):
    # Start by hiding all graphs
    styles = [{'display': 'none'}] * 7
    
    # Show only the graphs for the active tab
    if tab == 'tab-overview':
        styles[0] = {'display': 'block'}  # price-chart
        styles[1] = {'display': 'block'}  # volume-chart
    elif tab == 'tab-returns':
        styles[2] = {'display': 'block'}  # returns-histogram
        styles[3] = {'display': 'block'}  # autocorrelation-plot
    elif tab == 'tab-technical':
        styles[4] = {'display': 'block'}  # volatility-chart
        styles[5] = {'display': 'block'}  # range-chart
    elif tab == 'tab-correlation':
        styles[6] = {'display': 'block'}  # correlation-heatmap
        
    return styles

# Callback 3: Update all graph figures based on date selection
@app.callback(
    [Output('price-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('returns-histogram', 'figure'),
     Output('volatility-chart', 'figure'),
     Output('range-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('autocorrelation-plot', 'figure')],
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_all_charts(start_date, end_date):
    # Filter data based on date selection
    filtered_df = df_clean.loc[start_date:end_date]
    
    # 1. Price Chart with Moving Averages
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['close'], mode='lines', name='Closing Price', line=dict(width=1)))
    price_fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['MA_50'], mode='lines', name='50-Day MA', line=dict(color='orange', width=2)))
    price_fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['MA_200'], mode='lines', name='200-Day MA', line=dict(color='red', width=2)))
    price_fig.update_layout(title='Price with Moving Averages', yaxis_title='Price ($)', xaxis_title='Date')
    
    # 2. Volume Chart
    volume_fig = go.Figure(go.Bar(x=filtered_df.index, y=filtered_df['volume'], name='Volume', marker_color='blue', opacity=0.5))
    volume_fig.update_layout(title='Trading Volume', yaxis_title='Volume', xaxis_title='Date')
    
    # 3. Returns Histogram
    returns_histogram = px.histogram(filtered_df, x='daily_return', nbins=50, title='Distribution of Daily Returns', labels={'daily_return': 'Daily Return (%)'})
    returns_histogram.add_vline(x=filtered_df['daily_return'].mean(), line_dash="dash", line_color="red", annotation_text="Mean")
    returns_histogram.add_vline(x=filtered_df['daily_return'].median(), line_dash="dash", line_color="green", annotation_text="Median")
    
    # 4. Volatility Chart
    volatility_fig = go.Figure(go.Scatter(x=filtered_df.index, y=filtered_df['volatility_30d'], mode='lines', name='30-Day Volatility', line=dict(color='purple')))
    volatility_fig.update_layout(title='30-Day Rolling Volatility', yaxis_title='Volatility', xaxis_title='Date')
    
    # 5. Daily Range Chart
    range_fig = go.Figure(go.Scatter(x=filtered_df.index, y=filtered_df['daily_range_pct'], mode='lines', name='Daily Range %', line=dict(color='teal')))
    range_fig.update_layout(title='Daily High-Low Range (% of Close)', yaxis_title='Range (%)', xaxis_title='Date')
    
    # 6. Correlation Heatmap
    corr_matrix = filtered_df[['close', 'volume', 'daily_return', 'MA_50', 'MA_200', 'volatility_30d', 'daily_range_pct']].corr()
    correlation_fig = px.imshow(corr_matrix, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r', title='Correlation Between Features')
    
    # 7. Autocorrelation Plot
    lags = 30
    acf_values = [filtered_df['daily_return'].autocorr(lag=i) for i in range(lags+1)]
    autocorr_fig = go.Figure(go.Bar(x=list(range(lags+1)), y=acf_values, name='Autocorrelation'))
    autocorr_fig.update_layout(title='Autocorrelation of Daily Returns (Lags 0-30)', xaxis_title='Lag', yaxis_title='Autocorrelation')
    autocorr_fig.add_hline(y=1.96 / (len(filtered_df)**0.5), line_dash="dash", line_color="red", annotation_text="95% CI")
    autocorr_fig.add_hline(y=-1.96 / (len(filtered_df)**0.5), line_dash="dash", line_color="red")
    
    return (price_fig, volume_fig, returns_histogram, volatility_fig, range_fig, correlation_fig, autocorr_fig)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
