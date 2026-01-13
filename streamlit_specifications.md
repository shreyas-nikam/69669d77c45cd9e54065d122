
# Streamlit Application Specification: Audit-Ready AI Governance Artifact Exporter

## 1. Application Overview

The **Audit-Ready AI Governance Artifact Exporter** Streamlit application provides a robust, interactive platform for AI Program Leads and Model Risk Analysts to manage and document AI systems in a regulatory-compliant manner (SR 11-7-style). It simulates a real-world workflow to address challenges faced by professionals like Sarah, an AI Program Lead at Sentinel Financial, who needs to prepare comprehensive, verifiable AI governance artifacts for internal audits.

**High-Level Story Flow:**

1.  **Welcome & Overview:** The application introduces Sarah to her task: preparing auditable AI governance documents for an internal audit at Sentinel Financial.
2.  **AI System Inventory:** Sarah begins by registering new AI systems or viewing an existing inventory. She can add, edit, or delete AI system records, ensuring that all necessary metadata is captured consistently.
3.  **Risk Tiering:** For each inventoried AI system, the application allows Sarah to compute a deterministic risk tier (Tier 1, 2, or 3) based on predefined scoring dimensions (criticality, data sensitivity, automation level, etc.). She can review the score breakdown and enter specific justifications for the assigned tiers.
4.  **Lifecycle Risk Mapping:** Sarah then identifies and documents specific risks that may arise throughout an AI system's lifecycle (from design to decommissioning). She assigns impact and likelihood scores, allowing the application to calculate severity, and provides mitigation strategies. Risks are displayed, sorted by severity for prioritization.
5.  **Exports & Evidence:** Finally, Sarah generates a suite of audit-ready artifacts, including a model inventory (CSV), risk tiering results (JSON), lifecycle risk map (JSON), and an executive summary (Markdown). Crucially, the application computes SHA-256 cryptographic hashes for all generated documents, compiling them into an `evidence_manifest.json` to ensure integrity and traceability. All artifacts are then packaged into a single, downloadable ZIP archive for easy submission to auditors.

This workflow ensures that Sarah can confidently demonstrate Sentinel Financial's commitment to responsible AI governance, providing structured, verifiable, and tamper-proof documentation.

## 2. Code Requirements

### Import Statement

```python
import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime
from io import BytesIO
from pydantic import ValidationError, BaseModel # BaseModel needed for type hinting for export_pydantic_list_to_json

# Import all necessary components from source.py
from source import (
    AIType, DeploymentMode, DataSensitivity, DecisionCriticality, AutomationLevel, RiskTier, LifecyclePhase, RiskCategory,
    SystemRecord, RiskTierResult, LifecycleRisk, EvidenceArtifact, EvidenceManifest,
    SCORING_RUBRIC, TIER_THRESHOLDS, REQUIRED_CONTROLS,
    score_external_dependencies, calculate_risk_tier, calculate_sha256,
    export_dataframe_to_csv, export_pydantic_list_to_json, create_zip_archive,
    ai_systems_data, # Initial data for SystemRecord
    lifecycle_risks as initial_lifecycle_risks # Initial list of LifecycleRisk objects
)
```

### `st.session_state` Design

`st.session_state` is used to maintain the application's state across user interactions and page changes.

**Initialization (on first run):**

The following `st.session_state` keys will be initialized within a `if 'key' not in st.session_state:` block at the top of `app.py`.

*   `st.session_state.current_page`: Tracks the active page.
    *   **Initial Value**: `'Home'`
*   `st.session_state.system_records`: Stores a `List[SystemRecord]` of all registered AI systems.
    *   **Initial Value**: Populated by converting `ai_systems_data` (from `source.py`) into `SystemRecord` objects.
*   `st.session_state.risk_tier_results`: Stores a `List[RiskTierResult]` of computed risk tiers.
    *   **Initial Value**: `[]` (empty list, as tiers are computed on demand).
