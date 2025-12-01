# Data Pipeline Overview

This document outlines the architecture and implementation of the data pipeline for the NexSupply-AI project.

## 1. Existing Data Structures

The core data models are defined in `core/models.py`. The key models for the data pipeline are:

- **`ShipmentSpec`**: This model captures the structured data from a user's natural language input. It includes product name, quantity, origin/destination, pricing, and other details. The data pipeline will be responsible for providing the data to populate this model.
- **`AnalysisResult`**: This is the main output model that is passed to the UI. It contains the `ShipmentSpec` as well as other analysis results.

Other relevant models include:
- **`CostBreakdown`**: Contains the manufacturing, shipping, duty, and misc costs.
- **`ProfitabilityMetrics`**: Includes retail price, DDP, FBA fees, and marketing costs.

## 2. Proposed Folder Structure

The following folder structure is proposed for the data pipeline:

- **`/data_pipeline/`**: This directory will contain all the scripts for fetching and processing data.
  - `fetch_freight.py`: Script for fetching and processing freight data.
  - `fetch_duties.py`: Script for fetching and processing duty data.
  - `fetch_reference_transactions.py`: Script for fetching and processing reference transaction data.
  - `config.py`: Configuration file for the data pipeline.
  - `fetch_all.py`: Entrypoint script that calls all the other fetch scripts.
- **`/data/raw/`**: This directory will store the raw data files downloaded from various sources.
- **`/data/processed/`**: This directory will store the processed and cleaned data files that are ready to be used by the application.

This structure will ensure that the data pipeline is decoupled from the main application and that the data is stored in a structured and organized manner.
## 3. Running the Pipeline

### Local Execution

To run the data pipeline locally, execute the following command from the root of the project:

```bash
python -m data_pipeline.fetch_all
```

This will process the raw CSV files from `data/raw/` and output the processed files into `data/processed/`.

### Automated Execution with GitHub Actions

The data pipeline is configured to run automatically every day at 04:00 UTC using a GitHub Actions workflow. The workflow is defined in `.github/workflows/data-pipeline.yml`.

The workflow will:
- Set up the Python environment and install the required dependencies.
- Run the main data pipeline script.
- Commit and push any changes to the processed data files back to the repository.

### Required Secrets

The GitHub Actions workflow requires the following secrets to be configured in the repository settings:

- `GEMINI_API_KEY`: The API key for the Gemini API.
- `SUPABASE_URL`: The URL for the Supabase project.
- `SUPABASE_KEY`: The API key for the Supabase project.

These secrets are used to access the necessary services for the data pipeline and should be kept confidential.
### Security Notes

To maintain the security of the data pipeline, all sensitive information, such as API keys and secrets, must be stored as environment variables or in a secure secret management service like Google Secret Manager. 

The following files should never contain actual keys:
- `config.py`
- `docker-compose.yml`
- Any files in the `.github/workflows` directory

The `core/security/secrets.py` module is designed to handle secrets securely, and the `utils/secure_logger.py` module automatically masks sensitive data in logs to prevent accidental exposure.