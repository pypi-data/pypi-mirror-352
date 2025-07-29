from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from feature_engine.imputation import AddMissingIndicator, CategoricalImputer, MeanMedianImputer
from feature_engine.encoding import RareLabelEncoder, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from loan_approval_model import config

# Препроцессинг для числовых признаков
numeric_transformer = Pipeline([
    ('missing_indicator', AddMissingIndicator(variables=config.model_config_params.numerical_vars_with_na)),
    ('median_imputation', MeanMedianImputer(imputation_method='median',
                                          variables=config.model_config_params.numerical_vars_with_na)),
    ('scaler', StandardScaler())
])

# Препроцессинг для категориальных признаков
categorical_transformer = Pipeline([
    ('imputer', CategoricalImputer(imputation_method='missing',
                                 variables=config.model_config_params.categorical_vars_with_na)),
    ('rare_encoder', RareLabelEncoder(tol=0.05, n_categories=1,
                                    variables=config.model_config_params.categorical_vars)),
    ('onehot', OneHotEncoder(variables=config.model_config_params.categorical_vars,
                           drop_last=True))
])

# Объединяем трансформеры
preprocessor = ColumnTransformer([
    ('num', numeric_transformer, config.model_config_params.numerical_vars),
    ('cat', categorical_transformer, config.model_config_params.categorical_vars)
])

# Финальный пайплайн
loan_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(
        C=config.model_config_params.alpha,
        solver='liblinear',
        random_state=config.model_config_params.random_state
    ))
])