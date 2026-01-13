import pandas as pd
from pydantic import BaseModel, Field, ValidationError, UUID4
from typing import List, Optional
import uuid
from datetime import datetime
import hashlib
import json
import os
import shutil
from enum import Enum

print("Libraries imported successfully and environment prepared.")
# Define Enumerations for AI System attributes


class AIType(str, Enum):
    ML = "ML"
    LLM = "LLM"
    AGENT = "AGENT"


class DeploymentMode(str, Enum):
    BATCH = "BATCH"
    REAL_TIME = "REAL_TIME"
    HUMAN_IN_LOOP = "HUMAN_IN_LOOP"
    INTERNAL_ONLY = "INTERNAL_ONLY"


class DataSensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    REGULATED_PII = "REGULATED_PII"


class DecisionCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AutomationLevel(str, Enum):
    ADVISORY = "ADVISORY"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    FULLY_AUTOMATED = "FULLY_AUTOMATED"


class RiskTier(str, Enum):
    TIER_1 = "TIER_1"  # High Risk
    TIER_2 = "TIER_2"  # Medium Risk
    TIER_3 = "TIER_3"  # Low Risk


class LifecyclePhase(str, Enum):
    DESIGN = "DESIGN"
    DEVELOPMENT = "DEVELOPMENT"
    TRAINING = "TRAINING"
    TESTING = "TESTING"
    DEPLOYMENT = "DEPLOYMENT"
    MONITORING = "MONITORING"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONING = "DECOMMISSIONING"


class RiskCategory(str, Enum):
    BIAS_FAIRNESS = "BIAS_FAIRNESS"
    PERFORMANCE_ROBUSTNESS = "PERFORMANCE_ROBUSTNESS"
    DATA_PRIVACY_SECURITY = "DATA_PRIVACY_SECURITY"
    INTERPRETABILITY_EXPLAINABILITY = "INTERPRETABILITY_EXPLAINABILITY"
    OPERATIONAL_RELIABILITY = "OPERATIONAL_RELIABILITY"
    LEGAL_REGULATORY = "LEGAL_REGULATORY"
    REPUTATIONAL = "REPUTATIONAL"
    ENVIRONMENTAL_SOCIAL = "ENVIRONMENTAL_SOCIAL"


# Define Pydantic Models for our data structures
class SystemRecord(BaseModel):
    system_id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    description: str
    domain: str
    ai_type: AIType
    owner_role: str
    deployment_mode: DeploymentMode
    decision_criticality: DecisionCriticality
    automation_level: AutomationLevel
    data_sensitivity: DataSensitivity
    external_dependencies: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class RiskTierResult(BaseModel):
    system_id: UUID4
    risk_tier: RiskTier
    score_breakdown: dict
    justification: str
    required_controls: List[str]
    computed_at: datetime = Field(default_factory=datetime.now)
    scoring_version: str = "1.0"


class LifecycleRisk(BaseModel):
    risk_id: UUID4 = Field(default_factory=uuid.uuid4)
    system_id: UUID4
    lifecycle_phase: LifecyclePhase
    risk_category: RiskCategory
    risk_statement: str
    impact: int = Field(..., ge=1, le=5)  # 1-5
    likelihood: int = Field(..., ge=1, le=5)  # 1-5
    severity: int = Field(default=0)  # impact * likelihood
    mitigation: Optional[str] = None
    owner_role: Optional[str] = None
    evidence_links: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    def model_post_init(self, __context: any):
        self.severity = self.impact * self.likelihood


class EvidenceArtifact(BaseModel):
    name: str
    path: str
    sha256: str


class EvidenceManifest(BaseModel):
    run_id: UUID4 = Field(default_factory=uuid.uuid4)
    generated_at: datetime = Field(default_factory=datetime.now)
    team_or_user: str
    app_version: str = "1.0.0"
    inputs_hash: Optional[str] = None
    outputs_hash: Optional[str] = None
    artifacts: List[EvidenceArtifact]


