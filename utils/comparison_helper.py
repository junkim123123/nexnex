"""
Comparison Helper - Compare analysis results
Utility functions for comparing current and previous analysis results
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.graph_objects as go


def extract_comparison_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key metrics from analysis result for comparison.
    
    Args:
        result: Analysis result dictionary
        
    Returns:
        Dictionary with key metrics for comparison
    """
    assumptions = result.get('ai_context', {}).get('assumptions', {})
    cost_breakdown = result.get('cost_breakdown', {})
    profitability = result.get('profitability', {})
    risk_analysis = result.get('risk_analysis', {})
    lead_time = result.get('lead_time', {})
    
    # Calculate unit DDP
    manufacturing = float(cost_breakdown.get('manufacturing', 0) or 0)
    shipping = float(cost_breakdown.get('shipping', 0) or 0)
    duty = float(cost_breakdown.get('duty', 0) or 0)
    misc = float(cost_breakdown.get('misc', 0) or 0)
    unit_ddp = manufacturing + shipping + duty + misc
    
    # Get volume
    volume = assumptions.get('volume', 1000)
    
    # Get net margin
    net_margin = profitability.get('net_profit_percent', 0) if profitability else 0
    
    # Get risk level
    risk_level = risk_analysis.get('level', 'Safe')
    
    # Get lead time
    lead_time_days = 0
    if isinstance(lead_time, dict):
        lead_time_days = lead_time.get('total_days', 0)
    
    return {
        'product_category': assumptions.get('product_category', 'Unknown'),
        'volume': volume,
        'market': assumptions.get('market', 'Unknown'),
        'channel': assumptions.get('channel', 'Unknown'),
        'unit_ddp': unit_ddp,
        'manufacturing': manufacturing,
        'shipping': shipping,
        'duty': duty,
        'total_project_cost': unit_ddp * volume,
        'net_margin_percent': net_margin,
        'risk_level': risk_level,
        'lead_time_days': lead_time_days
    }


def create_comparison_chart(current_data: Dict[str, Any], previous_data: Dict[str, Any]) -> go.Figure:
    """
    Create a comparison chart showing current vs previous analysis.
    
    Args:
        current_data: Current analysis metrics
        previous_data: Previous analysis metrics
        
    Returns:
        Plotly Figure object
    """
    metrics = ['unit_ddp', 'manufacturing', 'shipping', 'duty', 'net_margin_percent']
    labels = ['Unit DDP', 'Manufacturing', 'Shipping', 'Duty', 'Net Margin %']
    
    current_values = [current_data.get(metric, 0) for metric in metrics]
    previous_values = [previous_data.get(metric, 0) for metric in metrics]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Previous',
        x=labels,
        y=previous_values,
        marker_color='#94a3b8'
    ))
    
    fig.add_trace(go.Bar(
        name='Current',
        x=labels,
        y=current_values,
        marker_color='#0f2b46'
    ))
    
    fig.update_layout(
        title='Analysis Comparison: Current vs Previous',
        xaxis_title='Metric',
        yaxis_title='Value',
        barmode='group',
        height=400,
        showlegend=True,
        # Dark theme styling
        plot_bgcolor='#1e293b',
        paper_bgcolor='#1e293b',
        font=dict(color='#ffffff', size=12),
        xaxis=dict(gridcolor='#334155', linecolor='#334155'),
        yaxis=dict(gridcolor='#334155', linecolor='#334155')
    )
    
    return fig


def create_comparison_table(current_data: Dict[str, Any], previous_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a comparison table showing differences.
    
    Args:
        current_data: Current analysis metrics
        previous_data: Previous analysis metrics
        
    Returns:
        pandas DataFrame with comparison
    """
    metrics = {
        'Unit DDP (USD)': ('unit_ddp', '${:,.2f}'),
        'Manufacturing (USD)': ('manufacturing', '${:,.2f}'),
        'Shipping (USD)': ('shipping', '${:,.2f}'),
        'Duty (USD)': ('duty', '${:,.2f}'),
        'Total Project Cost (USD)': ('total_project_cost', '${:,.2f}'),
        'Net Margin (%)': ('net_margin_percent', '{:.2f}%'),
        'Lead Time (days)': ('lead_time_days', '{:.0f}'),
        'Volume': ('volume', '{:,}'),
    }
    
    comparison_rows = []
    for label, (key, fmt) in metrics.items():
        current_val = current_data.get(key, 0)
        previous_val = previous_data.get(key, 0)
        
        # Calculate difference
        if 'USD' in label or '%' in label:
            diff = current_val - previous_val
            diff_pct = ((current_val - previous_val) / previous_val * 100) if previous_val != 0 else 0
            diff_str = f"{diff:+.2f} ({diff_pct:+.1f}%)"
        else:
            diff = current_val - previous_val
            diff_str = f"{diff:+,.0f}"
        
        comparison_rows.append({
            'Metric': label,
            'Previous': fmt.format(previous_val),
            'Current': fmt.format(current_val),
            'Difference': diff_str
        })
    
    return pd.DataFrame(comparison_rows)

