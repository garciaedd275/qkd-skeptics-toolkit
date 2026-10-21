"""Command-line interface: `qkd-skeptic template` and `qkd-skeptic assess`."""

from __future__ import annotations

import sys
from pathlib import Path

import click
import yaml

from qkd_skeptics import core


@click.group()
@click.version_option()
def cli():
    """QKD skeptic's toolkit: test whether a QKD claim is scoped and evidenced."""


@cli.command("template")
@click.option("-o", "--output", "output_path", required=True, type=click.Path(dir_okay=False), help="Where to write the blank answers file")
def template(output_path):
    """Write a blank QKD questionnaire (answers.yaml) to fill in."""
    Path(output_path).write_text(core.template_yaml(core.load_questions()))
    click.secho(f"Wrote {output_path}. Fill in answers (yes/no/unknown), then run `qkd-skeptic assess`.", fg="green")


@cli.command("assess")
@click.argument("answers_yaml", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", "output_path", required=True, type=click.Path(dir_okay=False), help="Report output path (.md)")
@click.option("--no-scan", is_flag=True, default=False, help="Skip scanning the key-management endpoints listed in the answers file.")
@click.option("--questions", "questions_path", type=click.Path(exists=True, dir_okay=False), default=None, help="Custom question bank YAML.")
def assess(answers_yaml, output_path, no_scan, questions_path):
    """Score a completed QKD questionnaire and scan any listed endpoints.

    Endpoint scanning opens TLS connections to the hosts you list: only list
    systems you own or are authorized to assess.
    """
    doc = yaml.safe_load(Path(answers_yaml).read_text()) or {}
    questions = core.load_questions(Path(questions_path) if questions_path else None)
    try:
        assessment = core.assess(doc, questions, scan=not no_scan)
    except ValueError as exc:
        click.secho(str(exc), fg="red", err=True)
        sys.exit(1)
    Path(output_path).write_text(core.render_markdown(assessment))
    click.secho(f"Wrote {output_path}", fg="green")
    click.echo(f"{assessment.rating} ({assessment.score_percent}%): {len(assessment.critical_gaps)} critical gap(s), {len(assessment.unverified)} unverified.")


if __name__ == "__main__":
    cli()
