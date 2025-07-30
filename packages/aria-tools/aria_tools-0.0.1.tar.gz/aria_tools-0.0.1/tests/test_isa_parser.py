"""Test module for ISA-Tab data parsing and analysis.

This module tests the functionality for parsing ISA-Tab investigation, study, assay,
and metabolite files, verifying that the tool correctly processes and structures the data.
"""

import pytest
from faker import Faker
from typing import Hashable, Any
from aria_tools.tools.isa_parser import (
    parse_isa_data,
    parse_investigation_data,
    parse_study_data,
    parse_assay_data,
    parse_metabolite_data,
)
from aria_tools.utils.models import Document, IsaStudy

fake = Faker()


@pytest.fixture(name="mock_investigation_file")
def fixture_mock_investigation_file() -> Document:
    """Generate a mock ISA-Tab investigation file for testing.

    Returns:
        Document: A Document instance with investigation file content.
    """
    # Create a realistic investigation file with standard ISA-Tab format
    content = [
        "ONTOLOGY SOURCE REFERENCE",
        "Term Source Name\tOBI\tCHEBI\tNCBITaxon",
        (
            "Term Source File\thttp://purl.obolibrary.org/obo/obi.owl\t"
            "http://purl.obolibrary.org/obo/chebi.owl"
            "\thttp://purl.obolibrary.org/obo/ncbitaxon.owl"
        ),
        "Term Source Version\t1.2\t1.1\t2022-06-01",
        (
            "Term Source Description\tOntology for Biomedical Investigations"
            "\tChemical Entities of Biological Interest\tNCBI Taxonomy"
        ),
        "",
        "INVESTIGATION",
        "Investigation Identifier\tMETB-001",
        "Investigation Title\tMetabolomics Study of Plant Response to Stress",
        (
            "Investigation Description\tInvestigation of metabolomic changes in plants"
            " under stress conditions"
        ),
        "Investigation Submission Date\t2023-06-15",
        "Investigation Public Release Date\t2023-12-01",
        "",
        "INVESTIGATION PUBLICATIONS",
        "Investigation PubMed ID\t12345678",
        "Investigation Publication DOI\t10.1234/example.2023.001",
        "Investigation Publication Author List\tJane Doe, John Smith",
        "Investigation Publication Title\tMetabolic Response Patterns in Plant Systems",
        "Investigation Publication Status\tpublished",
        "",
        "INVESTIGATION CONTACTS",
        "Investigation Person Last Name\tDoe",
        "Investigation Person First Name\tJane",
        "Investigation Person Email\tjdoe@example.edu",
        "Investigation Person Affiliation\tUniversity of Example",
        "Investigation Person Roles\tprincipal investigator",
        "",
        "STUDY",
        "Study Identifier\tSTD-001",
        "Study Title\tPlant Stress Response Study",
        (
            "Study Description\tCharacterization of metabolomic response in plants under"
            " drought stress"
        ),
        "Study Submission Date\t2023-05-10",
        "Study Public Release Date\t2023-11-01",
        "Study File Name\ts_STD-001.txt",
        "",
        "STUDY DESIGN DESCRIPTORS",
        "Study Design Type\tparallel group design",
        "Study Design Type Term Accession Number\tOBI:0500006",
        "Study Design Type Term Source REF\tOBI",
        "",
        "STUDY FACTORS",
        "Study Factor Name\tDrought Stress\tLight Intensity",
        "Study Factor Type\tstress\tlight",
        "Study Factor Type Term Accession Number\tOBI:0000517\tOBI:0000412",
        "Study Factor Type Term Source REF\tOBI\tOBI",
    ]

    return Document(
        content="\n".join(content),
        name="i_investigation.txt",
        metadata={"type": "isa-investigation", "delimiter": "\t"},
    )


