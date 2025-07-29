"""Testes do pacote de
datasets da biblioteca.
"""

import pytest

from aibox.nlp.data.datasets import DatasetDF
from aibox.nlp.factory import get_dataset
from aibox.nlp.factory.class_registry import get_class


@pytest.mark.parametrize("extended", [True, False])
@pytest.mark.parametrize(
    "target_competence", [f"C{i}" for i in range(1, 6)] + ["score"]
)
def test_essay_br(extended: bool, target_competence: str):
    ds = get_dataset("essayBR", extended=extended, target_competence=target_competence)
    assert ds.is_extended == extended
    assert ds.competence == target_competence
    assert ds.to_frame().shape == (4570 if not extended else 6564, 9)


@pytest.mark.parametrize("clean_tags", [True, False])
@pytest.mark.parametrize(
    "target_competence",
    [
        "cohesion",
        "thematic_coherence",
        "formal_register",
        "narrative_rhetorical_structure",
    ],
)
def test_portuguese_narrative_essays(clean_tags: bool, target_competence: str):
    ds = get_dataset(
        "narrativeEssaysBR", clean_tags=clean_tags, target_competence=target_competence
    )
    assert ds.competence == target_competence
    assert ds.to_frame().shape[0] == 1235


@pytest.mark.parametrize(
    "target_competence",
    [
        "cohesion",
        "thematic_coherence",
        "formal_register",
        "narrative_rhetorical_structure",
    ],
)
def test_dataset_df(target_competence: str):
    ds = DatasetDF.load_from_kaggle(
        "moesiof/portuguese-narrative-essays",
        "essay",
        target_competence,
        ["train.csv", "test.csv", "validation.csv"],
    )
    assert ds.to_frame().shape[0] == 1235


@pytest.mark.parametrize(
    "dataset_identifier,config",
    [
        *[("essayBR", dict(extended=e)) for e in [True, False]],
        ("narrativeEssaysBR", dict()),
    ],
)
def test_load_raw(dataset_identifier: str, config: dict):
    cls = get_class(dataset_identifier)
    df = cls.load_raw(**config)
    assert len(df) > 1
    assert len(df.columns) > 1