# Define the three AI systems as per the scenario
ai_systems_data = [
    {
        "name": "ML-based Credit Underwriting Model",
        "description": "Automates credit assessment for loan applications.",
        "domain": "Retail Banking",
        "ai_type": AIType.ML,
        "owner_role": "Head of Lending Products",
        "deployment_mode": DeploymentMode.REAL_TIME,
        "decision_criticality": DecisionCriticality.HIGH,
        "automation_level": AutomationLevel.FULLY_AUTOMATED,
        "data_sensitivity": DataSensitivity.REGULATED_PII,
        "external_dependencies": ["Credit Bureau API", "Fraud Detection Service"]
    },
    {
        "name": "LLM-based Customer Support Assistant",
        "description": "Provides initial support to customers by answering FAQs and routing queries.",
        "domain": "Customer Service",
        "ai_type": AIType.LLM,
        "owner_role": "Head of Customer Experience",
        "deployment_mode": DeploymentMode.HUMAN_IN_LOOP,
        "decision_criticality": DecisionCriticality.MEDIUM,
        "automation_level": AutomationLevel.ADVISORY,
        "data_sensitivity": DataSensitivity.CONFIDENTIAL,
        "external_dependencies": ["Internal Knowledge Base API"]
    },
    {
        "name": "Agentic Internal Report Generator",
        "description": "Automates the generation of internal compliance and operational reports by accessing various internal data sources.",
        "domain": "Internal Operations",
        "ai_type": AIType.AGENT,
        "owner_role": "Head of Operations",
        "deployment_mode": DeploymentMode.INTERNAL_ONLY,
        "decision_criticality": DecisionCriticality.LOW,
        "automation_level": AutomationLevel.FULLY_AUTOMATED,
        "data_sensitivity": DataSensitivity.INTERNAL,
        "external_dependencies": ["Internal Reporting DB", "Document Management System API"]
    }
]

# Create SystemRecord instances and store them
system_records: List[SystemRecord] = []
for data in ai_systems_data:
    try:
        system_records.append(SystemRecord(**data))
    except ValidationError as e:
        print(f"Error validating system record: {e}")

# Display the inventory in a tabular format
inventory_df = pd.DataFrame([s.model_dump(mode='json')
                            for s in system_records])
# system_id is already a string from mode='json', last_updated needs formatting
inventory_df['last_updated'] = pd.to_datetime(inventory_df['last_updated']).dt.strftime(
    '%Y-%m-%d %H:%M:%S')

print("--- AI System Inventory ---")
# display(inventory_df)

# Store system_id mapping for easy lookup
system_id_map = {str(s.system_id): s.name for s in system_records}
# Define scoring logic and required controls
SCORING_RUBRIC = {
    DecisionCriticality.LOW: 1, DecisionCriticality.MEDIUM: 3, DecisionCriticality.HIGH: 5,
    DataSensitivity.PUBLIC: 1, DataSensitivity.INTERNAL: 2, DataSensitivity.CONFIDENTIAL: 4, DataSensitivity.REGULATED_PII: 5,
    AutomationLevel.ADVISORY: 1, AutomationLevel.HUMAN_APPROVAL: 3, AutomationLevel.FULLY_AUTOMATED: 5,
    AIType.ML: 3, AIType.LLM: 4, AIType.AGENT: 5,
    DeploymentMode.INTERNAL_ONLY: 1, DeploymentMode.BATCH: 2, DeploymentMode.HUMAN_IN_LOOP: 3, DeploymentMode.REAL_TIME: 4,
}

# Mapping external dependencies to a score


def score_external_dependencies(dependencies: List[str]) -> int:
    # 2 points if any external dependencies exist, 0 otherwise
    return 2 if dependencies else 0


TIER_THRESHOLDS = {
    "TIER_1_MIN": 22,
    "TIER_2_MIN": 15, "TIER_2_MAX": 21,
    "TIER_3_MAX": 14
}

REQUIRED_CONTROLS = {
    RiskTier.TIER_1: [
        "Independent validation",
        "Full documentation pack",
        "Robustness & security testing",
        "Bias & interpretability assessment",
        "Monitoring dashboards",
        "Formal change control & rollback",
        "Incident response plan"
    ],
    RiskTier.TIER_2: [
        "Peer validation",
        "Standard documentation",
        "Basic robustness & security tests",
        "Periodic monitoring"
    ],
    RiskTier.TIER_3: [
        "Basic documentation",
        "Basic testing",
        "Periodic review"
    ]
}


