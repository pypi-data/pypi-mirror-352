from typing import Any, List, Tuple, Dict
import glob
from tqdm import tqdm

from blueness import module
from bluer_options import string
from bluer_objects import file, objects
from bluer_objects.graphics.gif import generate_animated_gif
from bluer_objects.metadata import post_to_object

from bluer_flow import NAME
from bluer_flow.logger import logger
from bluer_flow.workflow import dot_file
from bluer_flow.workflow.generic import Workflow


NAME = module.name(__file__, NAME)


class GenericRunner:
    def __init__(self):
        self.type_name: str = "generic"
        self.job_name: str = ""

    def monitor(
        self,
        workflow: Workflow,
        hot_node: str = "void",
    ) -> bool:
        self.job_name = workflow.job_name

        try:
            workflow = self.monitor_function(workflow, hot_node)
        except Exception as e:
            logger.warning(f"monitor failed: {e}")

        summary: Dict[str, str] = {}
        for node in workflow.G.nodes:
            summary.setdefault(workflow.G.nodes[node].get("status"), []).append(node)
        for status, nodes in summary.items():
            logger.info("{}: {}".format(status, ", ".join(sorted(nodes))))

        if not dot_file.export_graph_as_image(
            workflow.G,
            objects.path_of(
                "thumbnail-workflow-{}.png".format(
                    string.pretty_date(as_filename=True, unique=True),
                ),
                workflow.job_name,
            ),
            colormap=dot_file.status_color_map,
            hot_node=hot_node,
            caption=f"{workflow.name} @ {self.type_name}",
        ):
            return False

        return generate_animated_gif(
            [
                filename
                for filename in sorted(
                    glob.glob(
                        objects.path_of("thumbnail-workflow-*.png", workflow.job_name)
                    )
                )
                if len(file.name(filename)) > 15
            ],
            objects.path_of("workflow.gif", workflow.job_name),
            frame_duration=333,
        )

    def monitor_function(
        self,
        workflow: Workflow,
        hot_node: str,
    ) -> Workflow:
        logger.info(
            f"{NAME}.{self.__class__.__name__}.monitor: {workflow} @ {hot_node}"
        )

        post_to_object(
            workflow.node_job_name(hot_node),
            "monitor",
            {"hot_node": hot_node},
        )

        return workflow

    def submit(
        self,
        workflow: Workflow,
        dryrun: bool = True,
    ) -> bool:
        self.job_name = workflow.job_name

        logger.info(
            "{}.{}.submit({}, dryrun={})".format(
                NAME,
                self.__class__.__name__,
                workflow.G,
                dryrun,
            )
        )

        metadata: Dict[str, Any] = {}
        failure_count: int = 0
        round: int = 1
        while not all(
            workflow.G.nodes[node].get("job_id") for node in workflow.G.nodes
        ):
            for node in tqdm(workflow.G.nodes):
                if workflow.G.nodes[node].get("job_id"):
                    continue

                pending_dependencies = [
                    node_
                    for node_ in workflow.G.successors(node)
                    if not workflow.G.nodes[node_].get("job_id")
                ]
                if pending_dependencies:
                    logger.info(
                        '⏳ node "{}": {} pending dependenci(es): {}'.format(
                            node,
                            len(pending_dependencies),
                            ", ".join(pending_dependencies),
                        )
                    )
                    continue

                command_line = workflow.G.nodes[node]["command_line"]
                job_name = f"{workflow.job_name}-{node}"

                if dryrun:
                    workflow.G.nodes[node]["job_id"] = f"dryrun-round-{round}"
                    logger.info(f"{command_line} -> {job_name}")
                    continue

                success, metadata[node] = self.submit_command(
                    command_line=command_line,
                    job_name=job_name,
                    dependencies=[
                        workflow.G.nodes[node_].get("job_id")
                        for node_ in workflow.G.successors(node)
                    ],
                    verbose=False,
                    type=workflow.G.nodes[node].get("type", "cpu"),
                )
                if not success:
                    failure_count += 1

                workflow.G.nodes[node]["job_id"] = (
                    metadata[node]["job_id"] if success else "failed"
                )

            logger.info(f"end of round {round}")
            round += 1

        if failure_count:
            logger.error(f"{failure_count} failure(s).")

        if not workflow.save(caption=f"{self.__class__.__name__}.submit"):
            return False

        if not post_to_object(
            workflow.job_name,
            "submission",
            {
                "metadata": metadata,
                "failure_count": failure_count,
                "runner_type": self.type_name,
            },
        ):
            return False

        return failure_count == 0

    def submit_command(
        self,
        command_line: str,
        job_name: str,
        dependencies: List[str],
        verbose: bool = False,
        type: str = "cpu",
    ) -> Tuple[bool, Any]:
        logger.info(
            "⏳ {}.{}: {}[{}]: {} X {} dependency(s): {}".format(
                NAME,
                self.__class__.__name__,
                job_name,
                type,
                command_line,
                len(dependencies),
                ", ".join(dependencies),
            )
        )
        return True, {"job_id": job_name}
