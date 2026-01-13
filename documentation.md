id: 69669d77c45cd9e54065d122_documentation
summary: Enterprise AI Lifecycle & Model Risk Classification Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Enterprise AI Lifecycle & Model Risk Classification Codelab

## 1. Introduction to QuLab: Ensuring AI Accountability
Duration: 0:05:00

Welcome to the QuLab Codelab! In this guide, you will explore a Streamlit application designed to manage the enterprise AI lifecycle and classify model risks, crucial for robust AI governance and compliance.

### The Challenge: AI Accountability at Sentinel Financial

This application simulates the real-world workflow of Sarah, an AI Program Lead at Sentinel Financial. Sarah's primary task is to prepare for an upcoming internal audit of the institution's AI governance framework. She needs to demonstrate that all AI systems are properly inventoried, risk-tiered, and that potential lifecycle risks are identified and managed. A key requirement is to provide verifiable, tamper-proof evidence of these governance artifacts.

### Importance of AI Governance

In today's rapidly evolving technological landscape, AI systems are becoming integral to critical business operations, especially in regulated industries like finance. Effective AI governance is paramount to:
*   **Ensure Compliance:** Adhere to regulations like SR 11-7 (for financial institutions) and emerging AI-specific laws.
*   **Mitigate Risk:** Identify, assess, and manage risks such as bias, explainability, security vulnerabilities, and operational failures.
*   **Build Trust:** Foster confidence among stakeholders, regulators, and customers in the ethical and responsible use of AI.
*   **Drive Value:** Optimize AI development and deployment processes, leading to more reliable and impactful AI solutions.

### Learning Objectives

By the end of this codelab, you will be able to:
*   Understand and manage an enterprise AI model inventory.
*   Implement deterministic risk tiering (Tier 1-3) using defined scoring logic.
*   Identify and map lifecycle risks across design, deployment, and operations phases.
*   Generate audit-ready artifacts, including cryptographic evidence manifests.
*   Package all deliverables into a single, downloadable archive.

### Application Architecture Overview

The QuLab application is built using Streamlit, a powerful framework for creating data apps in Python. It leverages Pydantic for data validation and Pandas DataFrames for data manipulation and display.

<aside class="positive">
<b>Streamlit's power:</b> Streamlit allows rapid development of interactive web applications purely in Python, making it ideal for prototyping and internal tools.
</aside>

Here's a high-level conceptual architecture diagram of the application:

```mermaid
graph TD
    A[Streamlit Frontend] --> B{Session State}
    B -- Manages Data --> C[Pydantic Models]
    C -- Validates Data --> D[Data Lists (e.g., system_records)]
    D -- Transforms for Display --> E[Pandas DataFrames]
    E -- Displays to User --> A
    A -- User Actions --> F[Helper Functions (source.py)]
    F -- Artifact Generation --> G[Output Directory]
    G -- Hashes for Integrity --> H[Evidence Manifest]
    H -- Packages for Audit --> I[ZIP Archive]
```
*   **Streamlit Frontend:** The user interface for interacting with the application.
*   **Session State:** Streamlit's mechanism to store and persist data across reruns for a single user session.
*   **Pydantic Models:** Used for defining structured data schemas (e.g., `SystemRecord`, `RiskTierResult`, `LifecycleRisk`) and ensuring data validation. These are likely defined in `source.py`.
*   **Data Lists:** Python lists holding instances of Pydantic models, stored in Streamlit's session state.
*   **Pandas DataFrames:** Generated from the Pydantic model lists for tabular display and easier data manipulation.
*   **Helper Functions (`source.py`):** A module containing core logic such as risk calculation, data export, hashing, and ZIP archive creation.
*   **Output Directory:** A local directory (`output_artifacts`) where all generated audit files are stored.
*   **Evidence Manifest:** A JSON file containing cryptographic hashes of all generated artifacts to ensure their integrity.
*   **ZIP Archive:** The final bundled package of all audit artifacts for easy download and submission.

Let's begin exploring the functionalities!

## 2. Managing the AI System Inventory
Duration: 0:10:00

The first crucial step in any AI governance framework is to establish a comprehensive inventory of all AI systems. This step covers how to view, add, edit, and delete AI system records within the QuLab application.

### The `SystemRecord` Schema