def calculate_risk_tier(system: SystemRecord) -> RiskTierResult:
    """Calculates the risk tier for an AI system based on defined scoring logic."""
    score_breakdown = {
        "decision_criticality_score": SCORING_RUBRIC[system.decision_criticality],
        "data_sensitivity_score": SCORING_RUBRIC[system.data_sensitivity],
        "automation_level_score": SCORING_RUBRIC[system.automation_level],
        "ai_type_score": SCORING_RUBRIC[system.ai_type],
        "deployment_mode_score": SCORING_RUBRIC[system.deployment_mode],
        "external_dependencies_score": score_external_dependencies(system.external_dependencies)
    }

    total_score = sum(score_breakdown.values())
    score_breakdown["total_score"] = total_score

    risk_tier: RiskTier
    if total_score >= TIER_THRESHOLDS["TIER_1_MIN"]:
        risk_tier = RiskTier.TIER_1
    elif TIER_THRESHOLDS["TIER_2_MIN"] <= total_score <= TIER_THRESHOLDS["TIER_2_MAX"]:
        risk_tier = RiskTier.TIER_2
    else:  # total_score <= TIER_THRESHOLDS["TIER_3_MAX"]
        risk_tier = RiskTier.TIER_3

    justification = (
        f"The AI system '{system.name}' scored {total_score} points, "
        f"placing it in {risk_tier.value} based on its characteristics."
    )

    return RiskTierResult(
        system_id=system.system_id,
        risk_tier=risk_tier,
        score_breakdown=score_breakdown,
        justification=justification,
        required_controls=REQUIRED_CONTROLS[risk_tier]
    )


# Apply risk tiering to all inventoried systems
risk_tier_results: List[RiskTierResult] = []
for system in system_records:
    risk_tier_results.append(calculate_risk_tier(system))

# Display risk tiering results in a tabular format
risk_tier_df = pd.DataFrame([r.model_dump(mode='json')
                            for r in risk_tier_results])
# system_id is already a string from mode='json'
risk_tier_df['system_name'] = risk_tier_df['system_id'].map(
    system_id_map)  # Add system name for clarity
risk_tier_df['computed_at'] = pd.to_datetime(risk_tier_df['computed_at']).dt.strftime(
    '%Y-%m-%d %H:%M:%S')

# Reorder columns for better readability
risk_tier_df = risk_tier_df[['system_name', 'system_id', 'risk_tier', 'score_breakdown',
                             'justification', 'required_controls', 'computed_at', 'scoring_version']]

print("\n--- AI System Risk Tiering Results ---")
# display(risk_tier_df)
# Define lifecycle risks for each AI system
lifecycle_risks: List[LifecycleRisk] = []

# ML-based Credit Underwriting Model (Tier 1)
system_id_credit_model = next(
    s.system_id for s in system_records if s.name == "ML-based Credit Underwriting Model")
lifecycle_risks.extend([
    LifecycleRisk(
        system_id=system_id_credit_model,
        lifecycle_phase=LifecyclePhase.DESIGN,
        risk_category=RiskCategory.BIAS_FAIRNESS,
        risk_statement="Bias in historical training data leads to unfair lending decisions for certain demographics.",
        impact=5, likelihood=4,
        mitigation="Implement fairness metrics, re-balance training data, and conduct adversarial testing.",
        owner_role="Data Scientist Lead"
    ),
    LifecycleRisk(
        system_id=system_id_credit_model,
        lifecycle_phase=LifecyclePhase.DEVELOPMENT,
        risk_category=RiskCategory.PERFORMANCE_ROBUSTNESS,
        risk_statement="Model overfits to training data, leading to poor generalization on new applicants.",
        impact=4, likelihood=3,
        mitigation="Utilize regularization techniques, cross-validation, and hold-out test sets.",
        owner_role="ML Engineer"
    ),
    LifecycleRisk(
        system_id=system_id_credit_model,
        lifecycle_phase=LifecyclePhase.MONITORING,
        risk_category=RiskCategory.OPERATIONAL_RELIABILITY,
        risk_statement="Data drift leads to degradation of model performance in production over time.",
        impact=5, likelihood=4,
        mitigation="Implement continuous monitoring of input data and model predictions, with alerts for drift.",
        owner_role="Model Operations"
    ),
    LifecycleRisk(
        system_id=system_id_credit_model,
        lifecycle_phase=LifecyclePhase.DEPLOYMENT,
        risk_category=RiskCategory.LEGAL_REGULATORY,
        risk_statement="Inability to explain model decisions to regulators or customers, leading to compliance issues.",
        impact=5, likelihood=3,
        mitigation="Develop XAI (Explainable AI) tools and documentation for model interpretations.",
        owner_role="Compliance Officer"
    )
])

