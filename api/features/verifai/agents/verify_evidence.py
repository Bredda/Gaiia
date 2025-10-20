from pydantic import SecretStr

from langgraph.config import get_stream_writer
from langchain.chat_models import init_chat_model
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate

from api.settings import get_settings
from ..models import (FactCheckState, VerifaiConfig, VerdictOutput , Verdict)

prompt = PromptTemplate.from_template("""You are an expert fact-checker responsible for verifying claims.

CRITICAL INSTRUCTIONS FOR ACCURATE VERIFICATION:

Before making a SUPPORTS or REFUTES judgment, you MUST verify:
1. The evidence DIRECTLY addresses the SPECIFIC details in the claim
2. The evidence is COMPLETE enough to verify ALL parts of the claim
3. You are NOT making assumptions or inferences beyond what the evidence explicitly states

DEFAULT TO "NOT ENOUGH INFO" when:
- Evidence is related but doesn't address the SPECIFIC claim details
- Evidence provides general context but not specific facts claimed
- ANY part of the claim is not directly confirmed or refuted by evidence
- Evidence is tangential or only partially relevant
- You cannot find direct confirmation (absence of evidence ≠ REFUTES)

COMMON PITFALLS TO AVOID:
- Claim: "Founded by two men" | Evidence: "Founded by Arnold Hills and Dave Taylor" 
  → This is NOT ENOUGH INFO (doesn't explicitly confirm "two")
- Claim: "Worked on a sitcom in 2007" | Evidence: "Worked on TV shows in 2007"
  → This is NOT ENOUGH INFO (doesn't confirm "sitcom" specifically)
- Claim: "Person X is in Movie Y" | Evidence: Lists other movies
  → This is NOT ENOUGH INFO (absence isn't refutation)
- Claim has specific details | Evidence is general
  → This is NOT ENOUGH INFO

BE CONSERVATIVE: When in doubt, choose NOT ENOUGH INFO over making assumptions.

Now analyze this claim:

Claim: {claim_text}

Evidence:
{evidence_text}

Provide your verdict with:
1. Status: "SUPPORTS", "REFUTES", or "NOT ENOUGH INFO" 
2. Confidence: 0 to 1 (lower confidence for partial/indirect evidence)
3. Justification: Explain whether evidence DIRECTLY addresses ALL claim specifics
4. Used evidence: List provided evience ids used for the veerdict decision                                        
""")

def verify_evidence(state: FactCheckState, runtime: Runtime[VerifaiConfig]):
    writer = get_stream_writer()
    writer({"event":f"verify_evidence_start_{state['index']}"})
    evidence_list = state["evidence_list"]
    claim_text = state["claim"].text
    evidence_text = "\n\n".join([
                f"Id: {index}, Source: {ev.source}\nSnippet: {ev.snippet}"
                for index, ev in enumerate(evidence_list[:5])  # Limit to top 5 evidence pieces
            ])
            
    if not evidence_text:
        evidence_text = "No evidence found."
    llm = init_chat_model(
        api_key=SecretStr(get_settings().OPENAI_API_KEY),
        model=runtime.context.model_name,
        temperature=runtime.context.temperature
    )
    structured_llm = llm.with_structured_output(VerdictOutput )
    raw = prompt.pipe(structured_llm).invoke({"claim_text": claim_text, "evidence_text": evidence_text})
    verdict_output = VerdictOutput.model_validate(raw)
    verdict = Verdict(
        claim=claim_text,
        status=verdict_output.status,
        confidence=verdict_output.confidence,
        justification=verdict_output.justification,
        evidence_used= [
            obj for i, obj in enumerate(evidence_list) 
            if i in verdict_output.evidence_ids_used
        ]
    )
    writer({"event":f"verify_evidence_end_{state['index']}","payload": verdict})    
    return {"verdicts": [verdict]}