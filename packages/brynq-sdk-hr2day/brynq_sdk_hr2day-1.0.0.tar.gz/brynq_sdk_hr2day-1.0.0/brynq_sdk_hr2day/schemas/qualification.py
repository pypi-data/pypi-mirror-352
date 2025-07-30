from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from .base import BaseSchema


class ClassificationSchema(BaseModel):
    """Schema for classification related fields"""
    hr2d__Attribute__c: Optional[str] = Field(None, description="Unique or general characteristic of this qualification basis")
    hr2d__Category__c: Optional[str] = Field(None, description="Category of the qualification basis")
    hr2d__Level__c: Optional[str] = Field(None, description="Level of qualification")
    hr2d__Type__c: Optional[str] = Field(None, description="Type of qualification")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class RelationshipSchema(BaseModel):
    """Schema for relationship related fields"""
    hr2d__Department__c: Optional[str] = Field(None, description="Specific department this qualification relates to")
    hr2d__Employee__c: Optional[str] = Field(None, description="Employee")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ValiditySchema(BaseModel):
    """Schema for validity related fields"""
    hr2d__StartDate__c: Optional[date] = Field(None, description="Date from which this is valid")
    hr2d__EndDate__c: Optional[date] = Field(None, description="Date when this ends")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class AdditionalInfoSchema(BaseModel):
    """Schema for additional information fields"""
    hr2d__Notification__c: Optional[bool] = Field(None, description="Report data to external authority")
    hr2d__Remarks__c: Optional[str] = Field(None, description="Additional information")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class QualificationSchema(BaseModel):
    """Schema for hr2d__Qualification__c entity in HR2Day. Represents a qualification record."""
    base: BaseSchema = Field(None)
    classification: ClassificationSchema = Field(None)
    relationships: RelationshipSchema = Field(None)
    validity: ValiditySchema = Field(None)
    additional_info: AdditionalInfoSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 