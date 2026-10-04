from datetime import datetime
from pathlib import Path
import csv
import sqlite3

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ML.predict import predict

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "sensor_data.db"
CSV_FILE = BASE_DIR / "sensor_data.csv"

app = FastAPI(title="Smart Footwear API")


def init_storage():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS readings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            scenario TEXT,
            fsr1 REAL,
            fsr2 REAL,
            fsr3 REAL,
            fsr4 REAL,
            temp1 REAL,
            avg_pressure REAL,
            max_pressure REAL,
            anomaly_score REAL,
            healthy_match_percent REAL,
            mismatch_percent REAL,
            ulcer_risk TEXT
        )
        """)
        conn.commit()

    if not CSV_FILE.exists():
        with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "Timestamp", "Scenario", "FSR1", "FSR2", "FSR3", "FSR4",
                "Temperature", "AveragePressure", "MaximumPressure",
                "AnomalyScore", "HealthyMatchPercent", "MismatchPercent", "UlcerRisk"
            ])


init_storage()


class SensorData(BaseModel):
    scenario: str = "Walking"
    fsr1: float
    fsr2: float
    fsr3: float
    fsr4: float
    temp1: float


def row_to_dict(row):
    return {
        "timestamp": row[0],
        "scenario": row[1],
        "fsr1": row[2],
        "fsr2": row[3],
        "fsr3": row[4],
        "fsr4": row[5],
        "temp1": row[6],
        "avg_pressure": row[7],
        "max_pressure": row[8],
        "anomaly_score": row[9],
        "healthy_match_percent": row[10],
        "mismatch_percent": row[11],
        "ulcer_risk": row[12],
    }


@app.get("/")
def root():
    return {"status": "ok", "service": "Smart Footwear API"}


@app.post("/log")
def log_data(data: SensorData):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    inputs = pd.DataFrame([{
        "FSR1": data.fsr1,
        "FSR2": data.fsr2,
        "FSR3": data.fsr3,
        "FSR4": data.fsr4,
        "Temperature": data.temp1,
    }])

    result = predict(inputs).iloc[0]

    avg = (data.fsr1 + data.fsr2 + data.fsr3 + data.fsr4) / 4
    mx = max(data.fsr1, data.fsr2, data.fsr3, data.fsr4)

    values = (
        timestamp,
        data.scenario,
        data.fsr1,
        data.fsr2,
        data.fsr3,
        data.fsr4,
        data.temp1,
        avg,
        mx,
        float(result["AnomalyScore"]),
        float(result["HealthyMatchPercent"]),
        float(result["MismatchPercent"]),
        str(result["UlcerRisk"]),
    )

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        INSERT INTO readings(
            timestamp, scenario, fsr1, fsr2, fsr3, fsr4, temp1,
            avg_pressure, max_pressure, anomaly_score,
            healthy_match_percent, mismatch_percent, ulcer_risk
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, values)
        conn.execute("""
        DELETE FROM readings
        WHERE id NOT IN (
            SELECT id FROM readings ORDER BY id DESC LIMIT 100
        )
        """)
        conn.commit()

    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(values)

    return {
        "status": "success",
        "anomaly_score": float(result["AnomalyScore"]),
        "healthy_match_percent": float(result["HealthyMatchPercent"]),
        "mismatch_percent": float(result["MismatchPercent"]),
        "ulcer_risk": str(result["UlcerRisk"]),
    }


@app.get("/latest")
def latest():
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("""
        SELECT timestamp, scenario, fsr1, fsr2, fsr3, fsr4, temp1,
               avg_pressure, max_pressure, anomaly_score,
               healthy_match_percent, mismatch_percent, ulcer_risk
        FROM readings ORDER BY id DESC LIMIT 1
        """).fetchone()
    return row_to_dict(row) if row else {}


@app.get("/data")
def data():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
        SELECT timestamp, scenario, fsr1, fsr2, fsr3, fsr4, temp1,
               avg_pressure, max_pressure, anomaly_score,
               healthy_match_percent, mismatch_percent, ulcer_risk
        FROM readings ORDER BY id DESC LIMIT 100
        """).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/download_csv")
def download_csv():
    return FileResponse(CSV_FILE, filename="sensor_data.csv", media_type="text/csv")
