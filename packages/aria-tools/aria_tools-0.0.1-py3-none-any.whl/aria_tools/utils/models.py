"""Pydantic models for the Aria tools API."""

from dataclasses import dataclass
from typing import Any, Type, TypeVar
from pydantic import BaseModel, Field
from schema_agents.utils.common import EventBus  # type: ignore


T = TypeVar("T", bound=BaseModel)


def to_pydantic_model(
    model_class: Type[T],
    model_instance: T | dict[str, Any] | str,
) -> T:
    """Convert a dictionary or JSON string to specified pydantic model."""

    if isinstance(model_instance, (BaseModel, dict)):
        return model_class.model_validate(model_instance)

    return model_class.model_validate_json(model_instance)


@dataclass
class AgentConfig:
    """Configuration for the agent."""

    name: str
    instructions: str
    messages: list[Any]
    llm_model: str
    event_bus: EventBus | None = None
    tools: list[Any] | None = None
    output_schema: type[BaseModel] | None = None
    constraints: str | None = None


class ModelWithTemplate(BaseModel):
    """A model that has a template name for rendering"""

    template_name: str | None = Field(
        default="suggested_study.html",
        description="The name of the template to use for rendering the model",
    )


class HTMLPage(BaseModel):
    """A summary HTML page that neatly presents the suggested study or experimental protocol for
    user review"""

    html_code: str = Field(
        description=(
            "The html code for a single page website summarizing the information in the"
            " suggested study or experimental protocol appropriately including any"
            " diagrams. Make sure to include the original user request as well if"
            " available. References should appear as numbered links"
            " (e.g. a url`https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11129507/` can"
            " appear as a link with link text `[1]` referencing the link)."
            " Other sections of the text should refer to this reference by number"
        )
    )


class SuggestedStudy(ModelWithTemplate):
    """A suggested study to test a new hypothesis relevant to the user's request based on
    the cutting-edge literature review. Any time a reference is used anywhere, it MUST
    be cited directly."""

    user_request: str = Field(
        description="The original user request. This MUST be included."
    )
    experiment_name: str = Field(description="The name of the experiment")
    experiment_material: list[str] = Field(
        description="The materials required for the experiment"
    )
    experiment_expected_results: str = Field(
        description="The expected results of the experiment"
    )
    experiment_workflow: str = Field(
        description=(
            "A high-level description of the workflow for the experiment. "
            "References should be cited in the format of `[1]`, `[2]`, etc."
        )
    )
    experiment_hypothesis: str = Field(
        description="The hypothesis to be tested by the experiment"
    )
    experiment_reasoning: str = Field(
        description=(
            "The reasoning behind the choice of this experiment including the relevant"
            " background and citations."
        )
    )
    description: str = Field(description="A brief description of the study")
    references: list[str] = Field(
        description=(
            "Citations and references to where these ideas came from. For example,"
            " point to specific papers or PubMed IDs to support the choices in the"
            " study design."
        )
    )
    template_name: str | None = Field(
        default="suggested_study.html",
        description="The name of the template to use for rendering the suggested study",
    )


class ProtocolSection(BaseModel):
    """A section of an experimental protocol encompassing a specific set of steps falling
    under a coherent theme. The steps should be taken from existing protocols. When a
    step is taken from a reference protocol, you MUST include an inline citation. For
    example, in a section you might have the step `2. Wash cells in buffer for 30
    minutes [2]` where `[2]` cites the reference protocol."""

    section_name: str = Field(description="The name of this section of the protocol")
    steps: list[str] = Field(
        description="The ordered list of steps in this section of the protocol"
    )
    references: list[str] = Field(
        description="References supporting the steps in this section"
    )


class ExperimentalProtocol(ModelWithTemplate):
    """A detailed list of steps outlining an experimental procedure that to be carried
    out in the lab. The steps MUST be detailed enough for a new student to follow them
    exactly without any questions or doubts.
    Do not include any data analysis portion of the study, only the procedure through
    the point of data collection. That means no statistical tests or data processing
    should be included unless they are necessary for downstream data collection steps.
    """

    protocol_title: str = Field(description="The title of the protocol")
    equipment: list[str] = Field(
        description="Equipment, materials, reagents needed for the protocol"
    )
    sections: list[ProtocolSection] = Field(
        description="Ordered sections of the protocol"
    )
    queries: list[str] = Field(
        default=[],
        description="A list of queries used to search for protocol steps in the paper corpus",
    )
    template_name: str | None = Field(
        default="experimental_protocol.html",
        description="The name of the template to use for rendering the experimental protocol",
    )


class ProtocolFeedback(BaseModel):
    """Expert scientist's feedback on a protocol"""

    complete: bool = Field(
        description="Whether the protocol is complete and ready to use"
    )
    feedback_points: list[str] = Field(
        description="list of specific feedback points that need to be addressed"
    )
    suggestions: list[str] = Field(
        description=(
            "Suggestions for improving the protocol, such as 'fetch new sources about cell"
            " culture techniques'"
        )
    )
    previous_feedback: str = Field(
        "", description="Record of previous feedback that has been addressed"
    )


