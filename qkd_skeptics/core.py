"""QKD claims verification toolkit.

Software cannot verify the physics of a QKD system. What it can do is check
the parts around it: whether the vendor's claim is scoped and evidenced
(a questionnaire scored against an editable question bank), and whether the
classical interfaces that carry QKD-derived keys (key-management endpoints)
use strong cryptography (the existing TLS scanner and rule engine).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

import yaml

from pqc_audit.models import Classification, Exposure, Finding, TargetSpec
from pqc_audit.rules import RuleEngine
from pqc_audit.scanner import scan_targets

VALID_ANSWERS = {"yes", "no", "unknown"}


@dataclass
class Question:
    id: str
    category: str
    text: str
    expected: str
    weight: int
    why: str
    applies_if: dict[str, str] = field(default_factory=dict)


@dataclass
class QuestionResult:
    question: Question
    answer: str  # yes | no | unknown
    note: str
    status: str  # met | gap | unverified | not_applicable


@dataclass
class EndpointResult:
    target: str
    findings: list[Finding]
    error: Optional[str] = None


@dataclass
class QkdAssessment:
    vendor: str
    claim: str
    results: list[QuestionResult]
    endpoints: list[EndpointResult]
    score_percent: float
    rating: str

    @property
    def gaps(self) -> list[QuestionResult]:
        return sorted((r for r in self.results if r.status == "gap"), key=lambda r: -r.question.weight)

    @property
    def unverified(self) -> list[QuestionResult]:
        return sorted((r for r in self.results if r.status == "unverified"), key=lambda r: -r.question.weight)

    @property
    def critical_gaps(self) -> list[QuestionResult]:
        return [r for r in self.gaps if r.question.weight >= 3]


def load_questions(path: Optional[Path] = None) -> list[Question]:
    raw = Path(path).read_text() if path else resources.files("qkd_skeptics").joinpath("questions.yaml").read_text()
    return [
        Question(
            id=q["id"],
            category=q["category"],
            text=" ".join(q["text"].split()),
            expected=str(q["expected"]).lower(),
            weight=int(q["weight"]),
            why=" ".join(q["why"].split()),
            applies_if={k: str(v).lower() for k, v in (q.get("applies_if") or {}).items()},
        )
        for q in yaml.safe_load(raw)["questions"]
    ]


def template_yaml(questions: list[Question]) -> str:
    """A blank answers file the assessor fills in."""
    lines = [
        "# QKD claims assessment answers. Answer each question: yes | no | unknown",
        "vendor: ''            # vendor / product being assessed",
        "claim: ''             # the exact claim made (copy the marketing/RFP wording)",
        "endpoints: []         # key-management / key-delivery endpoints to scan, e.g.",
        "                      #   - {hostname: kme.example.com, port: 443}",
        "answers:",
    ]
    category = None
    for q in questions:
        if q.category != category:
            category = q.category
            lines.append(f"  # --- {category} ---")
        lines.append(f"  # {q.text}")
        lines.append(f"  {q.id}: {{answer: unknown, note: ''}}")
    return "\n".join(lines) + "\n"


def score_answers(questions: list[Question], answers: dict) -> tuple[list[QuestionResult], float, str]:
    normalized: dict[str, tuple[str, str]] = {}
    for qid, entry in (answers or {}).items():
        if isinstance(entry, dict):
            answer, note = str(entry.get("answer", "unknown")).lower(), str(entry.get("note") or "")
        else:
            answer, note = str(entry).lower(), ""
        if answer not in VALID_ANSWERS:
            raise ValueError(f"Answer for {qid} must be yes, no or unknown (got '{answer}')")
        normalized[str(qid)] = (answer, note)

    unknown_ids = set(normalized) - {q.id for q in questions}
    if unknown_ids:
        raise ValueError(f"Answers reference unknown question ids: {', '.join(sorted(unknown_ids))}")

    results: list[QuestionResult] = []
    for q in questions:
        answer, note = normalized.get(q.id, ("unknown", ""))
        applicable = all(normalized.get(dep, ("unknown", ""))[0] == val for dep, val in q.applies_if.items())
        if not applicable:
            status = "not_applicable"
        elif answer == "unknown":
            status = "unverified"
        elif answer == q.expected:
            status = "met"
        else:
            status = "gap"
        results.append(QuestionResult(q, answer, note, status))

    applicable_weight = sum(r.question.weight for r in results if r.status != "not_applicable")
    met_weight = sum(r.question.weight for r in results if r.status == "met")
    score = round(100 * met_weight / applicable_weight, 1) if applicable_weight else 0.0

    critical_gap = any(r.status == "gap" and r.question.weight >= 3 for r in results)
    if critical_gap:
        rating = "Critical gaps"
    elif score >= 80:
        rating = "Well evidenced"
    elif score >= 50:
        rating = "Partially evidenced"
    else:
        rating = "Weakly evidenced"
    return results, score, rating


def scan_endpoints(endpoints: list[dict], rules_path: Optional[Path] = None) -> list[EndpointResult]:
    """Scan key-management endpoints with the existing TLS scanner + rule engine."""
    if not endpoints:
        return []
    targets = [
        TargetSpec(
            hostname=e["hostname"],
            port=int(e.get("port", 443)),
            exposure=Exposure(str(e.get("exposure", "internal"))),
            retention_years=int(e.get("retention_years", 25)),
        )
        for e in endpoints
    ]
    observations, errors = scan_targets(targets)
    engine = RuleEngine.load(rules_path)
    findings = engine.classify_all(observations)

    out: list[EndpointResult] = []
    for target in targets:
        name = target.display_name()
        error = next((e.reason for e in errors if e.target == name), None)
        out.append(EndpointResult(name, [f for f in findings if f.observation.target == name], error))
    return out


def assess(
    answers_doc: dict,
    questions: Optional[list[Question]] = None,
    scan: bool = True,
    rules_path: Optional[Path] = None,
) -> QkdAssessment:
    questions = questions or load_questions()
    results, score, rating = score_answers(questions, answers_doc.get("answers"))
    endpoints = scan_endpoints(answers_doc.get("endpoints") or [], rules_path) if scan else []
    return QkdAssessment(
        vendor=str(answers_doc.get("vendor") or "(not stated)"),
        claim=str(answers_doc.get("claim") or "(not stated)"),
        results=results,
        endpoints=endpoints,
        score_percent=score,
        rating=rating,
    )


def render_markdown(a: QkdAssessment) -> str:
    out = [
        "# QKD Claims Assessment",
        "",
        f"**Vendor / product:** {a.vendor}",
        f"**Claim assessed:** {a.claim}",
        f"**Evidence score:** {a.score_percent}% — **{a.rating}**",
        "",
        "This assessment tests whether a QKD claim is scoped and evidenced. It does not "
        "verify the physics: hardware and side-channel security need independent lab testing.",
        "",
        "## Summary",
        "",
        f"- **{len(a.critical_gaps)}** critical gap(s), **{len(a.gaps)}** gap(s) in total, "
        f"**{len(a.unverified)}** unverified question(s).",
    ]
    vulnerable = sum(1 for e in a.endpoints for f in e.findings if f.classification == Classification.VULNERABLE)
    if a.endpoints:
        out.append(f"- Key-management endpoints scanned: **{len(a.endpoints)}**, with **{vulnerable}** quantum-vulnerable or weak algorithm finding(s).")
    out.append("")

    def section(title: str, rows: list[QuestionResult], show_why: bool = True) -> None:
        if not rows:
            return
        out.extend([f"## {title}", "", "| ID | Category | Question | Answer | Weight | Why it matters |", "|---|---|---|---|---|---|"])
        for r in rows:
            note = f" ({r.note})" if r.note else ""
            out.append(f"| {r.question.id} | {r.question.category} | {r.question.text} | {r.answer}{note} | {r.question.weight} | {r.question.why if show_why else ''} |")
        out.append("")

    section("Gaps (answer contradicts a secure design)", a.gaps)
    section("Unverified (vendor has not demonstrated)", a.unverified)
    section("Requirements met", [r for r in a.results if r.status == "met"], show_why=False)

    if a.endpoints:
        out.extend(["## Key-management endpoint scan", "",
                    "Keys delivered from a QKD system cross these classical interfaces. If they use RSA/ECDH, "
                    "an attacker who records the traffic can recover the keys once a quantum computer exists, "
                    "regardless of how the keys were generated.", ""])
        for e in a.endpoints:
            out.append(f"### {e.target}")
            if e.error:
                out.extend([f"Scan failed: {e.error}", ""])
                continue
            bad = [f for f in e.findings if f.classification in (Classification.VULNERABLE, Classification.WEAKENED)]
            if not bad:
                out.extend(["No vulnerable or weakened algorithms found.", ""])
                continue
            out.extend(["| Mechanism | Protocol | Algorithm | Classification |", "|---|---|---|---|"])
            seen = set()
            for f in bad:
                o = f.observation
                row = (o.mechanism.value, o.protocol_version or "-", o.algorithm, f.classification.value)
                if row not in seen:
                    seen.add(row)
                    out.append("| " + " | ".join(row) + " |")
            out.append("")

    out.extend([
        "## Sources behind the questions",
        "",
        "NSA position on QKD; ANSSI/BSI joint QKD position paper; UK NCSC QKD statement (2020); "
        "ETSI GS QKD 014 / GS QKD 016; ISO/IEC 23837. Verify current wording and document status "
        "before citing. The full rationale for each question is in `qkd_skeptics/questions.yaml`.",
        "",
    ])
    return "\n".join(out)
