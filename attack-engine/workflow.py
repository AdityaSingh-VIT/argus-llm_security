"""
LangGraph wiring for the attack-engine pipeline.

Previously this only wired the Attack Planner (START -> attack_planner ->
END). All five remaining stages are now implemented, so the graph can be
built end-to-end: planner -> generator -> executor -> analyzer ->
risk_scorer -> [report_generator] -> END.

Backward compatible by construction: `build_attack_planning_graph(planner)`
called with only a planner still produces exactly the single-node graph
it always did - every new stage is an additional optional keyword
argument, so no existing caller needs to change.
"""
from __future__ import annotations

from typing import Optional

from langgraph.graph import END, START, StateGraph

from agents.planner import PlannerAgent
from evaluation.evaluator import ResponseAnalyzerAgent
from executor.executor import AttackExecutorAgent
from generator.generator import PromptGeneratorAgent
from graph.state import WorkflowState
from reporting.report_generator import ReportGeneratorAgent
from risk.scorer import RiskScorerAgent


def build_attack_planning_graph(
    planner_agent: PlannerAgent,
    generator_agent: Optional[PromptGeneratorAgent] = None,
    executor_agent: Optional[AttackExecutorAgent] = None,
    analyzer_agent: Optional[ResponseAnalyzerAgent] = None,
    risk_scorer_agent: Optional[RiskScorerAgent] = None,
    report_agent: Optional[ReportGeneratorAgent] = None,
):
    """Compile the attack-engine LangGraph pipeline.

    Stages are wired in sequence, skipping any stage whose agent is not
    supplied (so partial pipelines - e.g. planner + generator only, for
    inspecting generated prompts without executing them - remain valid).
    """
    graph = StateGraph(WorkflowState)
    graph.add_node(planner_agent.name, planner_agent)
    graph.add_edge(START, planner_agent.name)
    last = planner_agent.name

    for agent in filter(None, [generator_agent, executor_agent, analyzer_agent, risk_scorer_agent, report_agent]):
        graph.add_node(agent.name, agent)
        graph.add_edge(last, agent.name)
        last = agent.name

    graph.add_edge(last, END)
    return graph.compile()


def build_full_attack_pipeline(
    planner_agent: PlannerAgent,
    generator_agent: PromptGeneratorAgent,
    executor_agent: AttackExecutorAgent,
    analyzer_agent: ResponseAnalyzerAgent,
    risk_scorer_agent: RiskScorerAgent,
    report_agent: Optional[ReportGeneratorAgent] = None,
):
    """Convenience wrapper for the common case: every stage wired,
    optionally including report generation as the final graph node."""
    return build_attack_planning_graph(
        planner_agent,
        generator_agent=generator_agent,
        executor_agent=executor_agent,
        analyzer_agent=analyzer_agent,
        risk_scorer_agent=risk_scorer_agent,
        report_agent=report_agent,
    )
