from datetime import datetime
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema


class JobSchema(BaseSalesforceSchema):
    """Schema for hr2d__Job__c entity in HR2Day. Represents a job record."""
    
    # HR2Day Custom Fields
    LastActivityDate: Series[datetime] = pa.Field(nullable=True, description="Last activity date for the record", coerce=True)
    hr2d__Employer__c: Series[str] = pa.Field(nullable=True, description="Employer where this job is defined")
    hr2d__Description__c: Series[str] = pa.Field(nullable=True, description="Description")
    hr2d__DescriptionShort__c: Series[str] = pa.Field(nullable=True, description="Short description of the job")

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 