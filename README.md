# QKD Skeptic's Toolkit

A toolkit for testing **claims** about quantum key distribution (QKD). It does
not and cannot verify the physics of a QKD system; that needs independent lab
testing. What it can check is everything around the physics:

1. **Is the claim scoped and evidenced?** A scored questionnaire (19 questions,
   editable in `qkd_skeptics/questions.yaml`) covering claim language,
   architecture (trusted relays, fallback), authentication, key delivery,
   key usage, independent evaluation and operations. Each question states why
   it matters and which public guidance it comes from.
2. **Are the classical interfaces strong?** Keys from a QKD system cross
   ordinary network interfaces (key-management/key-delivery endpoints). The
   tool scans any endpoints you list with the TLS scanner from
   [pqc-readiness-audit](https://github.com/garciaedd275/pqc-readiness-audit)
   and flags quantum-vulnerable or weak algorithms. A QKD-derived key sent
   over RSA/ECDH can be recovered later, however it was generated.

## Why a skeptic's toolkit

The NSA does not recommend QKD for National Security Systems, citing
dedicated hardware/fiber, trusted relays, authentication needs and limited
upgradability. ANSSI/BSI treat it as niche, prioritizing PQC, and accept it
only as defense-in-depth. The UK NCSC cautions against sole reliance. These
positions are from memory of public documents (2020-era in places): verify
current wording before citing. QKD standards referenced: ETSI GS QKD 014 (key
delivery API), ETSI GS QKD 016 (protection profile), ISO/IEC 23837 (evaluation);
document status varies, so check ETSI and ISO directly.

## Install

```bash
# macOS / Kali (PEP 668): use pipx
pipx install --python python3.13 git+https://github.com/garciaedd275/qkd-skeptics-toolkit.git
```

Use Python 3.10-3.13 (tested on 3.13). If your default `python3` is newer
(Homebrew moved to 3.15), the install fails with "ResolutionImpossible"
because `sslyze` has no compatible build yet; the `--python` flag fixes it.

For development: `pip install -e ~/pqc-readiness-audit && pip install -e ".[dev]"`.

## Use

```bash
qkd-skeptic template -o answers.yaml      # blank questionnaire
# fill in yes / no / unknown for each question, list any key-management endpoints
qkd-skeptic assess answers.yaml -o report.md
qkd-skeptic assess answers.yaml -o report.md --no-scan   # questionnaire only
```

Answers: `yes`, `no`, or `unknown`. `unknown` (or a missing answer) means the
vendor has not demonstrated it, and is reported as **unverified**, not as a pass.
Any weight-3 gap gives an overall **Critical gaps** rating; otherwise the
evidence score sets Well / Partially / Weakly evidenced. See
[`examples/sample_report.md`](examples/sample_report.md).

**Endpoint scanning opens TLS connections to the hosts you list. Only scan
systems you own or are authorized to assess.**

## Limits

- It tests evidence, not physics. A perfect score does not mean the hardware
  is secure.
- Scoring weights are judgments, not an industry standard. Edit them.
- Endpoint findings inherit the audit tool's scanner limits (see its README).
