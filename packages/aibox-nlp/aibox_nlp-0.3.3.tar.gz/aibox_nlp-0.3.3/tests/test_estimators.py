"""Testes do pacote de
estimadores da biblioteca.
"""

import numpy as np
import pytest

from aibox.nlp.core import Estimator
from aibox.nlp.factory import available_estimators, get_estimator


def _run_estimator_test(estimator: Estimator, is_clf: bool):
    # Train data
    X = np.array([[1.0], [2.0], [3.0]])
    y = np.array([1.0, 2.0, 3.0])
    if is_clf:
        y = y.astype(np.int32)

    # Fit
    estimator.fit(X, y)

    # Predict
    preds = estimator.predict(X)

    # Assertions
    assert preds.shape == y.shape
    assert np.issubdtype(preds.dtype, np.integer if is_clf else np.floating)
    if is_clf:
        assert np.isin(preds, y).all()


@pytest.mark.parametrize("estimator", available_estimators())
def test_estimators(estimator: str):
    _run_estimator_test(
        get_estimator(estimator, random_state=42),
        is_clf="classifier" in estimator.lower(),
    )
