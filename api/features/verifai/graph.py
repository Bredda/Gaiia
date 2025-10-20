from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .models import (
    VerifaiInputState, 
    VerifaiOutputState, 
    VerifaiConfig, 
    FactCheckState,
    VerifaiState)
from .agents import (
    extract_claims, 
    research_evidence, 
    verify_evidence,
    generate_report
)

def _build_fact_check_graph():
    fact_check_builder = StateGraph(FactCheckState,
        context_schema=VerifaiConfig)
    fact_check_builder.add_node("research_evidence", research_evidence)
    fact_check_builder.add_node("verify_evidence", verify_evidence)
    fact_check_builder.add_edge(START, "research_evidence")
    fact_check_builder.add_edge("research_evidence", "verify_evidence")
    fact_check_builder.add_edge("verify_evidence", END)
    return fact_check_builder.compile()

def _send_to_research_teams(state: VerifaiState):                        
    return [
        Send("research_team", {"index": index,"claim": claim}) 
        for index, claim in enumerate(state["claims"])]

def build_graph():
    main_builder = StateGraph(VerifaiState, 
        input_schema=VerifaiInputState, 
        output_schema=VerifaiOutputState, 
        context_schema=VerifaiConfig)

    main_builder.add_node("extract_claims", extract_claims)  # Add the answer node
    main_builder.add_node("research_team", _build_fact_check_graph())
    main_builder.add_node("generate_report", generate_report)


    main_builder.add_edge(START, "extract_claims")
    main_builder.add_conditional_edges("extract_claims", _send_to_research_teams, ["research_team"]) #Map-reduce to evidence research. Parallelize each claim to check
    main_builder.add_edge("research_team", "generate_report")
    main_builder.add_edge("generate_report", END)
    return main_builder.compile()  # Compile the graph

