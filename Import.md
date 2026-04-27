# Local-First Biometric AI Agent: Garmin & CrossFit Integration

A privacy-focused, agentic AI system designed to correlate biometric data (Garmin/Strava) with unstructured workout data (CrossFit Gym Portals) using a hybrid **FastAPI** and **NanoClaw** architecture.

## 🚀 The Vision
To move beyond simple fitness tracking by creating a local "AI Coach" that:
1. **Detects** workouts automatically via Garmin/Strava APIs.
2. **Contextualizes** the data by scraping today's specific CrossFit WOD (Workout of the Day).
3. **Interviews** the athlete via WhatsApp to gather qualitative data (RPE, scaling, feel).
4. **Analyzes** trends over time using a local LLM (Ollama) to provide meaningful recovery and performance insights.

## 🏗️ System Architecture (Hybrid Design)

This project uses a decoupled, event-driven architecture to maximize **scalability** (FastAPI) and **security** (NanoClaw).


| Layer | Component | Technical Responsibility |
| :--- | :--- | :--- |
| **Orchestrator** | **FastAPI** | State management (SQLite), User Webhooks, and scheduling the analysis pipeline. |
| **Execution** | **NanoClaw** | Secure, containerised "Agentic" web-scraping to navigate non-API gym portals. |
| **Brain** | **Ollama** | Local hosting of Llama 3 / Mistral for 100% private biometric data analysis. |
| **Interface** | **WhatsApp** | Real-time human-in-the-loop communication and data entry. |

## 🛠️ Tech Stack
- **Languages:** Python (FastAPI), TypeScript (NanoClaw).
- **AI/LLM:** Ollama (Llama 3 8B / Mistral).
- **Automation:** Playwright (Headless Browser Scraping), Cron (Polling).
- **Infrastructure:** Docker (Agent Sandboxing).
- **Communication:** Twilio API / WhatsApp Business Gateway.

## 🔄 The Data Pipeline
1. **Ingestion:** A Python worker polls Garmin/Strava for new activity IDs.
2. **Trigger:** On detection, FastAPI dispatches a request to a **NanoClaw Skill**.
3. **Scraping:** NanoClaw spawns a temporary Docker container to log into the CrossFit portal and extract the WOD structure.
4. **Synthesis:** FastAPI aggregates Garmin metrics (HR, Stress, HRV) and the WOD structure.
5. **Human-in-the-loop:** The system pings the user on WhatsApp: *"I see you finished the 5x5 Back Squat WOD. How did your intensity feel compared to your high stress scores this morning?"*
6. **Insight:** User replies are saved to a local SQLite database for weekly trend reporting.

## 📈 CV Highlights (Key Engineering Wins)
- **Agentic Security:** Leveraged NanoClaw's container isolation to prevent cross-contamination during web-navigation tasks.
- **Model Optimization:** Configured Ollama with quantized models for high-performance local inference on consumer hardware.
- **Data Fusion:** Engineered a pipeline to merge time-series biometric data with unstructured natural language workout descriptions.
- **Privacy-First:** Built a 100% local analysis engine, ensuring sensitive health data never leaves the host machine.

## 🚧 Status
- [x] Architecture Design
- [ ] FastAPI Gateway Setup
- [ ] NanoClaw CrossFit Skill Implementation
- [ ] WhatsApp Webhook Integration
