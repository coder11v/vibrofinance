import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.prediction_days = 60  # Number of days to use for prediction
        self.future_days = 30  # Number of days to predict into the future

    def prepare_data(self, data):
        """Prepare data for prediction"""
        try:
            # Create features from the closing price
            scaled_data = self.scaler.fit_transform(data['Close'].values.reshape(-1, 1))
            
            x = []  # Features
            y = []  # Target
            
            for i in range(self.prediction_days, len(scaled_data)):
                x.append(scaled_data[i-self.prediction_days:i, 0])
                y.append(scaled_data[i, 0])
                
            x = np.array(x)
            y = np.array(y)
            
            return x, y, scaled_data
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise

    def train_model(self, x, y):
        """Train the prediction model"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            # Split data into training and testing sets
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
            
            # Initialize and train the model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(x_train, y_train)
            
            # Calculate performance metrics
            train_score = model.score(x_train, y_train)
            test_score = model.score(x_test, y_test)
            
            logger.info(f"Model training complete. Train score: {train_score:.4f}, Test score: {test_score:.4f}")
            
            return model, (train_score, test_score)
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise

    def make_predictions(self, model, data):
        """Generate predictions"""
        try:
            # Prepare the last sequence for prediction
            last_sequence = data['Close'].values[-self.prediction_days:]
            last_sequence_scaled = self.scaler.transform(last_sequence.reshape(-1, 1))
            
            # Generate future dates
            last_date = data.index[-1]
            future_dates = [last_date + timedelta(days=x) for x in range(1, self.future_days + 1)]
            
            # Make predictions
            current_sequence = last_sequence_scaled.reshape(1, -1)
            predictions = []
            
            for _ in range(self.future_days):
                next_pred = model.predict(current_sequence)
                predictions.append(next_pred[0])
                
                # Update sequence for next prediction
                current_sequence = np.roll(current_sequence, -1)
                current_sequence[0, -1] = next_pred
            
            # Inverse transform predictions
            predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            
            # Create prediction DataFrame
            prediction_df = pd.DataFrame(
                predictions,
                index=future_dates,
                columns=['Predicted_Close']
            )
            
            return prediction_df
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise

    def calculate_metrics(self, y_true, y_pred):
        """Calculate prediction performance metrics"""
        try:
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            
            return {
                'MSE': mse,
                'RMSE': rmse,
                'R2': r2
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

    def analyze_stock(self, historical_data):
        """Complete stock analysis pipeline"""
        try:
            # Prepare data
            x, y, scaled_data = self.prepare_data(historical_data)
            
            # Train model
            model, (train_score, test_score) = self.train_model(x, y)
            
            # Generate predictions
            predictions = self.make_predictions(model, historical_data)
            
            # Calculate confidence metrics
            confidence = {
                'train_score': train_score,
                'test_score': test_score,
                'prediction_quality': 'High' if test_score > 0.7 else 'Medium' if test_score > 0.5 else 'Low'
            }
            
            return predictions, confidence
            
        except Exception as e:
            logger.error(f"Error in stock analysis pipeline: {str(e)}")
            raise