The application uses a `SystemRecord` Pydantic model (defined in `source.py`) to ensure consistent documentation of each AI system. This schema includes essential metadata:
*   `system_id` (UUID): Unique identifier.
*   `name` (str): Name of the AI system.
*   `description` (str): Detailed description.
*   `domain` (str): Business domain (e.g., Retail Banking).
*   `ai_type` (Enum `AIType`): Type of AI (e.g., ML, LLM, AGENT).
*   `owner_role` (str): Role of the system owner.
*   `deployment_mode` (Enum `DeploymentMode`): How the system is deployed (e.g., REAL_TIME, BATCH).
*   `decision_criticality` (Enum `DecisionCriticality`): Impact of the system's decisions (e.g., HIGH, MEDIUM, LOW).
*   `automation_level` (Enum `AutomationLevel`): Degree of human intervention.
*   `data_sensitivity` (Enum `DataSensitivity`): Sensitivity of data processed (e.g., REGULATED_PII, CONFIDENTIAL).
*   `external_dependencies` (List[str]): Any external systems or APIs it relies on.
*   `created_at` (datetime): Timestamp of creation.
*   `last_updated` (datetime): Timestamp of last update.

The inventory can be represented as a set of these records:
$$ \text{AI System Inventory} = \{ \text{SystemRecord}_1, \text{SystemRecord}_2, \ldots, \text{SystemRecord}_N \} $$
where $\text{SystemRecord}_N$ represents a single AI system's metadata.

### Viewing the Current Inventory

Navigate to the **"AI System Inventory"** page using the sidebar.
You will see a `st.dataframe` displaying all currently registered AI systems. If this is your first time running the app, it might be populated with initial data from `ai_systems_data` in `source.py`, or it might be empty.

<aside class="positive">
<b>Tip:</b> The `_update_dataframes()` helper function ensures that the Pandas DataFrames (`df_inventory`, `df_risk_tier`, `df_lifecycle_risk`) are always synchronized with the underlying Pydantic model lists in session state.
</aside>

### Adding a New AI System

1.  On the "AI System Inventory" page, scroll down to the "Add New AI System" section.
2.  Fill in the form fields. Pay attention to the `select_box` options which correspond to the `Enum` types defined in `source.py` (e.g., `AIType`, `DeploymentMode`).
3.  Click **"Add AI System"**.
4.  Upon successful submission, a success message will appear, and the inventory table will refresh with the new entry.

For example, to add a new "Fraud Detection Model":
*   **Name:** ML-based Fraud Detection Model
*   **Description:** Identifies suspicious transactions in real-time.
*   **Domain:** Fraud & Security
*   **AI Type:** ML
*   **Owner Role:** Head of Fraud Prevention
*   **Deployment Mode:** REAL_TIME
*   **Decision Criticality:** HIGH
*   **Automation Level:** HUMAN_APPROVAL
*   **Data Sensitivity:** REGULATED_PII
*   **External Dependencies:** Credit Bureau API, Internal Reporting DB

### Editing or Deleting an AI System

1.  In the "Edit or Delete AI System" section, select an existing AI system from the dropdown menu.
2.  The form fields will populate with the selected system's current data.
3.  **To Update:** Modify the desired fields and click **"Update AI System"**.
4.  **To Delete:** Click **"Delete AI System"**. This action will also remove any associated risk tiers and lifecycle risks for that system.

<aside class="negative">
<b>Warning:</b> Deleting an AI system is irreversible and will also remove all associated risk tiering results and lifecycle risks. Proceed with caution.
</aside>

## 3. Implementing Deterministic Risk Tiering
Duration: 0:15:00

Once AI systems are inventoried, the next crucial step is to assign a risk tier. This application implements a deterministic risk tiering logic, similar to SR 11-7 guidelines, ensuring transparency and reproducibility. This process involves summing scores from various attributes to arrive at a total risk score, which then maps to a predefined risk tier (Tier 1, Tier 2, or Tier 3).

### Scoring Logic

The risk tiering logic calculates a total score ($S_{total}$) for each AI system by summing scores from various attributes defined in the `SystemRecord`. Each attribute's contribution to the total score is predetermined:

*   **Decision Criticality:** LOW=1, MEDIUM=3, HIGH=5
*   **Data Sensitivity:** PUBLIC=1, INTERNAL=2, CONFIDENTIAL=4, REGULATED_PII=5
*   **Automation Level:** ADVISORY=1, HUMAN_APPROVAL=3, FULLY_AUTOMATED=5
*   **AI Type:** ML=3, LLM=4, AGENT=5
*   **Deployment Mode:** INTERNAL_ONLY=1, BATCH=2, HUMAN_IN_LOOP=3, REAL_TIME=4
*   **External Dependencies:** 0 if none, 2 if any

The total score $S_{total}$ for each AI system is calculated as:
$$ S_{total} = S_{criticality} + S_{sensitivity} + S_{automation} + S_{type} + S_{deployment} + S_{dependencies} $$
where $S_{criticality}$ is the score for `DecisionCriticality`, $S_{sensitivity}$ is the score for `DataSensitivity`, and so on.

### Risk Tier Thresholds

The calculated $S_{total}$ maps to risk tiers based on the following thresholds:
*   **Tier 1 (High Risk):** $S_{total} \geq 22$
*   **Tier 2 (Medium Risk):** $15 \leq S_{total} \leq 21$
*   **Tier 3 (Low Risk):** $S_{total} \leq 14$

