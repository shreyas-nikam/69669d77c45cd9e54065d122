
import pytest
import os
import shutil
from unittest.mock import patch, mock_open
from streamlit.testing.v1 import AppTest
from datetime import datetime
import uuid
import pandas as pd

# Assume 'app.py' and a dummy 'source.py' are in the same directory for AppTest.from_file.
# The dummy 'source.py' should contain simplified versions of the classes and functions
# imported by 'app.py' to allow the tests to run without errors.

@pytest.fixture(autouse=True)
def run_around_tests():
    """Fixture to set up and tear down test environment, ensuring clean state."""
    output_dir = "output_artifacts"
    # Setup: Ensure output directory is clean before each test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True) # Create it for tests that expect it

    yield # Run the actual test

    # Teardown: Clean up after each test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # Clean up dummy zip if created by a mock in tests
    if os.path.exists(f"{output_dir}/audit_package_ai_governance.zip"):
        os.remove(f"{output_dir}/audit_package_ai_governance.zip")

def test_initial_page_load():
    """Verify the app loads correctly to the 'Home' page and displays the main title."""
    at = AppTest.from_file("app.py").run()
    assert at.markdown[0].value == "### Case Study: Ensuring AI Accountability at Sentinel Financial"
    assert at.sidebar.selectbox("page_selector").value == "Home"

def test_page_navigation():
    """Verify that selecting different pages in the sidebar changes the main content."""
    at = AppTest.from_file("app.py").run()

    # Navigate to AI System Inventory
    at.sidebar.selectbox("page_selector").set_value("AI System Inventory").run()
    assert "AI System Inventory" in at.title[0].value
    assert at.markdown[1].value == "### Current AI System Inventory"

    # Navigate to Risk Tiering
    at.sidebar.selectbox("page_selector").set_value("Risk Tiering").run()
    assert "Implementing Deterministic Risk Tiering" in at.title[0].value
    assert at.markdown[1].value == "### Compute Risk Tiers"

    # Navigate to Lifecycle Risk Mapping
    at.sidebar.selectbox("page_selector").set_value("Lifecycle Risk Mapping").run()
    assert "Mapping AI System Lifecycle Risks" in at.title[0].value
    assert at.markdown[1].value == "### Current Lifecycle Risk Map (Sorted by Severity)"

    # Navigate to Exports & Evidence
    at.sidebar.selectbox("page_selector").set_value("Exports & Evidence").run()
    assert "Generating Core Audit Artifacts" in at.title[0].value
    assert at.markdown[1].value == "### Generate Core Artifacts"

def test_add_ai_system():
    """Test adding a new AI system and verifying its presence in the inventory."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("AI System Inventory").run()

    initial_system_count = len(at.session_state.system_records)

    at.text_input(label="Name")[0].set_value("New Test System").run()
    at.text_area(label="Description")[0].set_value("A system for testing purposes.").run()
    at.text_input(label="Domain")[1].set_value("Testing").run()
    at.selectbox(label="AI Type")[0].set_value("LLM").run()
    at.text_input(label="Owner Role")[2].set_value("Test Owner").run()
    at.selectbox(label="Deployment Mode")[0].set_value("Batch").run()
    at.selectbox(label="Decision Criticality")[0].set_value("Low").run()
    at.selectbox(label="Automation Level")[0].set_value("Advisory").run()
    at.selectbox(label="Data Sensitivity")[0].set_value("Public").run()
    at.multiselect(label="External Dependencies")[0].set_value(["Credit Bureau API"]).run()

    at.form("add_system_form").submit().run()

    assert at.success[0].value == "AI System 'New Test System' added successfully!"
    assert len(at.session_state.system_records) == initial_system_count + 1
    assert any(s.name == "New Test System" for s in at.session_state.system_records)
    assert not at.session_state.df_inventory.empty
    assert "New Test System" in at.session_state.df_inventory["name"].values

def test_edit_ai_system():
    """Test editing an existing AI system's details."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("AI System Inventory").run()

    # Pre-add a system to ensure one exists for editing
    at.text_input(label="Name")[0].set_value("System to Edit").run()
    at.text_area(label="Description")[0].set_value("Original Description.").run()
    at.text_input(label="Domain")[1].set_value("Finance").run()
    at.selectbox(label="AI Type")[0].set_value("ML").run()
    at.text_input(label="Owner Role")[2].set_value("Original Owner").run()
    at.selectbox(label="Deployment Mode")[0].set_value("Internal Only").run()
    at.selectbox(label="Decision Criticality")[0].set_value("Low").run()
    at.selectbox(label="Automation Level")[0].set_value("Advisory").run()
    at.selectbox(label="Data Sensitivity")[0].set_value("Public").run()
    at.form("add_system_form").submit().run()
    at.success[0].value # Clear success message from adding

    system_to_edit_id = next(s.system_id for s in at.session_state.system_records if s.name == "System to Edit")
    
    # Select the system to edit. Note global widget indexing.
    at.selectbox(label="Select AI System to Edit/Delete")[0].set_value(str(system_to_edit_id)).run()

    # Modify fields in the edit form. Note global widget indexing.
    at.text_input(label="Name")[3].set_value("Edited System Name").run()
    at.text_area(label="Description")[1].set_value("Updated Description.").run()
    at.text_input(label="Domain")[4].set_value("Edited Domain").run()

    at.form("edit_system_form").button("Update AI System").click().run()

    assert at.success[0].value == "AI System 'Edited System Name' updated successfully!"
    updated_system = next(s for s in at.session_state.system_records if s.system_id == system_to_edit_id)
    assert updated_system.name == "Edited System Name"
    assert updated_system.description == "Updated Description."
    assert "Edited System Name" in at.session_state.df_inventory["name"].values

