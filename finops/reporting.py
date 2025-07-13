"""
Reporting module for FinOpsOptimizer.
Handles report generation in HTML, PDF, and JSON formats.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import jinja2
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from .config import Config


class ReportGenerator:
    """
    Report generator for FinOpsOptimizer.
    
    Generates comprehensive reports in HTML, PDF, and JSON formats
    with interactive charts and detailed analysis.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Report Generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Create output directory
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self,
                       cost_data: Dict[str, Any],
                       recommendations: List[Dict[str, Any]],
                       report_type: str = "comprehensive",
                       output_format: str = "html") -> str:
        """
        Generate optimization report.
        
        Args:
            cost_data: Cost analysis data
            recommendations: Optimization recommendations
            report_type: Type of report (comprehensive, summary, recommendations)
            output_format: Output format (html, pdf, json)
            
        Returns:
            Path to generated report
        """
        self.logger.info(f"Generating {report_type} report in {output_format} format")
        
        # Prepare report data
        report_data = self._prepare_report_data(cost_data, recommendations)
        
        # Generate report based on format
        if output_format == "html":
            return self._generate_html_report(report_data, report_type)
        elif output_format == "pdf":
            return self._generate_pdf_report(report_data, report_type)
        elif output_format == "json":
            return self._generate_json_report(report_data, report_type)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _prepare_report_data(self,
                            cost_data: Dict[str, Any],
                            recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare data for report generation.
        
        Args:
            cost_data: Cost analysis data
            recommendations: Optimization recommendations
            
        Returns:
            Prepared report data
        """
        # Calculate summary statistics
        total_cost = cost_data.get('summary', {}).get('total_cost', 0)
        providers_analyzed = cost_data.get('summary', {}).get('providers_analyzed', [])
        
        # Categorize recommendations
        recommendation_categories = self._categorize_recommendations(recommendations)
        
        # Calculate potential savings
        total_potential_savings = sum(r.get('potential_savings', 0) for r in recommendations)
        
        # Generate charts
        charts = self._generate_charts(cost_data, recommendations)
        
        return {
            'report_date': datetime.now().isoformat(),
            'total_cost': total_cost,
            'providers_analyzed': providers_analyzed,
            'total_recommendations': len(recommendations),
            'total_potential_savings': total_potential_savings,
            'savings_percentage': (total_potential_savings / total_cost * 100) if total_cost > 0 else 0,
            'recommendation_categories': recommendation_categories,
            'cost_data': cost_data,
            'recommendations': recommendations,
            'charts': charts
        }
    
    def _categorize_recommendations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize recommendations by type.
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Dictionary of categorized recommendations
        """
        categories = {
            'rightsizing': [],
            'autoscaling': [],
            'cost_allocation': [],
            'storage_optimization': [],
            'reserved_instances': [],
            'other': []
        }
        
        for rec in recommendations:
            rec_type = rec.get('recommendation_type', 'other')
            
            if 'rightsizing' in rec_type.lower():
                categories['rightsizing'].append(rec)
            elif 'autoscaling' in rec_type.lower():
                categories['autoscaling'].append(rec)
            elif 'allocation' in rec_type.lower():
                categories['cost_allocation'].append(rec)
            elif 'storage' in rec_type.lower():
                categories['storage_optimization'].append(rec)
            elif 'reserved' in rec_type.lower() or 'savings' in rec_type.lower():
                categories['reserved_instances'].append(rec)
            else:
                categories['other'].append(rec)
        
        return categories
    
    def _generate_charts(self, cost_data: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate interactive charts for the report.
        
        Args:
            cost_data: Cost analysis data
            recommendations: Optimization recommendations
            
        Returns:
            Dictionary of chart HTML strings
        """
        charts = {}
        
        # Cost breakdown chart
        if 'summary' in cost_data:
            charts['cost_breakdown'] = self._create_cost_breakdown_chart(cost_data)
        
        # Recommendations chart
        charts['recommendations'] = self._create_recommendations_chart(recommendations)
        
        # Cost trends chart
        if any('cost_trends' in provider_data for provider_data in cost_data.values()):
            charts['cost_trends'] = self._create_cost_trends_chart(cost_data)
        
        # Savings potential chart
        charts['savings_potential'] = self._create_savings_potential_chart(recommendations)
        
        return charts
    
    def _create_cost_breakdown_chart(self, cost_data: Dict[str, Any]) -> str:
        """Create cost breakdown pie chart."""
        try:
            # Extract service costs
            service_costs = {}
            for provider_name, provider_data in cost_data.items():
                if provider_name == 'summary':
                    continue
                
                service_breakdown = provider_data.get('service_breakdown', {})
                for service, cost in service_breakdown.items():
                    service_costs[service] = service_costs.get(service, 0) + cost
            
            if not service_costs:
                return ""
            
            # Create pie chart
            fig = px.pie(
                values=list(service_costs.values()),
                names=list(service_costs.keys()),
                title="Cost Breakdown by Service"
            )
            
            return fig.to_html(full_html=False, include_plotlyjs=False)
            
        except Exception as e:
            self.logger.error(f"Error creating cost breakdown chart: {e}")
            return ""
    
    def _create_recommendations_chart(self, recommendations: List[Dict[str, Any]]) -> str:
        """Create recommendations bar chart."""
        try:
            # Group recommendations by type
            rec_types = {}
            for rec in recommendations:
                rec_type = rec.get('recommendation_type', 'other')
                savings = rec.get('potential_savings', 0)
                rec_types[rec_type] = rec_types.get(rec_type, 0) + savings
            
            if not rec_types:
                return ""
            
            # Create bar chart
            fig = px.bar(
                x=list(rec_types.keys()),
                y=list(rec_types.values()),
                title="Potential Savings by Recommendation Type",
                labels={'x': 'Recommendation Type', 'y': 'Potential Savings ($)'}
            )
            
            return fig.to_html(full_html=False, include_plotlyjs=False)
            
        except Exception as e:
            self.logger.error(f"Error creating recommendations chart: {e}")
            return ""
    
    def _create_cost_trends_chart(self, cost_data: Dict[str, Any]) -> str:
        """Create cost trends line chart."""
        try:
            # Extract daily costs from all providers
            all_daily_costs = []
            
            for provider_name, provider_data in cost_data.items():
                if provider_name == 'summary':
                    continue
                
                trends = provider_data.get('cost_trends', {})
                daily_costs = trends.get('daily_costs', [])
                
                for cost_point in daily_costs:
                    all_daily_costs.append({
                        'date': cost_point['date'],
                        'cost': cost_point['cost'],
                        'provider': provider_name
                    })
            
            if not all_daily_costs:
                return ""
            
            # Create line chart
            df = pd.DataFrame(all_daily_costs)
            df['date'] = pd.to_datetime(df['date'])
            
            fig = px.line(
                df, x='date', y='cost', color='provider',
                title="Cost Trends Over Time",
                labels={'date': 'Date', 'cost': 'Cost ($)', 'provider': 'Provider'}
            )
            
            return fig.to_html(full_html=False, include_plotlyjs=False)
            
        except Exception as e:
            self.logger.error(f"Error creating cost trends chart: {e}")
            return ""
    
    def _create_savings_potential_chart(self, recommendations: List[Dict[str, Any]]) -> str:
        """Create savings potential chart."""
        try:
            # Extract savings data
            savings_data = []
            for rec in recommendations:
                savings_data.append({
                    'resource_id': rec.get('resource_id', 'Unknown'),
                    'savings': rec.get('potential_savings', 0),
                    'priority': rec.get('priority', 'medium')
                })
            
            if not savings_data:
                return ""
            
            # Create horizontal bar chart
            df = pd.DataFrame(savings_data)
            df = df.sort_values('savings', ascending=True)
            
            fig = px.bar(
                df, x='savings', y='resource_id', orientation='h',
                title="Potential Savings by Resource",
                labels={'savings': 'Potential Savings ($)', 'resource_id': 'Resource'}
            )
            
            return fig.to_html(full_html=False, include_plotlyjs=False)
            
        except Exception as e:
            self.logger.error(f"Error creating savings potential chart: {e}")
            return ""
    
    def _generate_html_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Generate HTML report.
        
        Args:
            report_data: Prepared report data
            report_type: Type of report
            
        Returns:
            Path to generated HTML report
        """
        try:
            # Create HTML template
            html_content = self._create_html_template(report_data, report_type)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finops_report_{report_type}_{timestamp}.html"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            raise
    
    def _create_html_template(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Create HTML template for the report.
        
        Args:
            report_data: Prepared report data
            report_type: Type of report
            
        Returns:
            HTML content
        """
        # HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinOps Optimization Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }
        .card .value {
            font-size: 2em;
            font-weight: bold;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .recommendation {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .recommendation h4 {
            margin: 0 0 10px 0;
            color: #007bff;
        }
        .chart-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        .priority-high { border-left-color: #dc3545; }
        .priority-medium { border-left-color: #ffc107; }
        .priority-low { border-left-color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FinOps Optimization Report</h1>
            <p>Generated on {{ report_date }}</p>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Cost</h3>
                <div class="value">${{ "%.2f"|format(total_cost) }}</div>
            </div>
            <div class="card">
                <h3>Potential Savings</h3>
                <div class="value">${{ "%.2f"|format(total_potential_savings) }}</div>
            </div>
            <div class="card">
                <h3>Savings %</h3>
                <div class="value">{{ "%.1f"|format(savings_percentage) }}%</div>
            </div>
            <div class="card">
                <h3>Recommendations</h3>
                <div class="value">{{ total_recommendations }}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Cost Analysis</h2>
            <div class="chart-container">
                {{ charts.cost_breakdown | safe }}
            </div>
            <div class="chart-container">
                {{ charts.cost_trends | safe }}
            </div>
        </div>
        
        <div class="section">
            <h2>Optimization Recommendations</h2>
            <div class="chart-container">
                {{ charts.recommendations | safe }}
            </div>
            <div class="chart-container">
                {{ charts.savings_potential | safe }}
            </div>
            
            {% for category, recs in recommendation_categories.items() %}
            {% if recs %}
            <h3>{{ category|title }} Recommendations</h3>
            {% for rec in recs %}
            <div class="recommendation priority-{{ rec.priority }}">
                <h4>{{ rec.description }}</h4>
                <p><strong>Potential Savings:</strong> ${{ "%.2f"|format(rec.potential_savings) }}</p>
                <p><strong>Priority:</strong> {{ rec.priority|title }}</p>
                {% if rec.recommended_action %}
                <p><strong>Action:</strong> {{ rec.recommended_action }}</p>
                {% endif %}
            </div>
            {% endfor %}
            {% endif %}
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>Provider Analysis</h2>
            {% for provider_name, provider_data in cost_data.items() %}
            {% if provider_name != 'summary' %}
            <h3>{{ provider_name|upper }}</h3>
            <p><strong>Total Cost:</strong> ${{ "%.2f"|format(provider_data.total_cost) }}</p>
            {% if provider_data.service_breakdown %}
            <p><strong>Top Services:</strong></p>
            <ul>
            {% for service, cost in provider_data.service_breakdown.items()|sort(attribute='1', reverse=true)[:5] %}
                <li>{{ service }}: ${{ "%.2f"|format(cost) }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            {% endif %}
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
        
        # Render template
        template = jinja2.Template(html_template)
        return template.render(**report_data)
    
    def _generate_pdf_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Generate PDF report.
        
        Args:
            report_data: Prepared report data
            report_type: Type of report
            
        Returns:
            Path to generated PDF report
        """
        try:
            # For now, generate HTML and convert to PDF
            # In a full implementation, you would use a library like weasyprint or reportlab
            
            # Create simplified HTML for PDF
            pdf_html = self._create_pdf_template(report_data, report_type)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finops_report_{report_type}_{timestamp}.html"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(pdf_html)
            
            self.logger.info(f"PDF report (HTML version) generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _create_pdf_template(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Create simplified HTML template for PDF conversion."""
        # Simplified template for PDF
        pdf_template = """
<!DOCTYPE html>
<html>
<head>
    <title>FinOps Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { margin-bottom: 30px; }
        .section { margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>FinOps Optimization Report</h1>
        <p>Generated on {{ report_date }}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Cost</td><td>${{ "%.2f"|format(total_cost) }}</td></tr>
            <tr><td>Potential Savings</td><td>${{ "%.2f"|format(total_potential_savings) }}</td></tr>
            <tr><td>Savings Percentage</td><td>{{ "%.1f"|format(savings_percentage) }}%</td></tr>
            <tr><td>Total Recommendations</td><td>{{ total_recommendations }}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {% for category, recs in recommendation_categories.items() %}
        {% if recs %}
        <h3>{{ category|title }}</h3>
        <table>
            <tr><th>Description</th><th>Potential Savings</th><th>Priority</th></tr>
            {% for rec in recs %}
            <tr>
                <td>{{ rec.description }}</td>
                <td>${{ "%.2f"|format(rec.potential_savings) }}</td>
                <td>{{ rec.priority|title }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        {% endfor %}
    </div>
</body>
</html>
        """
        
        template = jinja2.Template(pdf_template)
        return template.render(**report_data)
    
    def _generate_json_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Generate JSON report.
        
        Args:
            report_data: Prepared report data
            report_type: Type of report
            
        Returns:
            Path to generated JSON report
        """
        try:
            # Remove charts from JSON (they're HTML strings)
            json_data = {k: v for k, v in report_data.items() if k != 'charts'}
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finops_report_{report_type}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            
            self.logger.info(f"JSON report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            raise 