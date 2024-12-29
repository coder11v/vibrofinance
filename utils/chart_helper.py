import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_stock_chart(df, predictions=None):
    """Create an interactive stock chart with technical indicators and predictions"""
    try:
        logger.info("Creating stock chart with technical indicators and predictions")
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

        # Add predictions if available
        if predictions is not None:
            fig.add_trace(
                go.Scatter(
                    x=predictions.index,
                    y=predictions['Predicted_Close'],
                    name='Prediction',
                    line=dict(color='green', width=2, dash='dash'),
                    hovertemplate='Date: %{x}<br>Predicted Price: $%{y:.2f}<extra></extra>'
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
            title_text="Stock Price & Technical Indicators with ML Predictions",
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

        logger.info("Successfully created stock chart with predictions")
        return fig
    except Exception as e:
        logger.error(f"Error creating stock chart: {str(e)}")
        raise Exception(f"Error creating stock visualization: {str(e)}")

def create_comparison_chart(stock_data_dict, period):
    """Create a comparison chart for multiple stocks"""
    try:
        logger.info("Creating comparison chart")
        if not stock_data_dict:
            raise ValueError("No stock data provided for comparison")

        fig = go.Figure()
        colors = ['#00AB41', '#0066CC', '#FF4B4B', '#FFB400']  # Add more colors if needed

        for i, (symbol, data) in enumerate(stock_data_dict.items()):
            try:
                df = data['history']
                normalized_prices = (df['Close'] / df['Close'].iloc[0]) * 100

                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=normalized_prices,
                        name=symbol,
                        line=dict(color=colors[i % len(colors)], width=2)
                    )
                )
                logger.info(f"Added {symbol} to comparison chart")
            except Exception as e:
                logger.error(f"Error adding {symbol} to comparison chart: {str(e)}")
                continue

        fig.update_layout(
            title="Comparative Stock Performance (Normalized to 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            height=500,
            template="plotly_white",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='x unified'
        )

        logger.info("Successfully created comparison chart")
        return fig
    except Exception as e:
        logger.error(f"Error creating comparison chart: {str(e)}")
        raise Exception(f"Error creating comparison visualization: {str(e)}")