def test_delete_ai_system():
    """Test deleting an AI system and verifying its removal, including associated risks."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("AI System Inventory").run()

    # Pre-add a system to delete
    at.text_input(label="Name")[0].set_value("System to Delete").run()
    at.text_area(label="Description")[0].set_value("Temp system.").run()
    at.text_input(label="Domain")[1].set_value("Temp").run()
    at.selectbox(label="AI Type")[0].set_value("ML").run()
    at.text_input(label="Owner Role")[2].set_value("Temp Owner").run()
    at.selectbox(label="Deployment Mode")[0].set_value("Batch").run()
    at.selectbox(label="Decision Criticality")[0].set_value("Low").run()
    at.selectbox(label="Automation Level")[0].set_value("Advisory").run()
    at.selectbox(label="Data Sensitivity")[0].set_value("Public").run()
    at.form("add_system_form").submit().run()
    at.success[0].value # Clear success message from adding

    system_to_delete_id = next(s.system_id for s in at.session_state.system_records if s.name == "System to Delete")
    initial_system_count = len(at.session_state.system_records)

    # Select the system to delete
    at.selectbox(label="Select AI System to Edit/Delete")[0].set_value(str(system_to_delete_id)).run()

    at.form("edit_system_form").button("Delete AI System").click().run()

    assert at.success[0].value == "AI System 'System to Delete' and its associated risks deleted successfully!"
    assert len(at.session_state.system_records) == initial_system_count - 1
    assert not any(s.name == "System to Delete" for s in at.session_state.system_records)
    assert "System to Delete" not in at.session_state.df_inventory["name"].values
    assert not any(r for r in at.session_state.risk_tier_results if str(r.system_id) == str(system_to_delete_id))
    assert not any(lr for lr in at.session_state.lifecycle_risks if str(lr.system_id) == str(system_to_delete_id))

def test_compute_risk_tiers():
    """Test computing risk tiers for all registered systems and verifying the results."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Risk Tiering").run()

    # Ensure there's at least one system for tiering (initial data from dummy source.py)
    assert len(at.session_state.system_records) > 0, "Precondition: At least one system must exist for risk tiering."

    at.button("Compute Risk Tiers for All Systems").click().run()

    assert at.success[0].value == "Risk tiers computed successfully!"
    assert not at.session_state.df_risk_tier.empty
    assert len(at.session_state.risk_tier_results) == len(at.session_state.system_records)
    assert "Automated calculation" in at.session_state.risk_tier_results[0].justification

