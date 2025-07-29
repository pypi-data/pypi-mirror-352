from typing import Callable

from prometheus_client import Gauge
from prometheus_fastapi_instrumentator.metrics import Info

from stadt_bonn_oparl.api.dependencies import (
    agendaitems_collection,
    memberships_collection,
    organizations_collection,
    papers_collection,
    persons_collection,
    meetings_collection,
)


def chromadb_documents_total() -> Callable[[Info], None]:
    METRIC = Gauge(
        "chromadb_documents_total",
        "Number of documents in the ChromaDB.",
        labelnames=("collection",),
    )

    def instrumentation(info: Info) -> None:
        """Instrument the number of documents in the ChromaDB."""
        for collection in (
            persons_collection,
            memberships_collection,
            organizations_collection,
            agendaitems_collection,
            papers_collection,
            meetings_collection,
        ):
            count = collection.count()
            METRIC.labels(collection=collection.name).set(count)

    return instrumentation
