"""
Cost forecasting module for FinOpsOptimizer.
Handles cost forecasting and budgeting across AWS, Azure, and GCP.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from .config import Config


class CostForecaster:
    """
    Cost forecaster for multi-cloud environments.
    
    Provides cost forecasting capabilities across AWS, Azure, and GCP
    based on historical cost data and usage patterns.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Cost Forecaster.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self.linear_model = LinearRegression()
        self.ensemble_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
    
    def forecast(self,
                cost_data: Dict[str, Any],
                forecast_period: int = 30,
                include_recommendations: bool = True) -> Dict[str, Any]:
        """
        Forecast future costs based on historical data.
        
        Args:
            cost_data: Historical cost data from all providers
            forecast_period: Number of days to forecast
            include_recommendations: Whether to include optimization impact
            
        Returns:
            Dictionary containing forecast results
        """
        self.logger.info(f"Starting cost forecast for {forecast_period} days")
        
        results = {
            'forecast_period': forecast_period,
            'forecast_date': datetime.now().isoformat(),
            'provider_forecasts': {},
            'total_forecast': {},
            'recommendations_impact': {}
        }
        
        # Forecast for each provider
        for provider_name, provider_data in cost_data.items():
            if provider_name == 'summary':
                continue
                
            try:
                provider_forecast = self._forecast_provider_costs(
                    provider_data, forecast_period
                )
                results['provider_forecasts'][provider_name] = provider_forecast
                
            except Exception as e:
                self.logger.error(f"Error forecasting costs for {provider_name}: {e}")
                results['provider_forecasts'][provider_name] = {'error': str(e)}
        
        # Calculate total forecast
        results['total_forecast'] = self._calculate_total_forecast(results['provider_forecasts'])
        
        # Include recommendations impact if requested
        if include_recommendations:
            results['recommendations_impact'] = self._calculate_recommendations_impact(
                results['total_forecast']
            )
        
        return results
    
    def _forecast_provider_costs(self,
                                provider_data: Dict[str, Any],
                                forecast_period: int) -> Dict[str, Any]:
        """
        Forecast costs for a specific provider.
        
        Args:
            provider_data: Cost data for the provider
            forecast_period: Number of days to forecast
            
        Returns:
            Forecast results for the provider
        """
        forecast_results = {
            'forecast_period': forecast_period,
            'daily_forecasts': [],
            'total_forecast': 0,
            'confidence_interval': {},
            'trend_analysis': {}
        }
        
        # Extract historical cost data
        historical_costs = self._extract_historical_costs(provider_data)
        
        if not historical_costs:
            self.logger.warning("No historical cost data available for forecasting")
            return forecast_results
        
        # Prepare data for forecasting
        X, y = self._prepare_forecasting_data(historical_costs)
        
        if len(X) < 7:  # Need at least 7 days of data
            self.logger.warning("Insufficient historical data for forecasting")
            return forecast_results
        
        # Train models
        self._train_forecasting_models(X, y)
        
        # Generate forecasts
        daily_forecasts = self._generate_daily_forecasts(X, forecast_period)
        forecast_results['daily_forecasts'] = daily_forecasts
        
        # Calculate total forecast
        forecast_results['total_forecast'] = sum(daily_forecasts)
        
        # Calculate confidence intervals
        forecast_results['confidence_interval'] = self._calculate_confidence_interval(daily_forecasts)
        
        # Analyze trends
        forecast_results['trend_analysis'] = self._analyze_forecast_trends(daily_forecasts)
        
        return forecast_results
    
    def _extract_historical_costs(self, provider_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract historical cost data from provider data.
        
        Args:
            provider_data: Cost data for the provider
            
        Returns:
            List of historical cost data points
        """
        historical_costs = []
        
        # Extract from cost trends if available
        if 'cost_trends' in provider_data:
            trends = provider_data['cost_trends']
            if 'daily_costs' in trends:
                for cost_point in trends['daily_costs']:
                    historical_costs.append({
                        'date': cost_point['date'],
                        'cost': cost_point['cost']
                    })
        
        # If no trends data, create synthetic data for demonstration
        if not historical_costs:
            historical_costs = self._create_synthetic_cost_data(provider_data)
        
        return historical_costs
    
    def _create_synthetic_cost_data(self, provider_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create synthetic cost data for forecasting when historical data is not available.
        
        Args:
            provider_data: Cost data for the provider
            
        Returns:
            List of synthetic cost data points
        """
        total_cost = provider_data.get('total_cost', 1000)
        days = 30
        
        # Create synthetic daily costs with some variation
        np.random.seed(42)  # For reproducible results
        base_daily_cost = total_cost / days
        variation = base_daily_cost * 0.3  # 30% variation
        
        synthetic_data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            cost = base_daily_cost + np.random.normal(0, variation)
            cost = max(0, cost)  # Ensure non-negative costs
            
            synthetic_data.append({
                'date': date,
                'cost': cost
            })
        
        return synthetic_data
    
    def _prepare_forecasting_data(self, historical_costs: List[Dict[str, Any]]) -> tuple:
        """
        Prepare data for forecasting models.
        
        Args:
            historical_costs: List of historical cost data
            
        Returns:
            Tuple of (X, y) for model training
        """
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(historical_costs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['lag_1'] = df['cost'].shift(1)
        df['lag_7'] = df['cost'].shift(7)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        # Prepare features and target
        feature_columns = ['day_of_week', 'day_of_month', 'month', 'lag_1', 'lag_7']
        X = df[feature_columns].values
        y = df['cost'].values
        
        return X, y
    
    def _train_forecasting_models(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train forecasting models.
        
        Args:
            X: Feature matrix
            y: Target values
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train linear model
        self.linear_model.fit(X_scaled, y)
        
        # Train ensemble model
        self.ensemble_model.fit(X_scaled, y)
    
    def _generate_daily_forecasts(self, X: np.ndarray, forecast_period: int) -> List[float]:
        """
        Generate daily cost forecasts.
        
        Args:
            X: Feature matrix from historical data
            forecast_period: Number of days to forecast
            
        Returns:
            List of daily cost forecasts
        """
        forecasts = []
        
        # Get the last row of features as starting point
        last_features = X[-1:].copy()
        
        for day in range(forecast_period):
            # Update features for the next day
            next_date = datetime.now() + timedelta(days=day+1)
            last_features[0, 0] = next_date.weekday()  # day_of_week
            last_features[0, 1] = next_date.day  # day_of_month
            last_features[0, 2] = next_date.month  # month
            
            # Update lag features (use previous forecast as lag_1)
            if forecasts:
                last_features[0, 3] = forecasts[-1]  # lag_1
                if len(forecasts) >= 7:
                    last_features[0, 4] = forecasts[-7]  # lag_7
            
            # Scale features
            X_scaled = self.scaler.transform(last_features)
            
            # Generate forecast using ensemble of models
            linear_pred = self.linear_model.predict(X_scaled)[0]
            ensemble_pred = self.ensemble_model.predict(X_scaled)[0]
            
            # Average the predictions
            forecast = (linear_pred + ensemble_pred) / 2
            forecast = max(0, forecast)  # Ensure non-negative
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _calculate_confidence_interval(self, forecasts: List[float]) -> Dict[str, float]:
        """
        Calculate confidence intervals for forecasts.
        
        Args:
            forecasts: List of daily forecasts
            
        Returns:
            Dictionary with confidence interval bounds
        """
        forecasts_array = np.array(forecasts)
        
        # Calculate basic statistics
        mean_forecast = np.mean(forecasts_array)
        std_forecast = np.std(forecasts_array)
        
        # 95% confidence interval
        confidence_level = 1.96  # 95% confidence
        margin_of_error = confidence_level * std_forecast
        
        return {
            'lower_bound': mean_forecast - margin_of_error,
            'upper_bound': mean_forecast + margin_of_error,
            'mean': mean_forecast,
            'std': std_forecast
        }
    
    def _analyze_forecast_trends(self, forecasts: List[float]) -> Dict[str, Any]:
        """
        Analyze trends in the forecast.
        
        Args:
            forecasts: List of daily forecasts
            
        Returns:
            Dictionary with trend analysis
        """
        if len(forecasts) < 2:
            return {}
        
        # Calculate trend
        x = np.arange(len(forecasts))
        slope, intercept = np.polyfit(x, forecasts, 1)
        
        # Calculate trend direction
        if slope > 0:
            trend_direction = 'increasing'
        elif slope < 0:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Calculate volatility
        volatility = np.std(forecasts)
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': slope,
            'volatility': volatility,
            'forecast_range': {
                'min': min(forecasts),
                'max': max(forecasts)
            }
        }
    
    def _calculate_total_forecast(self, provider_forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total forecast across all providers.
        
        Args:
            provider_forecasts: Forecasts for each provider
            
        Returns:
            Total forecast summary
        """
        total_forecast = 0
        total_confidence = {
            'lower_bound': 0,
            'upper_bound': 0,
            'mean': 0
        }
        
        valid_forecasts = 0
        
        for provider_name, provider_forecast in provider_forecasts.items():
            if 'error' not in provider_forecast:
                total_forecast += provider_forecast.get('total_forecast', 0)
                
                # Aggregate confidence intervals
                confidence = provider_forecast.get('confidence_interval', {})
                if confidence:
                    total_confidence['lower_bound'] += confidence.get('lower_bound', 0)
                    total_confidence['upper_bound'] += confidence.get('upper_bound', 0)
                    total_confidence['mean'] += confidence.get('mean', 0)
                    valid_forecasts += 1
        
        if valid_forecasts > 0:
            total_confidence['mean'] /= valid_forecasts
        
        return {
            'total_forecast': total_forecast,
            'confidence_interval': total_confidence,
            'providers_forecasted': valid_forecasts
        }
    
    def _calculate_recommendations_impact(self, total_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the impact of optimization recommendations on forecasts.
        
        Args:
            total_forecast: Total forecast data
            
        Returns:
            Dictionary with recommendations impact
        """
        base_forecast = total_forecast.get('total_forecast', 0)
        
        # Estimate savings from common optimization strategies
        estimated_savings = {
            'rightsizing': base_forecast * 0.15,  # 15% savings
            'autoscaling_optimization': base_forecast * 0.10,  # 10% savings
            'reserved_instances': base_forecast * 0.20,  # 20% savings
            'storage_optimization': base_forecast * 0.05,  # 5% savings
        }
        
        total_savings = sum(estimated_savings.values())
        optimized_forecast = base_forecast - total_savings
        
        return {
            'base_forecast': base_forecast,
            'optimized_forecast': optimized_forecast,
            'total_savings': total_savings,
            'savings_breakdown': estimated_savings,
            'savings_percentage': (total_savings / base_forecast * 100) if base_forecast > 0 else 0
        } 