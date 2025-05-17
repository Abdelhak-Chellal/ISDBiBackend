# ISDBiBackend – Installation & API Usage Guide

This guide provides **step-by-step installation instructions**, **API endpoint usage**, and **example outputs** for the ISDBiBackend project.

---

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Installation](#2-installation)
- [3. Running the Server](#3-running-the-server)
- [4. API Endpoints](#4-api-endpoints)
  - [4.1. Use Case Scenario](#41-use-case-scenario)
  - [4.2. Product Design](#42-product-design)
  - [4.3. Standards Enhancement](#43-standards-enhancement)
  - [4.4. Reverse Transactions](#44-reverse-transactions)
  - [4.5. Auditing](#45-auditing)
  - [4.6. Fraud Detection](#46-fraud-detection)
  - [4.7. Chat History](#47-chat-history)
- [5. Expected Output Formats](#5-expected-output-formats)
- [6. Docker Usage (Optional)](#6-docker-usage-optional)
- [7. Notes & Troubleshooting](#7-notes--troubleshooting)

---

## 1. Prerequisites

- **Python 3.11+** (recommended: install via [pyenv](https://github.com/pyenv/pyenv))
- **pip** (Python package manager)
- **git**
- (Optional) **Docker** for containerized usage

---

## 2. Installation

### Clone the Repository

```sh
git clone https://github.com/Abdelhak-Chellal/ISDBiBackend.git
cd ISDBiBackend
```

### Install Python Dependencies

It's recommended to use a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Dependencies include:
- Django (>=4.2)
- djangorestframework
- requests
- python-dotenv
- chromadb
- openai (or your preferred LLM provider)

### Database Initialization

By default, the project uses **SQLite**.

```sh
cd ISDBiBackend
python manage.py migrate
```

---

## 3. Running the Server

Start the Django development server:

```sh
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## 4. API Endpoints

All endpoints accept and return **JSON**. Most require two POST fields: `question` and `chat_id`.

### 4.1. Use Case Scenario

- **Endpoint:** `/scenario/prompt/`
- **Method:** `POST`
- **Payload:**
  ```json
  {
    "question": "Describe a Murabaha transaction.",
    "chat_id": "unique_chat_id_1"
  }
  ```
- **Response Example:**
  ```json
  {
    "answer": "<Detailed breakdown of standards, profit, ledger, etc.>"
  }
  ```

### 4.2. Product Design

- **Endpoint:** `/product-design/prompt/`
- **Method:** `POST`
- **Payload:** Same as above.

- **Response Example:**
  ```json
  {
    "answer": "<Unified report on product structure, standards, risk analysis, etc.>"
  }
  ```

### 4.3. Standards Enhancement

- **Endpoint:** `/standards/prompt/`
- **Method:** `POST`
- **Payload:** Same as above.

- **Response Example:**
  ```json
  {
    "answer": {
      "raw": {
        "review": "...",
        "proposal": "...",
        "validator": "..."
      },
      "summaries": {
        "review": "...",
        "proposal": "...",
        "validator": "..."
      }
    }
  }
  ```

### 4.4. Reverse Transactions

- **Endpoint:** `/reverse/prompt/`
- **Method:** `POST`
- **Payload:** Same as above.

- **Response Example:**
  ```json
  {
    "answer": "<Relevant FAS standards, justifications, and journal entries>"
  }
  ```

### 4.5. Auditing

- **Endpoint:** `/auditing/prompt/`
- **Method:** `POST`
- **Payload:** Same as above.

- **Response Example:**
  ```json
  {
    "answer": {
      "Compliance Status": "Non-Compliant",
      "Findings": [
        "No record of independent internal Shari’ah audit",
        "Board approval did not include documented review"
      ],
      "Applicable AAOIFI Standards": "GS 10, Clause 4.1; GS 11, Clause 6.2"
    }
  }
  ```

### 4.6. Fraud Detection

- **Endpoint:** `/fraud-detection/prompt/`
- **Method:** `POST`
- **Payload:** Same as above.

- **Response Example:**
  ```json
  {
    "answer": {
      "Compliance": "No",
      "Explanation": "Suspicious activity detected...",
      "Applicable AAOIFI Standards": "GS 11 Clause 7.1"
    }
  }
  ```

### 4.7. Chat History

- **Endpoint:** `/chat/history/<chat_id>/`
- **Method:** `GET`
- **Response Example:**
  ```json
  [
    {
      "chat_id": "unique_chat_id_1",
      "question": "Describe a Murabaha transaction.",
      "answer": "...",
      "timestamp": "2025-05-17T21:55:00Z"
    },
    ...
  ]
  ```

#### List All Chat IDs

- **Endpoint:** `/chat/ids/`
- **Method:** `GET`
- **Response Example:**
  ```json
  {
    "chat_ids": ["unique_chat_id_1", "unique_chat_id_2", ...]
  }
  ```

---

## 5. Expected Output Formats

- **Standardized JSON responses** giving answers, summaries, and validation verdicts.
- See above for example outputs per endpoint.
- For endpoints running "multiAgents" logic, you may receive both raw and summarized feedback.

---

## 6. Docker Usage (Optional)

This project provides a `Dockerfile` for easy containerization.

### Build the Docker Image

```sh
docker build -t isdbibackend .
```

### Run the Container

```sh
docker run -p 8000:8000 isdbibackend
```

(You may need to run migrations and seed the database inside the container if not already done.)

---

## 7. Notes & Troubleshooting

- **LLM API Key**: The system expects a valid `TOGETHER_API_KEY` (or OpenAI key) in the environment for all LLM operations.
- **Database**: By default, uses SQLite (`db.sqlite3`). For production, configure your preferred DB in `settings.py`.
- **Static Files**: Served via Django’s staticfiles in development.
- **CORS**: All origins are allowed (`CORS_ALLOW_ALL_ORIGINS=True`).
- **Error Handling**: Most endpoints will return a 400 error if required fields are missing.
- **Further Customization**: See the respective Django apps for detailed logic and model definitions.

---

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF (Django Rest Framework)](https://www.django-rest-framework.org/)

---

*For questions, raise an issue or contact the repository owner.*
