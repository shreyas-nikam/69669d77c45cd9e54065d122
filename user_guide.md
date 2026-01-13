id: 69669d77c45cd9e54065d122_user_guide
summary: Enterprise AI Lifecycle & Model Risk Classification User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Navigating Enterprise AI Lifecycle & Model Risk Classification

## 1. Introduction to AI Governance at Sentinel Financial
Duration: 00:05:00

Welcome to this codelab, where you will step into the role of Sarah, an AI Program Lead at Sentinel Financial. Your mission: to prepare a comprehensive and auditable package of AI governance artifacts for an upcoming internal audit. This scenario is crucial for any organization leveraging AI, as it demonstrates how to ensure accountability, transparency, and robust risk management for AI systems.

In this codelab, you will learn to:
- **Build an enterprise AI model inventory**: Systematically catalog all AI systems with essential metadata.
- **Assign risk tiers (Tier 1-3)**: Implement a deterministic scoring logic, inspired by frameworks like SR 11-7, to classify AI systems by risk level.
- **Identify lifecycle risks**: Map out potential risks across the entire AI system lifecycle, from design to operations.
- **Produce audit-ready artifacts**: Generate structured documentation and cryptographic evidence to prove the integrity of your governance efforts.

By the end of this guide, you will have a clear understanding of the practical steps involved in managing AI risks and ensuring compliance within a financial institution, or any organization dealing with critical AI deployments.

<aside class="positive">
<b>Understanding the "Why":</b> The ability to clearly articulate and demonstrate AI governance is becoming a mandatory requirement for businesses, especially in regulated industries. This application simulates a real-world workflow to build this essential capability.
</aside>

## 2. Building Your AI System Inventory
Duration: 00:15:00

The first step in any robust AI governance framework is to know what AI systems you have. This involves creating a detailed inventory, ensuring that each system is consistently documented with critical metadata. This structured approach is fundamental for standardized reporting and subsequent risk assessments.

Navigate to the **AI System Inventory** page using the sidebar.

Here, you will find the "Current AI System Inventory", which is a table listing all registered AI systems. Below that, you have forms to add new systems or edit/delete existing ones.

The application defines a `SystemRecord` schema, which dictates the essential information for each AI system, such as its type, criticality, data sensitivity, and deployment mode. Conceptually, your inventory is a collection of these records:
$$ \text{AI System Inventory} = \{ \text{SystemRecord}_1, \text{SystemRecord}_2, \ldots, \text{SystemRecord}_N \} $$
where $\text{SystemRecord}_N$ represents a single AI system's metadata.

### Add a New AI System

Use the "Add New AI System" form to register a new AI system.
1.  Fill in the details for a hypothetical AI system, for example:
    *   **Name**: `Fraud Detection Model`
    *   **Description**: `Identifies suspicious transactions in real-time.`
    *   **Domain**: `Risk Management`
    *   **AI Type**: `ML`
    *   **Owner Role**: `Head of Fraud Prevention`
    *   **Deployment Mode**: `Real-time`
    *   **Decision Criticality**: `High`
    *   **Automation Level**: `Human-in-Loop`
    *   **Data Sensitivity**: `Regulated PII`
    *   **External Dependencies**: `Fraud Detection Service`
2.  Click the "Add AI System" button.

You will see a success message, and the new system will appear in the "Current AI System Inventory" table.

### Edit or Delete an AI System

Below the add form, you'll find the "Edit or Delete AI System" section.
1.  Select an AI system from the dropdown list.
2.  The form will pre-populate with the selected system's details.
3.  You can modify any field. For instance, change the `Fraud Detection Model`'s `Automation Level` to `Fully Automated`.
4.  Click "Update AI System" to save changes, or "Delete AI System" to remove it from the inventory.

<aside class="positive">
<b>Best Practice:</b> A well-maintained inventory is the foundation of effective AI governance. Ensure all relevant metadata is captured consistently to facilitate accurate risk assessment and compliance checks.
</aside>

