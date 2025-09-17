from typing import List, Optional
from pydantic import BaseModel, Field


class PredictItem(BaseModel):
    """
    Model for house prediction (single).  
    Model accepts basic features and automatically enriches with demographic data from zipcode.
    
    Exemple payload:
    {
        "bedrooms": 3,
        "bathrooms": 2.5,
        "sqft_living": 2000,
        "sqft_lot": 5000,
        "floors": 2,
        "sqft_above": 1500,
        "sqft_basement": 500,
        "zipcode": "98125"
    }
    """
    # Basic Mandatory Features
    bedrooms: int = Field(..., description="Number of bedrooms", ge=0)
    bathrooms: float = Field(..., description="Number of bathrooms", ge=0)
    sqft_living: int = Field(..., description="Living area in sqft", gt=0)
    sqft_lot: int = Field(..., description="Lot area in sqft", gt=0)
    floors: float = Field(..., description="Number of floors", ge=0)
    sqft_above: int = Field(..., description="Above ground area in sqft", ge=0)
    sqft_basement: int = Field(..., description="Basement area in sqft", ge=0)
    
    # Optional Features
    zipcode: Optional[str] = Field(None, description="Postal code")
    waterfront: Optional[int] = Field(None, description="Is waterfront (0 ou 1)", ge=0, le=1)
    view: Optional[int] = Field(None, description="View quality (0-4)", ge=0, le=4)
    condition: Optional[int] = Field(None, description="House condition (1-5)", ge=1, le=5)
    grade: Optional[int] = Field(None, description="Overal House grade (1-13)", ge=1, le=13)
    yr_built: Optional[int] = Field(None, description="Year of construction", ge=1800, le=2024)
    yr_renovated: Optional[int] = Field(None, description="Year renovated (0 = never renovated)", ge=0, le=2024)
    lat: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    long: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)
    sqft_living15: Optional[int] = Field(None, description="Living area in sqft of 15 nearest neighbors", ge=0)
    sqft_lot15: Optional[int] = Field(None, description="Lot area in sqft of 15 nearest neighbors", ge=0)
    
    class Config:
        extra = "allow"


class PredictRequest(BaseModel):
    """
    Model for house price prediction.
    Accepts a list of instances (houses) for prediction

    Example payload:
    {
        "instances": [
            {
                "bedrooms": 3,
                "bathrooms": 2.5,
                "sqft_living": 2000,
                "sqft_lot": 5000,
                "floors": 2,
                "sqft_above": 1500,
                "sqft_basement": 500,
                "zipcode": "98125"
            },
            {
                "bedrooms": 4,
                "bathrooms": 3,
                "sqft_living": 2500,
                "sqft_lot": 6000,
                "floors": 2,
                "sqft_above": 2000,
                "sqft_basement": 500,
                "zipcode": "98136"
            }
        ]
    }
    """
    instances: List[PredictItem] = Field(..., description="List of house data for price prediction", min_items=1)
