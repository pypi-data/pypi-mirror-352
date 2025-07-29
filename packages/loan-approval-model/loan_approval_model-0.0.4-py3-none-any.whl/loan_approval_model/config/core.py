from pathlib import Path
import loan_approval_model
from pydantic import BaseModel
from strictyaml import YAML, load
from typing import List, Optional, Sequence

# Project Directories
PACKAGE_ROOT = Path(loan_approval_model.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_PATH = Path(__file__).parent.parent / "config.yml"
DATASET_DIR = PACKAGE_ROOT / "datasets"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_model"
LOG_DIR = PACKAGE_ROOT / "logs"


class AppConfig(BaseModel):
    """
    Application-level configuration.
    """
    package_name: str = "loan_approval_model"
    training_data_file: str = "train.csv"
    test_data_file: str = "test.csv"
    pipeline_save_file: str = "naive_bayes_loan_model.pkl"
    ordinal_encoder_file: str = "ordinal_encoder.pkl"
    label_encoder_file: str = "label_encoder.pkl"

class ModelConfig(BaseModel):
    target: str
    features: List[str]
    variables_to_drop: Sequence[str]
    categorical_vars: Sequence[str]
    numerical_vars: Sequence[str]
    categorical_vars_with_na: List[str]
    numerical_vars_with_na: List[str]
    test_size: float = 0.2
    random_state: int = 42
    alpha: float = 1.0  # Добавьте этот параметр
    model_type: str = "GaussianNB"  # Добавьте этот параметр

class Config(BaseModel):
    """
    Master configuration object.
    """
    app_config: AppConfig
    model_config_params: ModelConfig


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_PATH.is_file():
        return CONFIG_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Optional[Path] = None) -> YAML:
    """Parse YAML containing the package configuration."""
    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    # Specify the data attribute from the strictyaml YAML type.
    _config = Config(
        app_config=AppConfig(**parsed_config.data),
        model_config_params=ModelConfig(**parsed_config.data),
    )
    return _config


def get_config() -> Config:
    """Create and validate config from yaml."""
    try:
        return create_and_validate_config()
    except FileNotFoundError:
        # If config file not found, use defaults
        default_config = Config(
            app_config=AppConfig(),
            model_config=ModelConfig()
        )
        return default_config


config = get_config()