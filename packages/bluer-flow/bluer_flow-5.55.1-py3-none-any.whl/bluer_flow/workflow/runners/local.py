from typing import Any, List, Tuple
from tqdm import tqdm
from functools import reduce

from bluer_objects import file, objects

from bluer_flow.workflow.generic import Workflow
from bluer_flow.workflow.runners.generic import GenericRunner


class LocalRunner(GenericRunner):
    def __init__(self, **kw_args):
        super().__init__(**kw_args)
        self.type_name: str = "local"

        self.command_line_list: List[str] = []

    def monitor_function(
        self,
        workflow: Workflow,
        hot_node: str,
    ) -> Workflow:
        workflow = super().monitor_function(workflow, hot_node)

        for node in tqdm(workflow.G.nodes):
            if file.exists(
                objects.path_of(
                    "metadata.yaml",
                    workflow.node_job_name(node),
                )
            ):
                workflow.G.nodes[node]["status"] = "SUCCEEDED"

        return workflow

    def submit_command(
        self,
        command_line: str,
        job_name: str,
        dependencies: List[str],
        verbose: bool = False,
        type: str = "cpu",
    ) -> Tuple[bool, Any]:
        assert super().submit_command(
            command_line,
            job_name,
            dependencies,
            verbose,
            type,
        )[0]

        self.command_line_list += [command_line]

        filename = objects.path_of(f"{self.job_name}.sh", self.job_name)

        script = (
            [
                "#! /usr/bin/env bash",
                "",
                "function runme() {",
                '    echo "⏳ {} started: {} command(s)."'.format(
                    self.job_name,
                    len(self.command_line_list),
                ),
            ]
            + reduce(
                lambda x, y: x + y,
                [
                    [
                        "",
                        f"    bluer_ai_eval - {command_line}",
                        "    [[ $? -ne 0 ]] && return 1",
                    ]
                    for command_line in self.command_line_list
                ],
            )
            + [
                f'    echo "⏳ / {self.job_name}"',
                "}",
                "",
                'runme "$@"',
            ]
        )

        return file.save_text(filename, script, log=True), {"job_id": job_name}
