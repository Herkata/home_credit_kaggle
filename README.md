# Home Credit Risk Prediction

This project is part of a Kaggle competition aimed at predicting the probability of a loan applicant defaulting on their loan. By leveraging machine learning techniques, the goal is to assist Home Credit in making smarter and more reliable credit decisions.

## Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [Modeling Approach](#modeling-approach)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Home Credit Risk Prediction project focuses on analyzing customer data to predict the likelihood of loan repayment. This involves handling a large dataset, performing feature engineering, and building predictive models to achieve high accuracy.

The project is structured into three notebooks:
- [credit_EDA_prep.ipynb](credit_EDA_prep.ipynb): Exploratory Data Analysis and Data Preparation
- [credit_stat_inf.ipynb](credit_stat_inf.ipynb): Statistical Inference
- [credit_risk_ML.ipynb](credit_risk_ML.ipynb): Machine Learning Model Development - created in Google Colab

Write-up on the project plan: [Checklist and Plan](checklist.md)

## Dataset
The dataset is provided by Home Credit and is available on the [Kaggle competition page](https://www.kaggle.com/c/home-credit-default-risk). It includes:
- Application data
- Bureau and bureau balance data
- Previous application data
- Credit card balance data
- POS cash balance data
- Installments payments data


## Modeling Approach
- **Data Cleaning**: Handle missing values, outliers, and inconsistent data.
- **Feature Engineering**: Create meaningful features from raw data.
- **Model Selection**: Experiment with various machine learning models such as Logistic Regression, Random Forest, and Gradient Boosting (e.g., LightGBM, XGBoost).
- **Evaluation**: Use metrics like AUC-ROC to evaluate model performance.
- **Hyperparameter Tuning**: Optimize model parameters using techniques like Grid Search or Random Search.
- **Ensemble Methods**: Combine multiple models to improve prediction accuracy.

## Results
The final model achieved an AUC-ROC score of **0.74** on the test set.

## License
This project is licensed under the [MIT License](LICENSE).
