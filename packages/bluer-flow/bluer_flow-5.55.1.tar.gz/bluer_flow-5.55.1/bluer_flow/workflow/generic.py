from typing import Any, Dict, Any
import networkx as nx
from copy import deepcopy

from bluer_objects import objects, metadata, file

from bluer_flow import env
from bluer_flow.workflow import dot_file
from bluer_flow.workflow import patterns


class Workflow:
    def __init__(
        self,
        job_name: str = "",
        load: bool = False,
        name: str = "",
        args: Dict[str, Any] = {},
    ):
        self.job_name = job_name if job_name else objects.unique_object()

        self.name = name

        self.args = deepcopy(args)

        self.G: nx.DiGraph = nx.DiGraph()

        if load:
            success, self.G = dot_file.load_from_file(
                objects.path_of(
                    filename="workflow.dot",
                    object_name=self.job_name,
                )
            )
            assert success

            workflow_metadata = metadata.get_from_object(
                object_name=self.job_name,
                key="workflow",
                default={},
            )
            assert isinstance(workflow_metadata, dict)
            self.name = workflow_metadata.get("name", "not-found")
            self.args = workflow_metadata.get(
                "args",
                {"warning": "not-found"},
            )

    def get_metadata(self, key: str, default: str = "") -> str:
        return metadata.get_from_object(self.job_name, key, default)

    def load_pattern(
        self,
        pattern: str = env.BLUER_FLOW_DEFAULT_WORKFLOW_PATTERN,
        publish_as: str = "",
    ) -> bool:
        self.name = pattern
        self.args = {
            "pattern": pattern,
            "publish_as": publish_as,
        }

        success, self.G = patterns.load_pattern(
            pattern=pattern,
            export_as_image=objects.path_of(f"{pattern}.png", self.job_name),
        )
        if not success:
            return success

        self.G.add_node("X")
        for node in self.G.nodes:
            if self.G.in_degree(node) == 0 and node != "X":
                self.G.add_edge("X", node)

        for node in self.G.nodes:
            self.G.nodes[node]["command_line"] = (
                "bluer_flow_workflow monitor node={}{} {}".format(
                    node,
                    f",publish_as={publish_as}" if publish_as and node == "X" else "",
                    self.job_name,
                )
            )

        return self.post_metadata(
            "load_pattern",
            {"pattern": pattern},
        )

    def node_job_name(self, node: str) -> str:
        return f"{self.job_name}-{node}"

    def post_metadata(self, key: str, value: Any) -> bool:
        return metadata.post_to_object(self.job_name, key, value)

    def save(
        self,
        caption: str = "",
    ) -> bool:
        if not dot_file.save_to_file(
            objects.path_of(
                filename="workflow.dot",
                object_name=self.job_name,
            ),
            self.G,
            caption=" | ".join([item for item in [self.name, caption] if item]),
        ):
            return False

        return metadata.post_to_object(
            object_name=self.job_name,
            key="workflow",
            value={
                "name": self.name,
                "args": self.args,
            },
        )
