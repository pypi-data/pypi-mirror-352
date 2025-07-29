# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

from enum import Enum
from typing import List

from synalinks.src import testing
from synalinks.src.backend import DataModel
from synalinks.src.backend import is_schema_equal
from synalinks.src.backend.common.dynamic_json_schema_utils import dynamic_enum
from synalinks.src.backend.common.dynamic_json_schema_utils import dynamic_list


class DynamicEnumTest(testing.TestCase):
    def test_basic_dynamic_enum(self):
        class DecisionAnswer(DataModel):
            thinking: str
            choice: str

        class Choice(str, Enum):
            easy = "easy"
            difficult = "difficult"
            unknown = "unknown"

        class Decision(DataModel):
            thinking: str
            choice: Choice

        labels = ["easy", "difficult", "unkown"]

        schema = dynamic_enum(DecisionAnswer.get_schema(), "choice", labels)

        self.assertTrue(is_schema_equal(Decision.get_schema(), schema))

    def test_basic_dynamic_list(self):
        class Document(DataModel):
            text: str

        class Documents(DataModel):
            documents: List[Document]

        schema = dynamic_list(Document.get_schema())
        self.assertEqual(Documents.get_schema(), schema)
