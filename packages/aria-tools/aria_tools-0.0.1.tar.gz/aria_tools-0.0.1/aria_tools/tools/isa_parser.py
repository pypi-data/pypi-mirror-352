"""Data analysis tool for files from a single ISA-Tab study."""

from io import StringIO
from collections.abc import Callable
from typing import Any, Hashable
from pydantic import Field
import pandas as pd
from pandas import DataFrame
from hypha_rpc.utils.schema import schema_function  # type: ignore
from aria_tools.utils.models import Document, IsaStudy


def split_lines(content: str) -> list[str]:
    """Split content into non-empty stripped lines."""
    return [line.strip() for line in content.strip().split("\n") if line.strip()]


def parse_section(
    lines: list[str], header_check: Callable[..., bool]
) -> dict[str, dict[str, list[str]]]:
    """Parse sections of a file based on headers."""
    data: dict[str, dict[str, list[str]]] = {}
    current_section = None
    current_subsection = None

    for line in lines:
        if header_check(line):
            current_section = line
            data[current_section] = {}
            current_subsection = None
        elif current_section and "\t" in line:
            parts = line.split("\t")
            field_name = parts[0].strip()
            field_values = [v.strip() for v in parts[1:]]

            if field_name and not field_name.startswith(" "):
                current_subsection = field_name
                data[current_section][current_subsection] = field_values

    return data


def is_header(line: str) -> bool:
    """Check if a line is a header line in an ISA-Tab file.

    Args:
        line: The line to check

    Returns:
        True if the line is a header, False otherwise
    """

    header_names = [
        "ONTOLOGY SOURCE REFERENCE",
        "INVESTIGATION",
        "INVESTIGATION PUBLICATIONS",
        "INVESTIGATION CONTACTS",
        "STUDY",
        "STUDY DESIGN DESCRIPTORS",
        "STUDY PUBLICATIONS",
        "STUDY FACTORS",
        "STUDY ASSAYS",
        "STUDY PROTOCOLS",
        "STUDY CONTACTS",
    ]
    return line in header_names


def parse_investigation_data(
    investigation_file: Document,
) -> dict[str, Any]:
    """Parse the investigation file and return a structured dictionary of its contents."""
    lines = split_lines(investigation_file.content)
    return parse_section(lines, is_header)


def parse_study_data(
    study_file: Document,
) -> dict[str, list[str] | list[dict[Hashable, Any]]]:
    """Parse the study file and return a structured dictionary of its contents.

    Args:
        study_file: The ISA-Tab study file content

    Returns:
        A dictionary containing the parsed study data
    """

    df: DataFrame = pd.read_csv(StringIO(study_file.content), sep="\t")  # type: ignore
    headers: list[str] = df.columns.tolist()
    records: list[dict[Hashable, Any]] = df.to_dict(orient="records")  # type: ignore

    return {"headers": headers, "samples": records}


def parse_assay_data(assay_files: list[Document]) -> dict[str, Any]:
    """Parse the assay files and return a structured dictionary of their contents.

    Args:
        assay_files: The ISA-Tab assay files

    Returns:
        A dictionary containing the parsed assay data
    """
    assay_data: dict[str, Any] = {}

    for assay_file in assay_files:
        filename = assay_file.name
        assay_name = filename.replace("a_", "").replace(".txt", "")
        assay_data[assay_name] = parse_study_data(assay_file)

    return assay_data


def is_metadata_column(col: str) -> bool:
    """Check if a column is a metadata column.

    Args:
        col: The column name

    Returns:
        True if the column is a metadata column, False otherwise
    """
    known_metadata_cols = [
        "database_identifier",
        "chemical_formula",
        "smiles",
        "inchi",
        "metabolite_identification",
        "mass_to_charge",
        "fragmentation",
        "modifications",
        "charge",
        "retention_time",
        "taxid",
        "species",
        "database",
        "database_version",
        "reliability",
        "uri",
        "search_engine",
        "search_engine_score",
        "smallmolecule_abundance_sub",
        "smallmolecule_abundance_stdev_sub",
        "smallmolecule_abundance_std_error_sub",
    ]

    return col in known_metadata_cols


def parse_metabolite_file(metabolite_file: Document) -> dict[str, Any]:
    """Parse a single metabolite file and return its structured data."""
    df: DataFrame = pd.read_csv(StringIO(metabolite_file.content), sep="\t")  # type: ignore
    all_columns = df.columns.tolist()

    metadata_columns = [col for col in all_columns if is_metadata_column(col)]
    sample_columns = [col for col in all_columns if col not in metadata_columns]
    metabolites: list[dict[str, Any]] = []

    for _, row in df.iterrows():  # type: ignore
        metabolite_info: dict[str, Any] = {
            meta: row[meta] for meta in metadata_columns if meta in row.index  # type: ignore
        }

        # Add abundance values for each sample
        abundances: dict[str, Any] = {
            sample: row[sample] for sample in sample_columns if sample in row.index  # type: ignore
        }
        metabolite_info["abundances"] = abundances

        metabolites.append(metabolite_info)

    return {
        "metadata_columns": metadata_columns,
        "sample_columns": sample_columns,
        "metabolites": metabolites,
    }


def parse_metabolite_data(metabolite_files: list[Document]) -> dict[str, Any]:
    """Parse the metabolite files and return a structured dictionary of their contents.

    Args:
        metabolite_files: The ISA-Tab metabolite files

    Returns:
        A dictionary containing the parsed metabolite data
    """
    return {
        metabolite_file.name.replace("m_", "").replace(
            ".tsv", ""
        ): parse_metabolite_file(metabolite_file)
        for metabolite_file in metabolite_files
    }


def get_study_name(investigation_data: dict[str, Any]) -> str:
    """Get the study name from the study data.

    Args:
        investigation_data: The parsed investigation data

    Returns:
        The study name
    """
    return investigation_data["STUDY"]["Study Title"][0]


def get_study_description(investigation_data: dict[str, Any]) -> str:
    """Get the study description from the study data.

    Args:
        investigation_data: The parsed investigation data

    Returns:
        The study description
    """
    return investigation_data["STUDY"]["Study Description"][0]


@schema_function
async def parse_isa_data(
    investigation_file: Document = Field(
        description="The ISA-Tab investigation.txt file"
    ),
    study_file: Document = Field(description="The ISA-Tab study.txt file"),
    assay_files: list[Document] = Field(description="The ISA-Tab assay files"),
    metabolite_files: list[Document] = Field(
        description="The ISA-Tab metabolite files"
    ),
) -> IsaStudy:
    """Parses the ISA-Tab .txt files"""
    investigation_data = parse_investigation_data(investigation_file)
    study_data = parse_study_data(study_file)
    assay_data = parse_assay_data(assay_files)
    metabolite_data = parse_metabolite_data(metabolite_files)

    study_name = get_study_name(investigation_data)
    study_description = get_study_description(investigation_data)
    return IsaStudy(
        study_name=study_name,
        study_description=study_description,
        investigation_data=investigation_data,
        study_data=study_data,
        assay_data=assay_data,
        metabolite_data=metabolite_data,
    )
