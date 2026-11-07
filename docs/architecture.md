# NER-LIS — Architecture

## System Architecture

```
              ┌──────────────────────┐
              │     Data Sources     │
              │ Weather • GIS • GPS  │
              │ Incidents • History  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Ingestion Layer   │
              │ Validation • Mapping │
              │ Normalization        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Spatial/Data Layer  │
              │ PostgreSQL + PostGIS │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Feature & Risk Engine│
              │ Weather • Terrain    │
              │ Historical Risk      │
              └──────────┬───────────┘
                         │
              ┌──────────▼───────────┐
              │      AI/ML Layer     │
              │ Disruption • Delay   │
              │ Prediction           │
              └──────────┬───────────┘
                         │
              ┌──────────▼───────────┐
              │   Routing Engine     │
              │ Dijkstra / A*        │
              │ Risk-aware routing   │
              └──────────┬───────────┘
                         │
              ┌──────────▼───────────┐
              │ Decision Layer       │
              │ Shipment Risk        │
              │ Priority • Alerts    │
              └──────────┬───────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
 ┌───────────────────┐       ┌──────────────────┐
 │ Web Dashboard     │       │ Field App / PWA  │
 │ GIS • Analytics   │       │ Reports • GPS    │
 └───────────────────┘       └──────────────────┘
```

## Technology Stack

| Layer     | Technology                          |
| --------- | ----------------------------------- |
| Frontend  | Next.js 14, Tailwind CSS, Leaflet   |
| Backend   | Python 3.11, FastAPI, Uvicorn       |
| Database  | PostgreSQL 15, PostGIS 3            |
| ORM       | SQLAlchemy 2, Alembic               |
| Cache     | Redis 7                             |
| ML        | scikit-learn, XGBoost, Pandas       |
| Routing   | NetworkX + custom Dijkstra/A*       |
| Auth      | JWT (python-jose), bcrypt           |
| DevOps    | Docker Compose, GitHub Actions      |
| Testing   | pytest (backend), Jest (frontend)   |

## Pilot Corridor

The first deployment targets the **Guwahati → Shillong** corridor (NH6 / NH40).

## Database Tables

- `users` — system users with roles (admin, operator, field_officer)
- `road_segments` — PostGIS LineString geometry, status, risk score, disruption probability
- `incidents` — field-reported events (landslide, flood, road damage, etc.)
- `vehicles` — tracked fleet with GPS position
- `shipments` — cargo with priority (normal/high/critical) and status tracking
- `alerts` — system-generated notifications

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

| Endpoint                         | Method | Description                    |
| -------------------------------- | ------ | ------------------------------ |
| `/auth/register`                 | POST   | Create user account            |
| `/auth/login`                    | POST   | Authenticate and get JWT       |
| `/auth/me`                       | GET    | Current user profile           |
| `/roads/`                        | GET    | List road segments             |
| `/roads/geojson`                 | GET    | GeoJSON FeatureCollection      |
| `/roads/{id}`                    | GET    | Single road segment            |
| `/roads/{id}`                    | PATCH  | Update status/risk score       |
| `/incidents/`                    | GET    | List incidents                 |
| `/incidents/report`              | POST   | Submit new incident            |
| `/incidents/{id}/verify`         | POST   | Mark incident as verified      |
| `/incidents/geojson`             | GET    | GeoJSON incidents overlay      |
| `/vehicles/`                     | GET    | List vehicles                  |
| `/vehicles/{id}`                 | GET    | Single vehicle                 |
| `/vehicles/{id}/position`        | POST   | Update GPS position            |
| `/vehicles/positions/geojson`    | GET    | Live positions GeoJSON         |
| `/shipments/`                    | GET    | List shipments                 |
| `/shipments/`                    | POST   | Create shipment                |
| `/shipments/{id}`                | GET    | Single shipment                |
| `/shipments/{id}/status`         | PATCH  | Update shipment status         |
| `/routing/route`                 | POST   | Compute risk-aware route       |
| `/alerts/`                       | GET    | List active alerts             |
| `/alerts/{id}/resolve`           | POST   | Resolve an alert               |
| `/ml/predict-disruption`         | POST   | Disruption prediction          |
