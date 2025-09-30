"""
ML Model Iteration Framework
Continuous improvement of health scoring and prediction models based on real data
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, roc_auc_score
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_version: str
    trained_date: datetime
    training_samples: int

    # Classification metrics (risk category prediction)
    risk_classification_accuracy: float
    risk_auc_score: float

    # Regression metrics (cost prediction)
    cost_prediction_mae: float  # Mean Absolute Error
    cost_prediction_r2: float  # R-squared

    # Business metrics
    avg_prediction_error_pct: float  # Average % error in cost predictions
    high_risk_recall: float  # % of high-risk members correctly identified

    # Model calibration
    calibration_score: float  # How well predicted probabilities match actual outcomes


@dataclass
class ModelFeature:
    """Feature importance for interpretability"""
    feature_name: str
    importance_score: float
    feature_type: str  # 'demographic', 'clinical', 'behavioral', 'utilization'


class ModelIterationFramework:
    """
    Framework for iteratively improving ML models based on actual outcomes.

    Process:
    1. Collect actual outcomes (claims, health changes)
    2. Compare predictions vs reality
    3. Retrain models with new data
    4. A/B test new model vs current
    5. Deploy if improved
    """

    def __init__(self, model_registry_path: str = "./models"):
        self.model_registry_path = model_registry_path
        self.current_model_version = "1.0.0"

    def collect_training_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Collect training data from database.

        Combines:
        - Member demographics
        - Health profiles (biometrics, conditions, medications)
        - Wearable data (30-day aggregates)
        - Claims history
        - Actual outcomes (health score changes, costs)

        Returns:
            DataFrame with features and targets
        """
        # In production: query from database
        # For now, return schema
        logger.info(f"Collecting training data from {start_date} to {end_date}")

        # Example schema
        features = [
            # Demographics
            'age', 'gender',

            # Biometrics
            'bmi', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'glucose_level', 'cholesterol_total', 'cholesterol_hdl', 'cholesterol_ldl',

            # Behavioral
            'smoker', 'alcohol_use_numeric', 'avg_daily_steps', 'avg_sleep_hours',
            'exercise_minutes_per_week', 'stress_level',

            # Clinical
            'chronic_condition_count', 'medication_count',
            'has_diabetes', 'has_hypertension', 'has_heart_disease',

            # Utilization (past 12 months)
            'emergency_visits', 'hospital_admissions', 'primary_care_visits',
            'specialist_visits', 'total_claims_cost',

            # Targets
            'actual_risk_score', 'actual_annual_cost', 'risk_category'
        ]

        # In production, return actual data
        return pd.DataFrame()

    def evaluate_model_performance(
        self,
        model,
        X_test: pd.DataFrame,
        y_test_risk: np.ndarray,
        y_test_cost: np.ndarray
    ) -> ModelPerformance:
        """
        Comprehensive evaluation of model performance.

        Args:
            model: Trained model
            X_test: Test features
            y_test_risk: Actual risk scores
            y_test_cost: Actual costs

        Returns:
            ModelPerformance with all metrics
        """
        # Make predictions
        risk_pred = model.predict_risk(X_test)
        cost_pred = model.predict_cost(X_test)

        # Classification metrics
        risk_categories_actual = self._risk_score_to_category(y_test_risk)
        risk_categories_pred = self._risk_score_to_category(risk_pred)
        accuracy = np.mean(risk_categories_actual == risk_categories_pred)

        # If model provides probabilities
        try:
            risk_probs = model.predict_risk_proba(X_test)
            auc = roc_auc_score(risk_categories_actual, risk_probs, multi_class='ovr')
        except:
            auc = 0.0

        # Regression metrics
        cost_mae = mean_absolute_error(y_test_cost, cost_pred)
        cost_r2 = r2_score(y_test_cost, cost_pred)

        # Business metrics
        cost_error_pct = np.mean(np.abs(cost_pred - y_test_cost) / y_test_cost) * 100

        # High-risk recall (critical for intervention targeting)
        high_risk_actual = risk_categories_actual >= 2  # High or Critical
        high_risk_pred = risk_categories_pred >= 2
        high_risk_recall = np.sum(high_risk_actual & high_risk_pred) / np.sum(high_risk_actual)

        return ModelPerformance(
            model_version=self.current_model_version,
            trained_date=datetime.utcnow(),
            training_samples=len(X_test),
            risk_classification_accuracy=accuracy,
            risk_auc_score=auc,
            cost_prediction_mae=cost_mae,
            cost_prediction_r2=cost_r2,
            avg_prediction_error_pct=cost_error_pct,
            high_risk_recall=high_risk_recall,
            calibration_score=0.0  # Would calculate calibration curve
        )

    def analyze_feature_importance(
        self,
        model,
        feature_names: List[str]
    ) -> List[ModelFeature]:
        """
        Extract and rank feature importance for model interpretability.

        Important for:
        - Understanding what drives risk scores
        - Regulatory compliance (explainability)
        - Identifying intervention opportunities
        """
        try:
            # For tree-based models (XGBoost)
            importances = model.feature_importances_

            features = []
            for name, importance in zip(feature_names, importances):
                # Categorize feature
                if name in ['age', 'gender']:
                    feature_type = 'demographic'
                elif name in ['bmi', 'blood_pressure_systolic', 'glucose_level']:
                    feature_type = 'clinical'
                elif name in ['avg_daily_steps', 'smoker', 'avg_sleep_hours']:
                    feature_type = 'behavioral'
                else:
                    feature_type = 'utilization'

                features.append(ModelFeature(
                    feature_name=name,
                    importance_score=float(importance),
                    feature_type=feature_type
                ))

            # Sort by importance
            features.sort(key=lambda x: x.importance_score, reverse=True)

            logger.info(f"Top 5 features: {[f.feature_name for f in features[:5]]}")

            return features

        except Exception as e:
            logger.error(f"Failed to extract feature importance: {e}")
            return []

    def compare_models(
        self,
        current_model_performance: ModelPerformance,
        new_model_performance: ModelPerformance
    ) -> Dict[str, any]:
        """
        Compare new model against current production model.

        Decision criteria:
        1. Cost prediction must improve (lower MAE)
        2. High-risk recall must not decrease significantly
        3. Overall accuracy should improve
        4. Business impact (expected savings) should increase
        """
        improvements = {
            'cost_mae_improved': new_model_performance.cost_prediction_mae < current_model_performance.cost_prediction_mae,
            'accuracy_improved': new_model_performance.risk_classification_accuracy > current_model_performance.risk_classification_accuracy,
            'high_risk_recall_maintained': new_model_performance.high_risk_recall >= (current_model_performance.high_risk_recall - 0.05),
            'auc_improved': new_model_performance.risk_auc_score > current_model_performance.risk_auc_score,
        }

        # Calculate improvement percentages
        mae_improvement_pct = (
            (current_model_performance.cost_prediction_mae - new_model_performance.cost_prediction_mae) /
            current_model_performance.cost_prediction_mae * 100
        )

        accuracy_improvement_pct = (
            (new_model_performance.risk_classification_accuracy - current_model_performance.risk_classification_accuracy) /
            current_model_performance.risk_classification_accuracy * 100
        )

        # Deployment recommendation
        deploy_recommended = (
            improvements['cost_mae_improved'] and
            improvements['high_risk_recall_maintained'] and
            improvements['accuracy_improved']
        )

        return {
            'improvements': improvements,
            'mae_improvement_pct': mae_improvement_pct,
            'accuracy_improvement_pct': accuracy_improvement_pct,
            'deploy_recommended': deploy_recommended,
            'summary': self._generate_comparison_summary(
                current_model_performance,
                new_model_performance,
                improvements
            )
        }

    def _risk_score_to_category(self, scores: np.ndarray) -> np.ndarray:
        """Convert risk scores to categories (0=low, 1=moderate, 2=high, 3=critical)"""
        return np.digitize(scores, bins=[30, 60, 85])

    def _generate_comparison_summary(
        self,
        current: ModelPerformance,
        new: ModelPerformance,
        improvements: Dict[str, bool]
    ) -> str:
        """Generate human-readable comparison summary"""
        summary = f"""
Model Comparison: {current.model_version} vs {new.model_version}

Risk Classification:
  Current Accuracy: {current.risk_classification_accuracy:.2%}
  New Accuracy:     {new.risk_classification_accuracy:.2%}
  Change:           {'+' if improvements['accuracy_improved'] else '-'}{abs(new.risk_classification_accuracy - current.risk_classification_accuracy):.2%}

Cost Prediction:
  Current MAE: ${current.cost_prediction_mae:,.0f}
  New MAE:     ${new.cost_prediction_mae:,.0f}
  Change:      {'-' if improvements['cost_mae_improved'] else '+'}{abs(new.cost_prediction_mae - current.cost_prediction_mae):,.0f}

High-Risk Detection:
  Current Recall: {current.high_risk_recall:.1%}
  New Recall:     {new.high_risk_recall:.1%}
  Status:         {'✓ Maintained' if improvements['high_risk_recall_maintained'] else '✗ Degraded'}

Recommendation: {'DEPLOY' if all(improvements.values()) else 'HOLD for further testing'}
"""
        return summary

    def log_model_experiment(
        self,
        experiment_name: str,
        model_config: Dict,
        performance: ModelPerformance,
        feature_importance: List[ModelFeature]
    ):
        """
        Log model experiment for tracking and reproducibility.

        In production: Use MLflow or similar
        """
        experiment_log = {
            'experiment_name': experiment_name,
            'timestamp': datetime.utcnow().isoformat(),
            'model_version': performance.model_version,
            'model_config': model_config,
            'performance_metrics': {
                'risk_accuracy': performance.risk_classification_accuracy,
                'cost_mae': float(performance.cost_prediction_mae),
                'cost_r2': performance.cost_prediction_r2,
                'high_risk_recall': performance.high_risk_recall,
            },
            'top_10_features': [
                {'name': f.feature_name, 'importance': f.importance_score}
                for f in feature_importance[:10]
            ]
        }

        logger.info(f"Logging experiment: {experiment_name}")
        # In production: save to MLflow/database
        # mlflow.log_experiment(experiment_log)


# Example iteration workflow
if __name__ == "__main__":
    framework = ModelIterationFramework()

    print("""
    ═══════════════════════════════════════════════════════════════════════
    VitaNexus ML Model Iteration Framework
    ═══════════════════════════════════════════════════════════════════════

    Workflow:
    1. Collect training data (demographics, health, wearables, claims)
    2. Train new model with latest data
    3. Evaluate performance on hold-out test set
    4. Compare against current production model
    5. A/B test if performance improves
    6. Deploy if A/B test validates improvement
    7. Monitor post-deployment performance

    Key Metrics:
    - Cost Prediction MAE: How accurately we predict healthcare costs
    - High-Risk Recall: % of high-risk members we correctly identify
    - Risk Classification Accuracy: Overall risk category prediction
    - Feature Importance: What factors most influence risk

    Iteration Frequency:
    - Weekly: Retrain with new member data
    - Monthly: Full model evaluation and comparison
    - Quarterly: Architecture review and potential model replacement

    This ensures our models continuously improve as we collect more
    real-world data, making predictions more accurate and interventions
    more effective over time.
    ═══════════════════════════════════════════════════════════════════════
    """)