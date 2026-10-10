# SentinelOps Chaos Demo

A lightweight, deliberately breakable cloud e-commerce service designed for **SentinelOps Stage 22 Production-Like End-to-End Validation**.

It allows testing the entire SentinelOps lifecycle:
1. **GitHub Onboarding & Code Indexing**: SentinelOps indexes this codebase (models, routes, exceptions).
2. **Runtime Deployment Connection**: SentinelOps connects to the running service via Health Poller and Webhook Telemetry.
3. **Startup Ingress Handshake**: On startup, the service emits a non-error telemetry event (`event_type="chaos.service.started"`, `signal_type="log"`, `level="INFO"`) to establish baseline connectivity and advance `last_telemetry_at`.
4. **Controlled Incident Simulation**:
   - **Scenario A**: Simulated unhandled exception (`OrderProcessingError`) sends authenticated webhook telemetry, triggering an automated incident and investigation.
   - **Scenario B**: Simulated 503 outage (`Database connection pool exhausted`) detected by SentinelOps health poller, generating an automated HIGH health check failure incident.
   - **Scenario C**: Investigation report correlates runtime stack trace and health events directly to this repository's source code files.

---

## Endpoints

### Public Service API
| Method | Path | Description | Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service information & status | 200 OK |
| `GET` | `/health` | Health probe (normal: 200 OK; outage: 503 Service Unavailable) | 200 / 503 |
| `GET` | `/products` | List available catalog products | 200 OK |
| `GET` | `/products/{id}` | Get product details by ID | 200 OK / 404 |
| `POST` | `/orders` | Place an order (deducts inventory) | 201 Created / 500 |
| `GET` | `/orders/{id}` | Get order details | 200 OK / 404 |

### Admin Chaos Controls (Protected by `X-Admin-Token`)
| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/admin/failures` | Check state of failure toggles |
| `POST` | `/admin/failures/order-processing` | Explicitly set order processing failure (`{"enabled": true/false}`) |
| `POST` | `/admin/failures/order-processing/enable` | Explicitly enable simulated order checkout failure (`OrderProcessingError`) |
| `POST` | `/admin/failures/order-processing/disable` | Explicitly disable simulated order checkout failure |
| `POST` | `/admin/failures/health-outage` | Explicitly set health outage failure (`{"enabled": true/false}`) |
| `POST` | `/admin/failures/health-outage/enable` | Explicitly enable simulated 503 outage on `/health` |
| `POST` | `/admin/failures/health-outage/disable` | Explicitly disable simulated 503 outage on `/health` |
| `POST` | `/admin/failures/reset` | Reset all simulated failures to disabled (normal operating state) |

---

## Configuration

Set the following environment variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `PORT` | Listening port for web server | `8000` |
| `CHAOS_ADMIN_TOKEN` | Secret header required for `/admin/failures/*` | `chaos-admin-secret` |
| `SENTINELOPS_WEBHOOK_URL` | Complete SentinelOps webhook ingestion URL | `https://<public-ingress>/connectors/<connector_id>/ingest` |
| `SENTINELOPS_WEBHOOK_SECRET` | Secret token configured in SentinelOps connector (`X-Sentinel-Secret`) | `None` |
| `SERVICE_NAME` | Service name reported in telemetry | `sentinelops-chaos-demo` |

---

## Local Development & Testing

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run unit tests
```bash
pytest tests/ -v
```

### 3. Run application locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Triggering Chaos Failures

### 1. Simulate Order Processing Incident (Webhook Telemetry)
```bash
# Explicitly enable order processing failure
curl -X POST http://localhost:8000/admin/failures/order-processing/enable \
  -H "X-Admin-Token: chaos-admin-secret"

# Place an order -> returns HTTP 500 and emits telemetry to SentinelOps
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-1", "quantity": 1, "customer_email": "demo@sentinelops.local"}'

# Explicitly disable order processing failure
curl -X POST http://localhost:8000/admin/failures/order-processing/disable \
  -H "X-Admin-Token: chaos-admin-secret"
```

### 2. Simulate Health Outage Incident (Poller Failure)
```bash
# Explicitly enable health outage
curl -X POST http://localhost:8000/admin/failures/health-outage/enable \
  -H "X-Admin-Token: chaos-admin-secret"

# Probe /health -> returns HTTP 503 Service Unavailable
curl -i http://localhost:8000/health

# Explicitly disable health outage
curl -X POST http://localhost:8000/admin/failures/health-outage/disable \
  -H "X-Admin-Token: chaos-admin-secret"
```

### 3. Reset All Failures to Normal Operating State
```bash
curl -X POST http://localhost:8000/admin/failures/reset \
  -H "X-Admin-Token: chaos-admin-secret"
```

---

## Cloud Deployment (e.g. Render / Railway)

1. Push this repository to a public or private GitHub repository (e.g. `https://github.com/<username>/sentinelops-chaos-demo`).
2. Deploy as a Web Service on **Render** (using included `render.yaml` or standard Python web service).
3. Set environment variables `SENTINELOPS_WEBHOOK_URL` (pointing to your full SentinelOps ingress URL `https://<public-ingress>/connectors/<connector_id>/ingest`) and `SENTINELOPS_WEBHOOK_SECRET`.
