"""Data models for the Verifai workflow"""

from typing import List, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
import operator
from enum import StrEnum


class VerifaiModeEnum(StrEnum):
    """ Avaiable mode for the fact check workflow. Impacts used LLM and research depth. See VerifaiConfig class """
    DEFAULT = "default"
    HIGH = "high"
    FAST = "fast"

class VerifaiInput(BaseModel):
    """ Input for the graph endpoint """
    input_text: str = Field(..., description="Text to fact check")
    mode: VerifaiModeEnum = Field(default=VerifaiModeEnum.DEFAULT, description="Workflow mode. [default|fast|high]")





class Claim(BaseModel):
    """A single factual claim extracted from text"""
    text: str = Field(description="The claim text")
    priority: int = Field(default=5, description="Priority level (1-10, higher is more important)")


class ClaimsList(BaseModel):
    """List of claims extracted from text"""
    claims: List[Claim] = Field(description="List of factual claims to be verified")


class SearchQueries(BaseModel):
    """Search queries for evidence retrieval"""
    queries: List[str] = Field(description="List of 1-3 search queries to find evidence")


class Evidence(BaseModel):
    """Evidence retrieved for a claim"""
    source: str = Field(description="Source URL or reference")
    snippet: str = Field(description="Relevant text snippet")
    relevance_score: float = Field(default=0.0, description="How relevant this evidence is (0-1)")


class VerdictOutput(BaseModel):
    """Verification verdict output from LLM (without evidence)"""
    status: Literal["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"] = Field(
        description="Truth status of the claim (FEVER-compliant labels)"
    )
    confidence: float = Field(description="Confidence level (0-1)", ge=0.0, le=1.0)
    justification: str = Field(description="Explanation for the verdict")
    evidence_ids_used: List[int] = Field(default_factory=list, description="Liste of evidence ids used for the verdict")


class Verdict(BaseModel):
    """Verification verdict for a claim"""
    claim: str = Field(description="The original claim")
    status: Literal["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"] = Field(
        description="Truth status of the claim (FEVER-compliant labels)"
    )
    confidence: float = Field(description="Confidence level (0-1)")
    justification: str = Field(description="Explanation for the verdict")
    evidence_used: List[Evidence] = Field(default_factory=list, description="Evidence supporting this verdict")


class VerifaiInputState(TypedDict):
    """ Input state for the Verifai main graph"""
    input_text: str


class FactCheckState(TypedDict):
    """ Internal state for Evidence research teams subgraph """
    index: int
    claim: Claim
    evidence_list: List[Evidence]
    
class VerifaiOutputState(TypedDict):
    """ Output state for the Verifai main graph"""
    claims: List[Claim]
    verdicts:  Annotated[List[Verdict], operator.add]  # Reducer to aggregate verdicts from each parallel
    final_report: str
    error: str

class VerifaiState(VerifaiInputState, VerifaiOutputState):
    """ Global state for the Verifai main graph """
    pass


class VerifaiReport(BaseModel):
    """Final Verifai report"""
    input_text: str
    claims_found: int
    verdicts: List[Verdict]
    summary: str
    timestamp: str

class VerifaiConfig(BaseModel):
    """Configuration for the fact-checking workflow"""
    
    # Model settings
    model_name: str = Field(
        default="openai:gpt-4o-mini",
        description="OpenAI model to use (gpt-4o-mini, gpt-4, gpt-4-turbo, etc.)"
    )
    temperature: float = Field(
        default=0.0,
        description="Temperature for LLM responses (0.0 = deterministic, 1.0 = creative)",
        ge=0.0,
        le=2.0
    )
    
    # Search settings
    max_search_results_per_query: int = Field(
        default=3,
        description="Maximum number of search results to retrieve per query",
        ge=1,
        le=10
    )
    max_queries_per_claim: int = Field(
        default=2,
        description="Maximum number of search queries to generate per claim",
        ge=1,
        le=5
    )
    search_depth: Literal["basic", "advanced"] = Field(
        default="advanced",
        description="Tavily search depth (basic or advanced)"
    )
    
    # Evidence settings
    max_evidence_per_claim: int = Field(
        default=5,
        description="Maximum pieces of evidence to collect per claim",
        ge=1,
        le=20
    )
    snippet_max_length: int = Field(
        default=500,
        description="Maximum length of evidence snippets (characters)",
        ge=100,
        le=2000
    )
    
    # Verification settings
    evidence_for_verdict: int = Field(
        default=3,
        description="Number of top evidence pieces to include in verdicts",
        ge=1,
        le=10
    )

    
    class Config:
        """Pydantic config"""
        validate_assignment = True
