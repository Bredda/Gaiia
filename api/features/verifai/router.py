from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
from typing import AsyncGenerator
from langchain_core.messages import AIMessageChunk
import json

from api.common.utils import to_serializable

from .config import get_all_configs, get_config
from .graph import build_graph
from .models import VerifaiInput


router = APIRouter(prefix="/verifai", tags=["VerifAI"])

graph = build_graph()

@router.get("/modes")
async def get_available_modes():
    return get_all_configs()


@router.post("/run")
async def run_workflow(body: VerifaiInput):
    print(f"New verifai request.Mode: {body.mode}, Input text: {body.input_text} ")

    async def event_generator() -> AsyncGenerator[str, None]:
        yield json.dumps({"event": "start", "payload": {"input": body.input_text }}) + "\n"
        # astream returns a tuple, 
        # * _ is a dict indicating namespace graph (main is (), subgraph is {"research_team": <id>}),
        # * mode is the stream mode (ie. either messages or custom)
        # * data is the stream payload. 
        #    * Messages event are a tuple with AIMessageChunk object and langgraph node metadata,
        #    * Custom events are the payload from the writer function 
        async for _, mode, chunk in graph.astream(
            {"input_text": body.input_text},
            subgraphs= True, # Needed to stream subgraphs events
            stream_mode=["messages", "custom"], # Messages for report tokens and custom_data for node custom events
            context=get_config(body.mode)
        ):
            if mode == "messages":
                msg, metadata = chunk
                if (
                    isinstance(metadata, dict) 
                    and metadata.get("langgraph_node") == "generate_report"
                    and isinstance(msg, AIMessageChunk)
                    and msg.content
                ):
                    data = {"type": "token", "content": msg.content}
                    yield json.dumps(data) + "\n"

            elif mode == "custom":
                data = {"type": "event", "content": chunk}
                print(chunk)
                yield json.dumps(to_serializable(data)) + "\n"

        # Optionnel : message de fin de stream
        yield json.dumps({"event": "done"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/json")


@router.get("/show")
async def shwo_workflow():
    bytes = graph.get_graph(xray=True).draw_mermaid_png()
    return Response(content=bytes, media_type="image/png")