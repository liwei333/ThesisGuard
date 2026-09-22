"""Drive the real CLI with a synthetically tampered staged plugin."""

from pathlib import Path

from tg_verifier_tools.verification import wp04_02_r4_runner as runner

_original_stage = runner._stage_plugin_to_temp


def _tampered_stage() -> runner.StagedPlugin:
    staged = _original_stage()
    staged.plugin_path.write_text("# synthetic staged-byte mismatch\n", encoding="utf-8")
    return staged


runner._stage_plugin_to_temp = _tampered_stage

raise SystemExit(
    runner.main(
        [
            "--mode",
            "collect-only",
            "--candidate-root",
            "/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/"
            "codex-wp04-02-evidence-domain-service",
            "--main-root",
            "/Users/qianduoduo/Desktop/AI_app/ThesisGuard",
            "--evidence-dir",
            str(Path(__file__).resolve().parents[1] / "negative" / "staged-mismatch"),
            "--pytest",
            "/opt/homebrew/bin/pytest",
        ]
    )
)
