import streamlit as st
import pandas as pd
import json
import os
import shutil
import uuid
import time
from datetime import datetime, timedelta
from io import BytesIO
from pydantic import ValidationError
from source import *

# --- Page Configuration ---
st.set_page_config(
    page_title="QuLab: Enterprise AI Lifecycle & Model Risk Classification", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Enterprise AI Lifecycle & Model Risk Classification")
st.divider()

# --- Helper Functions for Session State Management ---


def cleanup_old_export_folders(base_dir="output_artifacts", days=7):
    """Remove export folders older than specified days."""
    if not os.path.exists(base_dir):
        return

    current_time = time.time()
    cutoff_time = current_time - (days * 24 * 60 * 60)

    try:
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path):
                folder_mtime = os.path.getmtime(folder_path)
                if folder_mtime < cutoff_time:
                    shutil.rmtree(folder_path)
                    print(f"Cleaned up old export folder: {folder_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def generate_unique_output_dir(base_dir="output_artifacts"):
    """Generate a unique output directory with timestamp and UUID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    folder_name = f"export_{timestamp}_{unique_id}"
    return os.path.join(base_dir, folder_name)


def delete_export_folder(folder_path):
    """Delete the export folder after download."""
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            return True
    except Exception as e:
        print(f"Error deleting folder {folder_path}: {e}")
    return False


def _update_dataframes():
    """Updates pandas DataFrames and ID maps based on current session state lists."""
    # Inventory DataFrame
    if st.session_state.system_records:
        data = [s.model_dump(mode='json')
                for s in st.session_state.system_records]
        st.session_state.df_inventory = pd.DataFrame(data)
        # Create ID map for dropdowns
        st.session_state.system_id_map = {
            str(s.system_id): s.name for s in st.session_state.system_records}
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
            system_id_str = str(r.system_id)
            system_name = st.session_state.system_id_map.get(
                system_id_str, "Unknown")

            # If still unknown, try to find by matching the UUID value
            if system_name == "Unknown" and st.session_state.system_records:
                matching_system = next((s for s in st.session_state.system_records
                                       if str(s.system_id) == system_id_str or s.system_id == r.system_id), None)
                if matching_system:
                    system_name = matching_system.name

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
            # Enrich with system name - try both UUID object and string representation
            system_id_str = str(lr.system_id)
            system_name = st.session_state.system_id_map.get(
                system_id_str, "Unknown")

            # If still unknown, try to find by matching the UUID value
            if system_name == "Unknown" and st.session_state.system_records:
                matching_system = next((s for s in st.session_state.system_records
                                       if str(s.system_id) == system_id_str or s.system_id == lr.system_id), None)
                if matching_system:
                    system_name = matching_system.name

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
    # Use the actual system_records from source.py to preserve UUIDs
    # This ensures lifecycle_risks can map to the correct systems
    try:
        st.session_state.system_records = system_records
    except Exception as e:
        st.error(f"Error initializing system records: {e}")
        st.session_state.system_records = []

if 'risk_tier_results' not in st.session_state:
    st.session_state.risk_tier_results = []

if 'lifecycle_risks' not in st.session_state:
    # Initialize Lifecycle Risks from source data
    # Using lifecycle_risks from source module
    try:
        # Check if they are already objects or need conversion
        if lifecycle_risks and isinstance(lifecycle_risks[0], dict):
            st.session_state.lifecycle_risks = [LifecycleRisk(
                **data) for data in lifecycle_risks]
        else:
            st.session_state.lifecycle_risks = lifecycle_risks
    except Exception as e:
        st.error(f"Error initializing lifecycle risks: {e}")
        st.session_state.lifecycle_risks = []

if 'output_dir' not in st.session_state:
    # Clean up old folders on first load
    cleanup_old_export_folders(base_dir="output_artifacts", days=7)
    # Generate unique output directory for this session
    st.session_state.output_dir = generate_unique_output_dir()

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

st.session_state.current_page = st.sidebar.selectbox(
    "AI Governance Workflow",
    ['Home', 'AI System Inventory', 'Risk Tiering',
        'Lifecycle Risk Mapping', 'Exports & Evidence'],
    key='page_selector'
)

# --- Main Content Area ---

if st.session_state.current_page == 'Home':
    st.markdown(
        f"### Case Study: Ensuring AI Accountability at Sentinel Financial")
    st.markdown(f"**Persona:** Sarah, an AI Program Lead at Sentinel Financial.")
    st.markdown(f"**Organization:** Sentinel Financial, a mid-size financial institution that leverages AI across various operations, from credit assessment to customer support.")
    st.markdown(f"**Scenario:** Sarah is facing an upcoming internal audit of Sentinel Financial's AI governance framework. She needs to demonstrate that all AI systems are properly inventoried, risk-tiered, and that potential lifecycle risks are identified and managed. The audit requires verifiable evidence of these governance artifacts, meaning the integrity and traceability of the documents must be guaranteed. Sarah's task is to compile all necessary information into a structured, tamper-proof package for the auditors, ensuring full compliance and accountability. This application simulates Sarah's real-world workflow to achieve this goal.")
    st.markdown(f"---")
    st.markdown(f"### Student Objectives")
    st.markdown(f"""- Build an enterprise AI model inventory
- Assign risk tiers (Tier 1-3) using SR 11-7-style reasoning
- Define minimum required controls per risk tier
- Identify lifecycle risks across design, deployment, and operations
- Produce audit-ready artifacts""")

elif st.session_state.current_page == 'AI System Inventory':
    st.title("1. AI System Inventory")
    st.markdown(f"To begin building the auditable package, my first task is to accurately inventory all AI systems within Sentinel Financial. This involves defining a structured format (schema) for each AI system's record and then populating this inventory with details of the three key AI systems currently in production or under development. A well-defined inventory is the cornerstone of robust AI governance.")
    st.markdown(f"The `SystemRecord` schema ensures that each AI system is consistently documented with essential metadata like its type, criticality, data sensitivity, and deployment mode. This structured approach helps in standardized reporting and downstream risk assessment.")
    st.markdown(
        r"$$ \text{AI System Inventory} = \{ \text{SystemRecord}_1, \text{SystemRecord}_2, \ldots, \text{SystemRecord}_N \} $$")
    st.markdown(
        r"where $\text{SystemRecord}_N$ represents a single AI system's metadata.")
    st.markdown(f"---")

    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 View Inventory", "➕ Add System", "✏️ Edit System", "🗑️ Delete System"])

    # Tab 1: View Inventory
    with tab1:
        st.subheader("Current AI System Inventory")
        if not st.session_state.df_inventory.empty:
            # Display count
            st.metric("Total AI Systems", len(st.session_state.system_records))

            # Option to select and view details
            if st.session_state.system_records:
                view_option = st.radio(
                    "View Mode:", ["Table View", "Detailed View"], horizontal=True)

                if view_option == "Table View":
                    st.dataframe(st.session_state.df_inventory,
                                 use_container_width=True)
                else:
                    system_options = {
                        str(s.system_id): s.name for s in st.session_state.system_records}
                    selected_view_id = st.selectbox(
                        "Select AI System to View Details",
                        options=list(system_options.keys()),
                        format_func=lambda x: system_options[x]
                    )

                    if selected_view_id:
                        selected_system = next((s for s in st.session_state.system_records if str(
                            s.system_id) == selected_view_id), None)
                        if selected_system:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Name:**", selected_system.name)
                                st.write("**Domain:**", selected_system.domain)
                                st.write("**AI Type:**",
                                         selected_system.ai_type.value)
                                st.write("**Owner Role:**",
                                         selected_system.owner_role)
                                st.write("**Deployment Mode:**",
                                         selected_system.deployment_mode.value)
                            with col2:
                                st.write("**Decision Criticality:**",
                                         selected_system.decision_criticality.value)
                                st.write("**Automation Level:**",
                                         selected_system.automation_level.value)
                                st.write("**Data Sensitivity:**",
                                         selected_system.data_sensitivity.value)
                                st.write(
                                    "**Last Updated:**", selected_system.last_updated.strftime('%Y-%m-%d %H:%M:%S'))

                            st.write("**Description:**")
                            st.info(selected_system.description)

                            if selected_system.external_dependencies:
                                st.write("**External Dependencies:**")
                                for dep in selected_system.external_dependencies:
                                    st.write(f"- {dep}")
        else:
            st.info(
                "No AI systems registered yet. Use the 'Add System' tab to add one.")

    # Tab 2: Add New System
    with tab2:
        st.subheader("Add New AI System")
        with st.form("add_system_form", clear_on_submit=False):
            name = st.text_input(
                "Name", help="e.g., ML-based Credit Underwriting Model")
            description = st.text_area(
                "Description", help="e.g., Automates credit assessment for loan applications.")
            domain = st.text_input("Domain", help="e.g., Retail Banking")

            col1, col2 = st.columns(2)
            with col1:
                ai_type = st.selectbox("AI Type", options=[
                                       e.value for e in AIType])
                deployment_mode = st.selectbox("Deployment Mode", options=[
                                               e.value for e in DeploymentMode])
                decision_criticality = st.selectbox("Decision Criticality", options=[
                                                    e.value for e in DecisionCriticality])
            with col2:
                owner_role = st.text_input(
                    "Owner Role", help="e.g., Head of Lending Products")
                automation_level = st.selectbox("Automation Level", options=[
                                                e.value for e in AutomationLevel])
                data_sensitivity = st.selectbox("Data Sensitivity", options=[
                                                e.value for e in DataSensitivity])

            external_dependencies = st.multiselect(
                "External Dependencies",
                options=["Credit Bureau API", "Fraud Detection Service", "Internal Knowledge Base API",
                         "Internal Reporting DB", "Document Management System API", "Third-Party Data Feed", "Cloud AI Service"]
            )

            submitted = st.form_submit_button("Add AI System", type="primary")
            if submitted:
                # Validation
                validation_errors = []

                if not name or not name.strip():
                    validation_errors.append("Name is required")
                elif len(name.strip()) < 3:
                    validation_errors.append(
                        "Name must be at least 3 characters long")
                elif len(name.strip()) > 200:
                    validation_errors.append(
                        "Name must not exceed 200 characters")
                elif any(s.name.lower() == name.strip().lower() for s in st.session_state.system_records):
                    validation_errors.append(
                        "An AI system with this name already exists")

                if not description or not description.strip():
                    validation_errors.append("Description is required")
                elif len(description.strip()) < 10:
                    validation_errors.append(
                        "Description must be at least 10 characters long")
                elif len(description.strip()) > 1000:
                    validation_errors.append(
                        "Description must not exceed 1000 characters")

                if not domain or not domain.strip():
                    validation_errors.append("Domain is required")
                elif len(domain.strip()) < 2:
                    validation_errors.append(
                        "Domain must be at least 2 characters long")
                elif len(domain.strip()) > 100:
                    validation_errors.append(
                        "Domain must not exceed 100 characters")

                if not owner_role or not owner_role.strip():
                    validation_errors.append("Owner Role is required")
                elif len(owner_role.strip()) < 2:
                    validation_errors.append(
                        "Owner Role must be at least 2 characters long")
                elif len(owner_role.strip()) > 100:
                    validation_errors.append(
                        "Owner Role must not exceed 100 characters")

                if validation_errors:
                    for error in validation_errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        new_system = SystemRecord(
                            name=name.strip(), description=description.strip(), domain=domain.strip(), ai_type=AIType(
                                ai_type),
                            owner_role=owner_role.strip(), deployment_mode=DeploymentMode(
                                deployment_mode),
                            decision_criticality=DecisionCriticality(
                                decision_criticality),
                            automation_level=AutomationLevel(automation_level),
                            data_sensitivity=DataSensitivity(data_sensitivity),
                            external_dependencies=external_dependencies
                        )
                        st.session_state.system_records.append(new_system)
                        _update_dataframes()
                        st.success(
                            f"✅ AI System '{name.strip()}' added successfully!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"Validation Error: {e}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

    # Tab 3: Edit System
    with tab3:
        st.subheader("Edit AI System")
        if st.session_state.system_records:
            system_options = {
                str(s.system_id): s.name for s in st.session_state.system_records}
            selected_edit_id = st.selectbox(
                "Select AI System to Edit",
                options=list(system_options.keys()),
                format_func=lambda x: system_options[x],
                key="edit_system_selector"
            )

            if selected_edit_id:
                selected_system = next((s for s in st.session_state.system_records if str(
                    s.system_id) == selected_edit_id), None)

                if selected_system:
                    with st.form("edit_system_form"):
                        st.info(f"Editing: **{selected_system.name}**")

                        edit_name = st.text_input(
                            "Name", value=selected_system.name)
                        edit_description = st.text_area(
                            "Description", value=selected_system.description)
                        edit_domain = st.text_input(
                            "Domain", value=selected_system.domain)

                        # Helper to get index safely
                        def get_index(enum_cls, val):
                            vals = [e.value for e in enum_cls]
                            try:
                                return vals.index(val)
                            except ValueError:
                                return 0

                        col1, col2 = st.columns(2)
                        with col1:
                            edit_ai_type = st.selectbox("AI Type", options=[e.value for e in AIType],
                                                        index=get_index(AIType, selected_system.ai_type.value))
                            edit_deployment_mode = st.selectbox("Deployment Mode", options=[e.value for e in DeploymentMode],
                                                                index=get_index(DeploymentMode, selected_system.deployment_mode.value))
                            edit_decision_criticality = st.selectbox("Decision Criticality", options=[e.value for e in DecisionCriticality],
                                                                     index=get_index(DecisionCriticality, selected_system.decision_criticality.value))
                        with col2:
                            edit_owner_role = st.text_input(
                                "Owner Role", value=selected_system.owner_role)
                            edit_automation_level = st.selectbox("Automation Level", options=[e.value for e in AutomationLevel],
                                                                 index=get_index(AutomationLevel, selected_system.automation_level.value))
                            edit_data_sensitivity = st.selectbox("Data Sensitivity", options=[e.value for e in DataSensitivity],
                                                                 index=get_index(DataSensitivity, selected_system.data_sensitivity.value))

                        edit_external_dependencies = st.multiselect(
                            "External Dependencies",
                            options=["Credit Bureau API", "Fraud Detection Service", "Internal Knowledge Base API",
                                     "Internal Reporting DB", "Document Management System API", "Third-Party Data Feed", "Cloud AI Service"],
                            default=selected_system.external_dependencies
                        )

                        update_submitted = st.form_submit_button(
                            "Update AI System", type="primary")

                        if update_submitted:
                            # Validation
                            validation_errors = []

                            if not edit_name or not edit_name.strip():
                                validation_errors.append("Name is required")
                            elif len(edit_name.strip()) < 3:
                                validation_errors.append(
                                    "Name must be at least 3 characters long")
                            elif len(edit_name.strip()) > 200:
                                validation_errors.append(
                                    "Name must not exceed 200 characters")
                            elif any(s.name.lower() == edit_name.strip().lower() and str(s.system_id) != selected_edit_id for s in st.session_state.system_records):
                                validation_errors.append(
                                    "An AI system with this name already exists")

                            if not edit_description or not edit_description.strip():
                                validation_errors.append(
                                    "Description is required")
                            elif len(edit_description.strip()) < 10:
                                validation_errors.append(
                                    "Description must be at least 10 characters long")
                            elif len(edit_description.strip()) > 1000:
                                validation_errors.append(
                                    "Description must not exceed 1000 characters")

                            if not edit_domain or not edit_domain.strip():
                                validation_errors.append("Domain is required")
                            elif len(edit_domain.strip()) < 2:
                                validation_errors.append(
                                    "Domain must be at least 2 characters long")
                            elif len(edit_domain.strip()) > 100:
                                validation_errors.append(
                                    "Domain must not exceed 100 characters")

                            if not edit_owner_role or not edit_owner_role.strip():
                                validation_errors.append(
                                    "Owner Role is required")
                            elif len(edit_owner_role.strip()) < 2:
                                validation_errors.append(
                                    "Owner Role must be at least 2 characters long")
                            elif len(edit_owner_role.strip()) > 100:
                                validation_errors.append(
                                    "Owner Role must not exceed 100 characters")

                            if validation_errors:
                                for error in validation_errors:
                                    st.error(f"❌ {error}")
                            else:
                                try:
                                    selected_system.name = edit_name.strip()
                                    selected_system.description = edit_description.strip()
                                    selected_system.domain = edit_domain.strip()
                                    selected_system.ai_type = AIType(
                                        edit_ai_type)
                                    selected_system.owner_role = edit_owner_role.strip()
                                    selected_system.deployment_mode = DeploymentMode(
                                        edit_deployment_mode)
                                    selected_system.decision_criticality = DecisionCriticality(
                                        edit_decision_criticality)
                                    selected_system.automation_level = AutomationLevel(
                                        edit_automation_level)
                                    selected_system.data_sensitivity = DataSensitivity(
                                        edit_data_sensitivity)
                                    selected_system.external_dependencies = edit_external_dependencies
                                    selected_system.last_updated = datetime.now()
                                    _update_dataframes()
                                    st.success(
                                        f"✅ AI System '{edit_name.strip()}' updated successfully!")
                                    st.rerun()
                                except ValidationError as e:
                                    st.error(f"Validation Error: {e}")
                                except Exception as e:
                                    st.error(
                                        f"An unexpected error occurred: {e}")
        else:
            st.info("No AI systems available to edit. Add a system first.")

    # Tab 4: Delete System
    with tab4:
        st.subheader("Delete AI System")
        if st.session_state.system_records:
            st.warning(
                "⚠️ Deleting an AI system will also remove all associated risk tiers and lifecycle risks.")

            system_options = {
                str(s.system_id): s.name for s in st.session_state.system_records}
            selected_delete_id = st.selectbox(
                "Select AI System to Delete",
                options=list(system_options.keys()),
                format_func=lambda x: system_options[x],
                key="delete_system_selector"
            )

            if selected_delete_id:
                selected_system = next((s for s in st.session_state.system_records if str(
                    s.system_id) == selected_delete_id), None)

                if selected_system:
                    # Show system details before deletion
                    st.write("**System Details:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Name:**", selected_system.name)
                        st.write("**Domain:**", selected_system.domain)
                        st.write("**AI Type:**", selected_system.ai_type.value)
                    with col2:
                        st.write("**Decision Criticality:**",
                                 selected_system.decision_criticality.value)
                        st.write("**Data Sensitivity:**",
                                 selected_system.data_sensitivity.value)

                    # Confirmation
                    confirm = st.checkbox(
                        f"I confirm that I want to delete **{selected_system.name}**")

                    if st.button("🗑️ Delete AI System", type="primary", disabled=not confirm):
                        st.session_state.system_records = [
                            s for s in st.session_state.system_records if str(s.system_id) != selected_delete_id]
                        # Also delete associated risk tiers and lifecycle risks
                        st.session_state.risk_tier_results = [
                            r for r in st.session_state.risk_tier_results if str(r.system_id) != selected_delete_id]
                        st.session_state.lifecycle_risks = [
                            lr for lr in st.session_state.lifecycle_risks if str(lr.system_id) != selected_delete_id]
                        _update_dataframes()
                        st.success(
                            f"✅ AI System '{selected_system.name}' and its associated risks deleted successfully!")
                        st.rerun()
        else:
            st.info("No AI systems available to delete.")

elif st.session_state.current_page == 'Risk Tiering':
    st.title("2. Implementing Deterministic Risk Tiering")
    st.markdown(f"With the AI systems inventoried, my next critical task is to assign a risk tier to each. This is central to Sentinel Financial's SR 11-7-style model risk management framework. I need a deterministic scoring logic that consistently assigns a risk tier (Tier 1, Tier 2, or Tier 3) based on defined dimensions, ensuring transparency and reproducibility for the auditors. This process directly addresses the `learningOutcomes` requirement to implement deterministic risk tiering.")
    st.markdown(
        f"The risk tiering logic will sum scores from various attributes, including decision criticality, data sensitivity, automation level, AI type, deployment mode, and external dependencies. The total score $S_{{total}}$ for each AI system is calculated as:")
    st.markdown(
        r"$$ S_{total} = S_{criticality} + S_{sensitivity} + S_{automation} + S_{type} + S_{deployment} + S_{dependencies} $$ ")
    st.markdown(
        r"where $S_{criticality}$ is the score for `DecisionCriticality`.")
    st.markdown(r"where $S_{sensitivity}$ is the score for `DataSensitivity`.")
    st.markdown(r"where $S_{automation}$ is the score for `AutomationLevel`.")
    st.markdown(r"where $S_{type}$ is the score for `AIType`.")
    st.markdown(r"where $S_{deployment}$ is the score for `DeploymentMode`.")
    st.markdown(
        r"where $S_{dependencies}$ is the score for `ExternalDependencies`.")
    st.markdown(
        f"The risk tiers are then assigned based on the following thresholds:")
    st.markdown(r"$$ \text{Tier 1 (High Risk)}: S_{total} \geq 22 $$ ")
    st.markdown(
        r"$$ \text{Tier 2 (Medium Risk)}: 15 \leq S_{total} \leq 21 $$ ")
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
        # Display count
        st.metric("Total Risk Assessments", len(
            st.session_state.risk_tier_results))

        view_option = st.radio("View Mode:", [
                               "Table View", "Detailed View"], horizontal=True, key="risk_tier_view")

        if view_option == "Table View":
            st.dataframe(st.session_state.df_risk_tier,
                         use_container_width=True)
        else:
            tier_system_options_view = {str(r.system_id): st.session_state.system_id_map.get(
                str(r.system_id), "Unknown System") for r in st.session_state.risk_tier_results}
            selected_tier_view_id = st.selectbox(
                "Select AI System to View Details",
                options=list(tier_system_options_view.keys()),
                format_func=lambda x: tier_system_options_view[x],
                key='select_tier_view_system'
            )

            if selected_tier_view_id:
                selected_tier = next((r for r in st.session_state.risk_tier_results if str(
                    r.system_id) == selected_tier_view_id), None)

                if selected_tier:
                    system_name = st.session_state.system_id_map.get(
                        str(selected_tier.system_id), "Unknown")

                    # Display risk tier with color coding
                    tier_colors = {
                        "TIER_1": "🔴",
                        "TIER_2": "🟡",
                        "TIER_3": "🟢"
                    }
                    tier_labels = {
                        "TIER_1": "Tier 1 (High Risk)",
                        "TIER_2": "Tier 2 (Medium Risk)",
                        "TIER_3": "Tier 3 (Low Risk)"
                    }

                    st.markdown(f"### {system_name}")
                    st.markdown(
                        f"## {tier_colors.get(selected_tier.risk_tier.value, '')} {tier_labels.get(selected_tier.risk_tier.value, selected_tier.risk_tier.value)}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(
                            "**Computed At:**", selected_tier.computed_at.strftime('%Y-%m-%d %H:%M:%S'))
                        st.write("**Scoring Version:**",
                                 selected_tier.scoring_version)
                    with col2:
                        # Calculate total score from breakdown
                        total_score = sum(
                            selected_tier.score_breakdown.values())
                        st.metric("Total Risk Score", total_score)

                    st.write("**Score Breakdown:**")
                    breakdown_df = pd.DataFrame([
                        {"Dimension": k, "Score": v}
                        for k, v in selected_tier.score_breakdown.items()
                    ])
                    st.dataframe(
                        breakdown_df, use_container_width=True, hide_index=True)

                    st.write("**Justification:**")
                    st.info(selected_tier.justification)

                    st.write("**Required Controls:**")
                    for control in selected_tier.required_controls:
                        st.write(f"- {control}")
    else:
        st.info("No risk tier results available. Click 'Compute Risk Tiers' above.")

    st.subheader("Update Risk Tier Justification")
    if st.session_state.risk_tier_results:
        tier_system_options = {str(r.system_id): st.session_state.system_id_map.get(
            str(r.system_id), "Unknown System") for r in st.session_state.risk_tier_results}
        selected_risk_system_id = st.selectbox(
            "Select AI System to Update Justification",
            options=list(tier_system_options.keys()),
            format_func=lambda x: tier_system_options[x],
            key='select_justification_system'
        )
        if selected_risk_system_id:
            selected_tier_result = next((r for r in st.session_state.risk_tier_results if str(
                r.system_id) == selected_risk_system_id), None)
            if selected_tier_result:
                current_justification = selected_tier_result.justification
                new_justification = st.text_area(
                    "Justification", value=current_justification, height=150)
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
    st.markdown(f"Beyond a general risk tier, Sarah needs to identify specific risks that can emerge throughout an AI system's lifecycle, from design to decommissioning. This detailed lifecycle risk mapping helps Sentinel Financial proactive address vulnerabilities and demonstrate a comprehensive risk management strategy to auditors. ")
    st.markdown(f"The severity of each risk is a critical metric for prioritization and is calculated as the product of its `impact` and `likelihood`.")
    st.markdown(
        r"$$ \text{Severity} = \text{Impact} \times \text{Likelihood} $$ ")
    st.markdown(
        r"where $\text{Impact}$ is the consequence of the risk, scored from 1 to 5.")
    st.markdown(
        r"where $\text{Likelihood}$ is the probability of the risk occurring, scored from 1 to 5.")
    st.markdown(f"---")

    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 View Risks", "➕ Add Risk", "✏️ Edit Risk", "🗑️ Delete Risk"])

    # Tab 1: View Risks
    with tab1:
        st.subheader("Current Lifecycle Risk Map (Sorted by Severity)")
        if not st.session_state.df_lifecycle_risk.empty:
            # Display count
            st.metric("Total Lifecycle Risks", len(
                st.session_state.lifecycle_risks))

            view_option = st.radio("View Mode:", [
                                   "Table View", "Detailed View"], horizontal=True, key="lifecycle_risk_view")

            if view_option == "Table View":
                st.dataframe(st.session_state.df_lifecycle_risk,
                             use_container_width=True)
            else:
                risk_options = {str(lr.risk_id): f"{st.session_state.system_id_map.get(str(lr.system_id), 'Unknown')} - {lr.risk_statement[:50]}..."
                                for lr in st.session_state.lifecycle_risks}
                selected_risk_view_id = st.selectbox(
                    "Select Risk to View Details",
                    options=list(risk_options.keys()),
                    format_func=lambda x: risk_options[x],
                    key='select_risk_view'
                )

                if selected_risk_view_id:
                    selected_risk = next((lr for lr in st.session_state.lifecycle_risks if str(
                        lr.risk_id) == selected_risk_view_id), None)

                    if selected_risk:
                        system_name = st.session_state.system_id_map.get(
                            str(selected_risk.system_id), "Unknown")
                        severity_color = "🔴" if selected_risk.severity >= 15 else "🟡" if selected_risk.severity >= 9 else "🟢"

                        st.markdown(f"### {system_name}")
                        st.markdown(
                            f"## {severity_color} Severity: {selected_risk.severity}")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Impact", selected_risk.impact)
                        with col2:
                            st.metric("Likelihood", selected_risk.likelihood)
                        with col3:
                            st.write("**Phase:**",
                                     selected_risk.lifecycle_phase.value)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(
                                "**Risk Category:**", selected_risk.risk_category.value.replace('_', ' ').title())
                            st.write("**Owner Role:**",
                                     selected_risk.owner_role or "Not specified")
                        with col2:
                            st.write(
                                "**Created At:**", selected_risk.created_at.strftime('%Y-%m-%d %H:%M:%S'))

                        st.write("**Risk Statement:**")
                        st.info(selected_risk.risk_statement)

                        st.write("**Mitigation:**")
                        st.success(selected_risk.mitigation)

                        if selected_risk.evidence_links:
                            st.write("**Evidence Links:**")
                            for link in selected_risk.evidence_links:
                                st.markdown(f"- [{link}]({link})")
        else:
            st.info(
                "No lifecycle risks defined yet. Use the 'Add Risk' tab to add one.")

    # Tab 2: Add New Risk
    with tab2:
        st.subheader("Add New Lifecycle Risk")
        if st.session_state.system_records:
            with st.form("add_lifecycle_risk_form", clear_on_submit=False):
                system_id_options = {
                    str(s.system_id): s.name for s in st.session_state.system_records}
                selected_system_for_risk = st.selectbox(
                    "Select AI System",
                    options=list(system_id_options.keys()),
                    format_func=lambda x: system_id_options[x]
                )
                lifecycle_phase = st.selectbox("Lifecycle Phase", options=[
                    e.value for e in LifecyclePhase])
                risk_category = st.selectbox("Risk Category", options=[
                    e.value for e in RiskCategory])
                risk_statement = st.text_area(
                    "Risk Statement", help="e.g., Bias in historical training data leads to unfair lending decisions.")
                impact = st.slider("Impact (1-5)", 1, 5, 3)
                likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
                mitigation = st.text_area(
                    "Mitigation", help="e.g., Implement fairness metrics, re-balance training data.")
                owner_role = st.text_input(
                    "Owner Role", help="e.g., Data Scientist Lead")
                evidence_links_input = st.text_input(
                    "Evidence Links (comma-separated URLs)",
                    help="e.g., https://example.com/doc1, https://example.com/doc2",
                    placeholder="https://example.com/doc1, https://example.com/doc2"
                )

                submitted = st.form_submit_button("Add Lifecycle Risk")
                if submitted:
                    # Validation
                    validation_errors = []

                    if not risk_statement or not risk_statement.strip():
                        validation_errors.append("Risk Statement is required")
                    elif len(risk_statement.strip()) < 10:
                        validation_errors.append(
                            "Risk Statement must be at least 10 characters long")
                    elif len(risk_statement.strip()) > 1000:
                        validation_errors.append(
                            "Risk Statement must not exceed 1000 characters")

                    if not mitigation or not mitigation.strip():
                        validation_errors.append("Mitigation is required")
                    elif len(mitigation.strip()) < 10:
                        validation_errors.append(
                            "Mitigation must be at least 10 characters long")
                    elif len(mitigation.strip()) > 1000:
                        validation_errors.append(
                            "Mitigation must not exceed 1000 characters")

                    if not owner_role or not owner_role.strip():
                        validation_errors.append("Owner Role is required")
                    elif len(owner_role.strip()) < 2:
                        validation_errors.append(
                            "Owner Role must be at least 2 characters long")
                    elif len(owner_role.strip()) > 100:
                        validation_errors.append(
                            "Owner Role must not exceed 100 characters")

                    # Parse and validate comma-separated URLs
                    evidence_links = []
                    if evidence_links_input and evidence_links_input.strip():
                        evidence_links = [
                            url.strip() for url in evidence_links_input.split(",") if url.strip()]
                        import re
                        url_pattern = re.compile(
                            r'^https?://'
                            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                            r'localhost|'
                            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                            r'(?::\d+)?'
                            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

                        for url in evidence_links:
                            if not url_pattern.match(url):
                                validation_errors.append(
                                    f"Invalid URL format: {url}")
                                break

                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"❌ {error}")
                    else:
                        try:
                            new_risk = LifecycleRisk(
                                system_id=uuid.UUID(selected_system_for_risk),
                                lifecycle_phase=LifecyclePhase(
                                    lifecycle_phase),
                                risk_category=RiskCategory(risk_category),
                                risk_statement=risk_statement.strip(),
                                impact=impact,
                                likelihood=likelihood,
                                mitigation=mitigation.strip(),
                                owner_role=owner_role.strip(),
                                evidence_links=evidence_links
                            )
                            st.session_state.lifecycle_risks.append(new_risk)
                            _update_dataframes()
                            st.success("✅ Lifecycle risk added successfully!")
                            st.rerun()
                        except ValidationError as e:
                            st.error(f"Validation Error: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
        else:
            st.info(
                "Please add AI systems in the 'AI System Inventory' page before adding lifecycle risks.")

    # Tab 3: Edit Risk
    with tab3:
        st.subheader("Edit Lifecycle Risk")
        if st.session_state.lifecycle_risks:
            risk_options = {str(lr.risk_id): f"{st.session_state.system_id_map.get(str(lr.system_id), 'Unknown')} - {lr.risk_statement[:50]}..."
                            for lr in st.session_state.lifecycle_risks}
            selected_edit_risk_id = st.selectbox(
                "Select Risk to Edit",
                options=list(risk_options.keys()),
                format_func=lambda x: risk_options[x],
                key='select_risk_edit'
            )

            if selected_edit_risk_id:
                selected_risk = next((lr for lr in st.session_state.lifecycle_risks if str(
                    lr.risk_id) == selected_edit_risk_id), None)

                if selected_risk:
                    with st.form("edit_lifecycle_risk_form"):
                        st.info(
                            f"Editing risk for: **{st.session_state.system_id_map.get(str(selected_risk.system_id), 'Unknown')}**")

                        # Can't change system ID, just display it
                        st.text_input("AI System", value=st.session_state.system_id_map.get(
                            str(selected_risk.system_id), 'Unknown'), disabled=True)

                        def get_index(enum_cls, val):
                            vals = [e.value for e in enum_cls]
                            try:
                                return vals.index(val)
                            except ValueError:
                                return 0

                        col1, col2 = st.columns(2)
                        with col1:
                            edit_lifecycle_phase = st.selectbox("Lifecycle Phase", options=[
                                e.value for e in LifecyclePhase], index=get_index(LifecyclePhase, selected_risk.lifecycle_phase.value))
                        with col2:
                            edit_risk_category = st.selectbox("Risk Category", options=[
                                e.value for e in RiskCategory], index=get_index(RiskCategory, selected_risk.risk_category.value))

                        edit_risk_statement = st.text_area(
                            "Risk Statement", value=selected_risk.risk_statement, help="e.g., Bias in historical training data leads to unfair lending decisions.")

                        col1, col2 = st.columns(2)
                        with col1:
                            edit_impact = st.slider(
                                "Impact (1-5)", 1, 5, selected_risk.impact)
                        with col2:
                            edit_likelihood = st.slider(
                                "Likelihood (1-5)", 1, 5, selected_risk.likelihood)

                        edit_mitigation = st.text_area(
                            "Mitigation", value=selected_risk.mitigation, help="e.g., Implement fairness metrics, re-balance training data.")
                        edit_owner_role = st.text_input(
                            "Owner Role", value=selected_risk.owner_role or "", help="e.g., Data Scientist Lead")
                        edit_evidence_links_input = st.text_input(
                            "Evidence Links (comma-separated URLs)",
                            value=", ".join(
                                selected_risk.evidence_links) if selected_risk.evidence_links else "",
                            help="e.g., https://example.com/doc1, https://example.com/doc2",
                            placeholder="https://example.com/doc1, https://example.com/doc2"
                        )

                        update_submitted = st.form_submit_button(
                            "Update Lifecycle Risk", type="primary")

                        if update_submitted:
                            # Validation
                            validation_errors = []

                            if not edit_risk_statement or not edit_risk_statement.strip():
                                validation_errors.append(
                                    "Risk Statement is required")
                            elif len(edit_risk_statement.strip()) < 10:
                                validation_errors.append(
                                    "Risk Statement must be at least 10 characters long")
                            elif len(edit_risk_statement.strip()) > 1000:
                                validation_errors.append(
                                    "Risk Statement must not exceed 1000 characters")

                            if not edit_mitigation or not edit_mitigation.strip():
                                validation_errors.append(
                                    "Mitigation is required")
                            elif len(edit_mitigation.strip()) < 10:
                                validation_errors.append(
                                    "Mitigation must be at least 10 characters long")
                            elif len(edit_mitigation.strip()) > 1000:
                                validation_errors.append(
                                    "Mitigation must not exceed 1000 characters")

                            if not edit_owner_role or not edit_owner_role.strip():
                                validation_errors.append(
                                    "Owner Role is required")
                            elif len(edit_owner_role.strip()) < 2:
                                validation_errors.append(
                                    "Owner Role must be at least 2 characters long")
                            elif len(edit_owner_role.strip()) > 100:
                                validation_errors.append(
                                    "Owner Role must not exceed 100 characters")

                            # Parse and validate comma-separated URLs
                            edit_evidence_links = []
                            if edit_evidence_links_input and edit_evidence_links_input.strip():
                                edit_evidence_links = [
                                    url.strip() for url in edit_evidence_links_input.split(",") if url.strip()]
                                import re
                                url_pattern = re.compile(
                                    r'^https?://'
                                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                                    r'localhost|'
                                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                                    r'(?::\d+)?'
                                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

                                for url in edit_evidence_links:
                                    if not url_pattern.match(url):
                                        validation_errors.append(
                                            f"Invalid URL format: {url}")
                                        break

                            if validation_errors:
                                for error in validation_errors:
                                    st.error(f"❌ {error}")
                            else:
                                try:
                                    selected_risk.lifecycle_phase = LifecyclePhase(
                                        edit_lifecycle_phase)
                                    selected_risk.risk_category = RiskCategory(
                                        edit_risk_category)
                                    selected_risk.risk_statement = edit_risk_statement.strip()
                                    selected_risk.impact = edit_impact
                                    selected_risk.likelihood = edit_likelihood
                                    selected_risk.severity = edit_impact * edit_likelihood
                                    selected_risk.mitigation = edit_mitigation.strip()
                                    selected_risk.owner_role = edit_owner_role.strip()
                                    selected_risk.evidence_links = edit_evidence_links
                                    _update_dataframes()
                                    st.success(
                                        "✅ Lifecycle risk updated successfully!")
                                    st.rerun()
                                except ValidationError as e:
                                    st.error(f"Validation Error: {e}")
                                except Exception as e:
                                    st.error(
                                        f"An unexpected error occurred: {e}")
        else:
            st.info("No lifecycle risks available to edit. Add a risk first.")

    # Tab 4: Delete Risk
    with tab4:
        st.subheader("Delete Lifecycle Risk")
        if st.session_state.lifecycle_risks:
            st.warning("⚠️ Deleting a lifecycle risk cannot be undone.")

            risk_options = {str(lr.risk_id): f"{st.session_state.system_id_map.get(str(lr.system_id), 'Unknown')} - {lr.risk_statement[:50]}..."
                            for lr in st.session_state.lifecycle_risks}
            selected_delete_risk_id = st.selectbox(
                "Select Risk to Delete",
                options=list(risk_options.keys()),
                format_func=lambda x: risk_options[x],
                key='select_risk_delete'
            )

            if selected_delete_risk_id:
                selected_risk = next((lr for lr in st.session_state.lifecycle_risks if str(
                    lr.risk_id) == selected_delete_risk_id), None)

                if selected_risk:
                    # Show risk details before deletion
                    st.write("**Risk Details:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(
                            "**System:**", st.session_state.system_id_map.get(str(selected_risk.system_id), "Unknown"))
                        st.write("**Phase:**",
                                 selected_risk.lifecycle_phase.value)
                        st.write(
                            "**Category:**", selected_risk.risk_category.value.replace('_', ' ').title())
                    with col2:
                        st.write("**Impact:**", selected_risk.impact)
                        st.write("**Likelihood:**", selected_risk.likelihood)
                        st.write("**Severity:**", selected_risk.severity)

                    st.write("**Risk Statement:**")
                    st.info(selected_risk.risk_statement[:200] + (
                        "..." if len(selected_risk.risk_statement) > 200 else ""))

                    # Confirmation
                    confirm = st.checkbox(
                        f"I confirm that I want to delete this risk")

                    if st.button("🗑️ Delete Lifecycle Risk", type="primary", disabled=not confirm):
                        st.session_state.lifecycle_risks = [lr for lr in st.session_state.lifecycle_risks if str(
                            lr.risk_id) != selected_delete_risk_id]
                        _update_dataframes()
                        st.success("✅ Lifecycle risk deleted successfully!")
                        st.rerun()
        else:
            st.info("No lifecycle risks available to delete.")

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
        model_inventory_csv_path = os.path.join(
            st.session_state.output_dir, "model_inventory.csv")
        export_dataframe_to_csv(
            st.session_state.df_inventory, model_inventory_csv_path)
        st.session_state.generated_files.append(model_inventory_csv_path)
        st.success(
            f"Generated: `{os.path.basename(model_inventory_csv_path)}`")

        # 2. risk_tiering.json
        risk_tiering_json_path = os.path.join(
            st.session_state.output_dir, "risk_tiering.json")
        export_pydantic_list_to_json(
            st.session_state.risk_tier_results, risk_tiering_json_path)
        st.session_state.generated_files.append(risk_tiering_json_path)
        st.success(f"Generated: `{os.path.basename(risk_tiering_json_path)}`")

        # 3. lifecycle_risk_map.json
        lifecycle_risk_map_json_path = os.path.join(
            st.session_state.output_dir, "lifecycle_risk_map.json")
        export_pydantic_list_to_json(
            st.session_state.lifecycle_risks, lifecycle_risk_map_json_path)
        st.session_state.generated_files.append(lifecycle_risk_map_json_path)
        st.success(
            f"Generated: `{os.path.basename(lifecycle_risk_map_json_path)}`")

        # 4. case1_executive_summary.md
        executive_summary_md_path = os.path.join(
            st.session_state.output_dir, "case1_executive_summary.md")

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
                total_score = row.get('score_breakdown', {}).get(
                    'total_score', 'N/A')
                justification = row.get('justification', 'N/A')
                # Truncate justification for table
                short_just = (
                    justification[:46] + '...') if len(justification) > 49 else justification
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
                short_stmt = (
                    r_stmt[:64] + '...') if len(r_stmt) > 67 else r_stmt
                executive_summary_content += f"| {s_name:<41} | {short_stmt:<67} | {sev:<8} | {l_phase:<15} |\n"
        else:
            executive_summary_content += "\nNo lifecycle risk data available for summary.\n"

        executive_summary_content += f"""\n## 5. Conclusion\nThis audit package demonstrates Sentinel Financial's commitment to responsible AI governance. By systematically inventorying, risk-tiering, and mapping lifecycle risks, we ensure accountability and maintain the integrity of our AI systems. The accompanying evidence manifest provides cryptographic proof of the authenticity of these artifacts."""

        with open(executive_summary_md_path, 'w') as f:
            f.write(executive_summary_content)
        st.session_state.generated_files.append(executive_summary_md_path)
        st.session_state.executive_summary_content = executive_summary_content
        st.success(
            f"Generated: `{os.path.basename(executive_summary_md_path)}`")

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
                evidence_artifacts_list.append(EvidenceArtifact(
                    name=file_name, path=f_path, sha256=file_hash))

            st.session_state.evidence_manifest = EvidenceManifest(
                team_or_user="Sarah (AI Program Lead)",
                artifacts=evidence_artifacts_list,
                run_id=uuid.uuid4(),
                generated_at=datetime.now()
            )

            evidence_manifest_json_path = os.path.join(
                st.session_state.output_dir, "evidence_manifest.json")
            with open(evidence_manifest_json_path, 'w') as f:
                json.dump(st.session_state.evidence_manifest.model_dump(
                    mode='json'), f, indent=4)

            # Ensure manifest is in the generated files list if not already (to avoid duplicates if clicked multiple times, check first)
            if evidence_manifest_json_path not in st.session_state.generated_files:
                st.session_state.generated_files.append(
                    evidence_manifest_json_path)

            st.success(
                f"Generated: `{os.path.basename(evidence_manifest_json_path)}`")
        else:
            st.warning("Please generate core artifacts first.")

    st.subheader("Evidence Manifest Content")
    if st.session_state.evidence_manifest:
        manifest_df = pd.DataFrame(
            [art.model_dump() for art in st.session_state.evidence_manifest.artifacts])
        st.dataframe(manifest_df, use_container_width=True)
    else:
        st.info(
            "No evidence manifest generated yet. Click 'Generate Evidence Manifest'.")

    st.markdown(f"---")
    st.title("6. Packaging Audit-Ready Deliverables")
    st.markdown(f"The final step for Sarah is to package all the generated artifacts, including the `evidence_manifest.json`, into a single, downloadable ZIP archive. This simplifies submission to the auditors, ensuring that all required files are bundled together and easy to manage. This directly fulfills the `Deliverable Summary` requirement.")
    st.markdown(f"---")

    st.subheader("Download Audit Package")
    if st.session_state.generated_files:
        if st.button("Create and Download ZIP Archive"):
            zip_archive_name_base = "audit_package_ai_governance"
            zip_file_path = create_zip_archive(
                st.session_state.generated_files, zip_archive_name_base, st.session_state.output_dir)

            if os.path.exists(zip_file_path):
                with open(zip_file_path, "rb") as f:
                    zip_bytes = BytesIO(f.read())

                # Create download button
                download_clicked = st.download_button(
                    label="Download Audit Package ZIP",
                    data=zip_bytes.getvalue(),
                    file_name=os.path.basename(zip_file_path),
                    mime="application/zip",
                    on_click=lambda: None  # Placeholder for cleanup
                )

                st.success(
                    f"Audit package '{os.path.basename(zip_file_path)}' created and ready for download!")

                # Delete the export folder after creating download
                # Note: Streamlit doesn't have a true "after download" callback,
                # so we delete immediately after preparing the download
                if delete_export_folder(st.session_state.output_dir):
                    st.success(f"Export folder cleaned up successfully.")
                    # Reset the output directory for next generation
                    st.session_state.output_dir = generate_unique_output_dir()
                    st.session_state.generated_files = []
                    st.session_state.evidence_manifest = None
                st.session_state.cleanup_after_download = False
            else:
                st.error("Failed to create ZIP archive.")
    else:
        st.warning(
            "Please generate artifacts and evidence manifest before creating the ZIP archive.")


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
