# Kidnapping Analysis and Modeling in Colombia

## Description  
This repository contains the code and data for a comprehensive study of kidnappings in Colombia (1996–2025). It starts with monthly and annual time series, normalizes counts using rates per 100,000 inhabitants, incorporates armed violence proxies (massacres, selective killings, conflict categories) and institutional variables (CAIs, police personnel). Finally, it compares panel models (Fixed Effects Regression), machine learning (XGBoost), and deep learning (neural network) to predict the number of kidnappings. Each model is trained via exhaustive hyperparameter search, accompanied by SHAP interpretations to explain their results.

## Repository Contents

| File / Notebook                                | Purpose                                                                                                      |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| **`1. Exploratory_Analysis.ipynb`**           | A standalone analysis of the kidnapping dataset with interactive widgets and statistical/geospatial analysis by municipality and department. |
| **`2. Composite_Analysis.ipynb`**             | Creates the kidnapping rate per 100k inhabitants and includes multiple variables to capture national violence and institutional strength. |
| **`3. Advanced_Analysis.ipynb`**              | Uses the dataset from scripts 1–2 to run correlation analysis, PCA, panel data regressions, and ML/DL models (XGBoost & PyTorch), each with hyperparameter tuning. |
| **`construccion_bases_series.py`**           | Contains four functions used throughout the project to clean and format the data as needed.                 |
| **`Datos`**                                  | A folder with all data sources used in the project, both tabular and geospatial.                            |

## Key Findings  
- **Historical Cycles**: Kidnapping peak between 1998–2002 linked to FARC and paramilitaries, followed by stabilization.  
- **Hidden Geography**: When normalizing by population, low-density municipalities (Plains, South) emerge with extreme rates (“miracle fishings”).  
- **Deterrent Effect**: Each additional CAI reduces ~0.8 kidnappings/month; post-demobilization also significantly lowers incidence.  
- **Predictive Models**:  
  - **PanelOLS** (Within R² ≈ 0.19) identifies causal coefficients for violence and institutional variables.  
  - **XGBoost** (R² ≈ 0.84, MAE ≈ 1.51) trained with 150 trees, offering an excellent balance of accuracy and speed.  
  - **Neural Network (PyTorch)** (R² ≈ 0.89) with 3 hidden layers maximizes R² and delivers outstanding performance. With a powerful GPU, both ML and DL models train quickly; while XGBoost seems near its limit with current data, the neural network could still benefit from Bayesian hyperparameter search.  
- **SHAP**: The “Slightly Affected & Persistent” category and the rate per 100,000 inhabitants are the most influential features for predicting kidnappings.

## Installation

To get the code and data on your machine, clone the repository and navigate to the project folder:

```bash
git clone https://github.com/SPMINE-2425/primer_repo_pablo.git
cd primer_repo_pablo
```

## Licencia  
This project is released under the MIT License.