## 3. Implementing Deterministic Risk Tiering
Duration: 00:15:00

Once your AI systems are inventoried, the next crucial step is to assign a risk tier to each. This application uses a deterministic scoring logic, inspired by frameworks like SR 11-7, to consistently assign a risk tier (Tier 1: High, Tier 2: Medium, Tier 3: Low) based on various attributes. This ensures transparency and reproducibility, which are vital for auditors.

Navigate to the **Risk Tiering** page using the sidebar.

The risk tiering logic sums scores from various attributes of each AI system. The total score $S_{total}$ for each AI system is calculated as:
$$ S_{total} = S_{criticality} + S_{sensitivity} + S_{automation} + S_{type} + S_{deployment} + S_{dependencies} $$
where $S_{criticality}$ is the score for `DecisionCriticality`, $S_{sensitivity}$ is the score for `DataSensitivity`, and so on for other attributes. Each attribute's score contributes to the overall risk assessment.

The risk tiers are then assigned based on specific thresholds:
$$ \text{Tier 1 (High Risk)}: S_{total} \geq 22 $$
$$ \text{Tier 2 (Medium Risk)}: 15 \leq S_{total} \leq 21 $$
$$ \text{Tier 3 (Low Risk)}: S_{total} \leq 14 $$

### Compute and View Risk Tiers

1.  Click the "Compute Risk Tiers for All Systems" button. The application will process all inventoried systems and apply the scoring logic.
2.  The "AI System Risk Tiering Results" table will populate, showing each system's assigned risk tier, total score, and a breakdown of how the score was calculated.

### Update Risk Tier Justification

Each risk tiering result includes a justification field. This is important for providing context and explanations to auditors or stakeholders.
1.  Select an AI system from the "Select AI System to Update Justification" dropdown.
2.  An editable text area will display the current justification. You can update it to provide more specific details about why a system received a particular risk tier.
3.  Click "Save Justification".

<aside class="positive">
<b>Deterministic Logic:</b> The use of a deterministic scoring logic is key for auditability. It means that given the same input attributes for an AI system, the risk tier will always be the same, providing consistent and justifiable results.
</aside>

## 4. Mapping AI System Lifecycle Risks
Duration: 00:10:00

Beyond a general risk tier, it's essential to identify specific risks that can emerge throughout an AI system's lifecycle – from its initial design to deployment and eventual decommissioning. This detailed mapping helps to proactively address vulnerabilities and demonstrates a comprehensive risk management strategy.

Navigate to the **Lifecycle Risk Mapping** page using the sidebar.

On this page, you can define and manage risks associated with different phases of an AI system's existence. The severity of each identified risk is a critical metric for prioritization and is calculated as the product of its `impact` and `likelihood`:
$$ \text{Severity} = \text{Impact} \times \text{Likelihood} $$
where $\text{Impact}$ represents the consequence of the risk (scored 1 to 5) and $\text{Likelihood}$ represents the probability of the risk occurring (scored 1 to 5). Higher severity risks require more immediate attention.

### Add a New Lifecycle Risk

