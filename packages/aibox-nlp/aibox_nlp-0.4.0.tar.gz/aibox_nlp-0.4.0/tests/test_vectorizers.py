"""Testes do pacote vectorizers."""

import os

import numpy as np
import pytest

from aibox.nlp.core import TrainableVectorizer
from aibox.nlp.factory import available_vectorizers, get_vectorizer
from aibox.nlp.typing import TextArrayLike
from aibox.nlp.vectorizers.fasttext_word_vectorizer import (
    FTAggregationStrategy,
    FTTokenizerStrategy,
)


@pytest.mark.skipif(
    os.environ.get("TEST_EXPENSIVE_AIBOX_NLP", None) is None,
    reason="'TEST_EXPENSIVE_AIBOX_NLP' is unset.",
)
@pytest.mark.parametrize("vectorizer_cls", available_vectorizers())
@pytest.mark.parametrize(
    "text",
    [
        "Esse é um texto de exemplo.",
        ["Teste com múltiplos textos."] * 20,
        np.array(["Teste com array de múltiplos textos."] * 20),
    ],
)
def test_vectorizer(vectorizer_cls: str, text: TextArrayLike):
    # Get vectorizer
    vectorizer = get_vectorizer(vectorizer_cls)

    # Maybe it's trainable?
    if isinstance(vectorizer, TrainableVectorizer):
        vectorizer.fit(["Esse é um texto de treinamento."])

    # Try to vectorize input
    for kind in ["numpy", "torch"]:
        vectorizer.vectorize(text, vector_type=kind)


@pytest.mark.skipif(
    os.environ.get("TEST_EXPENSIVE_AIBOX_NLP", None) is None,
    reason="'TEST_EXPENSIVE_AIBOX_NLP' is unset.",
)
@pytest.mark.parametrize("aggregation", FTAggregationStrategy)
@pytest.mark.parametrize("tokenizer", FTTokenizerStrategy)
def test_fasttext_vectorizer(
    aggregation: FTAggregationStrategy, tokenizer: FTTokenizerStrategy
):
    # Initialize vectorizer
    vectorizer = get_vectorizer(
        "fasttextWordVectorizer", aggregation=aggregation, tokenizer=tokenizer
    )

    # Vectorize text
    out = vectorizer.vectorize("Esse é um texto de exemplo.")

    # Assertions
    if aggregation == FTAggregationStrategy.NONE:
        assert len(out.shape) == 2
        assert out.shape[-1] == 50
    elif aggregation == FTAggregationStrategy.AVERAGE:
        assert out.shape == (50,)
