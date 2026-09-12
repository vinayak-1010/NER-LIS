# NER-LIS

### North Eastern Region – Logistics Intelligence System

> AI-powered logistics and accessibility intelligence platform for predicting road disruptions, recommending risk-aware routes, and tracking essential deliveries across the North Eastern Region of India.

[![Status](https://img.shields.io/badge/status-in%20development-yellow)]()
[![Python](https://img.shields.io/badge/python-3.x-blue)]()
[![React](https://img.shields.io/badge/frontend-React.js-blue)]()
[![PostGIS](https://img.shields.io/badge/database-PostgreSQL%20%2B%20PostGIS-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## Overview

Logistics in the North Eastern Region of India can be affected by difficult terrain, heavy rainfall, landslides, floods, road damage and connectivity limitations.

NER-LIS is designed as an operational decision-support platform that combines:

* GIS and road-network data
* Weather information
* Historical disruption data
* GPS/vehicle movement
* Field incident reports
* Machine learning
* Risk-aware route optimization
* Essential shipment prioritization

The goal is not simply to display a map or track a vehicle.

NER-LIS aims to answer three important questions:

1. Can this destination be reached?
2. Which route is safest and fastest under current conditions?
3. Which essential deliveries are affected?

---

## Problem

A conventional navigation system may show a route as available even when recent weather, incidents or road conditions make that route practically difficult or inaccessible.

At the same time, logistics information is often distributed across different sources such as weather systems, field reports, vehicle data and historical records.

NER-LIS brings these signals together into one location-aware intelligence layer.

---

## Solution

NER-LIS follows this intelligence loop:

**Data → Validation → Risk Prediction → Route Optimization → Shipment Impact → Alert/Action → Feedback**

The system can:

* Monitor road accessibility
* Predict potential disruptions
* Estimate delivery delay
* Calculate route risk
* Recommend alternative routes
* Track vehicles and shipments
* Prioritize essential goods
* Accept geo-tagged field reports
* Generate alerts
* Support what-if disruption planning

---

## Core Features

### Accessibility Intelligence

Road segments can be classified as:

* Open
* Risky
* Blocked
* Unknown

### AI Disruption Prediction

Predicts the probability of future disruption using factors such as:

* rainfall
* elevation
* slope
* historical incidents
* road characteristics
* traffic
* spatial vulnerability
* seasonal patterns

### Risk-Aware Routing

Provides multiple route modes:

* Fastest
* Safest
* Balanced
* Emergency

### Dynamic Route Safety Score

Routes are evaluated using factors such as:

* distance
* expected travel time
* road risk
* disruption probability
* road reliability
* expected delay

### Essential Supply Priority

Critical shipments such as medicines and emergency supplies receive higher priority.

### GPS Logistics Tracking

Track vehicle position, route progress and shipment status.

### Field Reporting

Field users can submit:

* incident type
* GPS location
* severity
* photographs
* timestamp
* verification status

### Offline Field Mode

Field reports can be stored locally when connectivity is unavailable and synchronized when connectivity returns.

### Alerts

Generate alerts for:

* blocked roads
* high-risk corridors
* predicted disruptions
* delivery delays
* emergency situations

### What-If Planning

Simulate a road or bridge closure and identify:

* affected routes
* affected shipments
* alternative routes
* potential delays

---

## System Architecture

```text
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

---

## Technology Stack

### Frontend

* React.js / Next.js
* Tailwind CSS
* Leaflet / MapLibre

### Backend

* Python
* FastAPI
* REST APIs

### Database

* PostgreSQL
* PostGIS

### AI / Machine Learning

* Python
* scikit-learn
* XGBoost / Random Forest
* Pandas
* NumPy

### Routing

* Graph-based road network
* Dijkstra / A*
* Dynamic route cost

### Mobile / Field Reporting

* Flutter / React Native / PWA

### Infrastructure

* Docker
* GitHub Actions
* Cloud deployment
* Object storage
* Redis where required

---

## AI/ML Pipeline

```text
Historical Data
      +
Weather
      +
Terrain
      +
Road Condition
      +
Incidents
      +
Traffic
      ↓
Feature Engineering
      ↓
Model Training
      ↓
Disruption Probability
      ↓
Confidence Score
      ↓
Risk-Aware Routing
      ↓
Shipment Impact
```

The project uses ML as a prediction layer rather than claiming certainty. High-impact decisions should retain human verification.

---

## Pilot Strategy

The first version focuses on **one pilot district/corridor**.

The system can then expand:

```text
Pilot Corridor
      ↓
Pilot District
      ↓
Multiple Districts
      ↓
State-Level Deployment
      ↓
Wider NER
```

---

## Example Workflow

Imagine a truck carrying emergency medicines.

1. Vehicle starts on its planned route.
2. Weather conditions deteriorate.
3. Rainfall and historical information increase corridor risk.
4. NER-LIS predicts elevated disruption probability.
5. The route engine evaluates alternatives.
6. The safest feasible route is recommended.
7. The shipment is marked at risk.
8. An alert is generated.
9. A field officer can verify the incident.
10. Routes and shipment status are recalculated.

---

## Project Status

### Current Stage

`In Development`

### Planned Milestones

* [ ] Project setup
* [ ] GIS map
* [ ] PostGIS data layer
* [ ] Core backend APIs
* [ ] GPS simulation
* [ ] Shipment tracking
* [ ] Disruption prediction
* [ ] Risk-aware routing
* [ ] Field reporting
* [ ] Offline synchronization
* [ ] Alerts
* [ ] What-if planning
* [ ] Cloud deployment
* [ ] Testing
* [ ] v1.0 release

---

## Repository Structure

```text
frontend/      → Web dashboard
mobile/        → Field reporting application
backend/       → APIs and business logic
ml/            → Machine learning pipeline
routing/       → Route optimization
scripts/       → Seed, reset and simulation scripts
infra/         → Docker and deployment configuration
docs/          → Architecture and technical documentation
tests/         → Integration and end-to-end tests
.github/       → CI/CD and GitHub templates
```

---

## Getting Started

### Prerequisites

* Node.js
* Python 3.x
* PostgreSQL
* PostGIS
* Docker
* Git

### Clone

```bash
git clone https://github.com/YOUR-USERNAME/ner-lis.git
cd ner-lis
```

### Environment Setup

Copy:

```bash
cp .env.example .env
```

Then configure:

```text
DATABASE_URL=
WEATHER_API_KEY=
MAP_API_KEY=
JWT_SECRET=
REDIS_URL=
```

Never commit `.env`.

### Run with Docker

```bash
docker compose up --build
```

---

## Development Workflow

1. Create an issue.
2. Create a feature branch.
3. Implement the feature.
4. Add/update tests.
5. Open a Pull Request.
6. Get another team member to review it.
7. Merge only after CI passes.

Example:

```bash
git checkout -b feat/risk-aware-routing
```

---

## Team

### Nexora

NER-LIS is being developed by a four-member student team under the team name **Nexora**.

| Member   | Area                |
| -------- | ------------------- |
| Member 1 | Frontend & GIS      |
| Member 2 | Backend & Data      |
| Member 3 | AI/ML & Routing     |
| Member 4 | Mobile, DevOps & QA |

---

## Roadmap

NER-LIS is being developed incrementally, beginning with a focused pilot and expanding toward a broader regional logistics intelligence platform.

---

## Disclaimer

NER-LIS is an academic/engineering project and prototype.

AI predictions represent estimated risk and should not be treated as a guarantee of road safety or real-world accessibility.

Real-world deployment would require validated data sources, field verification, operational approval, security controls and appropriate government/enterprise integrations.

---

## License

This project is licensed under the MIT License.
