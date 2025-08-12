from typing import Optional
from pydantic import BaseModel, Field

class LocationBase(BaseModel):
    location_name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    location_name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    active_status: Optional[bool] = None

class LocationResponse(LocationBase):
    id: int
    active_status: bool

    class Config:
        from_attributes = True

class LocationSearchRequest(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    active_only: bool = True