Along with the tier, a set of minimum required controls is automatically generated by the `calculate_risk_tier` function (from `source.py`), aligning with Sentinel Financial's governance policies.

### Computing and Viewing Risk Tiers

1.  Navigate to the **"Risk Tiering"** page.
2.  Click the **"Compute Risk Tiers for All Systems"** button.
3.  The application will iterate through all AI systems in the inventory, calculate their risk scores, and assign a tier.
4.  The "AI System Risk Tiering Results" `st.dataframe` will update, displaying the system name, calculated risk tier, total score, score breakdown, required controls, and an initial justification.

### Updating Risk Tier Justification

Sometimes, an initial justification might need refinement or additional context.
1.  In the "Update Risk Tier Justification" section, select an AI system from the dropdown.
2.  Edit the `text_area` with the new justification.
3.  Click **"Save Justification"**. The changes will be reflected in the internal session state and subsequently in the displayed DataFrame.

## 4. Mapping AI System Lifecycle Risks
Duration: 0:15:00

Beyond a general risk tier, it's crucial to identify specific risks that can emerge throughout an AI system's lifecycle – from design to deployment and ongoing operations. This detailed lifecycle risk mapping helps proactively address vulnerabilities and demonstrates a comprehensive risk management strategy to auditors.

### Lifecycle Risk Schema and Severity

The application uses a `LifecycleRisk` Pydantic model (defined in `source.py`) to capture detailed risk information:
*   `risk_id` (UUID): Unique identifier for the risk.
*   `system_id` (UUID): Links to the associated AI system.
*   `lifecycle_phase` (Enum `LifecyclePhase`): Where the risk occurs (e.g., DESIGN, DEVELOPMENT, DEPLOYMENT, MONITORING, DECOMMISSIONING).
*   `risk_category` (Enum `RiskCategory`): Type of risk (e.g., ETHICAL, PERFORMANCE, SECURITY).
*   `risk_statement` (str): Detailed description of the risk.
*   `impact` (int): Consequence of the risk (1-5).
*   `likelihood` (int): Probability of the risk occurring (1-5).
*   `severity` (int): Calculated as `Impact` $\times$ `Likelihood`.
*   `mitigation` (str): Steps to reduce or eliminate the risk.
*   `owner_role` (str): Role responsible for managing this risk.
*   `evidence_links` (List[str]): URLs to supporting documents or evidence.
*   `created_at` (datetime): Timestamp of creation.
*   `last_updated` (datetime): Timestamp of last update.

The severity of each risk is a critical metric for prioritization and is calculated as the product of its `impact` and `likelihood`:
$$ \text{Severity} = \text{Impact} \times \text{Likelihood} $$
where $\text{Impact}$ is the consequence of the risk, scored from 1 to 5, and $\text{Likelihood}$ is the probability of the risk occurring, scored from 1 to 5.

### Viewing the Current Lifecycle Risk Map

Navigate to the **"Lifecycle Risk Mapping"** page.
You will see a `st.dataframe` displaying all currently defined lifecycle risks, sorted by their calculated severity in descending order.

### Adding a New Lifecycle Risk

1.  On the "Lifecycle Risk Mapping" page, scroll down to the "Add New Lifecycle Risk" section.
2.  First, ensure you have AI systems registered in the "AI System Inventory" page, as risks are associated with specific systems.
3.  Select an **AI System** from the dropdown.
4.  Fill in the form fields:
    *   **Lifecycle Phase:** Select the phase where the risk occurs (e.g., `DESIGN`).
    *   **Risk Category:** Choose a category (e.g., `ETHICAL`).
    *   **Risk Statement:** Describe the risk (e.g., "Bias in historical training data leads to unfair lending decisions.").
    *   **Impact (1-5):** Use the slider (e.g., 5 for high impact).
    *   **Likelihood (1-5):** Use the slider (e.g., 4 for high likelihood).
    *   **Mitigation:** Detail how the risk will be addressed (e.g., "Implement fairness metrics, re-balance training data.").
    *   **Owner Role:** Assign a role responsible (e.g., "Data Scientist Lead").
    *   **Evidence Links (URLs):** Add any relevant documentation links.
5.  Click **"Add Lifecycle Risk"**.
6.  A success message will confirm the addition, and the risk map table will refresh, now including the new risk, sorted by its calculated severity.

## 5. Generating Core Audit Artifacts
Duration: 0:10:00

With the AI inventory, risk tiers, and lifecycle risks established, the next step is to generate the core audit artifacts. These files are the primary deliverables for auditors and must be well-structured and complete. The application creates specific files in an `output_artifacts` directory.

### Types of Artifacts

