from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.core.schema import DatasetSchema
from gencrafter.core.segmentation_partition import (
    segment_on_column,
    SegmentationPartition,
    ColumnMapperFunction,
    SegmentFilter
)
from datetime import datetime
from typing import Dict, Any, List
import warnings
import numpy as np

app = FastAPI()

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load REAL e-commerce dataset from UCI Machine Learning Repository
def load_real_ecommerce_data():
    # URL for the Online Retail dataset from UCI
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    
    try:
        # Load the dataset (this may take a moment as it downloads)
        df = pd.read_excel(url)
        
        # Process and rename columns to match our expected schema
        df = df.rename(columns={
            'InvoiceDate': 'date',
            'Description': 'product',
            'StockCode': 'product_id',
            'Quantity': 'sales_last_week',
            'UnitPrice': 'market_price'
        })
        
        # Create synthetic rating (since original dataset doesn't have ratings)
        np.random.seed(42)
        df['rating'] = np.random.randint(1, 6, size=len(df))
        
        # Create category based on product ID prefix
        df['category'] = df['product_id'].astype(str).str[0].map({
            '1': 'Electronics',
            '2': 'Home Goods',
            '3': 'Clothing',
            '4': 'Office Supplies',
            '5': 'Garden',
            '6': 'Toys',
            '7': 'Food',
            '8': 'Health',
            '9': 'Beauty'
        }).fillna('Other')
        
        # Select and return only the columns we need
        return df[['date', 'product', 'category', 'rating', 'market_price', 'sales_last_week']]
    
    except Exception as e:
        print(f"Error loading dataset: {e}")
        # Fallback to generated data if download fails
        return generate_fallback_data()

def generate_fallback_data():
    # Generate realistic synthetic data if download fails
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=1000)
    data = {
        'date': np.random.choice(dates, 1000),
        'product': [f'Product {i}' for i in range(1000)],
        'category': np.random.choice([
            'Electronics', 'Clothing', 'Home Goods', 
            'Office Supplies', 'Garden', 'Toys'
        ], 1000),
        'rating': np.random.randint(1, 6, 1000),
        'market_price': np.round(np.random.uniform(5, 500, 1000), 2),
        'sales_last_week': np.random.randint(1, 100, 1000)
    }
    return pd.DataFrame(data)

# Load the data
df = load_real_ecommerce_data()

def map_segmentation_to_whylabs(
    segmented_results: Dict[str, Any],
    segments: Dict[str, Any],
    dataset: pd.DataFrame
) -> Dict[str, Any]:
    """
    Properly maps segmented gencrafter results to WhyLabs-style format
    """
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": len(dataset),
            "segments_analyzed": len(segmented_results),
            "alert_status": "OK"
        },
        "segments": {},
        "segment_comparison": {
            "metrics": ["rating", "market_price", "sales_last_week"],
            "comparisons": {}
        }
    }

    for segment_key, segment_profile in segmented_results.items():
        segment_name = segment_key.split(",")[-1].strip("()'")  # Extract clean segment name
        segment_data = {
            "segment_definition": {
                "partition_by": list(segments.values())[0].mapper.col_names,
                "filter": str(list(segments.values())[0].filter) if list(segments.values())[0].filter else None
            },
            "metrics": {},
            "size": segment_profile.count() if hasattr(segment_profile, 'count') else 0
        }

        # Get metrics for each column in the segment
        for col in dataset.columns:
            col_profile = segment_profile.view().get_column(col)
            if col_profile:
                segment_data["metrics"][col] = {
                    "type": str(col_profile._type),
                    "stats": col_profile._metrics.to_summary_dict() if hasattr(col_profile, '_metrics') else {}
                }

        whylabs_data["segments"][segment_name] = segment_data

    # Add segment comparisons
    for metric in whylabs_data["segment_comparison"]["metrics"]:
        if metric in dataset.columns:
            whylabs_data["segment_comparison"]["comparisons"][metric] = {
                "mean": {},
                "distribution": {}
            }
            for segment_name, segment_info in whylabs_data["segments"].items():
                if metric in segment_info["metrics"]:
                    stats = segment_info["metrics"][metric]["stats"]
                    if "mean" in stats:
                        whylabs_data["segment_comparison"]["comparisons"][metric]["mean"][segment_name] = stats["mean"]
                    if "stddev" in stats:
                        whylabs_data["segment_comparison"]["comparisons"][metric]["distribution"][segment_name] = {
                            "mean": stats.get("mean"),
                            "stddev": stats.get("stddev"),
                            "min": stats.get("min"),
                            "max": stats.get("max")
                        }

    return whylabs_data

@app.get("/load_data")
def load_data():
    return {"message": "Data loaded successfully", "columns": list(df.columns)}

@app.get("/segment/single")
def segment_single():
    column_segments = segment_on_column("category")
    results = why.log(df, schema=DatasetSchema(segments=column_segments))
    
    # Get all segments
    segmented_profiles = results.segmented_profiles()
    
    whylabs_data = map_segmentation_to_whylabs(
        segmented_results=segmented_profiles,
        segments={"category": column_segments},
        dataset=df
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "segment_count": len(segmented_profiles)
    }

@app.get("/segment/multiple")
def segment_multiple():
    segmentation_partition = SegmentationPartition(
        name="category,rating", 
        mapper=ColumnMapperFunction(col_names=["category", "rating"])
    )
    multi_column_segments = {segmentation_partition.name: segmentation_partition}
    results = why.log(df, schema=DatasetSchema(segments=multi_column_segments))
    
    segmented_profiles = results.segmented_profiles()
    
    whylabs_data = map_segmentation_to_whylabs(
        segmented_results=segmented_profiles,
        segments=multi_column_segments,
        dataset=df
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "segment_count": len(segmented_profiles)
    }

@app.get("/segment/filter")
def segment_filter():
    segmentation_partition = SegmentationPartition(
        name="Filtered Category", 
        mapper=ColumnMapperFunction(col_names=["category"]),
        filter=SegmentFilter(filter_function=lambda row: row["category"] == "Office Supplies")
    )
    column_segments = {"Filtered Category": segmentation_partition}
    results = why.log(df, schema=DatasetSchema(segments=column_segments))
    
    segmented_profiles = results.segmented_profiles()
    
    whylabs_data = map_segmentation_to_whylabs(
        segmented_results=segmented_profiles,
        segments=column_segments,
        dataset=df
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "segment_count": len(segmented_profiles)
    }

@app.get("/segment/filter/custom")
def segment_filter_custom():
    segmentation_partition = SegmentationPartition(
        name="Filtered High Price & Rating", 
        mapper=ColumnMapperFunction(col_names=["category"]),
        filter=SegmentFilter(filter_function=lambda row: (row["market_price"] > 200) & (row["rating"] > 3))
    )
    column_segments = {"Filtered High Price & Rating": segmentation_partition}
    results = why.log(df, schema=DatasetSchema(segments=column_segments))
    
    segmented_profiles = results.segmented_profiles()
    
    whylabs_data = map_segmentation_to_whylabs(
        segmented_results=segmented_profiles,
        segments=column_segments,
        dataset=df
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "segment_count": len(segmented_profiles)
    }