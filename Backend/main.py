from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import csv
import os
from datetime import datetime
import joblib
import numpy as np

app = FastAPI()

DB_NAME = "sensor_data.db"
CSV_FILE = "dataset.csv"
MODEL = joblib.load("model.pkl")


def init_db():
    conn = sqlite3.connect(DB_NAME)
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
        prediction TEXT
    )
    """)
    conn.commit()
    conn.close()


init_db()


if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow([
            "Timestamp",
            "Scenario",
            "FSR1",
            "FSR2",
            "FSR3",
            "FSR4",
            "Temperature",
            "AveragePressure",
            "MaximumPressure",
            "Prediction"
        ])


class SensorData(BaseModel):
    scenario: str
    fsr1: float
    fsr2: float
    fsr3: float
    fsr4: float
    temp1: float


@app.post("/log")
def log_data(data: SensorData):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    avg = (
        data.fsr1 +
        data.fsr2 +
        data.fsr3 +
        data.fsr4
    ) / 4

    mx = max(
        data.fsr1,
        data.fsr2,
        data.fsr3,
        data.fsr4
    )

    features = np.array([[
        data.fsr1,
        data.fsr2,
        data.fsr3,
        data.fsr4,
        data.temp1
    ]])

    prediction = str(MODEL.predict(features)[0])

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO readings(
        timestamp,
        scenario,
        fsr1,
        fsr2,
        fsr3,
        fsr4,
        temp1,
        avg_pressure,
        max_pressure,
        prediction
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        timestamp,
        data.scenario,
        data.fsr1,
        data.fsr2,
        data.fsr3,
        data.fsr4,
        data.temp1,
        avg,
        mx,
        prediction
    ))

    conn.commit()

    # --------------------------------------------------
    # Keep ONLY the latest 100 readings
    # --------------------------------------------------
    cur.execute("""
    DELETE FROM readings
    WHERE id NOT IN (
        SELECT id
        FROM readings
        ORDER BY id DESC
        LIMIT 100
    )
    """)

    conn.commit()
    conn.close()

    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            timestamp,
            data.scenario,
            data.fsr1,
            data.fsr2,
            data.fsr3,
            data.fsr4,
            data.temp1,
            avg,
            mx,
            prediction
        ])

    return {
        "status": "success",
        "prediction": prediction
    }


@app.get("/latest")
def latest():

    conn = sqlite3.connect(DB_NAME)

    row = conn.execute("""
    SELECT
        timestamp,
        scenario,
        fsr1,
        fsr2,
        fsr3,
        fsr4,
        temp1,
        avg_pressure,
        max_pressure,
        prediction
    FROM readings
    ORDER BY id DESC
    LIMIT 1
    """).fetchone()

    conn.close()

    if not row:
        return {}

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
        "prediction": row[9]
    }


@app.get("/data")
def data():

    conn = sqlite3.connect(DB_NAME)

    rows = conn.execute("""
    SELECT
        timestamp,
        scenario,
        fsr1,
        fsr2,
        fsr3,
        fsr4,
        temp1,
        avg_pressure,
        max_pressure,
        prediction
    FROM readings
    ORDER BY id DESC
    LIMIT 100
    """).fetchall()

    conn.close()

    return [{
        "timestamp": r[0],
        "scenario": r[1],
        "fsr1": r[2],
        "fsr2": r[3],
        "fsr3": r[4],
        "fsr4": r[5],
        "temp1": r[6],
        "avg_pressure": r[7],
        "max_pressure": r[8],
        "prediction": r[9]
    } for r in rows]


@app.get("/download_csv")
def download_csv():
    return FileResponse(
        CSV_FILE,
        filename="dataset.csv",
        media_type="text/csv"
    )
