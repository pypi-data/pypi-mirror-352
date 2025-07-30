from datetime import date, datetime
import pandera as pa
from pandera.typing import Series, DataFrame

from .base import BaseSalesforceSchema


class SickLeavePeriodSchema(BaseSalesforceSchema):
    """Schema for hr2d__SickLeavePer__c entity in HR2Day. Represents a sick leave period record."""
    
    # Basic Salesforce fields
    LastActivityDate: Series[str] = pa.Field(nullable=True, description="Last activity date")
    
    # HR2Day fields
    hr2d__SickLeave__c: Series[str] = pa.Field(
        nullable=True, 
        description="Sick leave of which this sick leave period is part"
    )
    hr2d__EndDate__c: Series[datetime] = pa.Field(
        nullable=True, 
        description="Last day this sick leave period applies to",
        coerce=True
    )
    hr2d__SickPerc__c: Series[float] = pa.Field(
        nullable=True, 
        description="Percentage for partial sick leave. For complete sick leave: 100%",
        ge=0,
        le=100
    )
    hr2d__StartDate__c: Series[datetime] = pa.Field(
        nullable=True, 
        description="First day of sick leave period",
        coerce=True
    )

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True