# LLM-based Customer Support Assistant (Tier 2)
system_id_llm_assistant = next(
    s.system_id for s in system_records if s.name == "LLM-based Customer Support Assistant")
lifecycle_risks.extend([
    LifecycleRisk(
        system_id=system_id_llm_assistant,
        lifecycle_phase=LifecyclePhase.TRAINING,
        risk_category=RiskCategory.DATA_PRIVACY_SECURITY,
        risk_statement="LLM ingests sensitive customer information during RAG retrieval and potentially exposes it.",
        impact=4, likelihood=3,
        mitigation="Implement strict access controls for RAG sources and data anonymization techniques.",
        owner_role="Information Security"
    ),
    LifecycleRisk(
        system_id=system_id_llm_assistant,
        lifecycle_phase=LifecyclePhase.DEPLOYMENT,
        risk_category=RiskCategory.REPUTATIONAL,
        risk_statement="LLM generates incorrect or misleading information, damaging customer trust.",
        impact=4, likelihood=4,
        mitigation="Implement human-in-the-loop review, strict prompt engineering, and guardrails for output generation.",
        owner_role="Product Manager"
    ),
    LifecycleRisk(
        system_id=system_id_llm_assistant,
        lifecycle_phase=LifecyclePhase.MONITORING,
        risk_category=RiskCategory.OPERATIONAL_RELIABILITY,
        risk_statement="LLM experiences hallucinations or fails to respond due to unforeseen edge cases.",
        impact=3, likelihood=3,
        mitigation="Continuously log and review LLM interactions, update knowledge base and fine-tune guardrails.",
        owner_role="ML Engineer"
    )
])

# Agentic Internal Report Generator (Tier 3)
system_id_agent_report = next(
    s.system_id for s in system_records if s.name == "Agentic Internal Report Generator")
lifecycle_risks.extend([
    LifecycleRisk(
        system_id=system_id_agent_report,
        lifecycle_phase=LifecyclePhase.DESIGN,
        risk_category=RiskCategory.OPERATIONAL_RELIABILITY,
        risk_statement="Agent misunderstands query intent leading to irrelevant or incorrect reports.",
        impact=3, likelihood=2,
        mitigation="Implement clear tool descriptions and validation of generated report content.",
        owner_role="AI Architect"
    ),
    LifecycleRisk(
        system_id=system_id_agent_report,
        lifecycle_phase=LifecyclePhase.DEPLOYMENT,
        risk_category=RiskCategory.DATA_PRIVACY_SECURITY,
        risk_statement="Agent accesses unauthorized internal data sources during report generation.",
        impact=3, likelihood=2,
        mitigation="Enforce strict access control policies for agent's service account and data sources.",
        owner_role="Information Security"
    )
])

# Sort lifecycle risks by severity for easier prioritization
lifecycle_risks.sort(key=lambda x: x.severity, reverse=True)

# Display lifecycle risks in a tabular format
lifecycle_risk_df = pd.DataFrame(
    [lr.model_dump(mode='json') for lr in lifecycle_risks])
# system_id and risk_id are already strings from mode='json'
lifecycle_risk_df['system_name'] = lifecycle_risk_df['system_id'].map(
    system_id_map)
lifecycle_risk_df['created_at'] = pd.to_datetime(lifecycle_risk_df['created_at']).dt.strftime(
    '%Y-%m-%d %H:%M:%S')

# Reorder columns for better readability, putting system_name first
lifecycle_risk_df = lifecycle_risk_df[['system_name', 'risk_statement', 'lifecycle_phase', 'risk_category', 'impact',
                                       'likelihood', 'severity', 'mitigation', 'owner_role', 'evidence_links', 'created_at', 'system_id', 'risk_id']]


print("\n--- AI System Lifecycle Risk Map (Sorted by Severity) ---")
# display(lifecycle_risk_df)
# Create a directory for output artifacts
output_dir = "output_artifacts"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define file paths for artifacts
model_inventory_csv_path = os.path.join(output_dir, "model_inventory.csv")
risk_tiering_json_path = os.path.join(output_dir, "risk_tiering.json")
lifecycle_risk_map_json_path = os.path.join(
    output_dir, "lifecycle_risk_map.json")
executive_summary_md_path = os.path.join(
    output_dir, "case1_executive_summary.md")

# Function to write a DataFrame to CSV


