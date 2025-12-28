import os
import json
from .utils import write_json


def export_report(project_profile, mock_billing, recommendation, save_path=None):
    """Export a final report.

    The third argument may be either:
    - a list of recommendation objects (legacy), or
    - a dict containing at least a "recommendations" key and optional "analysis" / "project_name" keys (current output of generate_recommendations).
    """

    recommendations = recommendation


    report = {
        "metadata": {
            "tool": "AI-Powered Cloud Cost Optimizer - local",
        },
        "project_profile": project_profile,
        "mock_billing": mock_billing,
        "recommendations": recommendations,
    }

    if save_path:
        write_json(save_path, report)
    return report
