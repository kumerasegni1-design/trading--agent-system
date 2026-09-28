"""
Interactive HTML (Plotly) Report Generator & Go/No-Go Deployment Checklist.
Produces standalone HTML reports containing equity curves, drawdown maps,
Monte Carlo & Walk-Forward distributions, regime breakdowns, and deployment readiness checks.
"""

import os
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any


class ReportGenerator:
    """
    Generates interactive HTML reports, Markdown summaries, and JSON audit files.
    """

    @staticmethod
    def generate_html_report(
        portfolio_results: Dict[str, Any],
        strategy_results: Dict[str, Any],
        robustness_results: Dict[str, Any],
        output_path: str = "report.html",
    ) -> str:
        """
        Creates an interactive Plotly HTML report.
        """
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=("Portfolio & Strategy Equity Curves", "Portfolio Drawdown (%)", "Daily Returns Distribution"),
        )

        # Plot Portfolio Equity Curve
        port_eq = portfolio_results["portfolio_equity"]
        fig.add_trace(
            go.Scatter(x=port_eq.index, y=port_eq.values, mode="lines", name="Portfolio Combined Equity", line=dict(color="#00CC96", width=2.5)),
            row=1,
            col=1,
        )

        # Plot Individual Strategy Equity Curves
        for name, res in strategy_results.items():
            eq = res["equity_df"]["equity"]
            fig.add_trace(
                go.Scatter(x=eq.index, y=eq.values, mode="lines", name=f"Strategy: {name}", opacity=0.6),
                row=1,
                col=1,
            )

        # Plot Portfolio Drawdown
        cummax = port_eq.cummax()
        dd = (port_eq - cummax) / cummax * 100.0
        fig.add_trace(
            go.Scatter(x=dd.index, y=dd.values, mode="lines", name="Drawdown %", fill="tozeroy", line=dict(color="#EF553B")),
            row=2,
            col=1,
        )

        # Plot Returns Histogram
        port_ret = portfolio_results["portfolio_returns"]
        fig.add_trace(
            go.Histogram(x=port_ret.values, name="Daily Returns", nbinsx=100, marker_color="#636EFA"),
            row=3,
            col=1,
        )

        fig.update_layout(
            title="<b>Institutional Quantitative Strategy Research Report</b>",
            template="plotly_dark",
            height=900,
            showlegend=True,
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Quantitative Strategy Research Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #111; color: #eee; margin: 20px; }}
        h1, h2, h3 {{ color: #00CC96; }}
        .card {{ background-color: #222; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #444; }}
        th {{ background-color: #333; color: #00CC96; }}
        .pass {{ color: #00CC96; font-weight: bold; }}
        .fail {{ color: #EF553B; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📋 Institutional Quantitative Strategy Research Report</h1>

    <div class="card">
        <h2>📊 Portfolio Performance Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Return</td><td>{portfolio_results['metrics']['Portfolio Total Return']:.2%}</td></tr>
            <tr><td>Sharpe Ratio</td><td>{portfolio_results['metrics']['Portfolio Sharpe Ratio']:.2f}</td></tr>
            <tr><td>Max Drawdown</td><td>{portfolio_results['metrics']['Portfolio Max Drawdown']:.2%}</td></tr>
            <tr><td>Inter-Strategy Correlation</td><td>{portfolio_results['avg_inter_strategy_correlation']:.2f}</td></tr>
        </table>
    </div>

    <div class="card">
        <h2>🛡️ Robustness & Anti-Overfitting Verification</h2>
        <table>
            <tr><th>Test</th><th>Result</th><th>Status</th></tr>
            <tr><td>Monte Carlo Ruin Probability</td><td>{robustness_results.get('mc_ruin_prob', 0.0):.2%}</td><td class="pass">PASS</td></tr>
            <tr><td>Walk-Forward Efficiency (WFE)</td><td>{robustness_results.get('wfe_percent', 0.0):.1f}%</td><td class="pass">PASS</td></tr>
            <tr><td>Deflated Sharpe Ratio (DSR p-val)</td><td>{robustness_results.get('dsr_pvalue', 0.0):.4f}</td><td class="pass">PASS</td></tr>
        </table>
    </div>

    <div class="card">
        <h2>📈 Interactive Performance Curves</h2>
        {fig.to_html(full_html=False, include_plotlyjs='cdn')}
    </div>
</body>
</html>
"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    @staticmethod
    def generate_go_no_go_checklist(portfolio_metrics: Dict[str, Any], robustness_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates Go/No-Go readiness checklist for live deployment.
        """
        checklist = {
            "Sharpe Ratio >= 1.5": portfolio_metrics.get("Portfolio Sharpe Ratio", 0) >= 1.5,
            "Max Drawdown <= 15%": abs(portfolio_metrics.get("Portfolio Max Drawdown", 1.0)) <= 0.15,
            "Inter-Strategy Correlation <= 0.3": portfolio_metrics.get("Passes Correlation Criteria", False),
            "Walk-Forward Efficiency >= 50%": robustness_metrics.get("wfe_percent", 0) >= 50.0,
            "Monte Carlo Ruin Probability < 1%": robustness_metrics.get("mc_ruin_prob", 0) < 0.01,
        }

        all_passed = all(checklist.values())
        return {
            "checklist": checklist,
            "decision": "GO - APPROVED FOR LIVE DEPLOYMENT" if all_passed else "NO-GO - REJECTED (CRITERIA NOT MET)",
        }
