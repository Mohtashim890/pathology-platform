# Requirements: Breast Pathology AI Platform

*Lesson L1.1 deliverable. Copy to `docs/product/requirements.md` and make it your own.*
*Version 0.1 · 2026-10 · Source: [vision](vision.md)*

## How to read this document

- Each user story has an ID (`US-xx`), a role, an epic, a priority and the course module that builds it.
- **Priority** uses MoSCoW for release v1 (detection): **Must** = v1 fails without it; **Should** = important, v1 can ship without it; **Could** = nice to have; **Later** = v2 (grading) or v3 (real data).
- Acceptance criteria use **Given / When / Then**. Each criterion becomes at least one automated test or a demonstrated behaviour (L2.4).
- The stories are written so `tools/create_issues.py` can turn them into GitHub issues. Keep the heading and metadata line formats unchanged.

## Roles

| Role | Short description |
|---|---|
| Pathologist | Reviews slides and AI results, signs out cases, always makes the diagnosis |
| Lab technician | Scans and uploads slides, handles rescans |
| Lab manager | Runs the lab: turnaround time, backlog, triage settings |
| Data scientist | Trains, evaluates, registers and promotes models |
| Administrator | Users, roles, audit, data protection, configuration |

## Epics

| Epic | Covers | Modules |
|---|---|---|
| Ingestion | Upload, storage, metadata, tiles | M3 |
| Quality | Tissue detection, quality checks | M4 |
| Viewer | Viewing slides and AI overlays | M6 |
| AI results | Inference, uncertainty, grading | M5, M7 |
| Models | Model registry, promotion, lineage | M5, M12 |
| Reports | Report extraction, FHIR | M8 |
| Search | Similar-case search | M9 |
| Operations | Worklist, dashboards, KPIs | M6, M11 |
| Security | Identity, audit, de-identification, configuration | M10, M12 |

---

## User stories

### Pathologist

### US-01 Open a slide in the viewer
**Role:** Pathologist · **Epic:** Viewer · **Priority:** Must · **Module:** M6

As a pathologist, I want to open any ingested slide in the web viewer and pan and zoom smoothly, so that I can review it without a desktop viewer.

**Acceptance criteria**
- Given an ingested slide, when I open it from the case page, then the whole-slide overview appears within 2 seconds.
- Given an open slide, when I zoom from overview to full resolution, then each new view is sharp within 1 second on a normal connection.
- Given a slide whose tiles are still being generated, when I open it, then I see a "processing" message instead of an error.

### US-02 See a tumor heatmap
**Role:** Pathologist · **Epic:** Viewer · **Priority:** Must · **Module:** M6

As a pathologist, I want to see the AI's tumor probability as a colored overlay on the slide, so that I can go straight to the suspicious regions.

**Acceptance criteria**
- Given a slide with a finished AI result, when I switch on the tumor layer, then a heatmap is drawn aligned with the tissue at every zoom level.
- Given the tumor layer is on, when I move the opacity slider, then the overlay transparency changes between 0% and 100%.
- Given the tumor layer is on, then a legend shows the color scale from 0 to 1 using a colorblind-safe colormap.
- Given a slide with no AI result yet, when I open it, then the tumor layer is disabled with the reason shown.

### US-03 See how certain the AI is
**Role:** Pathologist · **Epic:** AI results · **Priority:** Must · **Module:** M5

As a pathologist, I want to see the AI's uncertainty for the slide and for each region, so that I know when not to rely on it.

**Acceptance criteria**
- Given a slide with a result, when I open the result panel, then I see the slide-level label, probability and an uncertainty value.
- Given a slide where the model's uncertainty is above the configured threshold, then the result is marked "AI uncertain, review fully".
- Given the uncertainty layer is on, then regions are colored by uncertainty with their own legend.

### US-04 Inspect a region
**Role:** Pathologist · **Epic:** Viewer · **Priority:** Should · **Module:** M6

