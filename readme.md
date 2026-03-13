# Multi-Camera Vehicle Tracking & AI Video Investigation

This project implements a **multi-camera vehicle tracking and analytics system** with an **AI interface** that allows users to query surveillance footage using natural language.

The system combines:

- Multi-camera vehicle tracking
- Digital fence / gate analytics
- LLM reasoning (Ollama)
- Vision-Language Models (VLMs) for visual understanding
- Automated video clip generation

---

## 📁 Dataset & Video Inputs

This demo uses two camera feeds from the RoundaboutHD dataset:

- `RoundaboutHD/imagesc001/video.mp4`
- `RoundaboutHD/imagesc002/video.mp4`

> These video files are referenced by `main_temp.py` via `config/config_files.json`.

---

## 🚀 Setup

### 1) Create and activate a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3) Pull relevant Ollama model(s) locally

This project uses an Ollama model defined in `config/config_files.json` (e.g. `llama3.1:8b`).

```bash
ollama pull llama3.1:8b
```

---

## ▶️ Generate Fence + Tracking Analytics

The first step is to draw the virtual fences on the two videos and generate the analytics JSON outputs.

### 1) Run the main script

```bash
python main_temp.py
```

### 2) Draw digital fences (mouse + keyboard)

The script opens a window for each camera feed. Use the following controls:

- **Left-click**: add a fence vertex
- **`n`**: finish the current fence polygon (requires at least 3 points)
- **`a`**: assign the fence type (entry or exit) to the most recent fence
- **`r`**: reset the current drawing points (clear unfinished polygon)
- **`s`**: finish fence setup and proceed with processing

After finishing the fence setup, the script will process the video and produce two JSON output files:

- `digital_fence_analytics.json`
- `video_analytics.json`

---

## 🧠 Start Ollama + FastAPI UI

With the analytics JSON files generated, start the AI service and API.

### 1) Start Ollama server (terminal #1)

```bash
ollama serve
```

### 2) Start FastAPI backend (terminal #2)

```bash
uvicorn app:app --reload
```

### 3) Open the web UI

Visit: http://localhost:8000

From there you can:

- Ask the AI questions about tracked vehicles and fences
- Use the API routes directly for structured queries

---

## 🧩 API Routes (Quick Reference)

The FastAPI app exposes several routes for querying or generating clips. Use your browser or tools like `curl` / Postman.

- `/objects` – object tracking data
- `/fences` – fence analytics
- `/clips` – clip generation
- `/gate` – gate event filtering
- `/chat` – natural language query interface

---

## ⚙️ Notes

- The configuration is stored in `config/config_files.json`.
- If you want to track a different object ID, update `TARGET_OBJECT` in the config.
- To change input videos, update `VIDEO_PATHS`.
