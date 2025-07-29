"""Vetorizador baseado no BERT."""

from sentence_transformers import SentenceTransformer, models

from aibox.nlp.core import Vectorizer
from aibox.nlp.typing import TextArrayLike


class BertVectorizer(Vectorizer):
    """Vetorização através de Embeddings do BERT.

    :param sentence_bert_name: nome do modelo do BERT a
        ser utilizado.
    :param pooling_type: estratégia de pooling.
    :param max_seq_len: tamanho máximo da sequência.
    :param do_lower_case: se a entrada deve ser convertida para
        lowercase.
    :param tokenizer_name: nome do tokenizador.
    :param batch_size: tamanho do batch.
    :param show_progress_bar: se deve ser exibida
        uma barra de progresso.
    :param device: dispositivo a ser utilizado.
    :param normalize_embeddings: se os embeddings devem ser
        normalizados.

    .. code-block:: python

        from aibox.nlp.vectorizers.bert_vectorizer import BertVectorizer

        # Instanciando modelo em CPU
        vectorizer = BertVectorizer()
        text = "Esse é um texto de exemplo."

        # Obtendo a representação vetorial do texto
        vectorizer.vectorize(text)
        # Out: array([4.12135035e-01, ... -1.46901190e-01])
    """

    def __init__(
        self,
        sentence_bert_name: str = "neuralmind/bert-base-portuguese-cased",
        pooling_type: str = "cls",
        max_seq_len: int = 512,
        do_lower_case: bool = False,
        tokenizer_name: str = None,
        batch_size: int = 32,
        show_progress_bar: bool = False,
        device: str = None,
        normalize_embeddings: bool = False,
    ) -> None:
        word_embedding_model = models.Transformer(
            sentence_bert_name,
            max_seq_length=max_seq_len,
            do_lower_case=do_lower_case,
            tokenizer_name_or_path=tokenizer_name,
        )
        pooling_model = models.Pooling(
            word_embedding_model.get_word_embedding_dimension(), pooling_type
        )
        bert_model = SentenceTransformer(
            modules=[word_embedding_model, pooling_model], device=device
        )
        self._model = bert_model
        self._batch_size = batch_size
        self._show_progress_bar = show_progress_bar
        self._device = device
        self._normalize_embeddings = normalize_embeddings

    def _batch_vectorize(self, texts: str | TextArrayLike, **kwargs):
        del kwargs
        return self._model.encode(
            sentences=texts,
            batch_size=self._batch_size,
            show_progress_bar=self._show_progress_bar,
            convert_to_numpy=True,
            device=self._device,
            normalize_embeddings=self._normalize_embeddings,
        )

    def _vectorize(self, text: str, **kwargs):
        return self._batch_vectorize(text, **kwargs)