As a pathologist, I want to click a region and see the AI's numbers for it, so that I can understand a specific prediction.

**Acceptance criteria**
- Given a slide with a result, when I click a point on the tissue, then I see the tile's probability, uncertainty and conformal prediction set.
- Given I click on background (no tissue), then I see "no tissue" instead of a score.

### US-05 Record my decision
**Role:** Pathologist · **Epic:** AI results · **Priority:** Should · **Module:** M6

As a pathologist, I want to mark whether I agree with the AI's slide result and add a comment, so that my decision is final and disagreements can improve the model.

**Acceptance criteria**
- Given a slide result, when I choose "agree" or "disagree" and save, then my decision, name and time are stored with the result.
- Given I have recorded a decision, then the AI result can no longer be changed for that run, only superseded by a new run.
- Given I disagree, then a comment is required.

### US-06 Find similar cases
**Role:** Pathologist · **Epic:** Search · **Priority:** Later · **Module:** M9

As a pathologist, I want to draw a region and find visually similar regions in past cases, so that I can compare with confirmed diagnoses.

**Acceptance criteria**
- Given an open slide, when I draw a rectangle and choose "find similar", then the 10 most similar regions from other cases are shown with thumbnails within 1 second.
- Given a result in the list, when I click it, then that slide opens at that region in a second viewer.

### US-07 See an estimated grade
**Role:** Pathologist · **Epic:** AI results · **Priority:** Later · **Module:** M5

As a pathologist, I want to see an estimated Nottingham grade with its three component scores and uncertainty, so that I can grade more consistently.

**Acceptance criteria**
- Given an invasive tumor slide with a grading result, then I see the estimated grade (1, 2 or 3), the three component scores and a confidence value.
- Given the grading model is uncertain between two grades, then both grades are shown as a prediction set.
- Given a slide without invasive tumor, then no grade is shown.

### US-08 See structured report fields
**Role:** Pathologist · **Epic:** Reports · **Priority:** Later · **Module:** M8

As a pathologist, I want the case's pathology report shown as structured fields (diagnosis, grade, ER, PR, HER2, Ki-67, lymph nodes), so that I can check the facts at a glance.

**Acceptance criteria**
- Given a case with a report, when I open the case page, then extracted fields are shown next to the original text, with each field linked to the sentence it came from.
- Given a field could not be extracted, then it is shown as "not found", never guessed.

### Lab technician

### US-09 Upload a slide
**Role:** Lab technician · **Epic:** Ingestion · **Priority:** Must · **Module:** M3

As a lab technician, I want to upload a slide file and attach it to a case, so that it enters the platform without copying files by hand.

**Acceptance criteria**
- Given a 2 GB SVS file, when I upload it, then it is stored and the server's memory use stays flat during the upload.
- Given an upload finishes, then a SHA-256 checksum is stored and the slide status is "ingested".
- Given the network drops during an upload, when I retry, then the upload resumes instead of starting again.

### US-10 Reject bad files clearly
**Role:** Lab technician · **Epic:** Ingestion · **Priority:** Must · **Module:** M3

As a lab technician, I want unsupported or damaged files rejected with a clear reason, so that I can fix the problem immediately.

**Acceptance criteria**
- Given a file that is not a supported slide format, when I upload it, then it is rejected with "unsupported format" and nothing is stored.
- Given a truncated or corrupt slide file, then it is rejected with "file could not be read".
- Given a slide without mpp in its metadata, then it is accepted with a warning and flagged for manual mpp entry.

### US-11 See the quality verdict
**Role:** Lab technician · **Epic:** Quality · **Priority:** Must · **Module:** M4

As a lab technician, I want to see each slide's quality verdict with reasons, so that I know whether it needs rescanning.

**Acceptance criteria**
- Given an ingested slide, then within 5 minutes it shows a QC verdict of pass, warn or fail.
- Given a warn or fail verdict, then the reasons (blur, folds, pen marks, too little tissue) and their scores are listed.
- Given a QC result, when I open it, then the tissue mask is shown over the thumbnail.

