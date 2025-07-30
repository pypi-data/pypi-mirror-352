from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from typing import Optional
from ....constants import MULTIPLAYER_OTEL_DEFAULT_LOGS_EXPORTER_HTTP_URL, MULTIPLAYER_OTLP_KEY

class MultiplayerOTLPLogExporter(OTLPLogExporter):
    def __init__(
        self,
        apiKey: Optional[str] = None,
        endpoint: Optional[str] = None,
        *args,
        **kwargs
    ):
        kwargs.setdefault("endpoint", endpoint or MULTIPLAYER_OTEL_DEFAULT_LOGS_EXPORTER_HTTP_URL)
        kwargs.setdefault("headers", {
            "Authorization": apiKey or MULTIPLAYER_OTLP_KEY
        })
        super().__init__(*args, **kwargs)