The application generates the following core documents:
1.  **`model_inventory.csv`**: A CSV file containing the complete AI system inventory, exported directly from the `df_inventory` DataFrame.
2.  **`risk_tiering.json`**: A JSON file containing all `RiskTierResult` objects, capturing the risk tier, score breakdown, required controls, and justification for each AI system. This is generated by the `export_pydantic_list_to_json` function.
3.  **`lifecycle_risk_map.json`**: A JSON file containing all `LifecycleRisk` objects, detailing the identified risks across lifecycle phases, their severity, and mitigation strategies. This is also generated by the `export_pydantic_list_to_json` function.
4.  **`case1_executive_summary.md`**: A markdown file providing a high-level executive summary of the audit package, including key highlights from the inventory, risk tiering, and lifecycle risk map.

### Generating the Artifacts

1.  Navigate to the **"Exports & Evidence"** page.
2.  Click the **"Generate All Core Artifacts"** button.
3.  The application will create the `output_artifacts` directory (if it doesn't exist) and then generate each file. Success messages will confirm the creation of each artifact.

<aside class="positive">
<b>Review the Executive Summary:</b> The content of `case1_executive_summary.md` is dynamically generated, summarizing the data present in your session state. Take a moment to read through it in the Streamlit app's `executive_summary_content` variable (though not directly displayed in the app, it's generated programmatically).
</aside>

## 6. Creating the Evidence Manifest for Integrity
Duration: 0:08:00

A crucial aspect of auditability is ensuring the integrity and immutability of the submitted documents. Sarah needs to provide cryptographic proof that the artifacts have not been tampered with. This involves generating SHA-256 hashes for each file and compiling them into an `evidence_manifest.json`.

### Cryptographic Hashing with SHA-256

The SHA-256 algorithm produces a fixed-size hash value ($H$) for any input data ($M$). A small change in the input data will result in a completely different hash value, making it ideal for detecting tampering.
$$ H = \text{SHA256}(M) $$
where $H$ is the SHA-256 hash value (a 256-bit hexadecimal number) and $M$ is the input data (the artifact file content).

The `EvidenceManifest` Pydantic model (from `source.py`) stores this information:
*   `run_id` (UUID): A unique identifier for this specific manifest generation.
*   `generated_at` (datetime): Timestamp of when the manifest was created.
*   `team_or_user` (str): Who generated the manifest.
*   `artifacts` (List of `EvidenceArtifact`): A list of objects, each containing:
    *   `name` (str): The filename.
    *   `path` (str): The file path within the output directory.
    *   `sha256` (str): The SHA-256 hash of the file's content.

### Generating the Evidence Manifest

1.  On the "Exports & Evidence" page, after generating the core artifacts, click the **"Generate Evidence Manifest"** button.
2.  The `calculate_sha256` function (from `source.py`) will be used to compute a hash for each generated artifact.
3.  An `evidence_manifest.json` file will be created in the `output_artifacts` directory, listing all artifacts and their corresponding SHA-256 hashes.

### Viewing the Evidence Manifest Content

After generation, the "Evidence Manifest Content" section will display a `st.dataframe` showing the `name`, `path`, and `sha256` hash for each artifact. This provides a clear, auditable record of all generated files and their cryptographic fingerprints.

## 7. Packaging Audit-Ready Deliverables
Duration: 0:05:00

The final step for Sarah is to package all the generated artifacts, including the `evidence_manifest.json`, into a single, downloadable ZIP archive. This simplifies submission to the auditors, ensuring that all required files are bundled together and easy to manage.

### Creating and Downloading the ZIP Archive

1.  On the "Exports & Evidence" page, ensure you have generated all core artifacts and the evidence manifest.
2.  Click the **"Create and Download ZIP Archive"** button.
3.  The `create_zip_archive` function (from `source.py`) will bundle all files present in the `st.session_state.generated_files` list into a single ZIP file (e.g., `audit_package_ai_governance_[timestamp].zip`) within the `output_artifacts` directory.
4.  Upon successful creation, a **"Download Audit Package ZIP"** button will appear. Click this button to download the entire package to your local machine.

<button>
  [Download Audit Package ZIP](https://www.example.com/audit_package.zip)
</button>
<aside class="positive">
<b>Verify integrity:</b> After downloading the ZIP, you can extract the files and independently calculate the SHA-256 hashes of each artifact. Compare these to the hashes recorded in the `evidence_manifest.json` file to confirm that the integrity of the documents has been preserved. This is a critical step in a real audit!
</aside>

Congratulations! You have successfully navigated the QuLab application, managing an AI system inventory, performing risk tiering, mapping lifecycle risks, and generating audit-ready, tamper-proof deliverables. This comprehensive workflow is essential for establishing robust AI governance and demonstrating accountability within any organization.
