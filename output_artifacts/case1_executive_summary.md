# AI Governance Audit Executive Summary - Sentinel Financial

**Date:** 2026-01-13
**Prepared By:** Sarah, AI Program Lead

## 1. Introduction
This summary provides an overview of Sentinel Financial's AI governance artifacts, compiled for the internal audit. It covers our AI system inventory, risk tiering results aligned with SR 11-7-style principles, and a detailed map of lifecycle risks. Our goal is to demonstrate a robust, structured, and auditable approach to managing AI systems within the institution.

## 2. AI System Inventory
Sentinel Financial maintains a comprehensive inventory of all AI systems. Currently, three key systems are highlighted for this audit:

| System Name                               | AI Type | Decision Criticality | Data Sensitivity |
|-------------------------------------------|---------|----------------------|------------------|
| ML-based Credit Underwriting Model        | ML      | HIGH                 | REGULATED_PII    |
| LLM-based Customer Support Assistant      | LLM     | MEDIUM               | CONFIDENTIAL     |
| Agentic Internal Report Generator         | AGENT   | LOW                  | INTERNAL         |

## 3. AI Risk Tiering Results
Each AI system undergoes a deterministic risk tiering process based on attributes like decision criticality, data sensitivity, automation level, and external dependencies. This ensures consistent risk classification and the assignment of appropriate controls.

### Scoring Logic:
The total risk score $S_{total}$ is calculated by summing scores from various dimensions. For instance:
*   Decision Criticality: LOW=1, MEDIUM=3, HIGH=5
*   Data Sensitivity: PUBLIC=1, INTERNAL=2, CONFIDENTIAL=4, REGULATED_PII=5
*   Automation Level: ADVISORY=1, HUMAN_APPROVAL=3, FULLY_AUTOMATED=5
*   AI Type: ML=3, LLM=4, AGENT=5
*   Deployment Mode: INTERNAL_ONLY=1, BATCH=2, HUMAN_IN_LOOP=3, REAL_TIME=4
*   External Dependencies: 0 if none, 2 if any

Risk Tiers:
*   Tier 1 (High Risk): $S_{total} \geq 22$
*   Tier 2 (Medium Risk): $15 \leq S_{total} \leq 21$
*   Tier 3 (Low Risk): $S_{total} \leq 14$

### Summary of Tiers:

| System Name                               | Risk Tier | Total Score | Key Justification                                 |
|-------------------------------------------|-----------|-------------|---------------------------------------------------|
| ML-based Credit Underwriting Model        | TIER_1 | 24 | High criticality, PII data, fully automated real-time decisions. |
| LLM-based Customer Support Assistant      | TIER_2 | 17 | Medium criticality, confidential data, human-in-loop advisory. |
| Agentic Internal Report Generator         | TIER_2 | 16 | Low criticality, internal data, fully automated internal use. |

## 4. Lifecycle Risk Map
We have identified and mapped specific risks across the lifecycle phases of our AI systems. Risks are prioritized by severity, calculated as Impact $	imes$ Likelihood.

### Top 3 Lifecycle Risks:

| System Name                               | Risk Statement                                                      | Severity | Lifecycle Phase |
|-------------------------------------------|---------------------------------------------------------------------|----------|-----------------|
| ML-based Credit Underwriting Model | Bias in historical training data leads to unfair lending decisions for certain demographics.                       | 20   | DESIGN |
| ML-based Credit Underwriting Model | Data drift leads to degradation of model performance in production over time.                       | 20   | MONITORING |
| LLM-based Customer Support Assistant | LLM generates incorrect or misleading information, damaging customer trust.                       | 16   | DEPLOYMENT |

## 5. Conclusion
This audit package demonstrates Sentinel Financial's commitment to responsible AI governance. By systematically inventorying, risk-tiering, and mapping lifecycle risks, we ensure accountability and maintain the integrity of our AI systems. The accompanying evidence manifest provides cryptographic proof of the authenticity of these artifacts.