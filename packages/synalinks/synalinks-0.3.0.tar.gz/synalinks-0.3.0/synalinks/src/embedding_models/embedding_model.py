# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

import warnings

import litellm

from synalinks.src.api_export import synalinks_export
from synalinks.src.saving.synalinks_saveable import SynalinksSaveable


@synalinks_export(
    ["synalinks.EmbeddingModel", "synalinks.embedding_models.EmbeddingModel"]
)
class EmbeddingModel(SynalinksSaveable):
    """An embedding model API wrapper.

    Embedding models are a type of machine learning model used to convert
    high-dimensional data, such as text into lower-dimensional vector
    representations while preserving the semantic meaning and relationships
    within the data. These vector representations, known as embeddings,
    allow for more efficient and effective processing in various tasks.

    Many providers are available like OpenAI, Azure OpenAI, Vertex AI or Ollama.

    For the complete list of models, please refer to the providers documentation.

    **Using OpenAI models**

    ```python
    import synalinks
    import os

    os.environ["OPENAI_API_KEY"] = "your-api-key"

    embedding_model = synalinks.EmbeddingModel(
        model="openai/text-embedding-ada-002",
    )
    ```

    **Using Azure OpenAI models**

    ```python
    import synalinks
    import os

    os.environ["AZURE_API_KEY"] = "your-api-key"
    os.environ["AZURE_API_BASE"] = "your-api-base"
    os.environ["AZURE_API_VERSION"] = "your-api-version"

    embedding_model = synalinks.EmbeddingModel(
        model="azure/<your_deployment_name>",
    )
    ```

    **Using VertexAI models**

    ```python
    import synalinks
    import os

    embedding_model = synalinks.EmbeddingModel(
        model="vertex_ai/text-embedding-004",
        vertex_project = "hardy-device-38811", # Your Project ID
        vertex_location = "us-central1",  # Project location
    )
    ```

    **Using Ollama models**

    ```python
    import synalinks

    embedding_model = synalinks.EmbeddingModel(
        model="ollama/mxbai-embed-large",
    )
    ```

    Args:
        model (str): The model to use.
        api_base (str): Optional. The endpoint to use.
        retry (int): Optional. The number of retry.
    """

    def __init__(self, model=None, api_base=None, retry=5):
        if model is None:
            raise ValueError(
                "You need to set the `model` argument for any EmbeddingModel"
            )
        self.model = model
        if self.model.startswith("ollama") and not api_base:
            self.api_base = "http://localhost:11434"
        else:
            self.api_base = api_base
        self.retry = retry

    async def __call__(self, texts, **kwargs):
        """
        Call method to get dense embeddings vectors

        Args:
            texts (list): A list of texts to embed.

        Returns:
            (list): The list of corresponding vectors.
        """
        for i in range(self.retry):
            try:
                if self.api_base:
                    response = litellm.embedding(
                        model=self.model,
                        input=texts,
                        api_base=self.api_base,
                        **kwargs,
                    )
                else:
                    response = litellm.embedding(
                        model=self.model,
                        input=texts,
                        **kwargs,
                    )
                vectors = []
                for data in response["data"]:
                    vectors.append(data["embedding"])
                return {"embeddings": vectors}
            except Exception as e:
                warnings.warn(f"Error occured while trying to call {self}: " + str(e))
        raise RuntimeError(
            f"Failed to retrieve embeddings with {self} after {self.retry} attempts."
        )

    def _obj_type(self):
        return "EmbeddingModel"

    def get_config(self):
        return {
            "model": self.model,
            "api_base": self.api_base,
            "retry": self.retry,
        }

    @classmethod
    def from_config(cls, config):
        return cls(**config)

    def __repr__(self):
        api_base = f" api_base={self.api_base}" if self.api_base else ""
        return f"<EmbeddingModel model={self.model}{api_base}>"
