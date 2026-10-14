# Architecture: Breast Pathology AI Platform

*Lesson L1.2 deliverable. Copy to `docs/architecture/README.md` and make it your own.*
*Version 0.1 · 2026-10 · Sources: [vision](../product/vision.md), [requirements](../product/requirements.md), [ADRs](../adr/)*

## Summary

The platform is a **modular monolith API with an event-driven processing pipeline**. One ASP.NET Core API handles every request from the Blazor web app. Long-running work (quality control, tiling, inference, report extraction, embeddings) is published as events to a message broker and done by independent workers in .NET and Python. All components share three stores: PostgreSQL (metadata and vectors), object storage (slides, tiles, overlays, models) and Parquet files (tile-level results).

## Quality attributes that drive the architecture

| Quality attribute | Requirement | Architectural answer |
|---|---|---|
| Large files | NFR-02: 2 GB upload with flat memory | Stream uploads straight to object storage; never hold a slide in memory |
| Throughput | NFR-04: scale with workers | Long work runs in workers that read from queues; add workers to go faster |
| Reliability | NFR-09: no slide silently lost | Durable queues, retries, dead-letter queues, idempotent consumers |
| Responsiveness | NFR-01: tiles p95 < 200 ms | Tiles served over HTTP straight from pre-built pyramids, bypassing Blazor |
| Privacy | NFR-05: no identifiers | De-identification at ingestion, the single entry point |
| Portability | NFR-12, US-29: local and cloud | Storage and messaging behind interfaces, chosen by configuration |
| Two languages | Python research, .NET platform | Models cross the boundary as ONNX files; Python services talk through events and HTTP |

## C4 level 1: System context

```mermaid
flowchart TB
    pathologist["Pathologist<br/>[Person]<br/>Reviews slides and AI results,<br/>signs out cases"]
    technician["Lab technician<br/>[Person]<br/>Uploads slides, handles rescans"]
    manager["Lab manager<br/>[Person]<br/>Turnaround, backlog, triage settings"]
    scientist["Data scientist<br/>[Person]<br/>Trains, registers and promotes models"]
    admin["Administrator<br/>[Person]<br/>Users, roles, audit, configuration"]

    platform["Breast Pathology AI Platform<br/>[Software system]<br/>Ingests slides, checks quality, runs AI detection and grading<br/>with uncertainty, shows results to pathologists"]

    scanner["Slide scanners / file share<br/>[External system]<br/>Produce WSI files"]
    lis["Laboratory information system<br/>[External system, later]<br/>Cases, orders, final reports"]
    idp["Identity provider<br/>[External system]<br/>Single sign-on (OpenID Connect)"]
    public["Public datasets<br/>[External system]<br/>CAMELYON16, PCam, TCGA-BRCA"]

    pathologist -- "Views slides, heatmaps, grades;<br/>records decisions" --> platform
    technician -- "Uploads slides, checks QC" --> platform
    manager -- "Reads dashboards, sets thresholds" --> platform
    scientist -- "Registers models, exports data" --> platform
    admin -- "Manages users, reads audit log" --> platform

    scanner -- "WSI files" --> platform
    public -- "Slides, patches, reports" --> platform
    platform -- "Authenticates users" --> idp
    platform -. "FHIR reports (later)" .-> lis

    classDef person fill:#08427b,stroke:#052e56,color:#fff
    classDef system fill:#1168bd,stroke:#0b4884,color:#fff
    classDef external fill:#999,stroke:#6b6b6b,color:#fff
    class pathologist,technician,manager,scientist,admin person
    class platform system
    class scanner,lis,idp,public external
```

## C4 level 2: Containers

"Container" in C4 means **a separately running or deployable unit** (an app, a service, a database), not necessarily a Docker container, although here most of them will also run in Docker.