@pytest.fixture(name="mock_study_file")
def fixture_mock_study_file() -> Document:
    """Generate a mock ISA-Tab study file for testing.

    Returns:
        Document: A Document instance with study file content.
    """
    # Create a realistic study file with sample entries
    content = [
        (
            "Source Name\tOrganism\tCharacteristics[Organism Part]\tProtocol REF"
            "\tSample Name\tFactor Value[Drought Stress]\tFactor Value[Light Intensity]"
        ),
        "plant1\tArabidopsis thaliana\tleaf\tsample collection\tsample1\tcontrol\thigh",
        "plant2\tArabidopsis thaliana\tleaf\tsample collection\tsample2\tdrought\thigh",
        "plant3\tArabidopsis thaliana\tleaf\tsample collection\tsample3\tcontrol\tlow",
        "plant4\tArabidopsis thaliana\tleaf\tsample collection\tsample4\tdrought\tlow",
        "plant5\tArabidopsis thaliana\troot\tsample collection\tsample5\tcontrol\thigh",
        "plant6\tArabidopsis thaliana\troot\tsample collection\tsample6\tdrought\thigh",
    ]

    return Document(
        content="\n".join(content),
        name="s_STD-001.txt",
        metadata={"type": "isa-study", "delimiter": "\t"},
    )


@pytest.fixture(name="mock_assay_file")
def fixture_mock_assay_file() -> Document:
    """Generate a mock ISA-Tab assay file for testing.

    Returns:
        Document: A Document instance with assay file content.
    """
    # Create a realistic assay file
    content = [
        (
            "Sample Name\tProtocol REF\tExtract Name\tProtocol REF\tMS Assay Name"
            "\tRaw Data File\tProtocol REF\tData Transformation Name\tDerived Data File"
        ),
        (
            "sample1\textraction\textract1\tchromatography\tassay1\traw1.mzML"
            "\tdata transformation\tnormalized1\tmetabolite_data1.tsv"
        ),
        (
            "sample2\textraction\textract2\tchromatography\tassay2\traw2.mzML"
            "\tdata transformation\tnormalized2\tmetabolite_data2.tsv"
        ),
        (
            "sample3\textraction\textract3\tchromatography\tassay3\traw3.mzML"
            "\tdata transformation\tnormalized3\tmetabolite_data3.tsv"
        ),
        (
            "sample4\textraction\textract4\tchromatography\tassay4\traw4.mzML"
            "\tdata transformation\tnormalized4\tmetabolite_data4.tsv"
        ),
    ]

    return Document(
        content="\n".join(content),
        name="a_metabolite.txt",
        metadata={"type": "isa-assay", "delimiter": "\t"},
    )


@pytest.fixture(name="mock_metabolite_file")
def fixture_mock_metabolite_file() -> Document:
    """Generate a mock ISA-Tab metabolite file for testing.

    Returns:
        Document: A Document instance with metabolite data file content.
    """
    # Create a realistic metabolite data file
    content = [
        (
            "database_identifier\tchemical_formula\tsmiles\tmetabolite_identification\tsample1"
            "\tsample2\tsample3\tsample4"
        ),
        "CHEBI:15428\tC6H12O6\tC(C1C(C(C(C(O1)O)O)O)O)O\tGlucose\t1023.4\t956.2\t1052.8\t911.5",
        "CHEBI:17234\tC6H12O6\tC(C1C(C(C(C(O1)O)O)O)O)O\tFructose\t867.3\t764.1\t893.5\t721.9",
        "CHEBI:15343\tC4H6O4\tC(CC(=O)O)C(=O)O\tSuccinic acid\t243.8\t325.6\t229.7\t349.2",
        "CHEBI:30031\tC5H9NO4\tC(CC(=O)O)C(C(=O)O)N\tGlutamic acid\t532.1\t627.8\t512.5\t683.4",
        "CHEBI:25017\tC3H7NO2\tCC(C(=O)O)N\tAlanine\t308.9\t276.5\t319.7\t253.2",
    ]

    return Document(
        content="\n".join(content),
        name="m_metabolite_data1.tsv",
        metadata={"type": "isa-metabolite", "delimiter": "\t"},
    )


