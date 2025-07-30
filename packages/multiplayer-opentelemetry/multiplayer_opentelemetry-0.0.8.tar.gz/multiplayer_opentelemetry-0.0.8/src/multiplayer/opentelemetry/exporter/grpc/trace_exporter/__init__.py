from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from typing import Optional
from ....constants import MULTIPLAYER_OTEL_DEFAULT_TRACES_EXPORTER_GRPC_URL, MULTIPLAYER_OTLP_KEY

class MultiplayerOTLPSpanExporter(OTLPSpanExporter):
    def __init__(
        self,
        apiKey: Optional[str] = None,
        endpoint: Optional[str] = None,
        *args,
        **kwargs
    ):
        kwargs.setdefault("endpoint", endpoint or MULTIPLAYER_OTEL_DEFAULT_TRACES_EXPORTER_GRPC_URL)
        kwargs.setdefault("headers", {
            "Authorization": apiKey or MULTIPLAYER_OTLP_KEY
        })
        super().__init__(*args, **kwargs)