def export_dataframe_to_csv(df: pd.DataFrame, file_path: str):
    df_copy = df.copy()  # Avoid modifying the original DF
    # Convert UUIDs and datetime objects to string for CSV export
    for col in df_copy.select_dtypes(include=['object', 'category']).columns:
        if any(isinstance(x, (uuid.UUID, datetime, Enum)) for x in df_copy[col].dropna()):
            df_copy[col] = df_copy[col].astype(str)
    # Convert lists to string representations for CSV
    for col in df_copy.select_dtypes(include=['object']).columns:
        if df_copy[col].apply(lambda x: isinstance(x, list)).any():
            df_copy[col] = df_copy[col].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else x)
    df_copy.to_csv(file_path, index=False)
    print(f"Generated: {file_path}")

# Function to write Pydantic models to JSON


def export_pydantic_list_to_json(data_list: List[BaseModel], file_path: str):
    with open(file_path, 'w') as f:
        # Use model_dump_json for Pydantic v2 or json() for Pydantic v1,
        # ensuring UUIDs and datetimes are correctly serialized.
        json_data = [item.model_dump(mode='json') for item in data_list]
        json.dump(json_data, f, indent=4)
    print(f"Generated: {file_path}")


# Generate Model Inventory CSV
export_dataframe_to_csv(inventory_df, model_inventory_csv_path)

# Generate Risk Tiering JSON
export_pydantic_list_to_json(risk_tier_results, risk_tiering_json_path)

# Generate Lifecycle Risk Map JSON
export_pydantic_list_to_json(lifecycle_risks, lifecycle_risk_map_json_path)


# Generate Executive Summary Markdown
executive_summary_content = f"""# AI Governance Audit Executive Summary - Sentinel Financial

**Date:** {datetime.now().strftime('%Y-%m-%d')}
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
The total risk score $S_{{total}}$ is calculated by summing scores from various dimensions. For instance:
*   Decision Criticality: LOW=1, MEDIUM=3, HIGH=5
*   Data Sensitivity: PUBLIC=1, INTERNAL=2, CONFIDENTIAL=4, REGULATED_PII=5
*   Automation Level: ADVISORY=1, HUMAN_APPROVAL=3, FULLY_AUTOMATED=5
*   AI Type: ML=3, LLM=4, AGENT=5
*   Deployment Mode: INTERNAL_ONLY=1, BATCH=2, HUMAN_IN_LOOP=3, REAL_TIME=4
*   External Dependencies: 0 if none, 2 if any

Risk Tiers:
*   Tier 1 (High Risk): $S_{{total}} \geq 22$
*   Tier 2 (Medium Risk): $15 \leq S_{{total}} \leq 21$
*   Tier 3 (Low Risk): $S_{{total}} \leq 14$

### Summary of Tiers:

| System Name                               | Risk Tier | Total Score | Key Justification                                 |
|-------------------------------------------|-----------|-------------|---------------------------------------------------|
| ML-based Credit Underwriting Model        | {risk_tier_df.loc[risk_tier_df['system_name'] == 'ML-based Credit Underwriting Model', 'risk_tier'].iloc[0]} | {risk_tier_df.loc[risk_tier_df['system_name'] == 'ML-based Credit Underwriting Model', 'score_breakdown'].iloc[0]['total_score']} | High criticality, PII data, fully automated real-time decisions. |
| LLM-based Customer Support Assistant      | {risk_tier_df.loc[risk_tier_df['system_name'] == 'LLM-based Customer Support Assistant', 'risk_tier'].iloc[0]} | {risk_tier_df.loc[risk_tier_df['system_name'] == 'LLM-based Customer Support Assistant', 'score_breakdown'].iloc[0]['total_score']} | Medium criticality, confidential data, human-in-loop advisory. |
| Agentic Internal Report Generator         | {risk_tier_df.loc[risk_tier_df['system_name'] == 'Agentic Internal Report Generator', 'risk_tier'].iloc[0]} | {risk_tier_df.loc[risk_tier_df['system_name'] == 'Agentic Internal Report Generator', 'score_breakdown'].iloc[0]['total_score']} | Low criticality, internal data, fully automated internal use. |

## 4. Lifecycle Risk Map
We have identified and mapped specific risks across the lifecycle phases of our AI systems. Risks are prioritized by severity, calculated as Impact $\times$ Likelihood.

### Top 3 Lifecycle Risks:

| System Name                               | Risk Statement                                                      | Severity | Lifecycle Phase |
|-------------------------------------------|---------------------------------------------------------------------|----------|-----------------|
| {lifecycle_risk_df.iloc[0]['system_name']} | {lifecycle_risk_df.iloc[0]['risk_statement']}                       | {lifecycle_risk_df.iloc[0]['severity']}   | {lifecycle_risk_df.iloc[0]['lifecycle_phase']} |
| {lifecycle_risk_df.iloc[1]['system_name']} | {lifecycle_risk_df.iloc[1]['risk_statement']}                       | {lifecycle_risk_df.iloc[1]['severity']}   | {lifecycle_risk_df.iloc[1]['lifecycle_phase']} |
| {lifecycle_risk_df.iloc[2]['system_name']} | {lifecycle_risk_df.iloc[2]['risk_statement']}                       | {lifecycle_risk_df.iloc[2]['severity']}   | {lifecycle_risk_df.iloc[2]['lifecycle_phase']} |

## 5. Conclusion
This audit package demonstrates Sentinel Financial's commitment to responsible AI governance. By systematically inventorying, risk-tiering, and mapping lifecycle risks, we ensure accountability and maintain the integrity of our AI systems. The accompanying evidence manifest provides cryptographic proof of the authenticity of these artifacts."""

