# Copyright (c) 2025 Corey Goldberg
# License: MIT
# adapted from: https://stackoverflow.com/a/71285627/16148

"""Progress bar for cloning Git repos."""

import git
from rich import console, progress


class GitProgress(git.RemoteProgress):
    OP_CODES = [
        "BEGIN",
        "CHECKING_OUT",
        "COMPRESSING",
        "COUNTING",
        "END",
        "FINDING_SOURCES",
        "RECEIVING",
        "RESOLVING",
        "WRITING",
    ]
    OP_CODE_MAP = {getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES}

    def __init__(self):
        super().__init__()
        self.progressbar = progress.Progress(
            progress.SpinnerColumn(),
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            "eta",
            progress.TimeRemainingColumn(),
            progress.TextColumn("{task.fields[message]}"),
            console=console.Console(),
            transient=False,
        )
        self.progressbar.start()
        self.active_task = None

    def __del__(self):
        self.progressbar.stop()

    @classmethod
    def get_curr_op(cls, op_code):
        """Get OP name from OP code."""
        # Remove BEGIN-flag and END-flag and get op name
        op_code_masked = op_code & cls.OP_MASK
        return cls.OP_CODE_MAP.get(op_code_masked, "?").title()

    def update(self, op_code, cur_count, max_count=None, message=""):
        # Start new bar on each BEGIN-flag
        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            if self.get_curr_op(op_code) == "Receiving":
                self.active_task = self.progressbar.add_task(
                    description=self.curr_op,
                    total=max_count,
                    message=message,
                )

        if self.get_curr_op(op_code) == "Receiving":
            self.progressbar.update(
                task_id=self.active_task,
                completed=cur_count,
                message=message,
            )

        # End progress monitoring on each END-flag
        if self.get_curr_op(op_code) == "Receiving":
            if op_code & self.END:
                self.progressbar.update(
                    task_id=self.active_task,
                    message=f"[bright_black]{message}",
                )
