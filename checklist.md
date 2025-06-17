
# Machine Learning Project Checklist (Home Credit Default Risk)

## 1. Frame the Problem and Look at the Big Picture

**1.1. Define the objective in business terms:**

* Develop a robust risk evaluation service for retail banks, leveraging the Home Credit dataset to predict loan default probabilities.
* Provide accurate and reliable risk assessments for both new and existing clients, enabling optimized loan approval decisions and risk management.

**1.2. How will the solution be used?**

* Integrate the risk evaluation service into bank loan approval workflows.
* Generate probability scores representing the likelihood of loan default.
* Enable banks to:
    * Automate loan approvals based on custom risk thresholds.
    * Dynamically adjust interest rates based on predicted risk.
    * Enhance portfolio risk management and reduce losses.

**1.3. What are the current solutions/workarounds?**

* Existing solutions include traditional credit scoring models (e.g., FICO), manual assessments, and internal statistical models.
* This solution aims to improve accuracy and comprehensiveness by utilizing machine learning on a broader dataset.

**1.4. How should the problem be framed?**

* **Supervised binary classification** with probability output.
* Predict the probability of loan default (0 or 1) based on applicant features.
* Focus on probability estimation rather than strict boolean classification for better risk assessment.
* Using probabilities allows the banks to define their own thresholds for automated processes.

**1.5. How should performance be measured?**

* **Primary Metric: Area Under the ROC Curve (AUC-ROC)** - Crucial for assessing the model's ability to rank applicants by risk.
* **Secondary Metrics:**
    * **Log Loss (Binary Cross-Entropy):** Quantifies the model's probabilistic accuracy.
    * **Precision and Recall:** Evaluate trade-offs between false positives and false negatives.
    * **F1-Score:** Balances precision and recall.
    * **Confusion Matrix:** Understand types of errors.
* **Calibration of probabilities:** Verify that the predicted probabilities match the actual observed frequencies.

**1.6. Check assumptions:**

* The Home Credit dataset is representative of the target market's loan default patterns.
* Features in the dataset are relevant and predictive of loan defaults.
* Banks will adopt and effectively utilize the risk evaluation service.
* Data accuracy and reliability are assumed.
* The imbalance in the data will be properly handled.

## 2. Get the Data:

* **Data Requirements:**
    * Home Credit Default Risk dataset from Kaggle.
    * Ensure sufficient statistical power for the minority class (defaults).
* **Data Sources:**
    * [Kaggle Competition: Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk/data)
    * Data description available on Kaggle and in project repository.
* **Storage and Legal:**
    * Approx. 3 GB storage required.
    * Implement strict access control due to sensitive data.
    * Adhere to all legal obligations regarding data privacy.
* **Workspace and Retrieval:**
    * Set up local development environment.
    * Download and store data securely.
* **Data Sampling:**
    * Utilize provided train and test splits.
    * Verify no data leakage (duplicates) between train and test sets.

## 3. Explore the Data:

* Create a copy of the data for exploration.
* Develop a Jupyter notebook for detailed documentation.
* Analyze attribute types, missing values, noise, and distributions.
* Visualize data and identify correlations.
* Determine necessary feature engineering and transformations.

## 4. Prepare the Data:

* Work on data copies and create reusable functions.
* **Data Cleaning:**
    * Address missing values (imputation, removal).
    * Handle outliers (detection, treatment).
* **Feature Selection:**
    * Identify and select relevant features.
    * Consider feature importance from tree-based models.
* **Feature Engineering:**
    * Create new features (e.g., ratios, aggregations).
    * Address data imbalance (oversampling, undersampling, class weights).
* **Feature Scaling:**
    * Normalize or standardize features for model compatibility.

## 5. Shortlist Promising Models:

* Train and evaluate various models quickly (e.g., Logistic Regression, LightGBM, XGBoost, Random Forest).
* Measure performance using AUC-ROC and log loss.
* Analyze feature importance and model errors.
* Iterate on model training and evaluation.

## 6. Fine-Tune the System:

* Hyperparameter tuning using Optuna.
* Explore ensemble methods - Voting.
* Evaluate the final model on the test set using AUC-ROC and other relevant metrics.
* Calibrate the model probabilities.

## 7. Present Your Solution:

* Document the entire process in a comprehensive report.
* Create a clear and concise presentation.
* Demonstrate how the solution meets the business objectives.

## 8. Launch, Monitor, and Maintain Your System:

* Prepare the model for production deployment using Google CLoud and Flask.
* Suggest improvements.
