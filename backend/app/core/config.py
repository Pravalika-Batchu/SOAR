import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = "Trust-Aware SOAR"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "trust-aware-soar-development-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trust_soar.db")
    
    # Network Adapter Mode ("MOCK" or "RYU")
    NETWORK_ADAPTER_MODE: str = os.getenv("NETWORK_ADAPTER_MODE", "MOCK")
    RYU_ENDPOINT: str = os.getenv("RYU_ENDPOINT", "http://localhost:8080")
    MININET_SUBNET: str = os.getenv("MININET_SUBNET", "10.0.0.0/24")
    
    # Dynamic Autonomy Default Thresholds
    AUTONOMY_THRESHOLD_HIGH: float = float(os.getenv("AUTONOMY_THRESHOLD_HIGH", "0.85"))
    AUTONOMY_THRESHOLD_LOW: float = float(os.getenv("AUTONOMY_THRESHOLD_LOW", "0.55"))
    
    # Weights for Response Reliability
    W_THREAT_CONFIDENCE: float = 0.25
    W_HISTORICAL_SUCCESS: float = 0.25
    W_POLICY_FIT: float = 0.20
    W_QOS_RISK: float = 0.15
    W_RESOURCE_RISK: float = 0.05
    W_UNCERTAINTY: float = 0.10

settings = Settings()
