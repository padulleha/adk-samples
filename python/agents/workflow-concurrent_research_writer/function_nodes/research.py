from collections.abc import AsyncGenerator

from google.adk.events.event import Event
from google.adk.workflow._function_node import FunctionNode
from google.adk.workflow._join_node import JoinNode
from google.genai.types import Content, ModelContent, Part


async def start_research(
    node_input: Content,
) -> AsyncGenerator[Event | list[str], None]:
    """Entry node for the research workflow. Puts the topic in state and yields a list of platforms to research."""
    topic = str(node_input.parts[0].text if node_input.parts else "")
    print(f"START_WORKFLOW 1: Research for topic: '{topic}'")
    yield Event(state={"topic": topic})

    platforms_to_research = ["X", "LinkedIn", "Reddit", "Medium"]
    yield platforms_to_research


async def combine_reports(
    node_input: Content,
) -> AsyncGenerator[str, None]:
    """Takes the Content object from parallel agents and joins their text parts into a single string."""
    if node_input.parts is None:
        yield "No reports received from"
    else:
        print(f"DEBUG-ENTIRE node_inut:\n{node_input}")
        report_texts = []
        for part in node_input.parts:
            if part.text:
                report_texts.append(part.text)

        yield "\n\n---\n\n".join(report_texts)


async def save_report(
    node_input: str,
) -> AsyncGenerator[Event | ModelContent, None]:
    """Saves the generated report to state and yields it for the user."""
    print("STATE_UPDATE: Saving generated report to session state.")
    yield Event(state={"research_report": node_input})
    yield ModelContent(parts=[Part.from_text(text=node_input)])


# Node Wrappers
start_node = FunctionNode(
    start_research, name="Start Research Node", rerun_on_resume=True
)

join_node = JoinNode(name="Combine Reports")

combine_reports_node = FunctionNode(combine_reports, name="Combinator Node")

save_node = FunctionNode(
    save_report, name="Save Report Node", rerun_on_resume=False
)
