"""Configuration module for Aria tools."""

from Bio import Entrez
from .io import load_config

config = load_config()

# Configure Entrez for PubMed access
Entrez.email = config["entrez"]["email"]
Entrez.tool = config["entrez"]["tool"]
