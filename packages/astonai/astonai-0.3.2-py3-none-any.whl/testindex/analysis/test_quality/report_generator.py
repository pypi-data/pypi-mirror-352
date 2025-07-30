"""
Test Quality Report Generator

Provides functionality to generate test quality reports in various formats.
"""
import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from testindex.analysis.test_quality.metrics import QualityMetrics
from testindex.core.utils import ensure_directory, format_timestamp
from testindex.core.logging import get_logger

logger = get_logger(__name__)

class QualityReportGenerator:
    """Generate reports from test quality metrics in various formats."""

    def __init__(self, output_dir: str = "reports"):
        """Initialize the report generator.
        
        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = output_dir
        
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_summary_report(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Generate a summary report as a dictionary.
        
        Args:
            metrics: Test quality metrics to include in the report
            
        Returns:
            Dict[str, Any]: Summary report as a dictionary
        """
        # Calculate health score if not already calculated
        if metrics.health_score == 0.0:
            metrics.calculate_health_score()
            
        # Create timestamp for the report
        timestamp = datetime.datetime.now().isoformat()
        
        return {
            "timestamp": timestamp,
            "metrics": metrics.to_dict(),
            "summary": {
                "total_tests": metrics.total_tests,
                "pass_rate": f"{metrics.pass_rate:.2f}%",
                "health_score": f"{metrics.health_score:.2f}",
                "code_coverage": f"{metrics.code_coverage_percentage:.2f}%",
                "flakiness_score": f"{metrics.flakiness_score:.2f}",
                "avg_execution_time": f"{metrics.avg_execution_time:.3f}s",
            }
        }
    
    def generate_json_report(self, metrics: QualityMetrics, filename: Optional[str] = None) -> str:
        """Generate a JSON report from test quality metrics.
        
        Args:
            metrics: Test quality metrics to include in the report
            filename: Output filename (default: test_quality_report_{timestamp}.json)
            
        Returns:
            str: Path to the generated report file
        """
        self._ensure_output_dir()
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_quality_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate report data
        report_data = self.generate_summary_report(metrics)
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        return filepath
    
    def generate_markdown_report(self, metrics: QualityMetrics, filename: Optional[str] = None) -> str:
        """Generate a Markdown report from test quality metrics.
        
        Args:
            metrics: Test quality metrics to include in the report
            filename: Output filename (default: test_quality_report_{timestamp}.md)
            
        Returns:
            str: Path to the generated report file
        """
        self._ensure_output_dir()
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_quality_report_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate report data
        report_data = self.generate_summary_report(metrics)
        
        # Format as Markdown
        with open(filepath, 'w') as f:
            f.write(f"# Test Quality Report\n\n")
            f.write(f"Generated: {report_data['timestamp']}\n\n")
            
            f.write("## Summary\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            for key, value in report_data["summary"].items():
                f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
            
            f.write("\n## Test Counts\n\n")
            test_counts = report_data["metrics"]["test_counts"]
            f.write("| Metric | Count | Percentage |\n")
            f.write("|--------|-------|------------|\n")
            f.write(f"| Total Tests | {test_counts['total']} | 100% |\n")
            f.write(f"| Passing Tests | {test_counts['passing']} | {test_counts['pass_rate']:.2f}% |\n")
            f.write(f"| Failing Tests | {test_counts['failing']} | {test_counts['failure_rate']:.2f}% |\n")
            f.write(f"| Skipped Tests | {test_counts['skipped']} | {test_counts['skip_rate']:.2f}% |\n")
            
            f.write("\n## Coverage\n\n")
            coverage = report_data["metrics"]["coverage"]
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Coverage Percentage | {coverage['percentage']:.2f}% |\n")
            f.write(f"| Covered Lines | {coverage['covered_lines']} |\n")
            f.write(f"| Total Lines | {coverage['total_lines']} |\n")
            
            f.write("\n## Performance\n\n")
            performance = report_data["metrics"]["performance"]
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Average Execution Time | {performance['average_execution_time']:.3f}s |\n")
            f.write(f"| Total Execution Time | {performance['total_execution_time']:.3f}s |\n")
            
            f.write("\n## Complexity\n\n")
            complexity = report_data["metrics"]["complexity"]
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Average Complexity | {complexity['average']:.2f} |\n")
            f.write(f"| Maximum Complexity | {complexity['maximum']:.2f} |\n")
            
            f.write("\n## Reliability\n\n")
            reliability = report_data["metrics"]["reliability"]
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Flakiness Score | {reliability['flakiness_score']:.2f} |\n")
            
            if metrics.metadata:
                f.write("\n## Additional Metadata\n\n")
                f.write("| Key | Value |\n")
                f.write("|-----|-------|\n")
                for key, value in metrics.metadata.items():
                    f.write(f"| {key} | {value} |\n")
        
        return filepath
    
    def generate_html_report(self, metrics: QualityMetrics, filename: Optional[str] = None) -> str:
        """Generate an HTML report from test quality metrics.
        
        Args:
            metrics: Test quality metrics to include in the report
            filename: Output filename (default: test_quality_report_{timestamp}.html)
            
        Returns:
            str: Path to the generated report file
        """
        self._ensure_output_dir()
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_quality_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate report data
        report_data = self.generate_summary_report(metrics)
        
        # Helper function for color coding
        def get_status_color(metric_name: str, value: float) -> str:
            """Determine color based on metric value."""
            if metric_name == "health_score" or metric_name == "pass_rate" or metric_name == "code_coverage":
                if value >= 90:
                    return "green"
                elif value >= 75:
                    return "orange"
                else:
                    return "red"
            elif metric_name == "flakiness_score":
                if value <= 0.1:
                    return "green"
                elif value <= 0.3:
                    return "orange"
                else:
                    return "red"
            # Default color
            return "black"
        
        # Format as HTML - use triple quotes for multi-line strings to avoid escaping issues
        with open(filepath, 'w') as f:
            # Write HTML header
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Quality Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .metric-value {{
            font-weight: bold;
        }}
        .good {{
            color: green;
        }}
        .warning {{
            color: orange;
        }}
        .poor {{
            color: red;
        }}
        .summary-card {{
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>Test Quality Report</h1>
    <p>Generated: {report_data['timestamp']}</p>
    
    <div class="summary-card">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
""")
            
            # Add summary metrics
            for key, value in report_data["summary"].items():
                # Parse the value to get a float for color coding
                try:
                    if isinstance(value, str) and "%" in value:
                        float_value = float(value.replace("%", ""))
                    else:
                        float_value = float(value)
                except ValueError:
                    float_value = 0
                
                color = get_status_color(key, float_value)
                
                f.write(f"""
            <tr>
                <td>{key.replace('_', ' ').title()}</td>
                <td><span class="metric-value" style="color: {color}">{value}</span></td>
            </tr>""")
            
            # Test counts section
            f.write("""
        </table>
    </div>
    
    <div class="summary-card">
        <h2>Test Counts</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>""")
            
            test_counts = report_data["metrics"]["test_counts"]
            
            # Get pass rate color
            pass_rate_color = get_status_color('pass_rate', test_counts['pass_rate'])
            
            f.write(f"""
            <tr>
                <td>Total Tests</td>
                <td>{test_counts['total']}</td>
                <td>100%</td>
            </tr>
            <tr>
                <td>Passing Tests</td>
                <td>{test_counts['passing']}</td>
                <td><span style="color: {pass_rate_color}">{test_counts['pass_rate']:.2f}%</span></td>
            </tr>
            <tr>
                <td>Failing Tests</td>
                <td>{test_counts['failing']}</td>
                <td>{test_counts['failure_rate']:.2f}%</td>
            </tr>
            <tr>
                <td>Skipped Tests</td>
                <td>{test_counts['skipped']}</td>
                <td>{test_counts['skip_rate']:.2f}%</td>
            </tr>""")
            
            # Coverage section
            f.write("""
        </table>
    </div>
    
    <div class="summary-card">
        <h2>Coverage</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>""")
            
            coverage = report_data["metrics"]["coverage"]
            coverage_color = get_status_color('code_coverage', coverage['percentage'])
            
            f.write(f"""
            <tr>
                <td>Coverage Percentage</td>
                <td><span style="color: {coverage_color}">{coverage['percentage']:.2f}%</span></td>
            </tr>
            <tr>
                <td>Covered Lines</td>
                <td>{coverage['covered_lines']}</td>
            </tr>
            <tr>
                <td>Total Lines</td>
                <td>{coverage['total_lines']}</td>
            </tr>""")
            
            # Performance section
            f.write("""
        </table>
    </div>
    
    <div class="summary-card">
        <h2>Performance</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>""")
            
            performance = report_data["metrics"]["performance"]
            f.write(f"""
            <tr>
                <td>Average Execution Time</td>
                <td>{performance['average_execution_time']:.3f}s</td>
            </tr>
            <tr>
                <td>Total Execution Time</td>
                <td>{performance['total_execution_time']:.3f}s</td>
            </tr>""")
            
            # Complexity section
            f.write("""
        </table>
    </div>
    
    <div class="summary-card">
        <h2>Complexity</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>""")
            
            complexity = report_data["metrics"]["complexity"]
            f.write(f"""
            <tr>
                <td>Average Complexity</td>
                <td>{complexity['average']:.2f}</td>
            </tr>
            <tr>
                <td>Maximum Complexity</td>
                <td>{complexity['maximum']:.2f}</td>
            </tr>""")
            
            # Reliability section
            f.write("""
        </table>
    </div>
    
    <div class="summary-card">
        <h2>Reliability</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>""")
            
            reliability = report_data["metrics"]["reliability"]
            flakiness_color = get_status_color('flakiness_score', reliability['flakiness_score'])
            
            f.write(f"""
            <tr>
                <td>Flakiness Score</td>
                <td><span style="color: {flakiness_color}">{reliability['flakiness_score']:.2f}</span></td>
            </tr>""")
            
            f.write("""
        </table>
    </div>""")
            
            # Metadata section if available
            if metrics.metadata:
                f.write("""
    <div class="summary-card">
        <h2>Additional Metadata</h2>
        <table>
            <tr>
                <th>Key</th>
                <th>Value</th>
            </tr>""")
                
                for key, value in metrics.metadata.items():
                    f.write(f"""
            <tr>
                <td>{key}</td>
                <td>{value}</td>
            </tr>""")
                
                f.write("""
        </table>
    </div>""")
            
            # Close HTML document
            f.write("""
</body>
</html>""")
        
        return filepath
    
    def generate_comparison_report(
        self, 
        before_metrics: QualityMetrics, 
        after_metrics: QualityMetrics, 
        filename: Optional[str] = None
    ) -> str:
        """Generate a comparison report between two sets of metrics.
        
        Args:
            before_metrics: Test quality metrics from before changes
            after_metrics: Test quality metrics from after changes
            filename: Output filename (default: test_quality_comparison_{timestamp}.html)
            
        Returns:
            str: Path to the generated report file
        """
        self._ensure_output_dir()
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_quality_comparison_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate health scores if not already calculated
        if before_metrics.health_score == 0.0:
            before_metrics.calculate_health_score()
        if after_metrics.health_score == 0.0:
            after_metrics.calculate_health_score()
        
        # Calculate differences
        diff = {
            "total_tests": after_metrics.total_tests - before_metrics.total_tests,
            "passing_tests": after_metrics.passing_tests - before_metrics.passing_tests,
            "failing_tests": after_metrics.failing_tests - before_metrics.failing_tests,
            "skipped_tests": after_metrics.skipped_tests - before_metrics.skipped_tests,
            "pass_rate": after_metrics.pass_rate - before_metrics.pass_rate,
            "code_coverage": after_metrics.code_coverage_percentage - before_metrics.code_coverage_percentage,
            "health_score": after_metrics.health_score - before_metrics.health_score,
            "avg_execution_time": after_metrics.avg_execution_time - before_metrics.avg_execution_time,
            "flakiness_score": after_metrics.flakiness_score - before_metrics.flakiness_score,
        }
        
        # Determine overall quality change
        is_quality_improved = diff["health_score"] > 0
        quality_change_class = "improved" if is_quality_improved else "degraded"
        health_score_change_class = "improved" if diff["health_score"] > 0 else "degraded" if diff["health_score"] < 0 else "neutral"
        
        # Generate recommendations based on differences
        recommendations = []
        
        if diff["failing_tests"] > 0:
            recommendations.append("Address the increased number of failing tests.")
        
        if diff["pass_rate"] < -1.0:  # More than 1% decrease
            recommendations.append("Investigate the decrease in test pass rate.")
        
        if diff["code_coverage"] < -1.0:  # More than 1% decrease
            recommendations.append("Review code coverage reduction and add tests for uncovered code.")
        
        if diff["flakiness_score"] > 0.05:  # More than 0.05 increase
            recommendations.append("Address the increased test flakiness.")
            
        if diff["avg_execution_time"] > 0.1:  # More than 0.1s increase
            recommendations.append("Optimize test performance to reduce execution time.")
            
        if not recommendations and is_quality_improved:
            recommendations.append("Good job! Test quality has improved.")
        elif not recommendations:
            recommendations.append("Maintain current test quality practices.")
        
        # Format as HTML
        with open(filepath, 'w') as f:
            # Add HTML header and style
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Quality Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .improved {{
            color: green;
        }}
        .degraded {{
            color: red;
        }}
        .neutral {{
            color: #666;
        }}
        .summary-card {{
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .recommendations {{
            background-color: #e9f7ef;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>Test Quality Comparison Report</h1>
    <p>Generated: {datetime.datetime.now().isoformat()}</p>
    
    <div class="summary-card">
        <h2>Overall Change</h2>
        <p>The overall test quality has <strong class="{quality_change_class}">{is_quality_improved and "improved" or "degraded"}</strong>.</p>
        <p>Health Score Change: <span class="{health_score_change_class}">{diff["health_score"]:+.2f}</span> points</p>
    </div>
""")
            
            # Recommendations section
            f.write("""
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
""")
            for recommendation in recommendations:
                f.write(f"            <li>{recommendation}</li>\n")
            
            f.write("""
        </ul>
    </div>
""")
            
            # Comparison table
            f.write("""
    <div class="summary-card">
        <h2>Metrics Comparison</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Before</th>
                <th>After</th>
                <th>Change</th>
            </tr>
""")
            
            # Helper function for formatting change indicators
            def format_change(metric_name, value, is_percentage=False, inverted=False):
                if value == 0:
                    return f'<span class="neutral">{value:+.2f}{"%" if is_percentage else ""}</span>'
                
                # For flakiness score and execution time, lower is better
                if inverted:
                    css_class = "degraded" if value > 0 else "improved"
                else:
                    css_class = "improved" if value > 0 else "degraded"
                
                return f'<span class="{css_class}">{value:+.2f}{"%" if is_percentage else ""}</span>'
            
            # Add rows for key metrics
            metrics_data = [
                ("Total Tests", before_metrics.total_tests, after_metrics.total_tests, diff["total_tests"], False, False),
                ("Passing Tests", before_metrics.passing_tests, after_metrics.passing_tests, diff["passing_tests"], False, False),
                ("Failing Tests", before_metrics.failing_tests, after_metrics.failing_tests, diff["failing_tests"], False, True),
                ("Skipped Tests", before_metrics.skipped_tests, after_metrics.skipped_tests, diff["skipped_tests"], False, False),
                ("Pass Rate", before_metrics.pass_rate, after_metrics.pass_rate, diff["pass_rate"], True, False),
                ("Code Coverage", before_metrics.code_coverage_percentage, after_metrics.code_coverage_percentage, diff["code_coverage"], True, False),
                ("Health Score", before_metrics.health_score, after_metrics.health_score, diff["health_score"], False, False),
                ("Avg Execution Time (s)", before_metrics.avg_execution_time, after_metrics.avg_execution_time, diff["avg_execution_time"], False, True),
                ("Flakiness Score", before_metrics.flakiness_score, after_metrics.flakiness_score, diff["flakiness_score"], False, True),
            ]
            
            for name, before, after, change, is_pct, inverted in metrics_data:
                change_display = format_change(name, change, is_pct, inverted)
                f.write(f"""
            <tr>
                <td>{name}</td>
                <td>{before:.2f}{"%" if is_pct else ""}</td>
                <td>{after:.2f}{"%" if is_pct else ""}</td>
                <td>{change_display}</td>
            </tr>""")
            
            # Complexity changes section
            avg_complexity_change = after_metrics.avg_test_complexity - before_metrics.avg_test_complexity
            max_complexity_change = after_metrics.max_test_complexity - before_metrics.max_test_complexity
            
            avg_complexity_display = format_change("avg_complexity", avg_complexity_change, False, True)
            max_complexity_display = format_change("max_complexity", max_complexity_change, False, True)
            
            f.write(f"""
        </table>
    </div>

    <div class="summary-card">
        <h2>Complexity Changes</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Before</th>
                <th>After</th>
                <th>Change</th>
            </tr>
            <tr>
                <td>Average Complexity</td>
                <td>{before_metrics.avg_test_complexity:.2f}</td>
                <td>{after_metrics.avg_test_complexity:.2f}</td>
                <td>{avg_complexity_display}</td>
            </tr>
            <tr>
                <td>Maximum Complexity</td>
                <td>{before_metrics.max_test_complexity:.2f}</td>
                <td>{after_metrics.max_test_complexity:.2f}</td>
                <td>{max_complexity_display}</td>
            </tr>
        </table>
    </div>
""")
            
            # Close HTML document
            f.write("""
</body>
</html>""")
        
        return filepath
    
    def generate_simple_report(self, metrics: QualityMetrics) -> str:
        """Generate a simple text representation of test quality metrics.
        
        Args:
            metrics: Test quality metrics to report
            
        Returns:
            str: Text representation of the metrics
        """
        # Calculate health score if not already calculated
        if metrics.health_score == 0.0:
            metrics.calculate_health_score()
        
        return f"""
Test Quality Report
==================

Total Tests: {metrics.total_tests}
Passing: {metrics.passing_tests} ({metrics.pass_rate:.2f}%)
Failing: {metrics.failing_tests} ({metrics.failure_rate:.2f}%)
Skipped: {metrics.skipped_tests} ({metrics.skip_rate:.2f}%)

Code Coverage: {metrics.code_coverage_percentage:.2f}%
Flakiness Score: {metrics.flakiness_score:.2f}
Average Complexity: {metrics.avg_test_complexity:.2f}
Average Execution Time: {metrics.avg_execution_time:.3f}s

Health Score: {metrics.health_score:.2f}/100
"""