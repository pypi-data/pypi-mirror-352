from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema


class DepartmentSchema(BaseSalesforceSchema):
    """Schema for hr2d__Department__c entity in HR2Day. Represents a department record."""
    
    # HR2Day Custom Fields
    hr2d__Employer__c: Series[str] = pa.Field(nullable=True, description="Employer to which this department belongs")
    hr2d__ParentDept__c: Series[str] = pa.Field(nullable=True, description="Department under which this department falls")
    hr2d__Description__c: Series[str] = pa.Field(nullable=True, description="Optional description (full name) of the department")
    hr2d__RecordId__c: Series[str] = pa.Field(
        nullable=True, 
        description="Case insensitive id (18 characters) of this record",
        str_length={"min_value": 18, "max_value": 18}
    )

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 