"""
Chart Helper Functions - Advanced Visualizations
Waterfall, Timeline, and other advanced chart types for NexSupply
"""

import plotly.graph_objects as go
from typing import Dict, Any, List, Optional


def create_waterfall_chart(
    manufacturing: float,
    shipping: float,
    duty: float,
    misc: float,
    fba_fees: Optional[float] = None,
    marketing: Optional[float] = None,
    unit_ddp: float = 0.0
) -> go.Figure:
    """
    Create a waterfall chart showing cost accumulation.
    
    Args:
        manufacturing: Manufacturing cost per unit
        shipping: Shipping cost per unit
        duty: Duty cost per unit
        misc: Miscellaneous cost per unit
        fba_fees: Optional FBA fees per unit
        marketing: Optional marketing cost per unit
        unit_ddp: Total unit DDP
        
    Returns:
        Plotly Figure object
    """
    # Build cost components and measures
    x_data = []
    y_data = []
    measure = []
    base_value = 0.0
    
    # Add each cost component as "relative"
    costs = [
        ("Manufacturing", manufacturing),
        ("Shipping", shipping),
        ("Duty", duty),
        ("Misc.", misc),
    ]
    
    if fba_fees and fba_fees > 0:
        costs.append(("FBA Fees", fba_fees))
    
    if marketing and marketing > 0:
        costs.append(("Marketing", marketing))
    
    for name, value in costs:
        if value > 0:
            x_data.append(name)
            y_data.append(value)
            measure.append("relative")
            base_value += value
    
    # Add total as "total"
    x_data.append("Total DDP")
    y_data.append(unit_ddp if unit_ddp > base_value else base_value)
    measure.append("total")
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=x_data,
        y=y_data,
        textposition="outside",
        text=[f"${v:,.2f}" for v in y_data],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#0f2b46"}},
        decreasing={"marker": {"color": "#3b82f6"}},
        totals={"marker": {"color": "#06b6d4"}},
    ))
    
    fig.update_layout(
        title="Cost Breakdown Waterfall (Per Unit)",
        showlegend=False,
        waterfallgroupgap=0.3,
        height=500,
        xaxis_title="Cost Component",
        yaxis_title="Cost (USD)",
        # Dark theme styling
        plot_bgcolor='#1e293b',
        paper_bgcolor='#1e293b',
        font=dict(color='#ffffff', size=12),
        xaxis=dict(gridcolor='#334155', linecolor='#334155'),
        yaxis=dict(gridcolor='#334155', linecolor='#334155')
    )
    
    return fig


def create_timeline_chart(
    production_days: int,
    shipping_days: int,
    customs_days: int,
    total_days: int
) -> go.Figure:
    """
    Create a horizontal timeline/Gantt chart for lead time visualization.
    
    Args:
        production_days: Production phase duration
        shipping_days: Shipping phase duration
        customs_days: Customs phase duration
        total_days: Total lead time
        
    Returns:
        Plotly Figure object
    """
    # Calculate cumulative positions
    start_production = 0
    start_shipping = production_days
    start_customs = production_days + shipping_days
    
    # Create timeline data - muted colors (designer requirement)
    phases = [
        {"name": "Production", "start": start_production, "duration": production_days, "color": "#475569"},  # Muted gray-blue
        {"name": "Shipping", "start": start_shipping, "duration": shipping_days, "color": "#64748b"},  # Muted gray
        {"name": "Customs", "start": start_customs, "duration": customs_days, "color": "#94a3b8"},  # Muted light gray
    ]
    
    fig = go.Figure()
    
    for phase in phases:
        fig.add_trace(go.Scatter(
            x=[phase["start"], phase["start"] + phase["duration"]],
            y=[phase["name"], phase["name"]],
            mode='lines+markers',
            name=phase["name"],
            line=dict(width=20, color=phase["color"]),
            marker=dict(size=15, color=phase["color"]),
            hovertemplate=f"<b>{phase['name']}</b><br>" +
                         f"Days: {phase['duration']}<br>" +
                         f"Start: Day {phase['start']}<extra></extra>"
        ))
    
    fig.update_layout(
        title=f"Lead Time Timeline",
        xaxis_title="Days",
        yaxis_title="Phase",
        height=300,
        showlegend=False,
        hovermode='closest',
        # Dark theme styling
        plot_bgcolor='transparent',
        paper_bgcolor='transparent',
        font=dict(color='#ffffff', size=12),
        xaxis=dict(gridcolor='rgba(51, 65, 85, 0.3)', linecolor='rgba(51, 65, 85, 0.5)', showgrid=False),
        yaxis=dict(gridcolor='rgba(51, 65, 85, 0.3)', linecolor='rgba(51, 65, 85, 0.5)', showgrid=False)
    )
    
    # Add total lead time annotation with accent color (designer requirement)
    fig.add_annotation(
        x=total_days,
        y=1.5,
        text=f"<b>{total_days} days</b>",
        showarrow=False,
        font=dict(size=16, color='#ec4899'),  # Accent color for total
        bgcolor='rgba(15, 23, 42, 0.8)',
        bordercolor='#ec4899',
        borderwidth=2,
        borderpad=4
    )
    
    fig.update_xaxes(range=[0, total_days])
    
    return fig


def create_channel_comparison_chart(
    channel_data: Dict[str, Dict[str, Any]]
) -> go.Figure:
    """
    Create a bar chart comparing different sales channels.
    
    Args:
        channel_data: Dictionary with channel names as keys and metrics as values
                      Example: {"Amazon FBA": {"margin": 18, "cost": 5.5}, ...}
        
    Returns:
        Plotly Figure object
    """
    channels = list(channel_data.keys())
    margins = [channel_data[ch].get("margin", 0) for ch in channels]
    
    fig = go.Figure(data=[
        go.Bar(
            x=channels,
            y=margins,
            text=[f"{m:.1f}%" for m in margins],
            textposition='outside',
            marker=dict(color=['#0f2b46', '#3b82f6', '#06b6d4'][:len(channels)])
        )
    ])
    
    fig.update_layout(
        title="Channel Profitability Comparison",
        xaxis_title="Sales Channel",
        yaxis_title="Net Margin (%)",
        height=400,
        showlegend=False,
        # Dark theme styling
        plot_bgcolor='#1e293b',
        paper_bgcolor='#1e293b',
        font=dict(color='#ffffff', size=12),
        xaxis=dict(gridcolor='#334155', linecolor='#334155'),
        yaxis=dict(gridcolor='#334155', linecolor='#334155')
    )
    
    # Ensure y-axis shows percentage range
    max_margin = max(margins) if margins else 50
    fig.update_yaxes(range=[0, max(max_margin * 1.2, 50)])
    
    return fig

