import logging
from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.services.rag.workflow.state import GraphState
from app.services.rag.workflow.nodes import (
    summarizer_node,
    guardrail_input_node,
    guardrail_reject_node,
    router_node,
    direct_chat_node,
    rewriter_node,
    retriever_node,
    grader_node,
    generator_node,
    fallback_node,
)

logger = logging.getLogger(__name__)


def route_after_guardrail(state: GraphState) -> Literal["guardrail_reject", "router"]:
    status = state.get("guardrail_status", "passed")
    if status in ["blocked_safety", "blocked_domain"]:
        return "guardrail_reject"
    return "router"


def route_after_router(state: GraphState) -> Literal["direct_chat", "rewriter"]:
    intent = state.get("intent", "rag")
    if intent == "direct_chat":
        return "direct_chat"
    return "rewriter"


def route_after_grader(state: GraphState) -> Literal["generator", "fallback"]:
    relevant_chunks = state.get("relevant_chunks", [])
    if len(relevant_chunks) > 0:
        return "generator"
    return "fallback"


def build_chat_graph():
    """
    Constructs and compiles the PolicyHelper multi-agent LangGraph workflow.
    """
    workflow = StateGraph(GraphState)

    # 1. Add all nodes
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("guardrail", guardrail_input_node)
    workflow.add_node("guardrail_reject", guardrail_reject_node)
    workflow.add_node("router", router_node)
    workflow.add_node("direct_chat", direct_chat_node)
    workflow.add_node("rewriter", rewriter_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("grader", grader_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("fallback", fallback_node)

    # 2. Add linear and conditional edges
    workflow.add_edge(START, "summarizer")
    workflow.add_edge("summarizer", "guardrail")

    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "guardrail_reject": "guardrail_reject",
            "router": "router",
        },
    )

    workflow.add_edge("guardrail_reject", END)

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "direct_chat": "direct_chat",
            "rewriter": "rewriter",
        },
    )

    workflow.add_edge("direct_chat", END)

    # RAG Subgraph Edges
    workflow.add_edge("rewriter", "retriever")
    workflow.add_edge("retriever", "grader")

    workflow.add_conditional_edges(
        "grader",
        route_after_grader,
        {
            "generator": "generator",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("generator", END)
    workflow.add_edge("fallback", END)

    compiled_graph = workflow.compile()
    logger.info("LangGraph chat workflow compiled successfully.")
    return compiled_graph
