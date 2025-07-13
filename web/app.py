"""
Flask web application for FinOpsOptimizer dashboard.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from finops import FinOpsOptimizer
from finops.config import load_config


class User(UserMixin):
    """User model for authentication."""
    
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash


class FinOpsWebApp:
    """FinOps web application."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize FinOps web application.
        
        Args:
            config_path: Path to configuration file
        """
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
        
        # Load configuration
        self.config = load_config(config_path) if config_path else load_config()
        
        # Initialize FinOps optimizer
        self.optimizer = FinOpsOptimizer(self.config)
        
        # Setup login manager
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'
        
        # Simple user storage (in production, use a database)
        self.users = {
            'admin': User(1, 'admin', generate_password_hash('admin123'))
        }
        
        self._setup_routes()
        self._setup_login_manager()
    
    def _setup_login_manager(self):
        """Setup login manager."""
        @self.login_manager.user_loader
        def load_user(user_id):
            for user in self.users.values():
                if user.id == int(user_id):
                    return user
            return None
    
    def _setup_routes(self):
        """Setup application routes."""
        
        @self.app.route('/')
        @login_required
        def dashboard():
            """Main dashboard."""
            return render_template('dashboard.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page."""
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                user = self.users.get(username)
                if user and check_password_hash(user.password_hash, password):
                    login_user(user)
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password')
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        @login_required
        def logout():
            """Logout."""
            logout_user()
            return redirect(url_for('login'))
        
        @self.app.route('/api/costs')
        @login_required
        def get_costs():
            """Get cost analysis data."""
            try:
                days = int(request.args.get('days', 30))
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                results = self.optimizer.analyze_costs(start_date, end_date)
                return jsonify(results)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/recommendations')
        @login_required
        def get_recommendations():
            """Get optimization recommendations."""
            try:
                recommendations = self.optimizer.generate_recommendations()
                return jsonify(recommendations)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/forecast')
        @login_required
        def get_forecast():
            """Get cost forecast."""
            try:
                days = int(request.args.get('days', 30))
                forecast = self.optimizer.forecast_costs(days)
                return jsonify(forecast)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/optimize', methods=['POST'])
        @login_required
        def run_optimization():
            """Run complete optimization."""
            try:
                results = self.optimizer.optimize_all()
                return jsonify(results)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/reports', methods=['POST'])
        @login_required
        def generate_report():
            """Generate report."""
            try:
                report_type = request.json.get('type', 'comprehensive')
                output_format = request.json.get('format', 'html')
                
                report_path = self.optimizer.generate_report(report_type, output_format)
                return jsonify({'report_path': report_path})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        @login_required
        def get_status():
            """Get provider status."""
            try:
                status = self.optimizer.get_provider_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/allocate', methods=['POST'])
        @login_required
        def allocate_costs():
            """Allocate costs."""
            try:
                allocation_rules = request.json
                results = self.optimizer.allocate_costs(allocation_rules)
                return jsonify(results)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/performance')
        @login_required
        def get_performance():
            """Get performance metrics."""
            try:
                # This would return performance metrics if available
                return jsonify({
                    'cache_hit_rate': 0.75,
                    'total_requests': 1000,
                    'average_response_time': 0.5
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        Run the web application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        self.app.run(host=host, port=port, debug=debug)


def create_app(config_path: str = None):
    """
    Create Flask application.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Flask application
    """
    webapp = FinOpsWebApp(config_path)
    return webapp.app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 