@pytest.mark.asyncio
async def test_parse_investigation_data(mock_investigation_file):
    """Test the investigation file parsing functionality.

    Verifies that parse_investigation_data correctly extracts data from the investigation file.
    """
    result = parse_investigation_data(mock_investigation_file)

    # Verify the result structure
    assert isinstance(result, dict)
    assert "INVESTIGATION" in result
    assert "STUDY" in result
    assert "STUDY FACTORS" in result

    # Check specific fields
    assert "Investigation Title" in result["INVESTIGATION"]
    assert (
        result["INVESTIGATION"]["Investigation Title"][0]
        == "Metabolomics Study of Plant Response to Stress"
    )
    assert "Study Factor Name" in result["STUDY FACTORS"]
    assert "Drought Stress" in result["STUDY FACTORS"]["Study Factor Name"]
    assert "Light Intensity" in result["STUDY FACTORS"]["Study Factor Name"]


@pytest.mark.asyncio
async def test_parse_study_data(mock_study_file):
    """Test the study file parsing functionality.

    Verifies that parse_study_data correctly extracts data from the study file.
    """
    result = parse_study_data(mock_study_file)

    # Verify the result structure
    assert isinstance(result, dict)
    assert "headers" in result
    assert "samples" in result
    assert isinstance(result["samples"], list)

    # Check specific fields
    assert "Factor Value[Drought Stress]" in result["headers"]
    assert len(result["samples"]) == 6
    assert isinstance(result["samples"][0], dict)
    first_sample: dict[Hashable, Any] = result["samples"][0]
    assert isinstance(result["samples"][1], dict)
    second_sample: dict[Hashable, Any] = result["samples"][1]
    assert first_sample["Source Name"] == "plant1"
    assert second_sample["Factor Value[Drought Stress]"] == "drought"


@pytest.mark.asyncio
async def test_parse_assay_data(mock_assay_file):
    """Test the assay file parsing functionality.

    Verifies that parse_assay_data correctly extracts data from assay files.
    """
    result = parse_assay_data([mock_assay_file])

    # Verify the result structure
    assert isinstance(result, dict)
    assert "metabolite" in result
    assert "headers" in result["metabolite"]
    assert "samples" in result["metabolite"]

    # Check specific fields
    assert "Protocol REF" in result["metabolite"]["headers"]
    assert len(result["metabolite"]["samples"]) == 4
    assert result["metabolite"]["samples"][0]["Sample Name"] == "sample1"
    assert result["metabolite"]["samples"][2]["MS Assay Name"] == "assay3"


@pytest.mark.asyncio
async def test_parse_metabolite_data(mock_metabolite_file):
    """Test the metabolite file parsing functionality.

    Verifies that parse_metabolite_data correctly extracts data from metabolite files.
    """
    result = parse_metabolite_data([mock_metabolite_file])

    # Verify the result structure
    assert isinstance(result, dict)
    assert "metabolite_data1" in result
    assert "metadata_columns" in result["metabolite_data1"]
    assert "sample_columns" in result["metabolite_data1"]
    assert "metabolites" in result["metabolite_data1"]

    # Check specific fields
    assert "chemical_formula" in result["metabolite_data1"]["metadata_columns"]
    assert "sample1" in result["metabolite_data1"]["sample_columns"]
    assert len(result["metabolite_data1"]["metabolites"]) == 5
    assert result["metabolite_data1"]["metabolites"][0]["chemical_formula"] == "C6H12O6"
    assert "abundances" in result["metabolite_data1"]["metabolites"][0]
    assert (
        result["metabolite_data1"]["metabolites"][0]["abundances"]["sample1"] == 1023.4
    )