def test_update_risk_tier_justification():
    """Test updating the justification for a specific risk tier."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Risk Tiering").run()

    # Compute tiers first to have results to update
    at.button("Compute Risk Tiers for All Systems").click().run()
    at.success[0].value # Clear success message from previous action

    # Select the first system for which a risk tier was computed (using its key)
    first_system_id = str(at.session_state.risk_tier_results[0].system_id)
    at.selectbox("select_justification_system").set_value(first_system_id).run()

    new_justification_text = "This is a custom justification for the risk tier."
    at.text_area(label="Justification")[0].set_value(new_justification_text).run()
    at.button("Save Justification").click().run()

    assert at.success[0].value == "Justification updated successfully!"
    updated_tier_result = next(r for r in at.session_state.risk_tier_results if str(r.system_id) == first_system_id)
    assert updated_tier_result.justification == new_justification_text

def test_add_lifecycle_risk():
    """Test adding a new lifecycle risk and verifying its details."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Lifecycle Risk Mapping").run()

    # Ensure at least one AI system exists to associate the risk with
    assert len(at.session_state.system_records) > 0, "Precondition: At least one system must exist for lifecycle risk mapping."
    system_id_for_risk = str(at.session_state.system_records[0].system_id)

    initial_risk_count = len(at.session_state.lifecycle_risks)

    at.selectbox(label="Select AI System")[0].set_value(system_id_for_risk).run()
    at.selectbox(label="Lifecycle Phase")[0].set_value("Deployment").run()
    at.selectbox(label="Risk Category")[0].set_value("Security").run()
    at.text_area(label="Risk Statement")[0].set_value("Deployment security vulnerability.").run()
    at.slider(label="Impact (1-5)")[0].set_value(4).run()
    at.slider(label="Likelihood (1-5)")[0].set_value(3).run()
    at.text_area(label="Mitigation")[1].set_value("Implement stronger security controls.").run()
    at.text_input(label="Owner Role")[0].set_value("Security Lead").run()
    at.multiselect(label="Evidence Links (URLs)")[0].set_value(["http://example.com/sec_doc"]).run()

    at.form("add_lifecycle_risk_form").submit().run()

    assert at.success[0].value == "Lifecycle risk added successfully!"
    assert len(at.session_state.lifecycle_risks) == initial_risk_count + 1
    assert any(lr.risk_statement == "Deployment security vulnerability." for lr in at.session_state.lifecycle_risks)
    assert not at.session_state.df_lifecycle_risk.empty
    assert "Deployment security vulnerability." in at.session_state.df_lifecycle_risk["risk_statement"].values
    assert at.session_state.df_lifecycle_risk["severity"].iloc[-1] == 12 # Impact 4 * Likelihood 3

@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
# Mock os.path.exists to simulate output_dir existing.
@patch("os.path.exists", side_effect=lambda path: "output_artifacts" in path)
def test_generate_core_artifacts(mock_path_exists, mock_file_open, mock_makedirs):
    """Test generating CSV, JSON, and Markdown artifacts and verifying success messages."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Exports & Evidence").run()

    # Pre-populate session state with dummy data for artifact generation
    from source import SystemRecord, AIType, DeploymentMode, DecisionCriticality, AutomationLevel, DataSensitivity
    test_system = SystemRecord(
        name="System for Artifacts", description="Desc", domain="Domain",
        ai_type=AIType.ML, owner_role="Owner", deployment_mode=DeploymentMode.INTERNAL_ONLY,
        decision_criticality=DecisionCriticality.LOW, automation_level=AutomationLevel.ADVISORY,
        data_sensitivity=DataSensitivity.PUBLIC
    )
    at.session_state.system_records.append(test_system)
    at.session_state.df_inventory = pd.DataFrame([test_system.model_dump(mode='json')])

    from source import RiskTierResult, RiskScoreBreakdown
    test_risk_tier = RiskTierResult(
        system_id=test_system.system_id, system_name=test_system.name, risk_tier="Tier 3 (Low Risk)",
        justification="Test justification", minimum_controls=[],
        score_breakdown=RiskScoreBreakdown(decision_criticality_score=1, data_sensitivity_score=1,
                                            automation_level_score=1, ai_type_score=3,
                                            deployment_mode_score=1, external_dependencies_score=0, total_score=7)
    )
    at.session_state.risk_tier_results.append(test_risk_tier)
    # Manually update df_risk_tier for display consistency during test
    data_risk_tier = []
    for r in at.session_state.risk_tier_results:
        row = r.model_dump(mode='json')
        row['system_name'] = at.session_state.system_id_map.get(str(r.system_id), "Unknown")
        data_risk_tier.append(row)
    at.session_state.df_risk_tier = pd.DataFrame(data_risk_tier)

    from source import LifecycleRisk, LifecyclePhase, RiskCategory
    test_lifecycle_risk = LifecycleRisk(
        system_id=test_system.system_id, lifecycle_phase=LifecyclePhase.DESIGN, risk_category=RiskCategory.ETHICS,
        risk_statement="Bias in design.", impact=5, likelihood=4, mitigation="Fairness review.",
        owner_role="Ethics Committee"
    )
    at.session_state.lifecycle_risks.append(test_lifecycle_risk)
    # Manually update df_lifecycle_risk for display consistency during test
    data_lifecycle_risk = []
    for lr in at.session_state.lifecycle_risks:
        row = lr.model_dump(mode='json')
        row['system_name'] = at.session_state.system_id_map.get(str(lr.system_id), "Unknown")
        row['severity'] = row.get('impact', 0) * row.get('likelihood', 0)
        data_lifecycle_risk.append(row)
    at.session_state.df_lifecycle_risk = pd.DataFrame(data_lifecycle_risk)

    at.button("Generate All Core Artifacts").click().run()

    expected_files_base = ["model_inventory.csv", "risk_tiering.json", "lifecycle_risk_map.json", "case1_executive_summary.md"]
    expected_files_full_paths = [os.path.join(at.session_state.output_dir, f) for f in expected_files_base]

    for i, file_name_base in enumerate(expected_files_base):
        assert at.success[i].value == f"Generated: `{file_name_base}`"

    assert len(at.session_state.generated_files) == len(expected_files_full_paths)
    for f_path in expected_files_full_paths:
        assert f_path in at.session_state.generated_files
    
    # Verify builtins.open was called for each file
    assert mock_file_open.call_count == len(expected_files_base)
    
    # Basic check for content in executive summary (from session state)
    assert "AI Governance Audit Executive Summary" in at.session_state.executive_summary_content
    assert "System for Artifacts" in at.session_state.executive_summary_content
    assert "Bias in design." in at.session_state.executive_summary_content

@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=True) # Mock os.path.exists to simulate output_dir existing
@patch("source.calculate_sha256", return_value="dummy_sha256_hash") # Mock the hash calculation function
def test_generate_evidence_manifest(mock_sha256, mock_path_exists, mock_file_open, mock_makedirs):
    """Test generating the evidence manifest with SHA-256 hashes for generated files."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Exports & Evidence").run()

    # Pre-populate generated_files for manifest creation
    at.session_state.generated_files = [
        "output_artifacts/model_inventory.csv",
        "output_artifacts/risk_tiering.json",
        "output_artifacts/lifecycle_risk_map.json",
        "output_artifacts/case1_executive_summary.md"
    ]

    at.button("Generate Evidence Manifest").click().run()

    assert at.success[0].value == "Generated: `evidence_manifest.json`"
    assert at.session_state.evidence_manifest is not None
    assert len(at.session_state.evidence_manifest.artifacts) == len(at.session_state.generated_files)
    assert at.session_state.evidence_manifest.artifacts[0].sha256 == "dummy_sha256_hash"
    
    # Verify the dataframe display of the manifest
    assert not at.dataframe[0].empty
    assert "name" in at.dataframe[0].columns
    assert "sha256" in at.dataframe[0].columns
    
    # Verify open was called to write the manifest file
    mock_file_open.assert_called_with(os.path.join(at.session_state.output_dir, "evidence_manifest.json"), 'w')

