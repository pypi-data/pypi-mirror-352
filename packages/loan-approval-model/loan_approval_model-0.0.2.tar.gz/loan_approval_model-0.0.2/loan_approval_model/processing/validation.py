from typing import List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel

from loan_approval_model import config


def drop_na_inputs(*, input_data: pd.DataFrame) -> pd.DataFrame:
    """Check model inputs for na values and filter."""
    validated_data = input_data.copy()
    new_vars_with_na = [
        var
        for var in config.model_config_params.features
        if
        var not in config.model_config_params.categorical_vars_with_na + config.model_config_params.numerical_vars_with_na
        and validated_data[var].isnull().sum() > 0
    ]
    validated_data.dropna(subset=new_vars_with_na, inplace=True)

    return validated_data


def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Check model inputs and handle missing values."""
    validated_data = input_data.copy()

    # Заполняем пропуски в категориальных признаках
    for col in config.model_config_params.categorical_vars_with_na:
        if col in validated_data.columns and validated_data[col].isnull().any():
            mode = validated_data[col].mode()[0] if not validated_data[col].mode().empty else 'Unknown'
            validated_data[col] = validated_data[col].fillna(mode)
            print(f"Заполнены пропуски в {col} значением: {mode}")  # Логируем

    # Заполняем пропуски в числовых признаках
    for col in config.model_config_params.numerical_vars_with_na:
        if col in validated_data.columns and validated_data[col].isnull().any():
            mean = validated_data[col].mean()
            validated_data[col] = validated_data[col].fillna(mean)
            print(f"Заполнены пропуски в {col} средним значением: {mean:.2f}")

    # Проверяем оставшиеся пропуски
    remaining_nulls = validated_data.isnull().sum().sum()
    if remaining_nulls > 0:
        error_msg = f"Обнаружены непредусмотренные пропуски в признаках: {validated_data.columns[validated_data.isnull().any()].tolist()}"
        print(f"Ошибка: {error_msg}")
        return validated_data, {"missing_values": error_msg}

    # Проверяем типы данных
    try:
        validated_data['ApplicantIncome'] = validated_data['ApplicantIncome'].astype(float)
        validated_data['CoapplicantIncome'] = validated_data['CoapplicantIncome'].astype(float)
        validated_data['LoanAmount'] = validated_data['LoanAmount'].astype(float)
        validated_data['Loan_Amount_Term'] = validated_data['Loan_Amount_Term'].astype(float)
        validated_data['Credit_History'] = validated_data['Credit_History'].astype(float)
    except Exception as e:
        error_msg = f"Ошибка преобразования типов: {str(e)}"
        print(f"Ошибка: {error_msg}")
        return validated_data, {"type_error": error_msg}

    return validated_data, None


class LoanInputSchema(BaseModel):
    Gender: Optional[str]
    Married: Optional[str]
    Education: Optional[str]
    Self_Employed: Optional[str]
    ApplicantIncome: Optional[float]
    CoapplicantIncome: Optional[float]
    LoanAmount: Optional[float]
    Loan_Amount_Term: Optional[float]
    Credit_History: Optional[float]
    Property_Area: Optional[str]


class MultipleLoanInputs(BaseModel):
    inputs: List[LoanInputSchema]