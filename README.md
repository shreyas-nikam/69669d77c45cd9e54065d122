# QuLab: Enterprise AI Lifecycle & Model Risk Classification

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## 🎯 Project Title and Description

**QuLab: Enterprise AI Lifecycle & Model Risk Classification** is a Streamlit application designed as a lab project to simulate an enterprise-grade AI governance workflow. It empowers AI Program Leads (like "Sarah" in the case study) to systematically manage and demonstrate accountability for AI systems within a financial institution.

The application guides users through critical stages of AI Model Risk Management (MRM), including:
1.  **AI System Inventory**: Documenting essential metadata for all AI systems.
2.  **Deterministic Risk Tiering**: Assigning risk tiers (Tier 1-3) based on a transparent scoring methodology, similar to SR 11-7 principles.
3.  **Lifecycle Risk Mapping**: Identifying and prioritizing specific risks across the AI system's lifecycle (design, deployment, operations).
4.  **Audit Artifact Generation**: Producing structured reports and summaries required for internal audits.
5.  **Cryptographic Evidence Manifest**: Generating a tamper-proof manifest with SHA-256 hashes of all audit artifacts to ensure data integrity.
6.  **Audit Package Export**: Bundling all deliverables into a single, downloadable ZIP archive.

This project is ideal for students and practitioners looking to understand the practical implementation of AI governance, risk management, and compliance in a regulated environment.

## ✨ Features

*   **Comprehensive AI System Inventory**:
    *   Add, edit, and delete AI system records with detailed metadata (name, description, domain, AI type, owner, criticality, data sensitivity, etc.).
    *   View the inventory in an interactive table.
*   **Deterministic Risk Tiering (SR 11-7-style)**:
    *   Automated calculation of risk scores based on predefined criteria (Decision Criticality, Data Sensitivity, Automation Level, AI Type, Deployment Mode, External Dependencies).
    *   Assignment of clear risk tiers (Tier 1: High, Tier 2: Medium, Tier 3: Low) with corresponding minimum required controls.
    *   Ability to add and update justification for assigned risk tiers.
    *   Mathematical formula for risk scoring displayed in-app.
*   **Lifecycle Risk Mapping**:
    *   Define and track specific risks associated with different phases of an AI system's lifecycle (Design, Development, Deployment, Operations, Decommissioning).
    *   Prioritize risks using a `Severity = Impact × Likelihood` calculation.
    *   Record mitigation strategies, owner roles, and evidence links for each risk.
*   **Audit Artifact Generation**:
    *   Export AI System Inventory as a `.csv` file.
    *   Export Risk Tiering results as a `.json` file.
    *   Export Lifecycle Risk Map as a `.json` file.
    *   Generate a structured Executive Summary in Markdown (`.md`) format, consolidating key insights.
*   **Cryptographic Evidence for Integrity**:
    *   Generate SHA-256 hashes for all produced artifacts.
    *   Compile hashes into an `evidence_manifest.json` file, ensuring the integrity and traceability of audit deliverables.
    *   Mathematical formula for SHA-256 hashing displayed in-app.
*   **Audit-Ready Package Export**:
    *   Download all generated artifacts and the `evidence_manifest.json` as a single, convenient ZIP archive.
*   **Intuitive User Interface**: Built with Streamlit for an interactive and user-friendly experience.
*   **Session State Management**: Persists data across user interactions within the application session.

## 🚀 Getting Started

Follow these instructions to set up and run the QuLab application on your local machine.

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/quLab-ai-governance.git # Replace with your actual repo URL
    cd quLab-ai-governance
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    The application relies on several Python libraries. Install them using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    If `requirements.txt` is not provided, you can create one with the following content:
    ```
    streamlit>=1.30.0
    pandas>=2.0.0
    pydantic>=2.0.0
    # Add any other specific versions if known
    ```

### Project Structure Notes

This project assumes the existence of a `source.py` file within the root directory. This file is critical as it contains:
*   Pydantic models (e.g., `SystemRecord`, `RiskTierResult`, `LifecycleRisk`, `EvidenceArtifact`, `EvidenceManifest`).
*   Enums (e.g., `AIType`, `DeploymentMode`, `DecisionCriticality`, `DataSensitivity`, `AutomationLevel`, `LifecyclePhase`, `RiskCategory`).
*   Helper functions (e.g., `calculate_risk_tier`, `export_dataframe_to_csv`, `export_pydantic_list_to_json`, `calculate_sha256`, `create_zip_archive`).
*   Initial data for the application (e.g., `ai_systems_data`, `initial_lifecycle_risks`).

