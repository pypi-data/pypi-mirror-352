"""Utility functions for reading and writing files"""

import os
import json
from typing import Any


def load_config() -> dict[str, Any]:
    """Load configuration from a JSON file.

    Returns:
        dict: The configuration data loaded from the JSON file.
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(this_dir, "config.json")
    with open(config_file, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config


def load_template(template_filename: str) -> str:
    """Load a HTML page template file from the html_templates directory"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(this_dir, f"../html_templates/{template_filename}")
    with open(template_file, "r", encoding="utf-8") as t_file:
        return t_file.read()
