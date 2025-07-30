"""Feature flags for Trustwise SDK."""


# Set of features that are currently in beta
BETA_FEATURES: set[str] = {
    "guardrails",
}

def is_beta_feature(feature_name: str) -> bool:
    """
    Check if a feature is currently in beta.
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        bool: True if the feature is in beta, False otherwise
    """
    return feature_name.lower() in BETA_FEATURES

def get_beta_features() -> set[str]:
    """
    Get the set of all features currently in beta.
    
    Returns:
        Set[str]: Set of feature names that are in beta
    """
    return BETA_FEATURES.copy() 