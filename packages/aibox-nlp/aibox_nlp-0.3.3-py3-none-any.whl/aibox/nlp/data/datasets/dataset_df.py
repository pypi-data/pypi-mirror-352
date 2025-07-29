"""Adapter para representar
:py:class:`~pandas.DataFrame`'s
como Datasets."""

from os import PathLike
from typing import Any, Callable

try:
    from typing import Self
except ImportError:
    # Self was added on Python 3.11
    from typing import TypeVar

    Self = TypeVar("Self", bound="DatasetDF")


import pandas as pd
from pandas.api import types

from aibox.nlp.core import Dataset

from . import utils


class DatasetDF(Dataset):
    """Dataset a partir de um :py:class:`~pandas.DataFrame`.

    :param df: :py:class:`~pandas.DataFrame`
        com os dados ou caminho para CSV.
    :param text_column: coluna que possui os textos.
    :param target_column: coluna com os valores target.
    :param copy: se devemos armazenar uma cópia do ou não.
    :param drop_others: se devemos remover outras
        colunas que não sejam as de texto e target.
    :param target_mapper: função de mapeamento para coluna target.
        Deve ser utilizada caso algum pré-processamento deva ser
        aplicado para converter a coluna para valores numéricos
        (default=não realiza mapeamento).
    """

    def __init__(
        self,
        df: pd.DataFrame | PathLike | str,
        text_column: str,
        target_column: str,
        copy: bool = True,
        drop_others: bool = False,
        target_mapper: Callable[[Any], int | float] = None,
    ):
        """Construtor."""
        # Caso não seja um DataFrame, tentar carregar
        if not isinstance(df, pd.DataFrame):
            df = pd.read_csv(df)

        assert text_column in df.columns, "Coluna não encontrada."
        assert target_column in df.columns, "Coluna não encontrada."
        assert len(df) > 0, "DataFrame não pode ser vazio."

        # Se o DataFrame original não deve ser alterado
        if copy:
            df = df.copy()

        # Talvez seja necessário aplicar algum mapeamento
        #   na coluna de target.
        if target_mapper is not None:
            df[target_column] = df[target_column].map(target_mapper)

        self._df = df.rename(columns={text_column: "text", target_column: "target"})

        if drop_others:
            columns = set(self._df.columns.tolist())
            columns.remove("text")
            columns.remove("target")
            self._df.drop(columns=columns, inplace=True)

        has_duplicates = self._df.text.duplicated().any()
        has_na_text = self._df.text.isnull().any()
        is_numeric = types.is_numeric_dtype(self._df.target.dtype)
        has_na_target = self._df.target.isnull().any()
        assert not has_na_text, "Não devem existir textos NULL."
        assert not has_duplicates, "Não devem existir textos duplicados."
        assert not has_na_target, "Não devem existir targets NULL."
        assert is_numeric, 'Coluna "target" deve ser numérica.'

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def to_frame(self):
        return self._df.copy()

    def cv_splits(self, k: int, stratified: bool, seed: int) -> list[pd.DataFrame]:
        if stratified and self._is_classification():
            return utils.stratified_splits_clf(df=self._df, k=k, seed=seed)

        return utils.splits(df=self._df, k=k, seed=seed)

    def train_test_split(
        self, frac_train: float, stratified: bool, seed: int
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if stratified and self._is_classification():
            return utils.train_test_clf(df=self._df, frac_train=frac_train, seed=seed)

        return utils.train_test(df=self._df, frac_train=frac_train, seed=seed)

    def _is_classification(self) -> bool:
        return types.is_integer_dtype(self._df.target.dtype)

    @classmethod
    def load_from_kaggle(
        cls,
        ds_name: str,
        text_column: str,
        target_column: str,
        files_to_load: str | list[str],
        drop_others: bool = False,
        target_mapper: Callable[[Any], int | float] = None,
    ) -> Self:
        """Carrega um dataset a partir de um identificador de
        dataset no Kaggle. Se o dataset é privado ou requer
        permissão do usuário, é necessário ter realizado login
        com `kagglehub.login()`.


        :param ds_name: identificador do dataset no Kaggle.
        :param text_column: coluna que contém textos.
        :param target_column: coluna que contém os targets.
        :param *files_to_load: uma ou mais strings com quais
            arquivos devem ser carregados (o DataFrame final
            é uma concatenação linha a linha).
        :param drop_others: se demais colunas devem ser
            removidas (default=False).
        :param target_mapper: função
            de mapeamento da coluna target.

        :return: instância com os dados do dataset do Kaggle.
        """
        import kagglehub
        from kagglehub import KaggleDatasetAdapter

        df = pd.concat(
            [
                kagglehub.dataset_load(
                    KaggleDatasetAdapter.PANDAS,
                    ds_name,
                    f,
                )
                for f in files_to_load
            ],
            axis=0,
            ignore_index=True,
        )

        return cls(
            df,
            text_column=text_column,
            target_column=target_column,
            target_mapper=target_mapper,
            drop_others=drop_others,
            copy=False,
        )
