# ApexScore backend

FastAPI backend for [ApexScore](https://github.com/Dami99-b/ApexScore), a credit-risk scoring prototype. It generates simulated applicants for Nigeria, the UK and the USA and scores them by combining alternative signals (location consistency, device stability, SIM verification) with traditional financial data (outstanding debt, loan history).

All applicant data is synthetic and held in memory. No real personal or financial data is used.

Live demo: https://apexscore.vercel.app

## API

| Method | Path | Returns |
|---|---|---|
| GET | `/api/applicants` | All simulated applicants |
| GET | `/api/search` | Applicants matching a query |
| GET | `/api/applicant/{id}` | One applicant and their score |
| GET | `/api/applicant/{id}/financial-profile` | Income and spending breakdown |
| GET | `/api/applicant/{id}/credit-report` | Credit history summary |
| GET | `/api/applicant/{id}/full-report` | Everything above in one response |
| GET | `/api/stats` | Portfolio-level statistics |

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API docs.

## Stack

Python, FastAPI, Pydantic, deployed on Vercel.
