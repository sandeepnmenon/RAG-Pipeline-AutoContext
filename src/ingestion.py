from typing import Iterator, Union

from r2r.core import BasicDocument
from r2r.pipelines import BasicIngestionPipeline, IngestionType


class AutoContextIngestionPipeline(BasicIngestionPipeline):
    def process_data(
        self,
        entry_type: IngestionType,
        entry_data: Union[bytes, str],
    ) -> Iterator[BasicDocument]:
        pass