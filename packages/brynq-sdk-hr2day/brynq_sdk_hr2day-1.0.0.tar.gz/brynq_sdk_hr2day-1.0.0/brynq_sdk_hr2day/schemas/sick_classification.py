from pandera.typing import Series
import pandera as pa

from .base import BaseSalesforceSchema

class SickClassificationSchema(BaseSalesforceSchema):
    """Schema for hr2d__SickClassification__c entity in HR2Day. Represents a sick leave classification record."""

    # HR2Day Custom Fields
    hr2d__Employer__c: Series[str] = pa.Field(nullable=True, description="Employer reference")
    hr2d__Type__c: Series[str] = pa.Field(nullable=True, description="Classification type")

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 