@pytest.mark.asyncio
async def test_parse_isa_data(
    mock_investigation_file, mock_study_file, mock_assay_file, mock_metabolite_file
):
    """Test ISA-Tab data parsing functionality.

    Verifies that the parse_isa_data schema tool correctly processes investigation, study,
    assay, and metabolite files and returns a properly structured IsaStudy object.
    """
    result = await parse_isa_data(
        investigation_file=mock_investigation_file,
        study_file=mock_study_file,
        assay_files=[mock_assay_file],
        metabolite_files=[mock_metabolite_file],
    )

    # Verify the result is an IsaStudy instance with expected structure
    assert isinstance(result, IsaStudy)

    # Check study name and description
    assert result.study_name == "Plant Stress Response Study"
    assert (
        result.study_description
        == "Characterization of metabolomic response in plants under drought stress"
    )

    # Verify investigation data is parsed correctly
    assert "INVESTIGATION" in result.investigation_data
    assert "STUDY" in result.investigation_data
    assert "STUDY FACTORS" in result.investigation_data

    # Verify study data
    assert "headers" in result.study_data
    assert "samples" in result.study_data
    assert len(result.study_data["samples"]) > 0
    assert "Factor Value[Drought Stress]" in result.study_data["headers"]

    # Verify assay data - now it should be a dict
    assert isinstance(result.assay_data, dict)
    assert "metabolite" in result.assay_data
    assert "headers" in result.assay_data["metabolite"]
    assert "samples" in result.assay_data["metabolite"]
    assert "Protocol REF" in result.assay_data["metabolite"]["headers"]

    # Verify metabolite data - now it should be a dict
    assert isinstance(result.metabolite_data, dict)
    assert "metabolite_data1" in result.metabolite_data
    assert "metadata_columns" in result.metabolite_data["metabolite_data1"]
    assert "sample_columns" in result.metabolite_data["metabolite_data1"]
    assert "metabolites" in result.metabolite_data["metabolite_data1"]


@pytest.mark.asyncio
async def test_parse_isa_data_multiple_assays(
    mock_investigation_file, mock_study_file, mock_assay_file
):
    """Test ISA-Tab data parsing with multiple assay files.

    Verifies that the parse_isa_data schema tool correctly handles multiple assay files.
    """
    # Create a second assay file with slight modifications
    second_assay_content = mock_assay_file.content.replace("metabolite", "proteome")
    second_assay = Document(
        content=second_assay_content,
        name="a_proteome.txt",
        metadata={"type": "isa-assay", "delimiter": "\t"},
    )

    # Test parse_assay_data directly to verify it handles multiple files correctly
    assay_data = parse_assay_data([mock_assay_file, second_assay])
    assert isinstance(assay_data, dict)
    assert len(assay_data) == 2
    assert "metabolite" in assay_data
    assert "proteome" in assay_data

    # Now test the full parse_isa_data function with multiple assays
    result = await parse_isa_data(
        investigation_file=mock_investigation_file,
        study_file=mock_study_file,
        assay_files=[mock_assay_file, second_assay],
        metabolite_files=[],  # No metabolite files for this test
    )

    # Verify the result is an IsaStudy instance
    assert isinstance(result, IsaStudy)

    # Verify assay data is a dict with multiple entries
    assert isinstance(result.assay_data, dict)
    assert len(result.assay_data) == 2
    assert "metabolite" in result.assay_data
    assert "proteome" in result.assay_data

    # Check that both assay entries have the expected structure
    assert "headers" in result.assay_data["metabolite"]
    assert "samples" in result.assay_data["metabolite"]
    assert "Protocol REF" in result.assay_data["metabolite"]["headers"]

    assert "headers" in result.assay_data["proteome"]
    assert "samples" in result.assay_data["proteome"]
    assert "Protocol REF" in result.assay_data["proteome"]["headers"]


