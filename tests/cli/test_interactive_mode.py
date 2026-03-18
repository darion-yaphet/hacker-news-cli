from __future__ import annotations

from hn_cli import cli


def test_interactive_runs_commands_and_prompts(capsys):
    prompts: list[str] = []
    inputs = iter(["help", "quit"])
    commands: list[list[str]] = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(inputs)

    def fake_runner(argv: list[str]) -> int:
        commands.append(argv)
        return 0

    code = cli.run_interactive(input_fn=fake_input, runner=fake_runner)

    out = capsys.readouterr().out
    assert code == 0
    assert prompts == ["> ", "> "]
    assert commands == [["help"]]
    assert "Interactive mode." in out


def test_interactive_supports_hn_prefix_and_skips_blank_lines():
    inputs = iter(["", "   ", "hn list --feed top --page 2", "quit"])
    commands: list[list[str]] = []

    def fake_input(_: str) -> str:
        return next(inputs)

    def fake_runner(argv: list[str]) -> int:
        commands.append(argv)
        return 0

    code = cli.run_interactive(input_fn=fake_input, runner=fake_runner)

    assert code == 0
    assert commands == [["list", "--feed", "top", "--page", "2"]]


def test_interactive_hn_quit_exits_without_running_command():
    inputs = iter(["hn quit"])
    commands: list[list[str]] = []

    def fake_input(_: str) -> str:
        return next(inputs)

    def fake_runner(argv: list[str]) -> int:
        commands.append(argv)
        return 0

    code = cli.run_interactive(input_fn=fake_input, runner=fake_runner)

    assert code == 0
    assert commands == []


def test_interactive_prevents_nested_mode(capsys):
    inputs = iter(["interactive", "quit"])

    def fake_input(_: str) -> str:
        return next(inputs)

    code = cli.run_interactive(input_fn=fake_input, runner=lambda _: 0)

    out = capsys.readouterr().out
    assert code == 0
    assert "Already in interactive mode." in out


def test_interactive_catches_keyboard_interrupt_from_runner(capsys):
    inputs = iter(["list", "quit"])
    calls = {"count": 0}

    def fake_input(_: str) -> str:
        return next(inputs)

    def fake_runner(_: list[str]) -> int:
        calls["count"] += 1
        raise KeyboardInterrupt()

    code = cli.run_interactive(input_fn=fake_input, runner=fake_runner)

    out = capsys.readouterr().out
    assert code == 0
    assert calls["count"] == 1
    assert "Interactive mode." in out


def test_run_interactive_command_delegates(monkeypatch):
    called = {"count": 0}

    def fake_interactive() -> int:
        called["count"] += 1
        return 0

    monkeypatch.setattr(cli, "run_interactive", fake_interactive)
    code = cli.run(["interactive"])

    assert code == 0
    assert called["count"] == 1
