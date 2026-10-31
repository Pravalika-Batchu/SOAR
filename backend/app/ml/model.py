import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from app.ml.features import FlowFeatureVector, extract_features_from_raw_flow

@dataclass
class AnomalyPrediction:
    is_anomaly: bool
    raw_decision_score: float
    normalized_anomaly_score: float # 0.0 (nominal) to 1.0 (extreme anomaly)
    uncertainty: float # 0.0 (high confidence) to 1.0 (boundary ambiguity)
    explanation: str

class IsolationForestDetector:
    """
    Local Anomaly Detector using Scikit-Learn Isolation Forest.
    Trained strictly on normal background traffic patterns to detect out-of-distribution
    threats, high-volume DoS spikes, port scan fan-outs, and unusual exfiltration.
    """
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=100,
            max_samples='auto',
            contamination=contamination,
            random_state=random_state,
            n_jobs=1
        )
        self.is_fitted = False

    def generate_synthetic_normal_baseline(self, num_samples: int = 1000) -> np.ndarray:
        """
        Synthesizes nominal network background traffic distribution:
        Standard web browsing, DNS queries, SSH administration, and periodic pings.
        """
        np.random.seed(self.random_state)
        # Normal pps: log-normal around 15-50 pps
        pps = np.random.exponential(scale=30.0, size=num_samples) + 5.0
        # Normal bps: roughly 500-1500 bytes per packet
        pkt_size = np.random.normal(loc=700.0, scale=150.0, size=num_samples)
        pkt_size = np.clip(pkt_size, 64.0, 1500.0)
        bps = pps * pkt_size
        # Normal connections: 1 to 10
        conns = np.random.poisson(lam=4, size=num_samples) + 1
        # Normal unique destinations: 1 to 4
        dests = np.random.poisson(lam=2, size=num_samples) + 1
        # Duration: 0.5 to 10 seconds
        durations = np.random.exponential(scale=3.0, size=num_samples) + 0.2
        # Failed ratio: near zero (0.0 to 0.05)
        failed_ratios = np.random.beta(a=0.5, b=20.0, size=num_samples)
        # Volume variation: moderate (0.1 to 0.3)
        vol_vars = np.random.uniform(low=0.05, high=0.35, size=num_samples)

        X = np.column_stack([
            pps, bps, conns, dests, pkt_size, durations, failed_ratios, vol_vars
        ])
        return X

    def train_baseline(self, custom_normal_data: Optional[np.ndarray] = None):
        """Fit Isolation Forest on normal baseline traffic."""
        data = custom_normal_data if custom_normal_data is not None else self.generate_synthetic_normal_baseline()
        self.model.fit(data)
        self.is_fitted = True

    def predict(self, feature_vector: FlowFeatureVector) -> AnomalyPrediction:
        """
        Evaluates a flow feature vector. Computes:
        - raw decision function
        - normalized anomaly score [0.0, 1.0]
        - uncertainty based on proximity to isolation boundary
        """
        if not self.is_fitted:
            self.train_baseline()

        x = feature_vector.to_array()
        pred = self.model.predict(x)[0] # -1 for anomaly, 1 for inlier
        raw_score = float(self.model.decision_function(x)[0])

        # Isolation forest raw score: >0 is normal, <0 is anomaly
        # Typically between -0.35 (extreme anomaly) and +0.25 (typical normal)
        # Normalize to [0.0, 1.0] where 1.0 is highest anomaly
        normalized_anomaly = 1.0 / (1.0 + np.exp(raw_score * 12.0))
        normalized_anomaly = float(np.clip(normalized_anomaly, 0.0, 1.0))
        normalized_anomaly = round(normalized_anomaly, 4)

        # Proximity to decision boundary (raw_score == 0.0) yields highest uncertainty
        # If |raw_score| < 0.05 -> High uncertainty
        dist_from_boundary = abs(raw_score)
        uncertainty = float(np.exp(-dist_from_boundary * 20.0))
        uncertainty = round(float(np.clip(uncertainty, 0.05, 0.85)), 4)

        is_anom = bool(pred == -1 or normalized_anomaly > 0.65)

        reasons = []
        if is_anom:
            if feature_vector.packets_per_second > 500.0:
                reasons.append(f"Abnormal packet velocity ({feature_vector.packets_per_second:.0f} pps).")
            if feature_vector.unique_destination_count > 15.0:
                reasons.append(f"High destination dispersion ({feature_vector.unique_destination_count:.0f} targets).")
            if feature_vector.failed_connection_ratio > 0.40:
                reasons.append(f"High TCP failure/RST ratio ({feature_vector.failed_connection_ratio:.0%}).")
            if not reasons:
                reasons.append("Multi-dimensional out-of-distribution deviation detected.")
            explanation = f"Anomaly detected (Score: {normalized_anomaly:.2f}). " + " ".join(reasons)
        else:
            explanation = f"Traffic flow conforms to nominal baseline distribution (Anomaly score: {normalized_anomaly:.2f})."

        return AnomalyPrediction(
            is_anomaly=is_anom,
            raw_decision_score=round(raw_score, 4),
            normalized_anomaly_score=normalized_anomaly,
            uncertainty=uncertainty,
            explanation=explanation
        )

    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                self.model = pickle.load(f)
            self.is_fitted = True

# Global model instance
detector = IsolationForestDetector()
detector.train_baseline()