### US-12 Get a rescan list
**Role:** Lab technician · **Epic:** Quality · **Priority:** Should · **Module:** M4

As a lab technician, I want a list of slides that failed QC, so that I can rescan them in one batch.

**Acceptance criteria**
- Given slides with a fail verdict, when I open the rescan list, then they are listed oldest first with case key and reason.
- Given I upload a rescan for a slide, then the old slide is marked "replaced" and the new one is linked to it.

### US-13 Detect duplicate uploads
**Role:** Lab technician · **Epic:** Ingestion · **Priority:** Should · **Module:** M3

As a lab technician, I want to be warned when I upload a slide that already exists, so that the same slide isn't processed twice.

**Acceptance criteria**
- Given a slide with the same checksum already exists, when I upload it again, then I am told which case it belongs to and no new slide is created.

### US-14 Upload a batch of slides
**Role:** Lab technician · **Epic:** Ingestion · **Priority:** Could · **Module:** M7

As a lab technician, I want to upload a folder of slides at once, so that a whole scanning run gets in without one-by-one uploads.

**Acceptance criteria**
- Given a folder of 50 slides, when I upload it, then each slide is processed independently and one failure doesn't stop the others.
- Given a batch upload, then I see progress per slide and a final summary of successes and failures.

### Lab manager

### US-15 Prioritized worklist
**Role:** Lab manager · **Epic:** Operations · **Priority:** Later · **Module:** M11

As a lab manager, I want cases ranked by AI probability, uncertainty and QC status, so that the most urgent cases are read first.

**Acceptance criteria**
- Given cases with results, when I open the worklist, then cases are sorted by priority score, highest first.
- Given a case with a QC fail, then it is shown separately and not ranked by AI score.
- Given a pathologist opens a case from the worklist, then it is marked "in review" for everyone.

### US-16 Turnaround and backlog dashboard
**Role:** Lab manager · **Epic:** Operations · **Priority:** Should · **Module:** M6

As a lab manager, I want to see turnaround time and backlog, so that I can act before targets are missed.

**Acceptance criteria**
- Given cases in the platform, then the dashboard shows median and 90th percentile turnaround time per week.
- Given cases waiting, then the dashboard shows how many are waiting at each stage (ingested, QC, AI, review).
- Given I choose a date range, then all charts update to that range.

### US-17 Adjust triage thresholds
**Role:** Lab manager · **Epic:** Operations · **Priority:** Later · **Module:** M11

As a lab manager, I want to change the triage thresholds and see their expected effect before saving, so that I can balance safety and workload.

**Acceptance criteria**
- Given the settings page, when I move a threshold, then the expected sensitivity and the number of cases in each priority group are shown using validation data.
- Given I save new thresholds, then the change is recorded in the audit log with old and new values.

### US-18 AI agreement by scanner
**Role:** Lab manager · **Epic:** Operations · **Priority:** Should · **Module:** M6

As a lab manager, I want to see how often pathologists agree with the AI, per scanner and per month, so that I notice if the AI gets worse on some data.

**Acceptance criteria**
- Given recorded pathologist decisions, then the dashboard shows the agreement rate by scanner and by month.
- Given the agreement rate for a scanner drops more than 10 points below its average, then it is highlighted.

### US-19 Export monthly KPIs
**Role:** Lab manager · **Epic:** Operations · **Priority:** Could · **Module:** M11

As a lab manager, I want to export the monthly KPIs as a CSV file, so that I can include them in management reports.

**Acceptance criteria**
- Given a month, when I export, then I get a CSV with turnaround time, case volume, QC failure rate and AI agreement, without any patient identifiers.

### Data scientist

### US-20 Register a model
**Role:** Data scientist · **Epic:** Models · **Priority:** Must · **Module:** M5

