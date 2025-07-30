"""Integration test module for the complete Aria workflow pipeline.

This module tests the full pipeline of Aria tools, simulating a complete user session
from initial PubMed query to final protocol review. It ensures that outputs from
each step can be successfully used as inputs to subsequent steps.
"""

import pytest
from aria_tools.utils.models import (
    IsaStudy,
    PMCQuery,
    PubmedResults,
    SuggestedStudy,
    StudyWithDiagram,
    ExperimentalProtocol,
    ProtocolFeedback,
)
from aria_tools.actions import register_to_existing_server


@pytest.fixture(scope="function", name="tool_service")
async def service_fixture():
    server = await register_to_existing_server(
        provided_url="https://hypha.aicell.io", port=None, service_id="aria-tools-test"
    )
    service = await server.get_service("aria-tools-test")
    yield service
    await server.disconnect()


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.expensive
async def test_full_pipeline_integration(
    tool_service, isa_investigation, isa_study, isa_assays, isa_metabolites
):
    """Test the full pipeline of Aria tools from start to finish.

    This test simulates a complete user session from generating a PubMed query to
    parsing ISA data, ensuring that all steps work together as expected.
    """
    user_request = "I'm interested in studying the metabolomics of U2OS cells"

    # Step 0:
    best_query = await tool_service.get_best_pubmed_query(user_request=user_request)
    PMCQuery.model_validate(best_query)

    # Step 1: Query PubMed tool
    pubmed_results = await tool_service.query_pubmed(
        pmc_query=best_query, max_results=8
    )
    PubmedResults.model_validate(pubmed_results)
    assert len(pubmed_results.documents) > 0

    # Step 2: Generate study suggestion
    suggested_study = await tool_service.study_suggester(
        user_request=user_request,
        documents=pubmed_results.documents,
        constraints="",
    )
    SuggestedStudy.model_validate(suggested_study)

    # Step 3: Create diagram
    study_diagram = await tool_service.create_diagram(suggested_study=suggested_study)
    StudyWithDiagram.model_validate(study_diagram)
    assert "graph TD" in study_diagram.study_diagram.diagram_code

    # Step 4: Write protocol
    protocol = await tool_service.write_protocol(
        suggested_study=suggested_study, constraints=""
    )
    ExperimentalProtocol.model_validate(protocol)
    assert len(protocol.sections) > 0

    # Step 5 & 6: Review, Update protocol based on feedback
    for _ in range(5):
        feedback = await tool_service.protocol_feedback(
            protocol=protocol, constraints=""
        )
        ProtocolFeedback.model_validate(feedback)
        if feedback.complete:
            break
        protocol = await tool_service.update_protocol(
            protocol=protocol,
            feedback=feedback,
            documents=pubmed_results.documents,
            constraints="",
        )
        ExperimentalProtocol.model_validate(protocol)

    # Step 7: Parse ISA files
    parsed_isa = await tool_service.parse_isa(
        investigation_file=isa_investigation,
        study_file=isa_study,
        assay_files=isa_assays,
        metabolite_files=isa_metabolites,
    )
    IsaStudy.model_validate(parsed_isa)