@pytest.mark.asyncio
async def test_parse_isa_data_multiple_metabolites(
    mock_investigation_file, mock_study_file, mock_assay_file, mock_metabolite_file
):
    """Test ISA-Tab data parsing with multiple metabolite files.

    Verifies that the parse_isa_data schema tool correctly handles multiple metabolite files.
    """
    # Create a second metabolite file with slight modifications
    second_metabolite_content = mock_metabolite_file.content.replace(
        "Glucose", "Galactose"
    )
    second_metabolite = Document(
        content=second_metabolite_content,
        name="m_metabolite_data2.tsv",
        metadata={"type": "isa-metabolite", "delimiter": "\t"},
    )

    # Test parse_metabolite_data directly to verify it handles multiple files correctly
    metabolite_data = parse_metabolite_data([mock_metabolite_file, second_metabolite])
    assert isinstance(metabolite_data, dict)
    assert len(metabolite_data) == 2
    assert "metabolite_data1" in metabolite_data
    assert "metabolite_data2" in metabolite_data

    # Now test the full parse_isa_data function with multiple metabolite files
    result = await parse_isa_data(
        investigation_file=mock_investigation_file,
        study_file=mock_study_file,
        assay_files=[mock_assay_file],
        metabolite_files=[mock_metabolite_file, second_metabolite],
    )

    # Verify the result is an IsaStudy instance
    assert isinstance(result, IsaStudy)

    # Verify metabolite data is a dict with multiple entries
    assert isinstance(result.metabolite_data, dict)
    assert len(result.metabolite_data) == 2
    assert "metabolite_data1" in result.metabolite_data
    assert "metabolite_data2" in result.metabolite_data

    # Check that both metabolite entries have the expected structure
    assert "metadata_columns" in result.metabolite_data["metabolite_data1"]
    assert "sample_columns" in result.metabolite_data["metabolite_data1"]
    assert "metabolites" in result.metabolite_data["metabolite_data1"]
    assert len(result.metabolite_data["metabolite_data1"]["metabolites"]) > 0

    assert "metadata_columns" in result.metabolite_data["metabolite_data2"]
    assert "sample_columns" in result.metabolite_data["metabolite_data2"]
    assert "metabolites" in result.metabolite_data["metabolite_data2"]
    assert len(result.metabolite_data["metabolite_data2"]["metabolites"]) > 0


@pytest.mark.asyncio
async def test_parse_isa_data_with_actual_files(
    isa_investigation, isa_study, isa_assays, isa_metabolites
):
    """Test ISA-Tab data parsing functionality using actual data files.

    Verifies that the parse_isa_data schema tool correctly processes investigation, study,
    and assay files and returns a properly structured IsaStudy object.
    """

    result = await parse_isa_data(
        investigation_file=isa_investigation,
        study_file=isa_study,
        assay_files=isa_assays,
        metabolite_files=isa_metabolites,
    )

    # Verify the result is an IsaStudy instance with expected structure
    assert isinstance(result, IsaStudy)

    # Check study name and description
    assert result.study_name == (
        "Metabolic abnormalities of the cortico-striato-thalamo-cortical circuit"
        " of rats with tic disorder"
    )
    assert len(result.study_description) > 0

    # Verify investigation data is parsed correctly
    assert "INVESTIGATION" in result.investigation_data
    assert "STUDY" in result.investigation_data
    assert "STUDY FACTORS" in result.investigation_data

    # Verify study data
    assert "headers" in result.study_data
    assert "samples" in result.study_data
    assert len(result.study_data["samples"]) > 0

    # Verify assay data
    assert isinstance(result.assay_data, dict)
    assert (
        "MTBLS11764_LC-MS_alternating_reverse-phase_metabolite_profiling"
        in result.assay_data
    )
    assert (
        "headers"
        in result.assay_data[
            "MTBLS11764_LC-MS_alternating_reverse-phase_metabolite_profiling"
        ]
    )
    assert (
        "samples"
        in result.assay_data[
            "MTBLS11764_LC-MS_alternating_reverse-phase_metabolite_profiling"
        ]
    )

    assert isinstance(result.metabolite_data, dict)
