"""Configuration settings for GroundCrew"""

from .models import VerifaiConfig, VerifaiModeEnum



def get_config(config: VerifaiModeEnum):
    match config:
        case VerifaiModeEnum.FAST: 
            return _FAST_CONFIG
        case VerifaiModeEnum.HIGH:
            return _HIGH_QUALITY_CONFIG
        case  _:
            return _DEFAULT_CONFIG

def get_all_configs():
    return {
        "default": _DEFAULT_CONFIG.model_dump(),
        "fast": _FAST_CONFIG.model_dump(),
        "high": _HIGH_QUALITY_CONFIG.model_dump(),
    }

# Default configuration
_DEFAULT_CONFIG = VerifaiConfig()

# High-quality configuration (slower, more accurate)
_HIGH_QUALITY_CONFIG = VerifaiConfig(
    model_name="openai:gpt-4o",
    max_search_results_per_query=5,
    max_queries_per_claim=3,
    max_evidence_per_claim=10
)

# Fast configuration (faster, lower cost)
_FAST_CONFIG = VerifaiConfig(
    model_name="openai:gpt-4o-mini",
    max_search_results_per_query=2,
    max_queries_per_claim=1,
    max_evidence_per_claim=3,
    search_depth="basic"
)
