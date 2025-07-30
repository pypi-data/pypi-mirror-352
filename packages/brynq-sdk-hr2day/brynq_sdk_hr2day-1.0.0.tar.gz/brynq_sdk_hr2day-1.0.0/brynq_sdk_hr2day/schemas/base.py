from datetime import datetime
import pandera as pa
from pandera.typing import Series
import pandas as pd


class BaseSalesforceSchema(pa.DataFrameModel):
    """Base Salesforce fields schema that all HR2Day entities inherit from"""
    Id: Series[str] = pa.Field(nullable=True, description="Record ID")
    IsDeleted: Series[bool] = pa.Field(nullable=True, description="Is deleted flag")
    Name: Series[str] = pa.Field(nullable=True, description="Name of the record")
    CreatedDate: Series[datetime] = pa.Field(nullable=True, description="Created date", coerce=True)
    CreatedById: Series[str] = pa.Field(nullable=True, description="Created by ID")
    LastModifiedDate: Series[datetime] = pa.Field(nullable=True, description="Last modified date", coerce=True)
    LastModifiedById: Series[str] = pa.Field(nullable=True, description="Last modified by ID")
    SystemModstamp: Series[datetime] = pa.Field(nullable=True, description="System modstamp", coerce=True)

    @pa.check("CreatedDate", "LastModifiedDate", "SystemModstamp")
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