*   `st.session_state.lifecycle_risks`: Stores a `List[LifecycleRisk]` of identified lifecycle risks.
    *   **Initial Value**: Populated with `initial_lifecycle_risks` (from `source.py`).
*   `st.session_state.output_dir`: Path for saving generated artifacts locally.
    *   **Initial Value**: `"output_artifacts"`
*   `st.session_state.generated_files`: A `List[str]` of paths to all artifacts generated for the current session.
    *   **Initial Value**: `[]`
*   `st.session_state.evidence_manifest`: Stores the `EvidenceManifest` object.
    *   **Initial Value**: `None`
*   `st.session_state.system_id_map`: A `Dict[str, str]` mapping `system_id` (UUID as string) to system name for display in dropdowns.
    *   **Initial Value**: Dynamically generated from `st.session_state.system_records`.
*   `st.session_state.selected_system_id`: Stores the `system_id` of the AI system currently selected for viewing/editing or for adding associated risks.
    *   **Initial Value**: `None`
*   `st.session_state.df_inventory`: `pd.DataFrame` representation of `st.session_state.system_records` for display.
    *   **Initial Value**: Populated by calling an internal `_update_dataframes()` helper function after initializing `system_records`.
*   `st.session_state.df_risk_tier`: `pd.DataFrame` representation of `st.session_state.risk_tier_results` for display.
    *   **Initial Value**: Populated by calling an internal `_update_dataframes()` helper function.
*   `st.session_state.df_lifecycle_risk`: `pd.DataFrame` representation of `st.session_state.lifecycle_risks` for display.
    *   **Initial Value**: Populated by calling an internal `_update_dataframes()` helper function.
*   `st.session_state.executive_summary_content`: Stores the markdown content for the executive summary.
    *   **Initial Value**: `""`

**Update and Read across Interactions/Pages:**

*   **`_update_dataframes()` Helper Function**: This internal function will be called whenever `st.session_state.system_records`, `st.session_state.risk_tier_results`, or `st.session_state.lifecycle_risks` are modified. It updates `st.session_state.system_id_map`, `st.session_state.df_inventory`, `st.session_state.df_risk_tier`, and `st.session_state.df_lifecycle_risk` to ensure all displayed DataFrames and dropdowns reflect the latest data.

### Application Structure and Flow

The application will use a sidebar dropdown to simulate a multi-page experience.

