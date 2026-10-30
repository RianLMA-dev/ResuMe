from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.classifier import classify_email
from app.agents.extractor import extract_application
from app.schemas import EmailInput, JobApplication


class PipelineState(TypedDict, total=False):
    email: EmailInput
    is_job_related: bool
    reason: str
    application: Optional[JobApplication]


def classify_node(state: PipelineState) -> dict:
    result = classify_email(state["email"])
    return {"is_job_related": result.is_job_related, "reason": result.reason}


def extract_node(state: PipelineState) -> dict:
    return {"application": extract_application(state["email"])}


def route_after_classify(state: PipelineState) -> str:
    return "extract" if state["is_job_related"] else "discard"


def build_graph():
    builder = StateGraph(PipelineState)
    builder.add_node("classify", classify_node)
    builder.add_node("extract", extract_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {"extract": "extract", "discard": END},
    )
    builder.add_edge("extract", END)

    return builder.compile()


graph = build_graph()