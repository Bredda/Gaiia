from pydantic import SecretStr

from langchain.chat_models import init_chat_model
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langgraph.config import get_stream_writer

from api.settings import get_settings
from ..models import VerifaiState, VerifaiConfig

prompt = PromptTemplate.from_template("""You are an expert at communicating fact-check results clearly.
Create a comprehensive, well-structured report that presents the fact-check findings.

The report should:
- Be clear and accessible to general readers
- Present each claim with its verdict and evidence
- Explain the reasoning behind each verdict
- Provide an overall summary
- Cite evidence using markdown links whenever needed                                      

Use clear formatting with sections and bullet points where appropriate.
                                      
"Original Text: {input_text}                                      
Fact-Check Results:{verdicts_text}

Generate a comprehensive fact-check report: """)

async def generate_report(state: VerifaiState, runtime: Runtime[VerifaiConfig]):
    writer = get_stream_writer()
    writer({"event":"generate_report_start"})
    verdicts_text = ""
    for i, verdict in enumerate(state["verdicts"], 1):
                verdicts_text += f"\n\nClaim {i}: {verdict.claim}\n"
                verdicts_text += f"Status: {verdict.status.upper()}\n"
                verdicts_text += f"Confidence: {verdict.confidence:.0%}\n"
                verdicts_text += f"Justification: {verdict.justification}\n"
                if verdict.evidence_used:
                    verdicts_text += "Key Evidence:\n"
                    for ev in verdict.evidence_used[:2]:
                        verdicts_text += f"  - {ev.source}\n"

    llm = init_chat_model(
        api_key=SecretStr(get_settings().OPENAI_API_KEY),
        model=runtime.context.model_name,
        temperature=runtime.context.temperature
    )
    response = await prompt.pipe(llm).ainvoke({"input_text": state["input_text"], "verdicts_text": verdicts_text})
    writer({"event":"generate_report_end","payload": response})
    return {"final_report": response.content}