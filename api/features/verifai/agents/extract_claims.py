from pydantic import SecretStr

from langchain.chat_models import init_chat_model
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate

from api.settings import get_settings
from ..models import VerifaiState, VerifaiConfig, ClaimsList

prompt =  PromptTemplate.from_template("""You are an expert claim extraction agent for fact-checking.
Your task is to identify specific factual claims that can be verified from the given text.

Focus on:
- Factual statements that can be true or false
- Statistical claims, dates, numbers
- Claims about events, people, or entities
- Statements that require evidence to verify

Avoid:
- Opinions or subjective statements
- Questions
- General statements without specific facts

Extract factual claims from this text and assign each a priority (1-10, higher is more important):

{input_text}""")

async def extract_claims(state: VerifaiState, runtime: Runtime[VerifaiConfig]):
    """Detection and extraction of check-worthy claims"""
    writer = get_stream_writer()
    writer({"event": "extract_claims_start"})
    llm = init_chat_model(
        api_key=SecretStr(get_settings().OPENAI_API_KEY),
        model=runtime.context.model_name,
        temperature=runtime.context.temperature
    )
    structured_llm = llm.with_structured_output(ClaimsList)

    raw = await prompt.pipe(structured_llm).ainvoke({"input_text": state["input_text"]})
    result = ClaimsList.model_validate(raw)
    claims = sorted(result.claims, key=lambda x: x.priority, reverse=True)
    writer({"event": "extract_claims_end", "payload": claims})
    return {"claims": claims}


