from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import pandas as pd, numpy as np, joblib, os
from sklearn.linear_model import LinearRegression

MODEL_PATH = "model.pkl"

# Train model if not available
if not os.path.exists(MODEL_PATH):
    df = pd.DataFrame({
        "hour": np.arange(0, 24),
        "energy": [1.0 if h < 6 or h > 21 else 2.5 if 17 <= h <= 21 else 1.5 for h in range(24)]
    })
    model = LinearRegression().fit(df[["hour"]], df["energy"])
    joblib.dump(model, MODEL_PATH)
else:
    model = joblib.load(MODEL_PATH)

app = FastAPI(title="Smart Home Energy Management System (SHEMS)")

# In-memory data store
records = []

class EnergyUsage(BaseModel):
    timestamp: str = Field(..., example="2025-07-22T00:00:00Z")
    energy_kwh: float = Field(..., example=1.5)
    device_id: str = Field(..., example="METER_MAIN")

@app.post("/api/energy/usage")
def record_usage(u: EnergyUsage):
    records.append(u.dict())
    return {"status": "ok", "total_records": len(records)}

@app.get("/api/energy/usage", response_model=List[EnergyUsage])
def get_usage(limit: int = 10):
    return records[-limit:]

@app.get("/api/energy/optimize")
def optimize(hour: int):
    if not (0 <= hour <= 23):
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")
    
    base = float(model.predict(np.array([[hour]]))[0])
    advice = (
        "Run heavy devices now" if base < 1.5 else
        "Avoid peak; defer tasks" if base > 2.0 else
        "Moderate load"
    )
    return {"hour": hour, "baseline": round(base, 2), "advice": advice}
