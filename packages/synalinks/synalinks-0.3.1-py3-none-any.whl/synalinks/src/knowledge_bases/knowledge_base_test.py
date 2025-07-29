# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

from typing import Literal

from synalinks.src import testing
from synalinks.src.backend import Entity
from synalinks.src.backend import Relation
from synalinks.src.embedding_models import EmbeddingModel
from synalinks.src.knowledge_bases import KnowledgeBase


class Document(Entity):
    label: Literal["Document"]
    text: str


class Chunk(Entity):
    label: Literal["Chunk"]
    text: str


class IsPartOf(Relation):
    subj: Chunk
    label: Literal["IsPartOf"]
    obj: Document


class KnowledgeBaseTest(testing.TestCase):
    async def test_knowledge_base(self):
        embedding_model = EmbeddingModel(
            model="ollama/mxbai-embed-large",
        )

        knowledge_base = KnowledgeBase(
            index_name="neo4j://localhost:7687",
            entity_models=[Document, Chunk],
            relation_models=[IsPartOf],
            embedding_model=embedding_model,
            metric="cosine",
            wipe_on_start=False,
        )

        _ = await knowledge_base.query("RETURN 1")

    def test_knowledge_base_serialization(self):
        embedding_model = EmbeddingModel(
            model="ollama/mxbai-embed-large",
        )

        knowledge_base = KnowledgeBase(
            index_name="neo4j://localhost:7687",
            entity_models=[Document, Chunk],
            relation_models=[IsPartOf],
            embedding_model=embedding_model,
            metric="cosine",
            wipe_on_start=False,
        )

        config = knowledge_base.get_config()
        cloned_knowledge_base = KnowledgeBase.from_config(config)
        self.assertEqual(
            cloned_knowledge_base.get_config(),
            knowledge_base.get_config(),
        )
