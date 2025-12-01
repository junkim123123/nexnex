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