```python
# --- Helper Functions for Session State Management and DataFrames (defined internally in app.py) ---
def _initialize_system_records():
    # Logic to convert ai_systems_data (list of dicts from source.py) to SystemRecord objects
    pass
def _initialize_lifecycle_risks():
    # Logic to copy initial_lifecycle_risks (list of Pydantic objects from source.py)
    pass
def _update_dataframes():
    # Logic to update system_id_map, df_inventory, df_risk_tier, df_lifecycle_risk
    pass
# --- End Helper Functions ---

# --- Session State Initialization ---
# (as described above)
# Call _update_dataframes() once after initial session state setup
# --- End Session State Initialization ---

# --- Sidebar Navigation ---
st.sidebar.title("AI Governance Workflow")
st.session_state.current_page = st.sidebar.selectbox(
    "Select a Page",
    ['Home', 'AI System Inventory', 'Risk Tiering', 'Lifecycle Risk Mapping', 'Exports & Evidence'],
    key='page_selector'
)
# --- End Sidebar Navigation ---

# --- Main Content Area (Conditional Rendering) ---
if st.session_state.current_page == 'Home':
    st.title("Audit-Ready AI Governance Artifact Exporter")
    st.markdown(f"## Case Study: Ensuring AI Accountability at Sentinel Financial")
    st.markdown(f"**Persona:** Sarah, an AI Program Lead at Sentinel Financial.")
    st.markdown(f"**Organization:** Sentinel Financial, a mid-size financial institution that leverages AI across various operations, from credit assessment to customer support.")
    st.markdown(f"**Scenario:** Sarah is facing an upcoming internal audit of Sentinel Financial's AI governance framework. She needs to demonstrate that all AI systems are properly inventoried, risk-tiered, and that potential lifecycle risks are identified and managed. The audit requires verifiable evidence of these governance artifacts, meaning the integrity and traceability of the documents must be guaranteed. Sarah's task is to compile all necessary information into a structured, tamper-proof package for the auditors, ensuring full compliance and accountability. This application simulates Sarah's real-world workflow to achieve this goal.")
    st.markdown(f"---")
    st.markdown(f"## Student Objectives")
    st.markdown(f"- Build an enterprise AI model inventory")
    st.markdown(f"- Assign risk tiers (Tier 1-3) using SR 11-7-style reasoning")
    st.markdown(f"- Define minimum required controls per risk tier")
    st.markdown(f"- Identify lifecycle risks across design, deployment, and operations")
    st.markdown(f"- Produce audit-ready artifacts")

elif st.session_state.current_page == 'AI System Inventory':
    st.title("1. AI System Inventory")
    st.markdown(f"To begin building the auditable package, my first task is to accurately inventory all AI systems within Sentinel Financial. This involves defining a structured format (schema) for each AI system's record and then populating this inventory with details of the three key AI systems currently in production or under development. A well-defined inventory is the cornerstone of robust AI governance.")
    st.markdown(f"The `SystemRecord` schema ensures that each AI system is consistently documented with essential metadata like its type, criticality, data sensitivity, and deployment mode. This structured approach helps in standardized reporting and downstream risk assessment.")
    st.markdown(r"$$ \text{{AI System Inventory}} = \{{ \text{{SystemRecord}}_1, \text{{SystemRecord}}_2, \ldots, \text{{SystemRecord}}_N \}} $$")
    st.markdown(r"where $\text{{SystemRecord}}_N$ represents a single AI system's metadata.")
    st.markdown(f"---")

    st.subheader("Current AI System Inventory")
    if not st.session_state.df_inventory.empty:
        st.dataframe(st.session_state.df_inventory, use_container_width=True)
    else:
        st.info("No AI systems registered yet. Use the form below to add one.")

    st.subheader("Add New AI System")
    with st.form("add_system_form", clear_on_submit=True):
        name = st.text_input("Name", help="e.g., ML-based Credit Underwriting Model")
        description = st.text_area("Description", help="e.g., Automates credit assessment for loan applications.")
        domain = st.text_input("Domain", help="e.g., Retail Banking")
        ai_type = st.selectbox("AI Type", options=[e.value for e in AIType])
        owner_role = st.text_input("Owner Role", help="e.g., Head of Lending Products")
        deployment_mode = st.selectbox("Deployment Mode", options=[e.value for e in DeploymentMode])
        decision_criticality = st.selectbox("Decision Criticality", options=[e.value for e in DecisionCriticality])
        automation_level = st.selectbox("Automation Level", options=[e.value for e in AutomationLevel])
        data_sensitivity = st.selectbox("Data Sensitivity", options=[e.value for e in DataSensitivity])
        external_dependencies = st.multiselect("External Dependencies",
                                               options=["Credit Bureau API", "Fraud Detection Service", "Internal Knowledge Base API", "Internal Reporting DB", "Document Management System API", "Third-Party Data Feed", "Cloud AI Service"])

        submitted = st.form_submit_button("Add AI System")
        if submitted:
            try:
                new_system = SystemRecord(
                    name=name, description=description, domain=domain, ai_type=AIType(ai_type),
                    owner_role=owner_role, deployment_mode=DeploymentMode(deployment_mode),
                    decision_criticality=DecisionCriticality(decision_criticality),
                    automation_level=AutomationLevel(automation_level),
                    data_sensitivity=DataSensitivity(data_sensitivity),
                    external_dependencies=external_dependencies
                )
                st.session_state.system_records.append(new_system)
                _update_dataframes()
                st.success(f"AI System '{name}' added successfully!")
            except ValidationError as e:
                st.error(f"Validation Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    st.subheader("Edit or Delete AI System")
    if st.session_state.system_records:
        system_options = {str(s.system_id): s.name for s in st.session_state.system_records}
        st.session_state.selected_system_id = st.selectbox(
            "Select AI System to Edit/Delete",
            options=list(system_options.keys()),
            format_func=lambda x: system_options[x]
        )

        if st.session_state.selected_system_id:
            selected_system = next((s for s in st.session_state.system_records if str(s.system_id) == st.session_state.selected_system_id), None)

            if selected_system:
                with st.form("edit_system_form"):
                    st.markdown(f"Editing system: **{selected_system.name}**")
                    edit_name = st.text_input("Name", value=selected_system.name)
                    edit_description = st.text_area("Description", value=selected_system.description)
                    edit_domain = st.text_input("Domain", value=selected_system.domain)
                    edit_ai_type = st.selectbox("AI Type", options=[e.value for e in AIType], index=[e.value for e in AIType].index(selected_system.ai_type.value))
                    edit_owner_role = st.text_input("Owner Role", value=selected_system.owner_role)
                    edit_deployment_mode = st.selectbox("Deployment Mode", options=[e.value for e in DeploymentMode], index=[e.value for e in DeploymentMode].index(selected_system.deployment_mode.value))
                    edit_decision_criticality = st.selectbox("Decision Criticality", options=[e.value for e in DecisionCriticality], index=[e.value for e in DecisionCriticality].index(selected_system.decision_criticality.value))
                    edit_automation_level = st.selectbox("Automation Level", options=[e.value for e in AutomationLevel], index=[e.value for e in AutomationLevel].index(selected_system.automation_level.value))
                    edit_data_sensitivity = st.selectbox("Data Sensitivity", options=[e.value for e in DataSensitivity], index=[e.value for e in DataSensitivity].index(selected_system.data_sensitivity.value))
                    edit_external_dependencies = st.multiselect("External Dependencies",
                                                                 options=["Credit Bureau API", "Fraud Detection Service", "Internal Knowledge Base API", "Internal Reporting DB", "Document Management System API", "Third-Party Data Feed", "Cloud AI Service"],
                                                                 default=selected_system.external_dependencies)

                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("Update AI System")
                    with col2:
                        delete_submitted = st.form_submit_button("Delete AI System")

                    if update_submitted:
                        try:
                            selected_system.name = edit_name
                            selected_system.description = edit_description
                            selected_system.domain = edit_domain
                            selected_system.ai_type = AIType(edit_ai_type)
                            selected_system.owner_role = edit_owner_role
                            selected_system.deployment_mode = DeploymentMode(edit_deployment_mode)
                            selected_system.decision_criticality = DecisionCriticality(edit_decision_criticality)
                            selected_system.automation_level = AutomationLevel(edit_automation_level)
                            selected_system.data_sensitivity = DataSensitivity(edit_data_sensitivity)
                            selected_system.external_dependencies = edit_external_dependencies
                            selected_system.last_updated = datetime.now() # Update timestamp
                            _update_dataframes()
                            st.success(f"AI System '{edit_name}' updated successfully!")
                        except ValidationError as e:
                            st.error(f"Validation Error: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
                    if delete_submitted:
                        st.session_state.system_records = [s for s in st.session_state.system_records if str(s.system_id) != st.session_state.selected_system_id]
                        # Also delete associated risk tiers and lifecycle risks
                        st.session_state.risk_tier_results = [r for r in st.session_state.risk_tier_results if str(r.system_id) != st.session_state.selected_system_id]
                        st.session_state.lifecycle_risks = [lr for lr in st.session_state.lifecycle_risks if str(lr.system_id) != st.session_state.selected_system_id]
                        _update_dataframes()
                        st.success(f"AI System '{selected_system.name}' and its associated risks deleted successfully!")
                        st.session_state.selected_system_id = None # Clear selection

            else:
                st.warning("Please select an AI System.")
    else:
        st.info("No AI systems to edit or delete.")

elif st.session_state.current_page == 'Risk Tiering':
    st.title("2. Implementing Deterministic Risk Tiering")
    st.markdown(f"With the AI systems inventoried, my next critical task is to assign a risk tier to each. This is central to Sentinel Financial's SR 11-7-style model risk management framework. I need a deterministic scoring logic that consistently assigns a risk tier (Tier 1, Tier 2, or Tier 3) based on defined dimensions, ensuring transparency and reproducibility for the auditors. This process directly addresses the `learningOutcomes` requirement to implement deterministic risk tiering.")
    st.markdown(f"The risk tiering logic will sum scores from various attributes, including decision criticality, data sensitivity, automation level, AI type, deployment mode, and external dependencies. The total score $S_{{total}}$ for each AI system is calculated as:")
    st.markdown(r"$$ S_{{total}} = S_{{criticality}} + S_{{sensitivity}} + S_{{automation}} + S_{{type}} + S_{{deployment}} + S_{{dependencies}} $$")
    st.markdown(r"where $S_{{criticality}}$ is the score for `DecisionCriticality`.")
    st.markdown(r"where $S_{{sensitivity}}$ is the score for `DataSensitivity`.")
    st.markdown(r"where $S_{{automation}}$ is the score for `AutomationLevel`.")
    st.markdown(r"where $S_{{type}}$ is the score for `AIType`.")
    st.markdown(r"where $S_{{deployment}}$ is the score for `DeploymentMode`.")
    st.markdown(r"where $S_{{dependencies}}$ is the score for `ExternalDependencies`.")
    st.markdown(f"The risk tiers are then assigned based on the following thresholds:")
    st.markdown(r"$$ \text{{Tier 1 (High Risk)}}: S_{{total}} \geq 22 $$")
    st.markdown(r"$$ \text{{Tier 2 (Medium Risk)}}: 15 \leq S_{{total}} \leq 21 $$")
    st.markdown(r"$$ \text{{Tier 3 (Low Risk)}}: S_{{total}} \leq 14 $$")
    st.markdown(f"Along with the tier, a set of minimum required controls is automatically generated, aligning with Sentinel Financial's governance policies.")
    st.markdown(f"---")

    st.subheader("Compute Risk Tiers")
    if st.button("Compute Risk Tiers for All Systems"):
        if st.session_state.system_records:
            st.session_state.risk_tier_results = [] # Clear previous results
            for system in st.session_state.system_records:
                tier_result = calculate_risk_tier(system) # Function from source.py
                st.session_state.risk_tier_results.append(tier_result)
            _update_dataframes()
            st.success("Risk tiers computed successfully!")
        else:
            st.warning("No AI systems registered to compute risk tiers.")

    st.subheader("AI System Risk Tiering Results")
    if not st.session_state.df_risk_tier.empty:
        st.dataframe(st.session_state.df_risk_tier, use_container_width=True)
    else:
        st.info("No risk tier results available. Click 'Compute Risk Tiers' above.")

    st.subheader("Update Risk Tier Justification")
    if st.session_state.risk_tier_results:
        tier_system_options = {str(r.system_id): st.session_state.system_id_map.get(str(r.system_id), "Unknown System") for r in st.session_state.risk_tier_results}
        selected_risk_system_id = st.selectbox(
            "Select AI System to Update Justification",
            options=list(tier_system_options.keys()),
            format_func=lambda x: tier_system_options[x],
            key='select_justification_system'
        )
        if selected_risk_system_id:
            selected_tier_result = next((r for r in st.session_state.risk_tier_results if str(r.system_id) == selected_risk_system_id), None)
            if selected_tier_result:
                current_justification = selected_tier_result.justification
                new_justification = st.text_area("Justification", value=current_justification, height=150)
                if st.button("Save Justification"):
                    selected_tier_result.justification = new_justification
                    _update_dataframes()
                    st.success("Justification updated successfully!")
            else:
                st.warning("Risk tier result not found for selected system.")
    else:
        st.info("No risk tiers available to update justification.")

elif st.session_state.current_page == 'Lifecycle Risk Mapping':
    st.title("3. Mapping AI System Lifecycle Risks")
    st.markdown(f"Beyond a general risk tier, Sarah needs to identify specific risks that can emerge throughout an AI system's lifecycle, from design to decommissioning. This detailed lifecycle risk mapping helps Sentinel Financial proactive address vulnerabilities and demonstrate a comprehensive risk management strategy to auditors. It addresses the `learningOutcomes` requirement to define and manage lifecycle risks.")
    st.markdown(f"The severity of each risk is a critical metric for prioritization and is calculated as the product of its `impact` and `likelihood`.")
    st.markdown(r"$$ \text{{Severity}} = \text{{Impact}} \times \text{{Likelihood}} $$")
    st.markdown(r"where $\text{{Impact}}$ is the consequence of the risk, scored from 1 to 5.")
    st.markdown(r"where $\text{{Likelihood}}$ is the probability of the risk occurring, scored from 1 to 5.")
    st.markdown(f"---")

    st.subheader("Current Lifecycle Risk Map (Sorted by Severity)")
    if not st.session_state.df_lifecycle_risk.empty:
        st.dataframe(st.session_state.df_lifecycle_risk, use_container_width=True)
    else:
        st.info("No lifecycle risks defined yet. Use the form below to add one.")

    st.subheader("Add New Lifecycle Risk")
    if st.session_state.system_records:
        with st.form("add_lifecycle_risk_form", clear_on_submit=True):
            system_id_options = {str(s.system_id): s.name for s in st.session_state.system_records}
            selected_system_for_risk = st.selectbox(
                "Select AI System",
                options=list(system_id_options.keys()),
                format_func=lambda x: system_id_options[x]
            )
            lifecycle_phase = st.selectbox("Lifecycle Phase", options=[e.value for e in LifecyclePhase])
            risk_category = st.selectbox("Risk Category", options=[e.value for e in RiskCategory])
            risk_statement = st.text_area("Risk Statement", help="e.g., Bias in historical training data leads to unfair lending decisions.")
            impact = st.slider("Impact (1-5)", 1, 5, 3)
            likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
            mitigation = st.text_area("Mitigation", help="e.g., Implement fairness metrics, re-balance training data.")
            owner_role = st.text_input("Owner Role", help="e.g., Data Scientist Lead")
            evidence_links = st.multiselect("Evidence Links (URLs)",
                                            options=["http://example.com/doc1", "http://example.com/doc2"])

            submitted = st.form_submit_button("Add Lifecycle Risk")
            if submitted:
                try:
                    new_risk = LifecycleRisk(
                        system_id=uuid.UUID(selected_system_for_risk),
                        lifecycle_phase=LifecyclePhase(lifecycle_phase),
                        risk_category=RiskCategory(risk_category),
                        risk_statement=risk_statement,
                        impact=impact,
                        likelihood=likelihood,
                        mitigation=mitigation,
                        owner_role=owner_role,
                        evidence_links=evidence_links
                    )
                    st.session_state.lifecycle_risks.append(new_risk)
                    _update_dataframes()
                    st.success("Lifecycle risk added successfully!")
                except ValidationError as e:
                    st.error(f"Validation Error: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
    else:
        st.info("Please add AI systems in the 'AI System Inventory' page before adding lifecycle risks.")

elif st.session_state.current_page == 'Exports & Evidence':
    st.title("4. Generating Core Audit Artifacts")
    st.markdown(f"Now that the AI inventory, risk tiers, and lifecycle risks are established, it's time to generate the core audit artifacts. These files are the primary deliverables for the auditors and must be well-structured and complete. I will create `model_inventory.csv`, `risk_tiering.json`, `lifecycle_risk_map.json`, and an executive summary in markdown format, `case1_executive_summary.md`.")
    st.markdown(f"These artifacts directly align with the `Required Deliverables` and `Export Formats` mentioned in the provided context, ensuring that Sarah has all the necessary documentation for the audit.")
    st.markdown(f"---")

    st.subheader("Generate Core Artifacts")
    if not os.path.exists(st.session_state.output_dir):
        os.makedirs(st.session_state.output_dir, exist_ok=True)

    if st.button("Generate All Core Artifacts"):
        st.session_state.generated_files = [] # Clear previous list

        # 1. model_inventory.csv
        model_inventory_csv_path = os.path.join(st.session_state.output_dir, "model_inventory.csv")
        export_dataframe_to_csv(st.session_state.df_inventory, model_inventory_csv_path) # Function from source.py
        st.session_state.generated_files.append(model_inventory_csv_path)
        st.success(f"Generated: `{os.path.basename(model_inventory_csv_path)}`")

        # 2. risk_tiering.json
        risk_tiering_json_path = os.path.join(st.session_state.output_dir, "risk_tiering.json")
        export_pydantic_list_to_json(st.session_state.risk_tier_results, risk_tiering_json_path) # Function from source.py
        st.session_state.generated_files.append(risk_tiering_json_path)
        st.success(f"Generated: `{os.path.basename(risk_tiering_json_path)}`")

        # 3. lifecycle_risk_map.json
        lifecycle_risk_map_json_path = os.path.join(st.session_state.output_dir, "lifecycle_risk_map.json")
        export_pydantic_list_to_json(st.session_state.lifecycle_risks, lifecycle_risk_map_json_path) # Function from source.py
        st.session_state.generated_files.append(lifecycle_risk_map_json_path)
        st.success(f"Generated: `{os.path.basename(lifecycle_risk_map_json_path)}`")

        # 4. case1_executive_summary.md
        executive_summary_md_path = os.path.join(st.session_state.output_dir, "case1_executive_summary.md")
        # Reconstruct markdown content based on current data in session state
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
"""
        # Dynamically add rows based on current risk_tier_df in session_state
        if not st.session_state.df_risk_tier.empty:
            executive_summary_content += """
| System Name                               | Risk Tier | Total Score | Key Justification                                 |
|-------------------------------------------|-----------|-------------|---------------------------------------------------|
"""
            for index, row in st.session_state.df_risk_tier.iterrows():
                system_name = row['system_name']
                risk_tier = row['risk_tier']
                total_score = row['score_breakdown']['total_score']
                justification = row['justification']
                executive_summary_content += f"| {system_name:<41} | {risk_tier:<9} | {total_score:<11} | {justification:<49} |\n"
        else:
            executive_summary_content += "\nNo risk tier data available for summary.\n"

        executive_summary_content += f"""
## 4. Lifecycle Risk Map
We have identified and mapped specific risks across the lifecycle phases of our AI systems. Risks are prioritized by severity, calculated as Impact $\times$ Likelihood.

### Top 3 Lifecycle Risks:
"""
        # Dynamically add top 3 lifecycle risks
        if not st.session_state.df_lifecycle_risk.empty:
            executive_summary_content += """
| System Name                               | Risk Statement                                                      | Severity | Lifecycle Phase |
|-------------------------------------------|---------------------------------------------------------------------|----------|-----------------|
"""
            for index, row in st.session_state.df_lifecycle_risk.head(3).iterrows():
                executive_summary_content += f"| {row['system_name']:<41} | {row['risk_statement']:<67} | {row['severity']:<8} | {row['lifecycle_phase']:<15} |\n"
        else:
            executive_summary_content += "\nNo lifecycle risk data available for summary.\n"

        executive_summary_content += f"""
## 5. Conclusion
This audit package demonstrates Sentinel Financial's commitment to responsible AI governance. By systematically inventorying, risk-tiering, and mapping lifecycle risks, we ensure accountability and maintain the integrity of our AI systems. The accompanying evidence manifest provides cryptographic proof of the authenticity of these artifacts."""

        with open(executive_summary_md_path, 'w') as f:
            f.write(executive_summary_content)
        st.session_state.generated_files.append(executive_summary_md_path)
        st.session_state.executive_summary_content = executive_summary_content # Store for potential display
        st.success(f"Generated: `{os.path.basename(executive_summary_md_path)}`")

    st.markdown(f"---")
    st.title("5. Creating the Evidence Manifest for Integrity")
    st.markdown(f"A crucial aspect of auditability is ensuring the integrity and immutability of the submitted documents. As an AI Program Lead, Sarah must provide cryptographic proof that the artifacts have not been tampered with. This involves generating SHA-256 hashes for each file and compiling them into an `evidence_manifest.json`. This directly addresses the `learningOutcomes` and `Deliverable Summary` requirements for cryptographic hashing.")
    st.markdown(f"The SHA-256 algorithm produces a fixed-size hash value ($H$) for any input data ($M$). A small change in the input data will result in a completely different hash value, making it ideal for detecting tampering.")
    st.markdown(r"$$ H = \text{{SHA256}}(M) $$")
    st.markdown(r"where $H$ is the SHA-256 hash value.")
    st.markdown(r"where $M$ is the input data (the artifact file content).")
    st.markdown(f"---")

    st.subheader("Generate Evidence Manifest")
    if st.button("Generate Evidence Manifest"):
        if st.session_state.generated_files:
            evidence_artifacts_list = []
            for f_path in st.session_state.generated_files:
                file_name = os.path.basename(f_path)
                file_hash = calculate_sha256(f_path) # Function from source.py
                evidence_artifacts_list.append(EvidenceArtifact(name=file_name, path=f_path, sha256=file_hash))

            st.session_state.evidence_manifest = EvidenceManifest(
                team_or_user="Sarah (AI Program Lead)",
                artifacts=evidence_artifacts_list,
                run_id=uuid.uuid4(), # Ensure uuid is imported (from pydantic in source.py or directly)
                generated_at=datetime.now()
            )

            evidence_manifest_json_path = os.path.join(st.session_state.output_dir, "evidence_manifest.json")
            with open(evidence_manifest_json_path, 'w') as f:
                json.dump(st.session_state.evidence_manifest.model_dump(mode='json'), f, indent=4)

            st.session_state.generated_files.append(evidence_manifest_json_path) # Add manifest to files list
            st.success(f"Generated: `{os.path.basename(evidence_manifest_json_path)}`")
        else:
            st.warning("Please generate core artifacts first.")

    st.subheader("Evidence Manifest Content")
    if st.session_state.evidence_manifest:
        manifest_df = pd.DataFrame([art.model_dump() for art in st.session_state.evidence_manifest.artifacts])
        st.dataframe(manifest_df, use_container_width=True)
    else:
        st.info("No evidence manifest generated yet. Click 'Generate Evidence Manifest'.")

    st.markdown(f"---")
    st.title("6. Packaging Audit-Ready Deliverables")
    st.markdown(f"The final step for Sarah is to package all the generated artifacts, including the `evidence_manifest.json`, into a single, downloadable ZIP archive. This simplifies submission to the auditors, ensuring that all required files are bundled together and easy to manage. This directly fulfills the `Deliverable Summary` requirement.")
    st.markdown(f"---")

    st.subheader("Download Audit Package")
    if st.session_state.generated_files:
        if st.button("Create and Download ZIP Archive"):
            zip_archive_name_base = "audit_package_ai_governance"
            zip_file_path = create_zip_archive(st.session_state.generated_files, zip_archive_name_base, st.session_state.output_dir) # Function from source.py

            # Read the created zip file into a BytesIO object for download
            if os.path.exists(zip_file_path):
                with open(zip_file_path, "rb") as f:
                    zip_bytes = BytesIO(f.read())
                st.download_button(
                    label="Download Audit Package ZIP",
                    data=zip_bytes.getvalue(),
                    file_name=os.path.basename(zip_file_path),
                    mime="application/zip"
                )
                st.success(f"Audit package '{os.path.basename(zip_file_path)}' created and ready for download!")
            else:
                st.error("Failed to create ZIP archive.")
    else:
        st.warning("Please generate artifacts and evidence manifest before creating the ZIP archive.")

# --- End Main Content Area ---
```
