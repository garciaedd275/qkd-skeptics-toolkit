import pytest
import yaml
from click.testing import CliRunner

from qkd_skeptics import core as qkd
from qkd_skeptics.cli import cli
from pqc_audit.models import Classification, CryptoObservation, Finding, Mechanism


def _all(answer_for_expected=True):
    """Answers that match every question's expected answer (or its opposite)."""
    qs = qkd.load_questions()
    flip = {"yes": "no", "no": "yes"}
    return {q.id: {"answer": q.expected if answer_for_expected else flip[q.expected]} for q in qs}


def test_question_bank_loads_and_is_well_formed():
    qs = qkd.load_questions()
    ids = [q.id for q in qs]
    assert len(ids) == len(set(ids)) > 10
    assert all(q.expected in ("yes", "no") and 1 <= q.weight <= 3 and q.why for q in qs)
    # conditional questions reference real questions
    for q in qs:
        assert set(q.applies_if) <= set(ids)


def test_all_expected_answers_score_100_well_evidenced():
    results, score, rating = qkd.score_answers(qkd.load_questions(), _all(True))
    assert rating == "Well evidenced"
    # A3 only applies when A2 == yes, so it is not applicable here.
    assert score == 100.0
    assert next(r for r in results if r.question.id == "A3").status == "not_applicable"


def test_all_wrong_answers_flag_critical_gaps():
    _, score, rating = qkd.score_answers(qkd.load_questions(), _all(False))
    assert rating == "Critical gaps"
    assert score == 0.0


def test_missing_answers_are_unverified_not_gaps():
    results, score, rating = qkd.score_answers(qkd.load_questions(), {})
    assert all(r.status in ("unverified", "not_applicable") for r in results)
    assert score == 0.0
    assert rating == "Weakly evidenced"


def test_conditional_question_activates_when_trusted_relays_used():
    answers = _all(True)
    answers["A2"] = {"answer": "yes"}  # trusted relays in use
    answers["A3"] = {"answer": "unknown"}  # relay security not demonstrated
    results, _, rating = qkd.score_answers(qkd.load_questions(), answers)
    assert next(r for r in results if r.question.id == "A3").status == "unverified"
    assert next(r for r in results if r.question.id == "A2").status == "gap"
    assert rating == "Critical gaps"  # A2 is weight 3


def test_invalid_answer_and_unknown_id_rejected():
    qs = qkd.load_questions()
    with pytest.raises(ValueError):
        qkd.score_answers(qs, {"C1": {"answer": "maybe"}})
    with pytest.raises(ValueError):
        qkd.score_answers(qs, {"ZZ9": {"answer": "yes"}})


def test_template_round_trips_as_valid_unknown_answers():
    qs = qkd.load_questions()
    doc = yaml.safe_load(qkd.template_yaml(qs))
    assert set(doc["answers"]) == {q.id for q in qs}
    _, _, rating = qkd.score_answers(qs, doc["answers"])
    assert rating == "Weakly evidenced"


def test_assess_scans_endpoints_with_mocked_scanner(monkeypatch):
    obs = CryptoObservation(target="kme.example.com:443", mechanism=Mechanism.KEY_EXCHANGE, algorithm="ECDHE", key_size=256, protocol_version="TLS 1.2")
    monkeypatch.setattr(qkd, "scan_targets", lambda targets: ([obs], []))
    doc = {"vendor": "Acme", "claim": "unhackable", "answers": _all(True), "endpoints": [{"hostname": "kme.example.com"}]}
    a = qkd.assess(doc)
    assert a.endpoints[0].findings[0].classification == Classification.VULNERABLE
    text = qkd.render_markdown(a)
    assert "Key-management endpoint scan" in text and "ECDHE" in text


def test_render_markdown_lists_gaps(monkeypatch):
    doc = {"vendor": "Acme", "claim": "quantum-proof link", "answers": _all(False)}
    text = qkd.render_markdown(qkd.assess(doc, scan=False))
    assert "Critical gaps" in text and "## Gaps" in text and "Acme" in text


def test_cli_template_then_assess(tmp_path):
    runner = CliRunner()
    answers = tmp_path / "answers.yaml"
    assert runner.invoke(cli, ["template", "-o", str(answers)]).exit_code == 0

    out = tmp_path / "report.md"
    result = runner.invoke(cli, ["assess", str(answers), "-o", str(out), "--no-scan"])
    assert result.exit_code == 0, result.output
    assert "QKD Claims Assessment" in out.read_text()


def test_cli_assess_rejects_bad_answer(tmp_path):
    answers = tmp_path / "answers.yaml"
    answers.write_text("answers:\n  C1: {answer: maybe}\n")
    result = CliRunner().invoke(cli, ["assess", str(answers), "-o", str(tmp_path / "r.md"), "--no-scan"])
    assert result.exit_code == 1
