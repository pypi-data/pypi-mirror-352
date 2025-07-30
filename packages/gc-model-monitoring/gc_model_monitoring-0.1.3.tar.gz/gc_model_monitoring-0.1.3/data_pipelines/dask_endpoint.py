from fastapi import FastAPI, BackgroundTasks
import pandas as pd
import gencrafter as why
from gencrafter.core import DatasetProfile
from gencrafter.api.writer.whylabs import WhyLabsWriter
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Disable verbose logging
logging.getLogger("gencrafter").setLevel(logging.WARNING)
app = FastAPI()

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"

# Initialize with performance optimizations
why.init(verbose=False)

@app.get("/fast-profile")
async def run_fast_profile(background_tasks: BackgroundTasks):
    """Optimized endpoint that returns immediately"""
    async def process_data():
        try:
            # 1. FAST Data Loading (with sampling)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    pd.read_parquet,
                    DATA_URL,
                    engine='pyarrow',  # Faster than 'auto'
                    columns=['fare_amount', 'trip_distance'],  # Only needed columns
                    filters=[('passenger_count', '>', 0)],  # Pushdown filtering
                )
                df = await asyncio.to_thread(future.result)
                
                # Sample if large dataset
                if len(df) > 100_000:
                    df = df.sample(100_000)

            # 2. FAST Profiling (disable expensive metrics)
            profile = why.log(
                df,
                schema=why.Schema(
                    resolvers=why.resolvers.LIMITED_RESOLVER,  # Skip expensive metrics
                    types=why.type_inference.ENABLED_TYPES - {"image"}  # Disable image
                )
            ).profile()

            # 3. Quick WhyLabs Mapping
            whylabs_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "columns": list(df.columns),
                "row_count": len(df),
                "metrics": {
                    col: {
                        "missing": profile.view().get_column(col).to_summary_dict().get("missing", 0),
                        "mean": profile.view().get_column(col).to_summary_dict().get("mean")
                    }
                    for col in df.columns
                }
            }

            return {"status": "success", "data": whylabs_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    background_tasks.add_task(process_data)
    return {"status": "started", "message": "Processing in background"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}