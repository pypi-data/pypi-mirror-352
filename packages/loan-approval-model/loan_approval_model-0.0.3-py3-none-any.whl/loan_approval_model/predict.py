import typing as t

import pandas as pd

from loan_approval_model import __version__ as _version
from loan_approval_model import config
from loan_approval_model.processing.data_manager import load_pipeline
from loan_approval_model.processing.validation import validate_inputs

pipeline_file_name = f"{config.app_config.pipeline_save_file}{_version}.pkl"
_loan_pipe = load_pipeline(file_name=pipeline_file_name)


def make_prediction(
        *,
        input_data: t.Union[pd.DataFrame, dict, list[dict]],
        threshold: float = 0.5  # Добавляем параметр порога
) -> dict:
    """Make a loan approval prediction with customizable threshold."""

    # Преобразование входных данных
    if isinstance(input_data, dict):
        data = pd.DataFrame([input_data])
    else:
        data = pd.DataFrame(input_data)

    validated_data, errors = validate_inputs(input_data=data)
    results: t.Dict[str, t.Any] = {"preds": None, "probs": None, "version": _version, "errors": errors}

    if not errors:
        # Получаем вероятности для класса 1 (одобрено)
        probs = _loan_pipe.predict_proba(X=validated_data[config.model_config_params.features])[:, 1]

        # Применяем кастомный порог
        preds = (probs >= threshold).astype(int)

        results["preds"] = preds.tolist()
        results["probs"] = probs.tolist()

    return results