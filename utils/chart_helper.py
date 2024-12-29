import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_stock_chart(df):
    """Create an interactive stock chart with technical indicators"""
    fig = make_subplots(rows=2, cols=1, 
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            name='20 SMA',
            line=dict(color='orange', width=1)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            name='50 SMA',
            line=dict(color='blue', width=1)
        ),
        row=1, col=1
    )

    # Add RSI
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            name='RSI',
            line=dict(color='purple', width=1)
        ),
        row=2, col=1
    )

    # Add RSI levels
    fig.add_hline(y=70, line_width=1, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="green", row=2, col=1)

    # Update layout
    fig.update_layout(
        title_text="Stock Price & Technical Indicators",
        xaxis_rangeslider_visible=False,
        height=800,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)

    return fig