class StudyDiagram(ModelWithTemplate):
    """A diagram written in mermaid.js showing the workflow for the study and what
    expected data from the study will look like. An example:
    ```
    graph TD
    X[Cells] --> |Culturing| A
    A[Aniline Exposed Samples] -->|With NAC| B[Reduced Hepatotoxicity]
    A -->|Without NAC| C[Increased Hepatotoxicity]
    B --> D[Normal mmu_circ_26984 Levels]
    C --> E[Elevated mmu_circ_26984 Levels]
    style D fill:#4CAF50
    style E fill:#f44336
    ```
    Do not include specific conditions, temperatures, times, or other specific
    experimental protocol conditions just the general workflow and expected outcomes
    (for example, instead of 40 degrees say "high temperature").
    Do not include any special characters, only simple ascii characters.
    """

    diagram_code: str = Field(
        description=(
            "The code for a mermaid.js figure showing the study workflow and what the expected"
            " outcomes would look like for the experiment"
        )
    )


class StudyWithDiagram(ModelWithTemplate):
    """A suggested study with its workflow diagram"""

    suggested_study: SuggestedStudy = Field(
        description="The suggested study to test a new hypothesis"
    )
    study_diagram: StudyDiagram = Field(
        description="The diagram illustrating the workflow for the suggested study"
    )
    template_name: str | None = Field(
        default="suggested_study.html",
        description="The name of the template to use for rendering the study with diagram",
    )


class PMCQuery(BaseModel):
    """A plain-text query in a single-key dict formatted according to the NCBI search
    syntax. The query must include:

    1. Exact Match Terms: Enclose search terms in double quotes for precise matches.
       For example, `"lung cancer"` searches for the exact phrase "lung cancer".

    2. Boolean Operators: Use Boolean operators (AND, OR, NOT) to combine search terms.
       For instance, `"lung cancer" AND ("mouse" OR "monkey")`.

    3. Field Specification: Append `[Title/Abstract]` to each term to limit the search
       to article titles and abstracts.
       For example: `"rat"[Title/Abstract] OR "mouse"[Title/Abstract]`.

    4. Specific Journal Search: To restrict the search to articles from a particular
       journal, use the format `"[Journal Name]"[journal]`.
       For example, `"Bio-protocol"[journal]`.

    5. Open Access Filter: To filter results to only include open-access articles,
       add `"open access"[filter]` to the query.

    Example Query:
    ```
    {'query_str': '"lung cancer"[Title/Abstract] AND ("mouse"[Title/Abstract] OR '
                 '"monkey"[Title/Abstract]) AND "Bio-protocol"[journal] AND '
                 '"open access"[filter]'}
    ```
    """

    query_str: str = Field(
        description="The query to search the NCBI PubMed Central Database"
    )


class PubmedHits(BaseModel):
    """The number of hits returned by a PubMed query"""

    hits: int = Field(description="The number of hits returned by the query")


class IsaStudy(BaseModel):
    """A single ISA-Tab study"""

    study_name: str = Field(description="The name of the ISA-Tab investigation")
    study_description: str = Field(
        description=(
            "The description of the ISA-Tab investigation, study, assays, and metabolite data files"
        )
    )
    investigation_data: dict[str, Any] = Field(
        description="The ISA-Tab investigation data"
    )
    study_data: dict[str, Any] = Field(description="The ISA-Tab study data")
    assay_data: dict[str, Any] = Field(
        description=(
            "The ISA-Tab assay data"
            " (there may be more than"
            " one assay per investigation)"
        )
    )
    metabolite_data: dict[str, Any] = Field(
        description=(
            "The ISA-Tab metabolite data (there may be more"
            " than one metabolite data file per investigation."
            " Each metabolite data file corresponds to an assay)"
        )
    )


class Document(BaseModel):
    """A single document from PubMed Central that can be directly used as input for the
    vector database"""

    content: str = Field(description="The full text content of the paper")
    name: str = Field(description="The title of the paper")
    metadata: dict[str, Any] = Field(
        default_factory=lambda: {"type": "pubmed_article"},
        description=(
            "Metadata about the document including pmcid, url, journal, publication_date, authors,"
            " etc"
        ),
    )

    def __str__(self) -> str:
        """Returns a string representation of the document with key metadata."""
        metadata_dict = dict(self.metadata)  # Convert FieldInfo to dict
        return (
            f"Document: {self.name}\n"
            f"Content: {self.content}\n"
            f"URL: {metadata_dict.get('url', 'Unknown')}\n"
            f"Journal: {metadata_dict.get('journal', 'Unknown')}\n"
            f"Published: {metadata_dict.get('publication_date', 'Unknown')}\n"
            f"---"
        )


class PubmedResults(BaseModel):
    """Results from a PubMed query"""

    documents: list[Document] = Field(
        default_factory=list[Document],
        description="list of documents retrieved from PubMed Central",
    )
    total_results: int = Field(
        default=0, description="Total number of results found for the query"
    )
