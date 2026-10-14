# 0003: Modular monolith API with an event-driven pipeline

- **Status:** Accepted
- **Date:** 2026-10-13
- **Deciders:** Mohtashim
- **Related:** US-09, US-14, US-23, US-25, NFR-02, NFR-03, NFR-04, NFR-09, NFR-15

## Context

The platform mixes two very different kinds of work:

- **Short requests** from users: list cases, open a slide, fetch a tile, save a decision. These need low latency.
- **Long jobs** per slide: quality control, tiling, inference, aggregation, report extraction, embeddings. These take seconds to minutes, use a lot of CPU or GPU, are partly written in Python, and must not be lost (NFR-09). Throughput must grow by adding workers (NFR-04).

There is one developer, so operational complexity has a real cost.

## Options considered

1. **Monolith**: one ASP.NET Core application does everything, including long jobs in background threads.
2. **Modular monolith**: one deployable application, split internally into modules with clear boundaries.
3. **Microservices / fully event-driven**: many small services, each with its own data, communicating only through events.
4. **Hybrid**: a modular monolith API for requests, plus an event-driven pipeline of independent workers for long jobs, sharing one database and one object store.

| Criterion | Monolith | Modular monolith | Microservices | Hybrid |
|---|---|---|---|---|
| Simple to build and run alone | Best | Good | Poor | Good |
| Scale long jobs independently (NFR-04) | No | No | Yes | Yes |
| Survive a worker crash without losing work (NFR-09) | Hard | Hard | Yes | Yes |
| Python and .NET side by side | Awkward | Awkward | Natural | Natural |
| Consistency of data | Simple (one transaction) | Simple | Hard (eventual everywhere) | Simple in the API, eventual in the pipeline |
| Operational load for one person | Lowest | Low | Highest | Medium |

## Decision

We will build a **modular monolith API** (`Platform.Api` with modules for slides, tiles, QC, results, models, reports, search, triage, admin) and an **event-driven pipeline**: the API publishes events such as `SlideIngested`; independent workers (`Platform.Workers` in .NET and Python services) consume them, do the work and publish the next event. Messaging uses **RabbitMQ** locally, accessed through **MassTransit**, so the transport can be swapped for **Azure Service Bus** in the cloud by configuration. Events are published with the **outbox pattern** (written in the same database transaction as the data change), and every consumer is **idempotent** (e.g. a unique `(slideId, modelVersionId)` per inference run).

## Consequences

- **Positive:** users never wait for long jobs; workers scale and fail independently; Python and .NET cooperate through events; retries and dead-letter queues make failures visible (US-25).
- **Negative:** the pipeline is **eventually consistent** (a slide's status lags the real work by seconds); debugging needs tracing across services (NFR-15, L7.5); a message broker must be run and monitored.
- **Licensing note:** MassTransit announced that version 9 is commercially licensed, while version 8 stays open source. Check the current licence before L7.1 and decide between MassTransit 8, a commercial licence, or an open-source alternative. Keep messaging behind our own interfaces so this choice stays reversible.
- **Follow-up:** event schemas are versioned contracts in `contracts/events/` (L1.3). Revisit if the API's modules need to scale separately, which would justify splitting it.
