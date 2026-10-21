# QKD Claims Assessment

**Vendor / product:** Example QKD Vendor (fictional)
**Claim assessed:** Our QKD link makes your network unhackable and quantum-proof.
**Evidence score:** 14.6% — **Critical gaps**

This assessment tests whether a QKD claim is scoped and evidenced. It does not verify the physics: hardware and side-channel security need independent lab testing.

## Summary

- **2** critical gap(s), **5** gap(s) in total, **14** unverified question(s).

## Gaps (answer contradicts a secure design)

| ID | Category | Question | Answer | Weight | Why it matters |
|---|---|---|---|---|---|
| A2 | Architecture | Does any segment rely on trusted relay nodes? | yes (Two trusted relay sites) | 3 | Over long distances fiber QKD needs trusted nodes, so end-to-end security is not achieved, and in most current implementations satellites are themselves trusted nodes (joint paper). Relays see the keys, so they are high-value targets. |
| E1 | Evidence | Has the system been independently evaluated (e.g. ISO/IEC 23837-based Common Criteria evaluation, ETSI GS QKD 016 protection profile)? | no (No third-party evaluation) | 3 | The joint paper says devices need rigorous evaluation because physical attacks exist. A Common Criteria protection profile (ETSI GS QKD 016, developed with BSI) and ISO/IEC 23837-1/-2 (2023) exist, but the paper says an evaluation methodology for physical attacks is still to be developed. |
| C1 | Claim language | Does the vendor describe the system as "unhackable", "unbreakable" or "quantum-proof" without qualification? | yes (Brochure says 'unhackable') | 2 | The joint paper says claims of "absolute" or "unconditional" security can never apply to actual implementations; several commercial QKD systems have been broken through their physical devices. |
| C2 | Claim language | Is the claim scoped to a specific link or segment, not the whole system? | no (Claim covers the whole network) | 2 | QKD protects key establishment on one link. Everything outside that link keeps its own risks. |
| U2 | Key usage | Are QKD keys combined with other keying (PQC hybrid or pre-shared symmetric keys), not relied on alone? | no (QKD keys used alone) | 2 | The joint paper's clear priority is PQC in hybrid with traditional keying. Sole reliance on QKD carries its implementation and availability risks. |

## Unverified (vendor has not demonstrated)

| ID | Category | Question | Answer | Weight | Why it matters |
|---|---|---|---|---|---|
| A3 | Architecture | Are trusted relay nodes physically secured, monitored, and inside the audit scope? | unknown | 3 | If relays are used, the whole security argument rests on them. |
| B2 | Authentication | Is that authentication quantum-safe (symmetric MACs with pre-shared keys, or PQC signatures) and not RSA/ECDSA? | unknown (Vendor would not say how the link is authenticated) | 3 | The joint paper lists two options, pre-shared keys with symmetric authentication or PQC signatures (which then rely on the PQC scheme). Breakable signatures defeat the purpose. |
| U3 | Key usage | Does the same data also travel over links protected only by RSA/ECDH key exchange that the QKD claim does not cover? | unknown | 3 | Harvest-now-decrypt-later targets the weakest path. A QKD segment does not help if the same data crosses a breakable one. |
| C3 | Claim language | Does the vendor claim "absolute" or information-theoretic security while the QKD keys are used with AES or a similar cipher, not a one-time pad? | unknown | 2 | Absolute security needs a one-time pad, which needs a QKD key rate equal to the data rate. With AES the claim no longer holds (joint paper). |
| J1 | Use case | Can the vendor show why PQC or pre-shared symmetric keys cannot meet this requirement, so the cost of QKD is justified? | unknown | 2 | The joint paper says QKD is only relevant where the security requirement justifies its very high costs and cheaper options are not feasible. |
| A4 | Architecture | Is there a documented fallback if the quantum link is disrupted (fiber cut, or eavesdropping detection tripping)? | unknown | 2 | Every eavesdropping attempt, and any interference with the channel, becomes a denial of service, and protecting against it is still unstudied (joint paper). Without a fallback, availability suffers or keys are bypassed. |
| B3 | Authentication | Is provisioning and refresh of the initial authentication keys documented and controlled? | unknown | 2 | Pre-shared authentication keys must be distributed and periodically renewed securely before QKD can run (joint paper). |
| K2 | Key delivery | Is the key-delivery / key-management interface protected by TLS 1.2+ with strong authentication? | unknown | 2 | Keys cross this classical interface. Weak transport protection exposes them. See the automated endpoint scan below. |
| P1 | Evidence | Is the protocol's security proof published, covering finite key sizes and realistic loss and detector imperfections? | unknown | 2 | The joint paper says no QKD protocol has been standardised and no proof for a practically relevant protocol meets these requirements. Some commercial protocols lacked sufficient proofs and were later shown insecure. |
| E2 | Evidence | Has the hardware had independent penetration and side-channel testing (e.g. detector-blinding attacks)? | unknown | 2 | Practical attacks target implementation flaws in detectors and optics (e.g. bright-illumination attacks on commercial systems cited in the joint paper), not the protocol. |
| O1 | Operations | Is there a process for patching, updating or replacing the QKD hardware and firmware? | unknown | 2 | QKD needs specialised hardware with very high life-cycle costs (joint paper) and cannot be patched like software (NSA objection, from secondary summaries). Lifecycle needs a plan. |
| O3 | Operations | Is there a PQC migration plan for the organization regardless of QKD? | unknown | 2 | The joint paper says the clear priority is migrating to PQC, which runs on classical hardware. QKD is not a substitute. |
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
