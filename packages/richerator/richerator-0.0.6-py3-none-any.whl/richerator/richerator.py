from rich.console import Console, Group
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    ProgressColumn,
)
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
import builtins
from io import StringIO
import time

# ─── custom columns ────────────────────────────────────────────────────────────


class NamedTimeElapsedColumn(TimeElapsedColumn):
    def __init__(self, label: str = "Elapsed:"):
        super().__init__()
        self.label = label

    def render(self, task):
        return Text(self.label + " ") + super().render(task)


class NamedTimeRemainingColumn(TimeRemainingColumn):
    def __init__(self, label: str = "Remaining:"):
        super().__init__()
        self.label = label

    def render(self, task):
        return Text(self.label + " ") + super().render(task)


class DynamicThroughputColumn(ProgressColumn):
    def render(self, task):
        elapsed = task.elapsed or 1e-6
        completed = task.completed or 1e-6
        speed = completed / elapsed
        if speed >= 1.0:
            return Text(f"{speed:>6.2f} iters/s")
        else:
            return Text(f"{elapsed / completed:>6.2f} s/iter")


# ─── the improved wrapper ──────────────────────────────────────────────────────


def richerator(
    iterable,
    *,
    description: str = "Processing",
    refresh_per_second: int = 10,
    progress_kwargs: dict = None,
    panel_kwargs: dict = None,
    total: int = None,
):
    console = Console()
    default_cols = [
        TextColumn(
            "[progress.completed]{task.completed}/{task.total}",
            justify="right",
        ),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        NamedTimeElapsedColumn(),
        NamedTimeRemainingColumn(),
        DynamicThroughputColumn(),
    ]
    # allow user overrides
    p_kwargs = {"console": console, "refresh_per_second": refresh_per_second}
    cols = default_cols
    if progress_kwargs:
        cols = progress_kwargs.pop("columns", default_cols)
        p_kwargs.update(progress_kwargs)

    progress = Progress(*cols, **p_kwargs)
    if total is None:
        total = len(iterable) if hasattr(iterable, "__len__") else None
    task = progress.add_task(description, total=total)

    live = Live(console=console, refresh_per_second=refresh_per_second)
    live.start()
    try:
        for item in iterable:
            buf = StringIO()
            old_print = builtins.print

            def patched_print(*args, **kwargs):
                # write into buffer
                old_print(*args, file=buf, **kwargs)
                # immediately re-render panel + bar
                panel = Panel(
                    buf.getvalue().rstrip("\n"),
                    title=description,
                    expand=True,
                    **(panel_kwargs or {}),
                )
                live.update(Group(progress, panel))

            builtins.print = patched_print

            try:
                yield item
            finally:
                # restore print and advance bar one final time for this iter
                builtins.print = old_print
                progress.advance(task)
                panel = Panel(
                    buf.getvalue().rstrip("\n"),
                    title=description,
                    expand=True,
                    **(panel_kwargs or {}),
                )
                live.update(Group(progress, panel))

    finally:
        live.stop()


# ─── example usage ────────────────────────────────────────────────────────────


if __name__ == "__main__":
    for x in richerator(range(1, 31), description="Looping Demo"):
        print(f"step {x}")
        print("  detail A", "detail B", sep=" | ")
        if x % 3 == 0:
            print(f"  detail C")
            time.sleep(0.5)

        time.sleep(0.1)
