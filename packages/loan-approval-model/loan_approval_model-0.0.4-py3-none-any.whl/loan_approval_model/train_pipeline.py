import logging
from pathlib import Path

from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from loan_approval_model import __version__ as _version
from loan_approval_model.config.core import LOG_DIR, config
from loan_approval_model.pipeline import loan_pipe
from loan_approval_model.processing.data_manager import load_dataset, save_pipeline


def run_training() -> None:
    """Train the loan approval model."""
    # Update logs
    log_path = Path(f"{LOG_DIR}/log_{_version}.log")
    if Path.exists(log_path):
        log_path.unlink()
    logging.basicConfig(filename=log_path, level=logging.DEBUG)

    # read training data
    data = load_dataset(file_name=config.app_config.training_data_file)

    # Drop unnecessary columns
    data.drop(labels=config.model_config_params.variables_to_drop, axis=1, inplace=True)

    # divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data[config.model_config_params.features],
        data[config.model_config_params.target],
        test_size=config.model_config_params.test_size,
        random_state=config.model_config_params.random_state,
    )

    # fit model
    loan_pipe.fit(X_train, y_train)

    # make predictions for train set
    class_ = loan_pipe.predict(X_train)
    pred = loan_pipe.predict_proba(X_train)[:, 1]

    # determine train accuracy and roc-auc
    train_accuracy = accuracy_score(y_train, class_)
    train_roc_auc = roc_auc_score(y_train, pred)

    print(f"train accuracy: {train_accuracy}")
    print(f"train roc-auc: {train_roc_auc}")
    print()

    logging.info(f"train accuracy: {train_accuracy}")
    logging.info(f"train roc-auc: {train_roc_auc}")

    # make predictions for test set
    class_ = loan_pipe.predict(X_test)
    pred = loan_pipe.predict_proba(X_test)[:, 1]

    # determine test accuracy and roc-auc
    test_accuracy = accuracy_score(y_test, class_)
    test_roc_auc = roc_auc_score(y_test, pred)

    print(f"test accuracy: {test_accuracy}")
    print(f"test roc-auc: {test_roc_auc}")
    print()

    logging.info(f"test accuracy: {test_accuracy}")
    logging.info(f"test roc-auc: {test_roc_auc}")

    # persist trained model
    save_pipeline(pipeline_to_persist=loan_pipe)


if __name__ == "__main__":
    run_training()