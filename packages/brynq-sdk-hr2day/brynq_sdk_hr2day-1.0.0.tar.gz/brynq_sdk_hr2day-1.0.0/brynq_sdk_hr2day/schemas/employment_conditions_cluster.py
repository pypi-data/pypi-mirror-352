from datetime import datetime
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema

class EmploymentConditionsClusterSchema(BaseSalesforceSchema):
    """Schema for hr2d__ArbVoorwCluster__c entity in HR2Day. Represents an employment conditions cluster record."""
    
    # Salesforce Standard Fields
    OwnerId: Series[str] = pa.Field(nullable=True, description="Owner ID")
    LastViewedDate: Series[datetime] = pa.Field(nullable=True, description="Last viewed date", coerce=True)
    LastReferencedDate: Series[datetime] = pa.Field(nullable=True, description="Last referenced date", coerce=True)
    
    # HR2Day Custom Fields
    hr2d__Subgroepnaam__c: Series[str] = pa.Field(nullable=True, description="Employment conditions cluster name in overviews and selection lists")

    @pa.check("CreatedDate", "LastModifiedDate", "SystemModstamp", "LastViewedDate", "LastReferencedDate")
    def validate_date_format(self, series: Series) -> Series[bool]:
        """Validates that date strings are in the correct format before coercion."""
        def is_valid_date(value):
            if pd.isna(value):
                return True
            if isinstance(value, datetime):
                return True
            if not isinstance(value, str):
                return False
            
            try:
                pd.to_datetime(value)
                return True
            except (ValueError, TypeError):
                return False
        
        return series.apply(is_valid_date)

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 