"""
FILE: visualization_service.py
STATUS: Active
RESPONSIBILITY: Generate interactive visualizations for statistical queries
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import logging
from typing import Any

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from src.services.visualization_patterns import QueryPatternDetector, VisualizationPattern
from src.services.stat_labels import get_stat_label, format_stat_labels

logger = logging.getLogger(__name__)


class VisualizationService:
    """Generate interactive visualizations for SQL query results."""

    def __init__(self):
        """Initialize visualization service."""
        self.detector = QueryPatternDetector()
        self.color_scheme = px.colors.qualitative.Plotly

    def generate_visualization(
        self,
        query: str,
        sql_result: list[dict[str, Any]],
        pattern: VisualizationPattern | None = None,
    ) -> dict[str, Any]:
        """Generate visualization for SQL results.

        Args:
            query: Original user query
            sql_result: SQL query results as list of dicts
            pattern: Optional pre-detected pattern (if None, will auto-detect)

        Returns:
            Dict with:
                - pattern: Detected pattern name
                - viz_type: Visualization type used
                - plot_json: Plotly figure as JSON (for API)
                - plot_html: Plotly figure as HTML (for UI)
        """
        if not sql_result:
            logger.warning("Empty SQL result - returning no visualization")
            return {
                "pattern": "none",
                "viz_type": "none",
                "plot_json": None,
                "plot_html": None,
                "message": "No data to visualize",
            }

        # Detect pattern if not provided
        if pattern is None:
            pattern = self.detector.detect_pattern(query, sql_result)

        logger.info(f"Generating visualization for pattern: {pattern.value}")

        # Route to appropriate visualization generator
        viz_generators = {
            VisualizationPattern.TOP_N: self._generate_top_n,
            VisualizationPattern.PLAYER_COMPARISON: self._generate_comparison,
            VisualizationPattern.MULTI_ENTITY_COMPARISON: self._generate_multi_comparison,
            VisualizationPattern.SINGLE_ENTITY: self._generate_single_entity,
            VisualizationPattern.DISTRIBUTION: self._generate_distribution,
            VisualizationPattern.CORRELATION: self._generate_correlation,
            VisualizationPattern.THRESHOLD_FILTER: self._generate_threshold_filter,
            VisualizationPattern.COMPOSITION: self._generate_composition,
            VisualizationPattern.GENERIC_TABLE: self._generate_table,
        }

        generator = viz_generators.get(pattern, self._generate_table)
        fig = generator(query, sql_result)

        return {
            "pattern": pattern.value,
            "viz_type": self.detector.get_recommended_viz_type(pattern, len(sql_result)),
            "plot_json": fig.to_json(),
            "plot_html": fig.to_html(include_plotlyjs="cdn", div_id="viz"),
        }

    def _generate_top_n(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate horizontal bar chart for top N rankings."""
        # Identify the key columns
        keys = list(data[0].keys())
        name_col = self._find_name_column(keys)
        value_col = self._find_value_column(keys, name_col)

        if not name_col or not value_col:
            logger.warning("Could not identify columns for top_n chart")
            return self._generate_table(query, data)

        names = [row[name_col] for row in data]
        values = [row.get(value_col, 0) or 0 for row in data]  # Convert None to 0

        # Determine if ascending or descending (top = descending, bottom = ascending)
        is_ascending = "bottom" in query.lower() or "worst" in query.lower() or "lowest" in query.lower()
        if is_ascending:
            # Reverse for ascending order
            names = names[::-1]
            values = values[::-1]

        fig = go.Figure(
            go.Bar(
                y=names,
                x=values,
                orientation="h",
                marker=dict(
                    color=values,
                    colorscale="Viridis",
                    showscale=True,
                ),
                text=values,
                textposition="auto",
            )
        )

        # Format the stat label with full description
        stat_label = get_stat_label(value_col)

        fig.update_layout(
            title=f"Top {len(data)} - {stat_label}",
            xaxis_title=stat_label,
            yaxis_title="Player/Team",
            height=max(400, len(data) * 40),
            showlegend=False,
            template="plotly_white",
        )

        return fig

    def _generate_comparison(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate radar chart for comparing 2-4 entities."""
        if len(data) > 4:
            return self._generate_multi_comparison(query, data)

        keys = list(data[0].keys())
        name_col = self._find_name_column(keys)
        stat_cols = [k for k in keys if k != name_col and isinstance(data[0].get(k), (int, float))]

        if not name_col or not stat_cols:
            logger.warning("Could not identify columns for comparison")
            return self._generate_table(query, data)

        # Create radar chart with formatted stat labels
        fig = go.Figure()
        formatted_stat_labels = format_stat_labels(stat_cols)

        for i, row in enumerate(data):
            name = row[name_col]
            values = [row.get(col, 0) or 0 for col in stat_cols]  # Convert None to 0

            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=formatted_stat_labels,
                    fill="toself",
                    name=name,
                    marker=dict(color=self.color_scheme[i % len(self.color_scheme)]),
                )
            )

        max_val = max(
            max((row.get(col, 0) or 0) for col in stat_cols)
            for row in data
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max_val * 1.1])),
            title=f"Player Comparison: {', '.join([row[name_col] for row in data])}",
            showlegend=True,
            height=600,
            template="plotly_white",
        )

        return fig

    def _generate_multi_comparison(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate grouped bar chart for comparing many entities."""
        keys = list(data[0].keys())
        name_col = self._find_name_column(keys)
        value_col = self._find_value_column(keys, name_col)

        if not name_col or not value_col:
            return self._generate_table(query, data)

        names = [row[name_col] for row in data]
        values = [row.get(value_col, 0) or 0 for row in data]  # Convert None to 0

        fig = go.Figure(
            go.Bar(
                x=names,
                y=values,
                marker=dict(
                    color=values,
                    colorscale="Blues",
                    showscale=False,
                ),
                text=values,
                textposition="auto",
            )
        )

        # Format the stat label with full description
        stat_label = get_stat_label(value_col)

        fig.update_layout(
            title=f"{stat_label} Comparison",
            xaxis_title="Player/Team",
            yaxis_title=stat_label,
            xaxis_tickangle=-45,
            height=500,
            showlegend=False,
            template="plotly_white",
        )

        return fig

    def _generate_single_entity(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate stat card / table for single entity."""
        row = data[0]

        # Create a simple stat card display with formatted labels
        stats_text = "<br>".join([f"<b>{get_stat_label(k)}:</b> {v}" for k, v in row.items()])

        fig = go.Figure()

        fig.add_annotation(
            text=stats_text,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16),
            align="left",
        )

        # Use entity name from data if available, otherwise generic title
        entity_name = row.get("name", row.get("team", ""))
        title = f"{entity_name} Stats" if entity_name else "Player Stats"

        # Adjust height based on number of stats
        height = max(300, 50 + len(row) * 30)

        fig.update_layout(
            title=title,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=height,
            template="plotly_white",
        )

        return fig

    def _generate_distribution(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate histogram for distributions."""
        keys = list(data[0].keys())
        value_col = self._find_value_column(keys)

        if not value_col:
            return self._generate_table(query, data)

        values = [row.get(value_col, 0) or 0 for row in data]  # Convert None to 0

        fig = go.Figure(
            go.Histogram(
                x=values,
                nbinsx=min(20, len(values) // 2),
                marker=dict(color="skyblue", line=dict(color="black", width=1)),
            )
        )

        # Format the stat label with full description
        stat_label = get_stat_label(value_col)

        fig.update_layout(
            title=f"Distribution of {stat_label}",
            xaxis_title=stat_label,
            yaxis_title="Count",
            height=500,
            template="plotly_white",
        )

        return fig

    def _generate_correlation(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate scatter plot for correlations."""
        keys = list(data[0].keys())
        name_col = self._find_name_column(keys)
        numeric_cols = [k for k in keys if k != name_col and isinstance(data[0].get(k), (int, float))]

        if len(numeric_cols) < 2:
            logger.warning("Need at least 2 numeric columns for correlation")
            return self._generate_table(query, data)

        x_col, y_col = numeric_cols[0], numeric_cols[1]
        x_values = [row.get(x_col, 0) or 0 for row in data]  # Convert None to 0
        y_values = [row.get(y_col, 0) or 0 for row in data]  # Convert None to 0
        names = [row[name_col] for row in data] if name_col else [f"Player {i+1}" for i in range(len(data))]

        # Format stat labels with full descriptions
        x_label = get_stat_label(x_col)
        y_label = get_stat_label(y_col)

        fig = go.Figure(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers",
                marker=dict(size=10, color="blue", opacity=0.6),
                text=names,
                hovertemplate=f"<b>%{{text}}</b><br>{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>",
            )
        )

        fig.update_layout(
            title=f"{x_label} vs {y_label}",
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=500,
            template="plotly_white",
        )

        return fig

    def _generate_threshold_filter(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate highlighted table for threshold filters."""
        return self._generate_table(query, data, highlight=True)

    def _generate_composition(self, query: str, data: list[dict[str, Any]]) -> go.Figure:
        """Generate pie chart for composition/breakdown."""
        keys = list(data[0].keys())
        name_col = self._find_name_column(keys)
        value_col = self._find_value_column(keys, name_col)

        if not name_col or not value_col:
            return self._generate_table(query, data)

        names = [row[name_col] for row in data]
        values = [row.get(value_col, 0) or 0 for row in data]  # Convert None to 0

        fig = go.Figure(
            go.Pie(
                labels=names,
                values=values,
                hole=0.3,
                textinfo="label+percent",
                marker=dict(colors=self.color_scheme),
            )
        )

        # Format the stat label with full description
        stat_label = get_stat_label(value_col)

        fig.update_layout(
            title=f"{stat_label} Breakdown",
            height=500,
            template="plotly_white",
        )

        return fig

    def _generate_table(self, query: str, data: list[dict[str, Any]], highlight: bool = False) -> go.Figure:
        """Generate interactive table."""
        if not data:
            return go.Figure()

        keys = list(data[0].keys())
        # Format header values with full stat descriptions
        header_values = [get_stat_label(k) for k in keys]
        cell_values = [[row.get(k, "") for row in data] for k in keys]

        # Add highlighting for threshold queries
        cell_colors = None
        if highlight:
            # Simple highlighting: color rows alternately
            cell_colors = [["white" if i % 2 == 0 else "lightgray" for i in range(len(data))] for _ in keys]

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=header_values,
                        fill_color="paleturquoise",
                        align="left",
                        font=dict(size=12, color="black"),
                    ),
                    cells=dict(
                        values=cell_values,
                        fill_color=cell_colors if cell_colors else "white",
                        align="left",
                        font=dict(size=11),
                    ),
                )
            ]
        )

        fig.update_layout(
            title="Query Results",
            height=max(300, min(800, len(data) * 30 + 100)),
            template="plotly_white",
        )

        return fig

    # Helper methods
    def _find_name_column(self, columns: list[str]) -> str | None:
        """Find the column likely containing names."""
        name_keywords = ["name", "player", "team", "entity", "type", "category", "label", "group"]
        for col in columns:
            if any(keyword in col.lower() for keyword in name_keywords):
                return col
        # Fallback: first string-valued column (if data is available)
        return None

    def _find_value_column(self, columns: list[str], exclude: str | None = None) -> str | None:
        """Find the main value column (first numeric column)."""
        for col in columns:
            if col != exclude and col.lower() not in ["id", "player_id", "team_id"]:
                return col
        return None