with open(executive_summary_md_path, 'w') as f:
    f.write(executive_summary_content)
print(f"Generated: {executive_summary_md_path}")

print("\nAll core audit artifacts have been generated successfully.")


def calculate_sha256(file_path: str) -> str:
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string in chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# List all generated artifact files
generated_files = [
    model_inventory_csv_path,
    risk_tiering_json_path,
    lifecycle_risk_map_json_path,
    executive_summary_md_path
]

# Calculate SHA-256 for each artifact
evidence_artifacts: List[EvidenceArtifact] = []
print("\n--- Calculating SHA-256 Hashes for Artifacts ---")
for f_path in generated_files:
    file_name = os.path.basename(f_path)
    file_hash = calculate_sha256(f_path)
    evidence_artifacts.append(EvidenceArtifact(
        name=file_name, path=f_path, sha256=file_hash))
    print(f"  - {file_name}: {file_hash}")

# Create the Evidence Manifest
evidence_manifest = EvidenceManifest(
    team_or_user="Sarah (AI Program Lead)",
    artifacts=evidence_artifacts,
    run_id=uuid.uuid4(),  # Generate a new run_id for this specific manifest generation
    generated_at=datetime.now()
)

# Define path for the evidence manifest
evidence_manifest_json_path = os.path.join(
    output_dir, "evidence_manifest.json")

# Export the Evidence Manifest to JSON
with open(evidence_manifest_json_path, 'w') as f:
    json.dump(evidence_manifest.model_dump(mode='json'), f, indent=4)
print(f"\nGenerated: {evidence_manifest_json_path}")

# Display the contents of the evidence manifest for verification
print("\n--- Evidence Manifest Content ---")
manifest_df = pd.DataFrame([art.model_dump()
                           for art in evidence_manifest.artifacts])
# display(manifest_df)
# Define the name of the final ZIP archive
zip_archive_name = "audit_package_ai_governance"
# Will create zip in current directory
zip_archive_path = os.path.join(".", zip_archive_name)

# List all files to be included in the ZIP archive
files_to_zip = [
    model_inventory_csv_path,
    risk_tiering_json_path,
    lifecycle_risk_map_json_path,
    executive_summary_md_path,
    evidence_manifest_json_path
]


def create_zip_archive(files: List[str], archive_name: str, source_dir: str):
    """Creates a ZIP archive from a list of files."""
    # Ensure all files are in the specified source_dir for zipping relative paths
    base_name = os.path.basename(archive_name)
    shutil.make_archive(archive_name, 'zip', root_dir=source_dir)
    print(f"Successfully created ZIP archive: {base_name}.zip containing:")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    return f"{archive_name}.zip"


# Create the ZIP archive
final_zip_file = create_zip_archive(files_to_zip, zip_archive_path, output_dir)

print(f"\nSarah has successfully prepared the audit package: {final_zip_file}")
print("This ZIP file contains all required governance artifacts, including the evidence manifest with cryptographic hashes, ready for submission to the auditors.")

# Optional: Clean up the individual artifact files and directory after zipping, if desired
# shutil.rmtree(output_dir)
# print(f"\nCleaned up temporary directory: {output_dir}")