```mermaid
flowchart TB
    users["Users<br/>[Person]<br/>Pathologist, technician, manager,<br/>data scientist, administrator"]

    subgraph platform["Breast Pathology AI Platform"]
        web["Web app<br/>[Blazor Web App, .NET 10]<br/>Viewer (WebAssembly + OpenSeadragon),<br/>dashboards and admin (Server)"]
        api["Platform API<br/>[ASP.NET Core minimal APIs]<br/>Modules: slides, tiles, QC, results,<br/>models, reports, search, triage, admin"]

        subgraph workers["Workers [.NET BackgroundService + MassTransit]"]
            qc["QC worker<br/>OpenCvSharp"]
            tiling["Tiling worker<br/>NetVips dzsave"]
            inference["Inference worker<br/>ONNX Runtime"]
            aggregator["Aggregator<br/>slide results, heatmaps"]
        end

        subgraph python["Python services [Python 3.12]"]
            nlp["Report NLP service<br/>FastAPI, spaCy / LLM"]
            embed["Embedding worker<br/>foundation model"]
        end

        bus[("Message broker<br/>[RabbitMQ; Azure Service Bus in cloud]<br/>Events between components")]
        db[("Metadata database<br/>[PostgreSQL + pgvector]<br/>Cases, slides, results, audit, vectors")]
        blob[("Object storage<br/>[MinIO; Azure Blob in cloud]<br/>Slides, tiles, overlays, ONNX models,<br/>Parquet tile scores")]
    end

    mlflow["MLflow<br/>[Python, research side]<br/>Experiments and model training runs"]
    idp["Identity provider<br/>[Keycloak]<br/>OpenID Connect"]
    obs["Observability<br/>[OpenTelemetry, Prometheus, Grafana]"]

    users -- "HTTPS" --> web
    web -- "JSON over HTTPS; SignalR for live updates" --> api
    web -- "Tile requests (HTTP, cached)" --> api
    web -- "Login" --> idp
    api -- "Reads/writes" --> db
    api -- "Streams uploads, reads tiles" --> blob
    api -- "Publishes events" --> bus

    bus -- "SlideIngested" --> qc
    bus -- "SlideQcCompleted" --> tiling
    bus -- "SlideTiled" --> inference
    bus -- "SlideTiled" --> embed
    bus -- "InferenceCompleted" --> aggregator
    bus -- "ReportReceived" --> nlp

    workers -- "Read slides, write results" --> blob
    workers -- "Write rows" --> db
    workers -- "Publish next event" --> bus
    python -- "Write results" --> db
    python -- "Publish events" --> bus

    mlflow -. "Exported ONNX + model card,<br/>registered through the API" .-> api
    platform -. "Traces, metrics, logs" .-> obs

    classDef person fill:#08427b,stroke:#052e56,color:#fff
    classDef container fill:#438dd5,stroke:#2e6295,color:#fff
    classDef store fill:#2f6f9f,stroke:#1f4f73,color:#fff
    classDef external fill:#999,stroke:#6b6b6b,color:#fff
    class users person
    class web,api,qc,tiling,inference,aggregator,nlp,embed container
    class bus,db,blob store
    class mlflow,idp,obs external
```

## Main flow: from upload to result

```mermaid
sequenceDiagram
    autonumber
    actor Tech as Lab technician
    participant Web as Web app
    participant API as Platform API
    participant Blob as Object storage
    participant DB as PostgreSQL
    participant Bus as Message broker
    participant QC as QC worker
    participant Tile as Tiling worker
    participant Inf as Inference worker
    participant Agg as Aggregator
    actor Path as Pathologist

    Tech->>Web: Choose slide file
    Web->>API: POST /slides (streamed)
    API->>Blob: Stream file to raw/{slideId}, compute SHA-256
    API->>DB: Insert Slide (status = ingested) + outbox event
    API-->>Web: 201 Created
    API->>Bus: SlideIngested
    Bus->>QC: SlideIngested
    QC->>Blob: Read thumbnail level
    QC->>DB: Insert QcResult (pass / warn / fail)
    QC->>Bus: SlideQcCompleted
    Bus->>Tile: SlideQcCompleted (if pass or warn)
    Tile->>Blob: Write tile pyramid to tiles/{slideId}/
    Tile->>Bus: SlideTiled
    Bus->>Inf: SlideTiled
    Inf->>Blob: Read tissue tiles at model mpp, write TileScore Parquet
    Inf->>Bus: InferenceCompleted
    Bus->>Agg: InferenceCompleted
    Agg->>DB: Insert SlideResult (label, score, uncertainty)
    Agg->>Bus: SlideResultReady
    Bus->>API: SlideResultReady
    API-->>Web: SignalR push "result ready"
    Path->>Web: Open slide, switch on heatmap
```

Each arrow into a worker is **asynchronous**: the technician gets "201 Created" after step 5 and doesn't wait for QC, tiling or inference. If a worker crashes, its message stays in the queue and is retried.

## Code structure (preview of L2.1)

| Container | Project / package |
|---|---|
| Web app | `src/Platform.Web` |
| Platform API | `src/Platform.Api`, `src/Platform.Domain`, `src/Platform.Data` |
| Workers | `src/Platform.Workers`, `src/Platform.Imaging` |
| FHIR mapping | `src/Platform.Fhir` |
| Python services | `ml/nlp`, `ml/embeddings`, `ml/serving` |
| Research | `ml/qc`, `ml/model` |
| Shared contracts | `contracts/` (schema, OpenAPI, event schemas) |

## Decisions

| ADR | Decision | Status |
|---|---|---|
| [0001](../adr/0001-blazor-for-the-user-interface.md) | Blazor Web App with OpenSeadragon for the user interface | Accepted |
| [0002](../adr/0002-postgresql-with-pgvector.md) | PostgreSQL with pgvector for metadata and vectors | Accepted |
| [0003](../adr/0003-modular-api-with-event-driven-pipeline.md) | Modular monolith API with an event-driven pipeline on RabbitMQ | Accepted |
| [0004](../adr/0004-onnx-for-model-deployment.md) | ONNX as the model format between Python and .NET | Accepted |
| [0005](../adr/0005-azure-as-cloud-platform.md) | Azure as the cloud platform | Accepted |
| [0006](../adr/0006-breast-cancer-data-scope.md) | Breast cancer data scope: detection first, grading second | Accepted |
