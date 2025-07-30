from fastapi import FastAPI
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry import trace

def init_monitoring(app: FastAPI, service_name: str, connection_string: str):
    # ✅ This sets the cloud_RoleName in Application Insights
    resource = Resource.create({SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Export telemetry to Azure Monitor
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Auto-instrument FastAPI and ASGI middleware
    FastAPIInstrumentor.instrument_app(app)
    app.add_middleware(OpenTelemetryMiddleware)

    @app.on_event("startup")
    async def startup_event():
        print(f"✅ Monitoring initialized for: {service_name}")
