import streamlit as st
import pandas as pd
import json
import os
import shutil
import uuid
from datetime import datetime
from io import BytesIO
from pydantic import ValidationError
from source import *

# --- Page Configuration ---
st.set_page_config(page_title="QuLab: Enterprise AI Lifecycle & Model Risk Classification", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Enterprise AI Lifecycle & Model Risk Classification")
st.divider()

# --- Helper Functions for Session State Management ---
def _update_dataframes():
    """Updates pandas DataFrames and ID maps based on current session state lists."""
    # Inventory DataFrame
    if st.session_state.system_records:
        data = [s.model_dump(mode='json') for s in st.session_state.system_records]
        st.session_state.df_inventory = pd.DataFrame(data)
        # Create ID map for dropdowns
        st.session_state.system_id_map = {str(s.system_id): s.name for s in st.session_state.system_records}
    else:
        st.session_state.df_inventory = pd.DataFrame()
        st.session_state.system_id_map = {}

    # Risk Tier DataFrame
    if st.session_state.risk_tier_results:
        # Flattening slightly for better display if needed, but model_dump is usually sufficient
        data = []
        for r in st.session_state.risk_tier_results:
            row = r.model_dump(mode='json')
            # Enrich with system name for display
            system_name = st.session_state.system_id_map.get(str(r.system_id), "Unknown")
            row['system_name'] = system_name
            data.append(row)
        st.session_state.df_risk_tier = pd.DataFrame(data)
    else:
        st.session_state.df_risk_tier = pd.DataFrame()

    # Lifecycle Risk DataFrame
    if st.session_state.lifecycle_risks:
        data = []
        for lr in st.session_state.lifecycle_risks:
            row = lr.model_dump(mode='json')
            # Enrich with system name
            system_name = st.session_state.system_id_map.get(str(lr.system_id), "Unknown")
            row['system_name'] = system_name
            # Calculate severity for sorting/display (Impact * Likelihood)
            row['severity'] = row.get('impact', 0) * row.get('likelihood', 0)
            data.append(row)
        
        df = pd.DataFrame(data)
        if not df.empty:
            # Sort by severity descending
            df = df.sort_values(by='severity', ascending=False)
        st.session_state.df_lifecycle_risk = df
    else:
        st.session_state.df_lifecycle_risk = pd.DataFrame()

# --- Session State Initialization ---
if 'system_records' not in st.session_state:
    # Initialize System Records from source data
    # Assuming ai_systems_data is a list of dictionaries suitable for SystemRecord
    try:
        st.session_state.system_records = [SystemRecord(**data) for data in ai_systems_data]
    except Exception as e:
        st.error(f"Error initializing system records: {e}")
        st.session_state.system_records = []

if 'risk_tier_results' not in st.session_state:
    st.session_state.risk_tier_results = []

if 'lifecycle_risks' not in st.session_state:
    # Initialize Lifecycle Risks from source data
    # Assuming initial_lifecycle_risks is a list of LifecycleRisk objects or dicts
    try:
        # Check if they are already objects or need conversion
        if initial_lifecycle_risks and isinstance(initial_lifecycle_risks[0], dict):
             st.session_state.lifecycle_risks = [LifecycleRisk(**data) for data in initial_lifecycle_risks]
        else:
             st.session_state.lifecycle_risks = initial_lifecycle_risks
    except Exception as e:
        st.error(f"Error initializing lifecycle risks: {e}")
        st.session_state.lifecycle_risks = []

if 'output_dir' not in st.session_state:
    st.session_state.output_dir = "output_artifacts"

if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []

if 'evidence_manifest' not in st.session_state:
    st.session_state.evidence_manifest = None

if 'system_id_map' not in st.session_state:
    st.session_state.system_id_map = {}

if 'selected_system_id' not in st.session_state:
    st.session_state.selected_system_id = None

if 'df_inventory' not in st.session_state:
    st.session_state.df_inventory = pd.DataFrame()

if 'df_risk_tier' not in st.session_state:
    st.session_state.df_risk_tier = pd.DataFrame()

if 'df_lifecycle_risk' not in st.session_state:
    st.session_state.df_lifecycle_risk = pd.DataFrame()

if 'executive_summary_content' not in st.session_state:
    st.session_state.executive_summary_content = ""

# Initial DataFrame Update
if 'initialized' not in st.session_state:
    _update_dataframes()
    st.session_state.initialized = True

# --- Sidebar Navigation ---
st.sidebar.title("AI Governance Workflow")
st.session_state.current_page = st.sidebar.selectbox(
    "Select a Page",
    ['Home', 'AI System Inventory', 'Risk Tiering', 'Lifecycle Risk Mapping', 'Exports & Evidence'],
    key='page_selector'
)

# --- Main Content Area ---

if st.session_state.current_page == 'Home':
    st.markdown(f"### Case Study: Ensuring AI Accountability at Sentinel Financial")
    st.markdown(f"**Persona:** Sarah, an AI Program Lead at Sentinel Financial.")
    st.markdown(f"**Organization:** Sentinel Financial, a mid-size financial institution that leverages AI across various operations, from credit assessment to customer support.")
    st.markdown(f"**Scenario:** Sarah is facing an upcoming internal audit of Sentinel Financial's AI governance framework. She needs to demonstrate that all AI systems are properly inventoried, risk-tiered, and that potential lifecycle risks are identified and managed. The audit requires verifiable evidence of these governance artifacts, meaning the integrity and traceability of the documents must be guaranteed. Sarah's task is to compile all necessary information into a structured, tamper-proof package for the auditors, ensuring full compliance and accountability. This application simulates Sarah's real-world workflow to achieve this goal.")
    st.markdown(f"---")
    st.markdown(f"### Student Objectives")
    st.markdown(f"- Build an enterprise AI model inventory")
    st.markdown(f"- Assign risk tiers (Tier 1-3) using SR 11-7-style reasoning")
    st.markdown(f"- Define minimum required controls per risk tier")
    st.markdown(f"- Identify lifecycle risks across design, deployment, and operations")
    st.markdown(f"- Produce audit-ready artifacts")

elif st.session_state.current_page == 'AI System Inventory':
    st.title("1. AI System Inventory")
    st.markdown(f"To begin building the auditable package, my first task is to accurately inventory all AI systems within Sentinel Financial. This involves defining a structured format (schema) for each AI system's record and then populating this inventory with details of the three key AI systems currently in production or under development. A well-defined inventory is the cornerstone of robust AI governance.")
    st.markdown(f"The `SystemRecord` schema ensures that each AI system is consistently documented with essential metadata like its type, criticality, data sensitivity, and deployment mode. This structured approach helps in standardized reporting and downstream risk assessment.")
    st.markdown(r"$$ \text{AI System Inventory} = \{ \text{SystemRecord}_1, \text{SystemRecord}_2, \ldots, \text{SystemRecord}_N \} $$")
    st.markdown(r"where $\text{SystemRecord}_N$ represents a single AI system's metadata.")
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
                st.rerun()
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
                    
                    # Helper to get index safely
                    def get_index(enum_cls, val):
                        vals = [e.value for e in enum_cls]
                        try:
                            return vals.index(val)
                        except ValueError:
                            return 0

                    edit_ai_type = st.selectbox("AI Type", options=[e.value for e in AIType], index=get_index(AIType, selected_system.ai_type.value))
                    edit_owner_role = st.text_input("Owner Role", value=selected_system.owner_role)
                    edit_deployment_mode = st.selectbox("Deployment Mode", options=[e.value for e in DeploymentMode], index=get_index(DeploymentMode, selected_system.deployment_mode.value))
                    edit_decision_criticality = st.selectbox("Decision Criticality", options=[e.value for e in DecisionCriticality], index=get_index(DecisionCriticality, selected_system.decision_criticality.value))
                    edit_automation_level = st.selectbox("Automation Level", options=[e.value for e in AutomationLevel], index=get_index(AutomationLevel, selected_system.automation_level.value))
                    edit_data_sensitivity = st.selectbox("Data Sensitivity", options=[e.value for e in DataSensitivity], index=get_index(DataSensitivity, selected_system.data_sensitivity.value))
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
                            selected_system.last_updated = datetime.now()
                            _update_dataframes()
                            st.success(f"AI System '{edit_name}' updated successfully!")
                            st.rerun()
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
                        st.session_state.selected_system_id = None 
                        st.rerun()

            else:
                st.warning("Please select an AI System.")
    else:
        st.info("No AI systems to edit or delete.")

elif st.session_state.current_page == 'Risk Tiering':
    st.title("2. Implementing Deterministic Risk Tiering")
    st.markdown(f"With the AI systems inventoried, my next critical task is to assign a risk tier to each. This is central to Sentinel Financial's SR 11-7-style model risk management framework. I need a deterministic scoring logic that consistently assigns a risk tier (Tier 1, Tier 2, or Tier 3) based on defined dimensions, ensuring transparency and reproducibility for the auditors. This process directly addresses the `learningOutcomes` requirement to implement deterministic risk tiering.")
    st.markdown(f"The risk tiering logic will sum scores from various attributes, including decision criticality, data sensitivity, automation level, AI type, deployment mode, and external dependencies. The total score $S_{total}$ for each AI system is calculated as:")
    st.markdown(r"$$ S_{total} = S_{criticality} + S_{sensitivity} + S_{automation} + S_{type} + S_{deployment} + S_{dependencies} $$ ")
    st.markdown(r"where $S_{criticality}$ is the score for `DecisionCriticality`.")
    st.markdown(r"where $S_{sensitivity}$ is the score for `DataSensitivity`.")
    st.markdown(r"where $S_{automation}$ is the score for `AutomationLevel`.")
    st.markdown(r"where $S_{type}$ is the score for `AIType`.")
    st.markdown(r"where $S_{deployment}$ is the score for `DeploymentMode`.")
    st.markdown(r"where $S_{dependencies}$ is the score for `ExternalDependencies`.")
    st.markdown(f"The risk tiers are then assigned based on the following thresholds:")
    st.markdown(r"$$ \text{Tier 1 (High Risk)}: S_{total} \geq 22 $$ ")
    st.markdown(r"$$ \text{Tier 2 (Medium Risk)}: 15 \leq S_{total} \leq 21 $$ ")
    st.markdown(r"$$ \text{Tier 3 (Low Risk)}: S_{total} \leq 14 $$ ")
    st.markdown(f"Along with the tier, a set of minimum required controls is automatically generated, aligning with Sentinel Financial's governance policies.")
    st.markdown(f"---")

    st.subheader("Compute Risk Tiers")
    if st.button("Compute Risk Tiers for All Systems"):
        if st.session_state.system_records:
            st.session_state.risk_tier_results = [] 
            for system in st.session_state.system_records:
                tier_result = calculate_risk_tier(system) 
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
    st.markdown(r"$$ \text{Severity} = \text{Impact} \times \text{Likelihood} $$ ")
    st.markdown(r"where $\text{Impact}$ is the consequence of the risk, scored from 1 to 5.")
    st.markdown(r"where $\text{Likelihood}$ is the probability of the risk occurring, scored from 1 to 5.")
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
                    st.rerun()
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
        st.session_state.generated_files = [] 

        # 1. model_inventory.csv
        model_inventory_csv_path = os.path.join(st.session_state.output_dir, "model_inventory.csv")
        export_dataframe_to_csv(st.session_state.df_inventory, model_inventory_csv_path) 
        st.session_state.generated_files.append(model_inventory_csv_path)
        st.success(f"Generated: `{os.path.basename(model_inventory_csv_path)}`")

        # 2. risk_tiering.json
        risk_tiering_json_path = os.path.join(st.session_state.output_dir, "risk_tiering.json")
        export_pydantic_list_to_json(st.session_state.risk_tier_results, risk_tiering_json_path) 
        st.session_state.generated_files.append(risk_tiering_json_path)
        st.success(f"Generated: `{os.path.basename(risk_tiering_json_path)}`")

        # 3. lifecycle_risk_map.json
        lifecycle_risk_map_json_path = os.path.join(st.session_state.output_dir, "lifecycle_risk_map.json")
        export_pydantic_list_to_json(st.session_state.lifecycle_risks, lifecycle_risk_map_json_path) 
        st.session_state.generated_files.append(lifecycle_risk_map_json_path)
        st.success(f"Generated: `{os.path.basename(lifecycle_risk_map_json_path)}`")

        # 4. case1_executive_summary.md
        executive_summary_md_path = os.path.join(st.session_state.output_dir, "case1_executive_summary.md")
        
        executive_summary_content = f"""# AI Governance Audit Executive Summary - Sentinel Financial\n\n**Date:** {datetime.now().strftime('%Y-%m-%d')}\n**Prepared By:** Sarah, AI Program Lead\n\n## 1. Introduction\nThis summary provides an overview of Sentinel Financial's AI governance artifacts, compiled for the internal audit. It covers our AI system inventory, risk tiering results aligned with SR 11-7-style principles, and a detailed map of lifecycle risks. Our goal is to demonstrate a robust, structured, and auditable approach to managing AI systems within the institution.\n\n## 2. AI System Inventory\nSentinel Financial maintains a comprehensive inventory of all AI systems. Currently, three key systems are highlighted for this audit:\n\n| System Name                               | AI Type | Decision Criticality | Data Sensitivity |\n|-------------------------------------------|---------|----------------------|------------------|\n"""
        
        # Add static example rows if needed or generated from current inventory
        # For dynamic generation matching the description:
        if not st.session_state.df_inventory.empty:
             for index, row in st.session_state.df_inventory.iterrows():
                executive_summary_content += f"| {row.get('name', 'N/A'):<41} | {row.get('ai_type', 'N/A'):<7} | {row.get('decision_criticality', 'N/A'):<20} | {row.get('data_sensitivity', 'N/A'):<16} |\n"
        
        executive_summary_content += f"""\n## 3. AI Risk Tiering Results\nEach AI system undergoes a deterministic risk tiering process based on attributes like decision criticality, data sensitivity, automation level, and external dependencies. This ensures consistent risk classification and the assignment of appropriate controls.\n\n### Scoring Logic:\nThe total risk score $S_{{total}}$ is calculated by summing scores from various dimensions. For instance:\n*   Decision Criticality: LOW=1, MEDIUM=3, HIGH=5\n*   Data Sensitivity: PUBLIC=1, INTERNAL=2, CONFIDENTIAL=4, REGULATED_PII=5\n*   Automation Level: ADVISORY=1, HUMAN_APPROVAL=3, FULLY_AUTOMATED=5\n*   AI Type: ML=3, LLM=4, AGENT=5\n*   Deployment Mode: INTERNAL_ONLY=1, BATCH=2, HUMAN_IN_LOOP=3, REAL_TIME=4\n*   External Dependencies: 0 if none, 2 if any\n\nRisk Tiers:\n*   Tier 1 (High Risk): $S_{{total}} \geq 22$\n*   Tier 2 (Medium Risk): $15 \leq S_{{total}} \leq 21$\n*   Tier 3 (Low Risk): $S_{{total}} \leq 14$\n\n### Summary of Tiers:\n"""
        if not st.session_state.df_risk_tier.empty:
            executive_summary_content += """\n| System Name                               | Risk Tier | Total Score | Key Justification                                 |\n|-------------------------------------------|-----------|-------------|---------------------------------------------------|\n"""
            for index, row in st.session_state.df_risk_tier.iterrows():
                system_name = row.get('system_name', 'N/A')
                risk_tier = row.get('risk_tier', 'N/A')
                total_score = row.get('score_breakdown', {}).get('total_score', 'N/A')
                justification = row.get('justification', 'N/A')
                # Truncate justification for table
                short_just = (justification[:46] + '...') if len(justification) > 49 else justification
                executive_summary_content += f"| {system_name:<41} | {risk_tier:<9} | {total_score:<11} | {short_just:<49} |\n"
        else:
            executive_summary_content += "\nNo risk tier data available for summary.\n"

        executive_summary_content += f"""\n## 4. Lifecycle Risk Map\nWe have identified and mapped specific risks across the lifecycle phases of our AI systems. Risks are prioritized by severity, calculated as Impact $\times$ Likelihood.\n\n### Top 3 Lifecycle Risks:\n"""
        if not st.session_state.df_lifecycle_risk.empty:
            executive_summary_content += """\n| System Name                               | Risk Statement                                                      | Severity | Lifecycle Phase |\n|-------------------------------------------|---------------------------------------------------------------------|----------|-----------------|\n"""
            for index, row in st.session_state.df_lifecycle_risk.head(3).iterrows():
                s_name = row.get('system_name', 'N/A')
                r_stmt = row.get('risk_statement', 'N/A')
                sev = row.get('severity', 0)
                l_phase = row.get('lifecycle_phase', 'N/A')
                short_stmt = (r_stmt[:64] + '...') if len(r_stmt) > 67 else r_stmt
                executive_summary_content += f"| {s_name:<41} | {short_stmt:<67} | {sev:<8} | {l_phase:<15} |\n"
        else:
            executive_summary_content += "\nNo lifecycle risk data available for summary.\n"

        executive_summary_content += f"""\n## 5. Conclusion\nThis audit package demonstrates Sentinel Financial's commitment to responsible AI governance. By systematically inventorying, risk-tiering, and mapping lifecycle risks, we ensure accountability and maintain the integrity of our AI systems. The accompanying evidence manifest provides cryptographic proof of the authenticity of these artifacts."""

        with open(executive_summary_md_path, 'w') as f:
            f.write(executive_summary_content)
        st.session_state.generated_files.append(executive_summary_md_path)
        st.session_state.executive_summary_content = executive_summary_content
        st.success(f"Generated: `{os.path.basename(executive_summary_md_path)}`")

    st.markdown(f"---")
    st.title("5. Creating the Evidence Manifest for Integrity")
    st.markdown(f"A crucial aspect of auditability is ensuring the integrity and immutability of the submitted documents. As an AI Program Lead, Sarah must provide cryptographic proof that the artifacts have not been tampered with. This involves generating SHA-256 hashes for each file and compiling them into an `evidence_manifest.json`. This directly addresses the `learningOutcomes` and `Deliverable Summary` requirements for cryptographic hashing.")
    st.markdown(f"The SHA-256 algorithm produces a fixed-size hash value ($H$) for any input data ($M$). A small change in the input data will result in a completely different hash value, making it ideal for detecting tampering.")
    st.markdown(r"$$ H = \text{SHA256}(M) $$ ")
    st.markdown(r"where $H$ is the SHA-256 hash value.")
    st.markdown(r"where $M$ is the input data (the artifact file content).")
    st.markdown(f"---")

    st.subheader("Generate Evidence Manifest")
    if st.button("Generate Evidence Manifest"):
        if st.session_state.generated_files:
            evidence_artifacts_list = []
            for f_path in st.session_state.generated_files:
                file_name = os.path.basename(f_path)
                file_hash = calculate_sha256(f_path) 
                evidence_artifacts_list.append(EvidenceArtifact(name=file_name, path=f_path, sha256=file_hash))

            st.session_state.evidence_manifest = EvidenceManifest(
                team_or_user="Sarah (AI Program Lead)",
                artifacts=evidence_artifacts_list,
                run_id=uuid.uuid4(),
                generated_at=datetime.now()
            )

            evidence_manifest_json_path = os.path.join(st.session_state.output_dir, "evidence_manifest.json")
            with open(evidence_manifest_json_path, 'w') as f:
                json.dump(st.session_state.evidence_manifest.model_dump(mode='json'), f, indent=4)

            # Ensure manifest is in the generated files list if not already (to avoid duplicates if clicked multiple times, check first)
            if evidence_manifest_json_path not in st.session_state.generated_files:
                st.session_state.generated_files.append(evidence_manifest_json_path) 
            
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
            zip_file_path = create_zip_archive(st.session_state.generated_files, zip_archive_name_base, st.session_state.output_dir) 

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


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
