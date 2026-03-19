# import asyncio
from functools import partial

# from uuid import uuid4
# from google.adk.agents.workflow.join_node import JoinNode
from google.adk.workflow import FunctionNode, Workflow
from google.adk.workflow._parallel_worker import _ParallelWorker

from .agent_nodes.publishing import generate_blog_post_agent
from .agent_nodes.research import (
    distill_agent,
    research_worker_agent,
)
from .function_nodes.publishing import (
    post_node,
    route_changer,
    shoutout_node,
    start_blog,
)
from .function_nodes.research import join_node, save_node, start_node

# --- 1. Workflow Definitions ---

# Research Workflow: A simple, linear chain. The `research_worker_agent`
# is marked with `parallel_worker=True` so the framework will automatically
# handle fanning out for each query and fanning in the results.
research_workflow = Workflow(
    name="research_workflow",
    edges=[
        (
            "START",
            start_node,
            _ParallelWorker(research_worker_agent),
            join_node,
            # combine_reports,
            distill_agent,
            save_node,
        ),
    ],
)

# Blog Workflow
# Nodes for posting the main article
post_to_x = FunctionNode(partial(post_node, "X"), name="Post to X")
post_to_linkedin = FunctionNode(
    partial(post_node, "LINKEDIN"), name="Post to LinkedIn"
)
post_to_medium = FunctionNode(
    partial(post_node, "MEDIUM"), name="Post to Medium"
)

# Nodes for posting shoutouts
shoutout_to_x = FunctionNode(partial(shoutout_node, "X"), name="Shoutout to X")
shoutout_to_linkedin = FunctionNode(
    partial(shoutout_node, "LINKEDIN"), name="Shoutout to LinkedIn"
)
shoutout_to_medium = FunctionNode(
    partial(shoutout_node, "MEDIUM"), name="Shoutout to Medium"
)
shoutout_to_reddit = FunctionNode(
    partial(shoutout_node, "REDDIT"), name="Shoutout to Reddit"
)

blog_workflow = Workflow(
    name="blog_workflow",
    edges=[
        # 1. Start, write blog, then route by length
        ("START", start_blog),
        (start_blog, generate_blog_post_agent),
        (generate_blog_post_agent, route_changer),
        # 2. Post to the primary platform based on the route from route_changer
        (route_changer, post_to_x, "X"),
        (route_changer, post_to_linkedin, "LINKEDIN"),
        (route_changer, post_to_medium, "MEDIUM"),
        # 3. From each primary post, trigger shoutouts based on the new objective rules.
        # If posted to X -> Shoutout to LinkedIn and Reddit
        (post_to_x, shoutout_to_linkedin, "SHOUTOUT_LINKEDIN"),
        (post_to_x, shoutout_to_reddit, "SHOUTOUT_REDDIT"),
        # If posted to LinkedIn -> Shoutout to X and Reddit
        (post_to_linkedin, shoutout_to_x, "SHOUTOUT_X"),
        (post_to_linkedin, shoutout_to_reddit, "SHOUTOUT_REDDIT"),
        # If posted to Medium -> Shoutout to X and LinkedIn
        (post_to_medium, shoutout_to_x, "SHOUTOUT_X"),
        (post_to_medium, shoutout_to_linkedin, "SHOUTOUT_LINKEDIN"),
    ],  # type: ignore
)

root_agent = Workflow(
    name="root_agent",
    description="""
        Main workflow contucting the research and pubication phases of blog 
        publication and advertisement.
    """,
    rerun_on_resume=True,
    edges=[("START", research_workflow, blog_workflow)],
)
