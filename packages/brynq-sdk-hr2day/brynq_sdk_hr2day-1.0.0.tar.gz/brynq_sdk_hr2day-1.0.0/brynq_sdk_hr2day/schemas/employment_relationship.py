from datetime import datetime
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema


class EmploymentRelationshipSchema(BaseSalesforceSchema):
    """Schema for hr2d__Arbeidsrelatie__c entity in HR2Day. Represents an employment relationship record."""
    
    # Salesforce Standard Fields
    LastActivityDate: Series[datetime] = pa.Field(nullable=True, description="Last activity date", coerce=True)
    
    # HR2Day Custom Fields
    hr2d__Employee__c: Series[str] = pa.Field(nullable=True, description="Employee")
    hr2d__Aanvang_arbrel__c: Series[datetime] = pa.Field(nullable=True, description="Start date of the employment relationship", coerce=True)
    hr2d__ArbVoorwCluster__c: Series[str] = pa.Field(nullable=True, description="Employment conditions cluster")
    hr2d__Contract_Aanvang__c: Series[datetime] = pa.Field(nullable=True, description="Contract start date", coerce=True)
    hr2d__Contract_Einde__c: Series[datetime] = pa.Field(nullable=True, description="Contract end date", coerce=True)
    hr2d__Contract_bep_tijd__c: Series[str] = pa.Field(nullable=True, description="Temporary contract indicator")
    hr2d__Department__c: Series[str] = pa.Field(nullable=True, description="Department")
    hr2d__Einde_arbrel__c: Series[datetime] = pa.Field(nullable=True, description="End date of the employment relationship", coerce=True)
    hr2d__Geldig_tot__c: Series[datetime] = pa.Field(nullable=True, description="Valid until date", coerce=True)
    hr2d__Geldig_van__c: Series[datetime] = pa.Field(nullable=True, description="Valid from date", coerce=True)
    hr2d__Rooster_DagenWk__c: Series[str] = pa.Field(nullable=True, description="Schedule days per week")
    hr2d__Rooster__c: Series[str] = pa.Field(nullable=True, description="Schedule")
    hr2d__Volgnummer__c: Series[float] = pa.Field(nullable=True, description="Sequence number", ge=0)
    hr2d__Job__c: Series[str] = pa.Field(nullable=True, description="Job")
    hr2d__DeeltijdFactor__c: Series[float] = pa.Field(nullable=True, description="Part-time factor", ge=0, le=1)
    hr2d__UrenWeek__c: Series[float] = pa.Field(nullable=True, description="Hours per week", ge=0)
    hr2d__Einde_arbrelFilter__c: Series[str] = pa.Field(nullable=True, description="End date filter of the employment relationship", coerce=True)
    hr2d__Geldig_totFilter__c: Series[datetime] = pa.Field(nullable=True, description="Valid until date filter", coerce=True)

    @pa.check("hr2d__Contract_Aanvang__c", "hr2d__Contract_Einde__c")
    def validate_contract_dates(self, series: Series) -> Series[bool]:
        """Validates that contract start date is before or equal to end date."""
        if series.name == "hr2d__Contract_Einde__c":
            df = pd.DataFrame({
                'end_date': pd.to_datetime(series, errors='coerce'),
                'start_date': pd.to_datetime(series.index, errors='coerce')
            })
            return pd.isna(df['end_date']) | pd.isna(df['start_date']) | (df['end_date'] >= df['start_date'])
        return True

    @pa.check("hr2d__Geldig_van__c", "hr2d__Geldig_tot__c")
    def validate_validity_dates(self, series: Series) -> Series[bool]:
        """Validates that valid from date is before or equal to valid until date."""
        if series.name == "hr2d__Geldig_tot__c":
            df = pd.DataFrame({
                'end_date': pd.to_datetime(series, errors='coerce'),
                'start_date': pd.to_datetime(series.index, errors='coerce')
            })
            return pd.isna(df['end_date']) | pd.isna(df['start_date']) | (df['end_date'] >= df['start_date'])
        return True

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True 