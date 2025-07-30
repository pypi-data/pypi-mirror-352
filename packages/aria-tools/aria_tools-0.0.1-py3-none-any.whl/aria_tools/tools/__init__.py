"""Core tools for scientific research automation.

This module provides tools for automating various aspects of scientific research,
including study suggestion, protocol management, literature search, and data analysis.
Each tool is designed to handle a specific task in the research workflow.
"""

from .study_suggester import create_study_suggester_function
from .html_pager import create_make_html_page
from .diagrammer import create_diagram_function
from .protocol_reviewer import create_protocol_feedback_function
from .protocol_writer import create_write_protocol
from .protocol_updater import create_protocol_update_function
from .pubmed_hitter import check_pubmed_hits
from .pubmed_querier import query_pubmed
from .best_pubmed_query import create_best_pubmed_query_tool
from .isa_parser import parse_isa_data

__all__ = [
    "create_study_suggester_function",
    "create_make_html_page",
    "create_diagram_function",
    "create_protocol_feedback_function",
    "create_write_protocol",
    "create_protocol_update_function",
    "create_best_pubmed_query_tool",
    "check_pubmed_hits",
    "query_pubmed",
    "parse_isa_data",
]
