import asyncio
from collections import deque
from dataclasses import dataclass
from typing import AsyncGenerator, AsyncIterator

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from flyte._api_commons import syncer
from flyte._initialize import get_client, requires_client
from flyte._protos.logs.dataplane import payload_pb2
from flyte._protos.workflow import run_definition_pb2, run_logs_service_pb2


def _format_line(logline: payload_pb2.LogLine, show_ts: bool) -> Text:
    style_map = {
        payload_pb2.LogLineOriginator.SYSTEM: "bold magenta",
        payload_pb2.LogLineOriginator.USER: "cyan",
        payload_pb2.LogLineOriginator.UNKNOWN: "light red",
    }
    style = style_map.get(logline.originator, "")
    if "flyte" in logline.message and "flyte.errors" not in logline.message:
        style = "dim"
    ts = ""
    if show_ts:
        ts = f"[{logline.timestamp.ToDatetime().isoformat()}]"
    return Text(f"{ts} {logline.message}", style=style)


class AsyncLogViewer:
    """
    A class to view logs asynchronously in the console or terminal or jupyter notebook.
    """

    def __init__(self, log_source: AsyncIterator, max_lines: int = 30, name: str = "Logs", show_ts: bool = False):
        self.console = Console()
        self.log_source = log_source
        self.max_lines = max_lines
        self.lines: deque = deque(maxlen=max_lines + 1)
        self.name = name
        self.show_ts = show_ts
        self.total_lines = 0

    def _render(self):
        log_text = Text()
        for line in self.lines:
            log_text.append(line)
        return Panel(log_text, title=self.name, border_style="yellow")

    async def run(self):
        with Live(self._render(), refresh_per_second=10, console=self.console) as live:
            try:
                async for logline in self.log_source:
                    formatted = _format_line(logline, show_ts=self.show_ts)
                    self.lines.append(formatted)
                    self.total_lines += 1
                    live.update(self._render())
            except asyncio.CancelledError:
                pass
        self.console.print(f"Scrolled {self.total_lines} lines of logs.")


@dataclass
class Logs:
    @classmethod
    @requires_client
    @syncer.wrap
    async def tail(
        cls, action_id: run_definition_pb2.ActionIdentifier, attempt: int = 1
    ) -> AsyncGenerator[payload_pb2.LogLine, None]:
        """
        Tail the logs for a given action ID and attempt.
        :param action_id: The action ID to tail logs for.
        :param attempt: The attempt number (default is 0).
        """
        resp = get_client().logs_service.TailLogs(
            run_logs_service_pb2.TailLogsRequest(action_id=action_id, attempt=attempt)
        )
        async for log_set in resp:
            if log_set.logs:
                for log in log_set.logs:
                    for line in log.lines:
                        yield line

    @classmethod
    async def create_viewer(
        cls,
        action_id: run_definition_pb2.ActionIdentifier,
        attempt: int = 1,
        max_lines: int = 30,
        show_ts: bool = False,
        raw: bool = False,
    ):
        """
        Create a log viewer for a given action ID and attempt.
        :param action_id: Action ID to view logs for.
        :param attempt: Attempt number (default is 1).
        :param max_lines: Maximum number of lines to show if using the viewer. The logger will scroll
           and keep only max_lines in view.
        :param show_ts: Whether to show timestamps in the logs.
        :param raw: if True, return the raw log lines instead of a viewer.
        """
        if raw:
            console = Console()
            async for line in cls.tail.aio(cls, action_id=action_id, attempt=attempt):
                console.print(_format_line(line, show_ts=show_ts), end="")
            return
        viewer = AsyncLogViewer(
            log_source=cls.tail.aio(cls, action_id=action_id, attempt=attempt),
            max_lines=max_lines,
            show_ts=show_ts,
            name=f"{action_id.run.name}:{action_id.name} ({attempt})",
        )
        await viewer.run()
