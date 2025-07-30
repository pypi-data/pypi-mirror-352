multiplayer-opentelemetry
============================================================================
##  Introduction
The multiplayer-opentelemetry module integrates OpenTelemetry with the Multiplayer platform to enable seamless trace collection and analysis. This library helps developers monitor, debug, and document application performance with detailed trace data. It supports flexible trace ID generation, sampling strategies.

## Installation

To install the `multiplayer-opentelemetry` module, use the following command:

```bash
pip install multiplayer-opentelemetry 
```

## Multiplayer Http Trace Exporter

```python
from multiplayer.opentelemetry.exporter.http.trace_exporter import MultiplayerOTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(MultiplayerOTLPSpanExporter(
    url = '<opentelemetry-collector-url>', # url is optional and can be omitted - default is https://api.multiplayer.app/v1/traces
    apiKey = "<multiplayer-otel-key>"
))
```

## Multiplayer Http Log Exporter

```python
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from multiplayer.opentelemetry.exporter.http.log_exporter import MultiplayerOTLPLogExporter

logProcessor = BatchLogRecordProcessor(MultiplayerOTLPLogExporter(
    url = "<opentelemetry-collector-url>", # url is optional and can be omitted - default is https://api.multiplayer.app/v1/logs
    apiKey = "<multiplayer-otel-key>"
))
```

## Multiplayer Grpc Trace Exporter

```python
from multiplayer.opentelemetry.exporter.grpc.trace_exporter import MultiplayerOTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

processor = BatchSpanProcessor(MultiplayerOTLPSpanExporter(
    url = '<opentelemetry-collector-url>', # url is optional and can be omitted - default is https://api.multiplayer.app/v1/traces
    apiKey = "<multiplayer-otel-key>"
))
```

## Multiplayer Grpc Log Exporter

```python
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from multiplayer.opentelemetry.exporter.grpc.log_exporter import MultiplayerOTLPLogExporter

logProcessor = BatchLogRecordProcessor(MultiplayerOTLPLogExporter(
    url = "<opentelemetry-collector-url>", # url is optional and can be omitted - default is https://api.multiplayer.app/v1/logs
    apiKey = "<multiplayer-otel-key>"
))
```


## Multiplayer trace Id generator

```python
from multiplayer.opentelemetry.trace.sampler import MultiplayerTraceIdRatioBasedSampler

sampler = MultiplayerTraceIdRatioBasedSampler(rate = 1/2)
```

## Multiplayer trace id ratio based sampler

```python
from multiplayer.opentelemetry.trace.id_generator import MultiplayerRandomIdGenerator

id_generator = MultiplayerRandomIdGenerator(autoDocTracesRatio = 1/1000)
```