@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists") # Needs to return True for output dir, and for the zip file path
@patch("source.calculate_sha256", return_value="dummy_sha256_hash") # Mock for potential implicit calls
@patch("source.create_zip_archive", return_value="output_artifacts/audit_package_ai_governance.zip")
@patch("io.BytesIO") # Mock BytesIO for the download button's data
def test_create_and_download_zip(mock_bytesio, mock_create_zip, mock_sha256, mock_path_exists, mock_file_open, mock_makedirs):
    """Test creating a ZIP archive and providing a download button."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox("page_selector").set_value("Exports & Evidence").run()

    # Mock os.path.exists calls: first for output_dir, second for the zip file itself
    mock_path_exists.side_effect = [True, True]

    # Pre-populate generated_files and evidence_manifest for zip creation
    at.session_state.generated_files = [
        "output_artifacts/model_inventory.csv",
        "output_artifacts/risk_tiering.json",
        "output_artifacts/lifecycle_risk_map.json",
        "output_artifacts/case1_executive_summary.md",
        "output_artifacts/evidence_manifest.json"
    ]
    
    from source import EvidenceArtifact, EvidenceManifest
    at.session_state.evidence_manifest = EvidenceManifest(
        team_or_user="Test User",
        artifacts=[EvidenceArtifact(name="test.txt", path="output_artifacts/test.txt", sha256="123")],
        run_id=uuid.uuid4(),
        generated_at=datetime.now()
    )

    # Configure the mock BytesIO instance to return dummy content when getvalue() is called
    mock_bytesio_instance = mock_bytesio.return_value
    mock_bytesio_instance.getvalue.return_value = b"dummy zip content"

    at.button("Create and Download ZIP Archive").click().run()

    assert at.success[0].value == "Audit package 'audit_package_ai_governance.zip' created and ready for download!"
    assert at.download_button[0].label == "Download Audit Package ZIP"
    mock_create_zip.assert_called_once_with(at.session_state.generated_files, "audit_package_ai_governance", at.session_state.output_dir)
    mock_bytesio.assert_called_once() # Verify BytesIO was instantiated
    mock_bytesio_instance.getvalue.assert_called_once() # Verify getvalue() was called on the instance