1.  Use the "Add New Lifecycle Risk" form.
2.  Select an AI system from the dropdown (e.g., the `Fraud Detection Model` you added).
3.  Choose a `Lifecycle Phase` (e.g., `Design`).
4.  Select a `Risk Category` (e.g., `Bias and Fairness`).
5.  Enter a `Risk Statement` (e.g., `Historical transaction data contains patterns that may lead to algorithmic bias against certain demographics, resulting in unfair fraud detection.`
6.  Adjust the `Impact` and `Likelihood` sliders (e.g., Impact 4, Likelihood 3). This will result in a Severity of 12.
7.  Provide a `Mitigation` strategy (e.g., `Implement debiasing techniques in training, regular fairness audits.`).
8.  Assign an `Owner Role` (e.g., `Model Risk Manager`).
9.  Add any `Evidence Links` if available (e.g., `http://example.com/fairness_report`).
10. Click "Add Lifecycle Risk".

The new risk will appear in the "Current Lifecycle Risk Map", which is sorted by severity (highest first) to help prioritize risk management efforts.

<aside class="positive">
<b>Proactive Risk Management:</b> Mapping risks across the lifecycle enables your organization to anticipate and mitigate issues before they become critical, rather than reacting to failures post-deployment.
</aside>

## 5. Generating Core Audit Artifacts
Duration: 00:05:00

With the AI inventory, risk tiers, and lifecycle risks now established, you can generate the primary deliverables for the auditors. These artifacts must be well-structured and complete, forming the core of your audit package.

Navigate to the **Exports & Evidence** page using the sidebar.

This section allows you to create several key documents:
-   `model_inventory.csv`: A CSV file containing your complete AI system inventory.
-   `risk_tiering.json`: A JSON file detailing the risk tiering results for all systems.
-   `lifecycle_risk_map.json`: A JSON file summarizing the identified lifecycle risks.
-   `case1_executive_summary.md`: A human-readable markdown summary for executive stakeholders and auditors.

### Generate All Core Artifacts

1.  Click the "Generate All Core Artifacts" button.
2.  The application will generate each of the files and confirm their creation with success messages. These files are stored temporarily in an `output_artifacts` directory for the application's current session.

<aside class="negative">
<b>Important:</b> Ensure you have added at least one AI system, computed risk tiers, and added at least one lifecycle risk before generating artifacts. Otherwise, the generated files might be empty or incomplete.
</aside>

## 6. Creating the Evidence Manifest for Integrity
Duration: 00:05:00

A crucial part of auditability is proving the integrity and immutability of your submitted documents. As an AI Program Lead, Sarah must provide cryptographic proof that the artifacts have not been tampered with. This is achieved by generating SHA-256 hashes for each file and compiling them into an `evidence_manifest.json`.

The SHA-256 algorithm produces a fixed-size hash value ($H$) for any input data ($M$). A tiny change in the input data will result in a completely different hash value, making it an excellent tool for detecting tampering:
$$ H = \text{SHA256}(M) $$
where $H$ is the SHA-256 hash value, and $M$ is the input data (the content of the artifact file).

### Generate Evidence Manifest

1.  After generating the core artifacts, click the "Generate Evidence Manifest" button.
2.  The application will compute a SHA-256 hash for each of the previously generated files and compile them into a new file, `evidence_manifest.json`.
3.  You will see a success message, and the content of the manifest will be displayed in the "Evidence Manifest Content" table, showing each file's name, path, and its unique SHA-256 hash.

<aside class="positive">
<b>Verification:</b> The evidence manifest acts as a digital fingerprint for your audit package. Auditors can use this manifest to verify that the files they receive are exactly the same as the ones you generated, ensuring trust and compliance.
</aside>

## 7. Packaging Audit-Ready Deliverables
Duration: 00:05:00

The final step is to package all the generated artifacts, including the `evidence_manifest.json`, into a single, downloadable ZIP archive. This simplifies submission to the auditors, ensuring that all required files are bundled together and easy to manage.

Navigate to the **Exports & Evidence** page, and scroll to the "Download Audit Package" section.

### Create and Download ZIP Archive

1.  Click the "Create and Download ZIP Archive" button.
2.  The application will bundle all generated files into a ZIP archive named `audit_package_ai_governance.zip`.
3.  Once created, a "Download Audit Package ZIP" button will appear. Click this button to download the entire package to your local machine.

You have now successfully completed the process of generating an audit-ready AI governance package, covering inventory, risk tiering, lifecycle risks, core artifacts, and cryptographic evidence of integrity. This comprehensive approach demonstrates a strong commitment to responsible AI deployment and accountability at Sentinel Financial.
