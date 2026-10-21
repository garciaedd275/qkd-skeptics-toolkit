# QKD Claims Assessment

**Vendor / product:** Example QKD Vendor (fictional)
**Claim assessed:** Our QKD link makes your network unhackable and quantum-proof.
**Evidence score:** 16.7% — **Critical gaps**

This assessment tests whether a QKD claim is scoped and evidenced. It does not verify the physics: hardware and side-channel security need independent lab testing.

## Summary

- **2** critical gap(s), **5** gap(s) in total, **11** unverified question(s).

## Gaps (answer contradicts a secure design)

| ID | Category | Question | Answer | Weight | Why it matters |
|---|---|---|---|---|---|
| A2 | Architecture | Does any segment rely on trusted relay nodes? | yes (Two trusted relay sites) | 3 | Trusted relays see the keys in the clear, so they become high-value insider and physical targets (NSA objection). |
| E1 | Evidence | Has the system been independently evaluated (e.g. ISO/IEC 23837-based Common Criteria evaluation, ETSI GS QKD 016 protection profile)? | no (No third-party evaluation) | 3 | Without third-party evaluation, security claims are the vendor's own. |
| C1 | Claim language | Does the vendor describe the system as "unhackable", "unbreakable" or "quantum-proof" without qualification? | yes (Brochure says 'unhackable') | 2 | Security depends on hardware and implementation, not physics alone. Unqualified claims are a red flag. |
| C2 | Claim language | Is the claim scoped to a specific link or segment, not the whole system? | no (Claim covers the whole network) | 2 | QKD protects key establishment on one link. Everything outside that link keeps its own risks. |
| U2 | Key usage | Are QKD keys combined with PQC or classical keys (defense in depth), not used alone? | no (QKD keys used alone) | 2 | ANSSI accepts QKD only as defense-in-depth alongside classical or PQC protection. |

## Unverified (vendor has not demonstrated)

| ID | Category | Question | Answer | Weight | Why it matters |
|---|---|---|---|---|---|
| A3 | Architecture | Are trusted relay nodes physically secured, monitored, and inside the audit scope? | unknown | 3 | If relays are used, the whole security argument rests on them. |
| B2 | Authentication | Is that authentication quantum-safe (information-theoretic MACs with pre-shared keys, or PQC) and not RSA/ECDSA? | unknown (Vendor would not say how the link is authenticated) | 3 | Authenticating a quantum-safe key exchange with breakable signatures defeats the purpose. |
| U3 | Key usage | Does the same data also travel over links protected only by RSA/ECDH key exchange that the QKD claim does not cover? | unknown | 3 | Harvest-now-decrypt-later targets the weakest path. A QKD segment does not help if the same data crosses a breakable one. |
| A4 | Architecture | Is there a documented fallback if the quantum link is disrupted (fiber cut, or eavesdropping detection tripping)? | unknown | 2 | Eavesdropping detection turns any tampering into a denial of service (ANSSI/BSI). Without fallback, availability suffers or keys are bypassed. |
| B3 | Authentication | Is provisioning and refresh of the initial authentication keys documented and controlled? | unknown | 2 | QKD needs a pre-shared secret to bootstrap authentication. Its handling is a key dependency. |
| K2 | Key delivery | Is the key-delivery / key-management interface protected by TLS 1.2+ with strong authentication? | unknown | 2 | Keys cross this classical interface. Weak transport protection exposes them. See the automated endpoint scan below. |
| E2 | Evidence | Has the hardware had independent penetration and side-channel testing (e.g. detector-blinding attacks)? | unknown | 2 | Practical QKD attacks target implementation flaws in detectors and optics, not the protocol. |
| O1 | Operations | Is there a process for patching, updating or replacing the QKD hardware and firmware? | unknown | 2 | QKD is hardware-based and hard to upgrade (NSA objection). Lifecycle needs a plan. |
| O3 | Operations | Is there a PQC migration plan for the organization regardless of QKD? | unknown | 2 | Agencies prioritize PQC. QKD is not a substitute for it. |
| E3 | Evidence | Are key rate, error rate (QBER) and uptime measured and available for audit? | unknown | 1 | Operating metrics show whether the link works as claimed. |
| O2 | Operations | Is supply-chain provenance of the QKD hardware documented? | unknown | 1 | Specialized hardware from few vendors is a supply-chain concentration risk. |

## Requirements met

| ID | Category | Question | Answer | Weight | Why it matters |
|---|---|---|---|---|---|
| A1 | Architecture | Are the physical link type (fiber or free-space/satellite) and maximum distance documented? | yes | 1 |  |
| B1 | Authentication | Is the classical channel used for QKD post-processing authenticated? | yes | 3 |  |
| K1 | Key delivery | Does the key-delivery interface follow a published standard (e.g. ETSI GS QKD 014)? | yes (ETSI GS QKD 014 interface) | 1 |  |
| U1 | Key usage | Are QKD-derived keys used with a strong cipher (AES-256 or equivalent)? | yes | 2 |  |

## Sources behind the questions

NSA position on QKD; ANSSI/BSI joint QKD position paper; UK NCSC QKD statement (2020); ETSI GS QKD 014 / GS QKD 016; ISO/IEC 23837. Verify current wording and document status before citing. The full rationale for each question is in `qkd_skeptics/questions.yaml`.