As a data scientist, I want to register an ONNX model with its model card, so that the platform can run it.

**Acceptance criteria**
- Given an ONNX file and a model card JSON, when I register them, then a model version is created with status "staging".
- Given a model card missing required fields (training data, metrics, intended use, input mpp), then registration is rejected with the missing fields listed.
- Given an ONNX file whose input shape doesn't match the model card, then registration is rejected.

### US-21 Promote a model safely
**Role:** Data scientist · **Epic:** Models · **Priority:** Should · **Module:** M12

As a data scientist, I want a model promoted to production only if it beats the current model on a fixed golden set and is approved, so that production never gets worse.

**Acceptance criteria**
- Given a staging model, when promotion is requested, then it is evaluated on the golden set and compared with the production model.
- Given the new model is not better on the agreed metrics, then promotion is blocked with the comparison shown.
- Given it is better, then promotion waits for a named approver and the previous model is kept for rollback.

### US-22 Trace every result
**Role:** Data scientist · **Epic:** Models · **Priority:** Must · **Module:** M3

As a data scientist, I want every result to record which model, pipeline and QC versions produced it, so that any result can be explained and reproduced.

**Acceptance criteria**
- Given any slide result, then its model version, pipeline version, QC version and run time are stored and shown in the result details.
- Given a model version, then I can list every result it produced.

### US-23 Re-run inference without duplicates
**Role:** Data scientist · **Epic:** AI results · **Priority:** Must · **Module:** M7

As a data scientist, I want to re-run inference on a slide with a chosen model without creating duplicate results, so that retries and re-runs are safe.

**Acceptance criteria**
- Given a slide already processed by a model version, when the same request arrives again, then no second run is created.
- Given a new model version, when I request a re-run, then a new run is created and the old result stays available.

### US-24 Export a training dataset
**Role:** Data scientist · **Epic:** AI results · **Priority:** Could · **Module:** M5

As a data scientist, I want to export tissue tiles with their labels at a chosen mpp, so that I can train models on platform data.

**Acceptance criteria**
- Given a set of slides and a target mpp, when I export, then tiles are written at that mpp with a manifest of slide ID, coordinates and label.
- Given a slide failed QC, then its tiles are excluded unless I explicitly include them.

### US-25 See failed jobs
**Role:** Data scientist · **Epic:** AI results · **Priority:** Should · **Module:** M7

As a data scientist, I want to see pipeline jobs that failed and retry them, so that no slide is silently left unprocessed.

**Acceptance criteria**
- Given a job that failed after all automatic retries, then it appears on the failed-jobs page with the error and the slide.
- Given a failed job, when I click retry, then it is processed again and removed from the list if it succeeds.

### Administrator

### US-26 Manage users and roles
**Role:** Administrator · **Epic:** Security · **Priority:** Later · **Module:** M10

As an administrator, I want users to log in with single sign-on and have one of the five roles, so that each person can only do what their job needs.

**Acceptance criteria**
- Given a user without a role, when they log in, then they can see nothing except a "no access" page.
- Given a user with the lab technician role, when they call a model registration endpoint, then the request is refused (403).
- Given every API endpoint, then each is covered by an authorization policy (checked by an automated test).

### US-27 Audit every access
**Role:** Administrator · **Epic:** Security · **Priority:** Should · **Module:** M10

As an administrator, I want every read and change of slides, results and reports recorded, so that I can answer "who saw or changed what, and when".

**Acceptance criteria**
- Given any user views a slide or result, then an audit entry with user, action, entity and time is written.
- Given the audit page, when I filter by user, entity or date, then matching entries are shown.
- Given an audit entry, then it cannot be edited or deleted through the platform.

### US-28 Remove identifying information
**Role:** Administrator · **Epic:** Security · **Priority:** Must · **Module:** M10

As an administrator, I want slide label and macro images and identifying metadata removed on ingestion, so that no patient identifiers enter the platform.

