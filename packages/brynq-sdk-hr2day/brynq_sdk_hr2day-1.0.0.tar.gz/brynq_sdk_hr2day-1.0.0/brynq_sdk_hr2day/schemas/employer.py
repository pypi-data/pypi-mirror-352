from datetime import datetime
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema

class EmployerSchema(BaseSalesforceSchema):
    """Schema for hr2d__Employer__c entity in HR2Day. Represents an employer record."""
    
    # Salesforce Standard Fields
    OwnerId: Series[str] = pa.Field(nullable=True, description="Owner ID")
    LastActivityDate: Series[datetime] = pa.Field(nullable=True, description="Last activity date", coerce=True)
    LastViewedDate: Series[datetime] = pa.Field(nullable=True, description="Last viewed date", coerce=True)
    LastReferencedDate: Series[datetime] = pa.Field(nullable=True, description="Last referenced date", coerce=True)
    
    # HR2Day Custom Fields
    hr2d__FullName__c: Series[str] = pa.Field(nullable=True, description="Full name of the employer")
    hr2d__Status__c: Series[str] = pa.Field(
        nullable=True, 
        description="Employer status (Prod, Test, or Archief)",
        isin=["Prod", "Test", "Archief"]
    )
    hr2d__TaxId__c: Series[str] = pa.Field(
        nullable=True, 
        description="Tax ID (Wage tax number)",
        str_length={"min_value": 11, "max_value": 12}  # Gerçek verilerden gözlemlenen uzunluk
    )

    @pa.check("CreatedDate", "LastModifiedDate", "SystemModstamp", "LastActivityDate",
              "LastViewedDate", "LastReferencedDate")
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