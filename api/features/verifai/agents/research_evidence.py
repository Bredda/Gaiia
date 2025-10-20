
from langchain.chat_models import init_chat_model
from langgraph.config import get_stream_writer
from pydantic import SecretStr
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from tavily import TavilyClient
from langgraph.config import get_stream_writer

from api.settings import get_settings
from ..models import (
    Evidence, 
    SearchQueries, 
    FactCheckState, 
    VerifaiConfig
)

prompt = PromptTemplate.from_template("""You are an expert at formulating search queries for fact-checking.
Given a claim, create 2 effective search queries that would help verify or refute the claim.
Claim: {claim_text}
Generate search queries that will find relevant evidence.""")

async def research_evidence(state: FactCheckState, runtime: Runtime[VerifaiConfig]):
    index = state["index"]
    writer = get_stream_writer()
    writer({"event":f"research_evidence_start_{index}", "payload": {"claim_index": index}})
    evidence_list: list[Evidence] = []
    claim_text = state["claim"].text
    llm = init_chat_model(
        api_key=SecretStr(get_settings().OPENAI_API_KEY),
        model=runtime.context.model_name,
        temperature=runtime.context.temperature
    )
    structured_llm = llm.with_structured_output(SearchQueries)

    raw = await prompt.pipe(structured_llm).ainvoke({"claim_text": claim_text})
    search_queries = SearchQueries.model_validate(raw)
    queries = search_queries.queries

    
    writer({"event":f"research_evidence_queries{index}", "payload": {"claim_index": index, "queries": queries}})
    
    for query_index, query in enumerate(queries):  # Limit to 2 queries per claim

        search_params = {
            "query": query,
            "max_results": 3,
            "search_depth": "advanced"
        }
        query_evidence: list[Evidence] = [] # For event purpose only
        # Restrict to specific domain if specified (e.g., Wikipedia)
        #if search_domain:
        #    search_params["include_domains"] = [search_domain]
        tavily_client = TavilyClient(api_key=get_settings().TAVILY_API_KEY)
        search_results = tavily_client.search(**search_params)
        
        for result in search_results.get('results', []):
            evidence = Evidence(
                source=result.get('url', ''),
                snippet=result.get('content', '')[:500],  # Limit snippet length
                relevance_score=result.get('score', 0.5)
            )
            evidence_list.append(evidence)
            query_evidence.append(evidence)
        writer({"event":f"research_evidence_results_{index}", "payload":{"claim_index": index, "query_index": query_index ,"evidences": evidence_list}})
        
    writer({"event":f"research_evidence_end_{index}", "payload":{"claim_index": index, "evidences": evidence_list}})
    
    return {"evidence_list": evidence_list}