Make sure your `source.py` file is correctly defined and located in the same directory as `app.py`.

## 🏃 Usage

To run the application, navigate to the project's root directory in your terminal and execute:

```bash
streamlit run app.py
```

This command will open the QuLab application in your default web browser (usually at `http://localhost:8501`).

### Basic Workflow

1.  **Home:** Read the case study and objectives.
2.  **AI System Inventory:**
    *   Review the pre-loaded AI systems.
    *   Use the "Add New AI System" form to register new systems.
    *   Select an existing system to "Edit or Delete AI System" if needed.
3.  **Risk Tiering:**
    *   Click "Compute Risk Tiers for All Systems" to apply the deterministic scoring logic.
    *   Review the "AI System Risk Tiering Results" table.
    *   Select a system to "Update Risk Tier Justification" as required.
4.  **Lifecycle Risk Mapping:**
    *   Review existing lifecycle risks (sorted by severity).
    *   Use the "Add New Lifecycle Risk" form to document potential risks for specific AI systems and phases.
5.  **Exports & Evidence:**
    *   Click "Generate All Core Artifacts" to create `model_inventory.csv`, `risk_tiering.json`, `lifecycle_risk_map.json`, and `case1_executive_summary.md` in the `output_artifacts/` directory.
    *   Click "Generate Evidence Manifest" to compute SHA-256 hashes for all generated files and compile them into `evidence_manifest.json`.
    *   Click "Create and Download ZIP Archive" to package all artifacts and the manifest into a single ZIP file for easy submission.

## 📁 Project Structure

```
.
├── app.py                  # Main Streamlit application script
├── source.py               # Contains Pydantic models, enums, helper functions, and initial data
├── requirements.txt        # List of Python dependencies
├── README.md               # This README file
└── output_artifacts/       # Directory created at runtime for generated audit files
    ├── model_inventory.csv
    ├── risk_tiering.json
    ├── lifecycle_risk_map.json
    ├── case1_executive_summary.md
    └── evidence_manifest.json
    └── audit_package_ai_governance_<timestamp>.zip
```

## 🛠 Technology Stack

*   **Frontend/Backend Framework**: [Streamlit](https://streamlit.io/) (for building interactive web applications in Python)
*   **Programming Language**: [Python](https://www.python.org/) (version 3.9+)
*   **Data Handling**: [Pandas](https://pandas.pydata.org/) (for DataFrame operations and CSV exports)
*   **Data Validation & Serialization**: [Pydantic](https://docs.pydantic.dev/latest/) (for defining robust data schemas and models)
*   **Serialization**: `json` (for JSON exports)
*   **File System Operations**: `os`, `shutil` (for directory management and ZIP archive creation)
*   **Unique Identifiers**: `uuid` (for generating unique IDs)
*   **Date/Time**: `datetime` (for timestamping artifacts)
*   **Cryptographic Hashing**: `hashlib` (used within `source.py` for SHA-256 generation)
*   **In-app Equations**: LaTeX via Streamlit's `st.markdown` for mathematical formulas.

## 🤝 Contributing

As a lab project, direct contributions might not be the primary focus, but feedback, bug reports, and suggestions for improvement are always welcome!

1.  **Fork the repository.**
2.  **Create a new branch** (`git checkout -b feature/AmazingFeature`).
3.  **Make your changes.**
4.  **Commit your changes** (`git commit -m 'Add some AmazingFeature'`).
5.  **Push to the branch** (`git push origin feature/AmazingFeature`).
6.  **Open a Pull Request.**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (If a LICENSE file is not present, consider creating one).

## ✉️ Contact

For questions, suggestions, or further information, please contact:

*   **QuantUniversity** (The organization behind QuLab)
    *   Website: [www.quantuniversity.com](https://www.quantuniversity.com)
    *   General Inquiries: info@quantuniversity.com
*   **Project Lead / Developer**: [Your Name/GitHub Username]
    *   GitHub: [https://github.com/yourusername](https://github.com/yourusername)
    *   Email: [your.email@example.com] (Optional)