**Acceptance criteria**
- Given a slide with a label or macro image, when it is ingested, then the stored copy contains neither.
- Given a slide whose de-identification check fails, then it is rejected and quarantined, not stored.
- Given any log line, then it contains case keys only, never names, dates of birth or hospital numbers.

### US-29 Switch storage and messaging by configuration
**Role:** Administrator · **Epic:** Security · **Priority:** Should · **Module:** M12

As an administrator, I want to change storage (MinIO or Azure Blob) and messaging (RabbitMQ or Azure Service Bus) through configuration, so that the same build runs locally and in the cloud.

**Acceptance criteria**
- Given the same container images, when the configuration selects Azure Blob instead of MinIO, then uploads and tile reads work with no code change.
- Given an invalid storage configuration, then the service fails at startup with a clear error rather than at the first request.

### US-30 Delete a case completely
**Role:** Administrator · **Epic:** Security · **Priority:** Could · **Module:** M10

As an administrator, I want to delete a case and everything derived from it, so that the lab can honor data retention rules and data withdrawal requests.

**Acceptance criteria**
- Given a case, when I delete it, then its slides, tiles, results, reports and embeddings are removed from storage and the database.
- Given a deletion, then an audit entry remains recording that the case key was deleted, by whom and when.

---

## Non-functional requirements

| ID | Category | Requirement | Target | Verified in |
|---|---|---|---|---|
| NFR-01 | Performance | Tile response time | p95 < 200 ms for cached tiles | L3.4 benchmark |
| NFR-02 | Performance | Upload memory | Server memory flat for a 2 GB upload | L3.2 metrics |
| NFR-03 | Performance | End-to-end processing | One slide from upload to result < 10 min on CPU | L7.5 benchmark |
| NFR-04 | Scalability | Throughput grows with workers | Slides per hour scales ≥ 1.6× from 1 to 2 workers | L7.5 benchmark |
| NFR-05 | Privacy | No patient identifiers | Only pseudonymous case keys stored or logged | L10.2 tests |
| NFR-06 | Security | Encryption | TLS in transit; encryption at rest for database and object storage | L10.3, L12.2 |
| NFR-07 | Security | Supply chain | Dependency, secret and container scans pass in CI | L10.3 |
| NFR-08 | Availability | Service availability | ≥ 99.5% monthly during lab hours (cloud) | L13.1 SLOs |
| NFR-09 | Reliability | No lost work | Every ingested slide reaches a result, a failed job or a QC fail; none silently lost | L7.1 tests |
| NFR-10 | Recoverability | Backup and restore | Database and slides restorable; restore drill < 4 hours | L13.1 drill |
| NFR-11 | Interoperability | Standards | Slides: SVS, NDPI, MRXS, TIFF, DICOM WSI; reports: FHIR R4 | L3.3, L8.3 |
| NFR-12 | Portability | Data swap | Partner data replaces public data by configuration only | L12.2, v3 |
| NFR-13 | Reproducibility | ML runs | Every training run records code version, config, data version and seed | L5.1 |
| NFR-14 | Model quality | Calibration | ECE ≤ 0.05 on the test set for production models | L5.4 |
| NFR-15 | Observability | Tracing | One trace connects upload, queue, workers and result | L7.5 |
| NFR-16 | Usability | First use | A pathologist opens a slide and finds the heatmap without training in < 2 min | L6.4 usability test |
| NFR-17 | Maintainability | Quality gates | CI builds, tests and lints every pull request; main branch protected | L2.3 |

## Out of scope

Primary diagnosis without a pathologist; regulatory clearance; scanner control; billing and multi-tenant SaaS (see [vision](vision.md)).

## Open questions

1. What uncertainty threshold marks a result "AI uncertain"? (decide in L5.4 from calibration data)
2. How long must slides be kept, and who may delete them? (ask a real lab manager)
3. Should pathologists be able to see the AI result before forming their own opinion, or only after? (automation bias risk; ask real pathologists)
