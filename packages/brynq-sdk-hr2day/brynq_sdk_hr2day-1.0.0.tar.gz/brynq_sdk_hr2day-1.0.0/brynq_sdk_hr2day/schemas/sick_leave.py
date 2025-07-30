from datetime import datetime
import pandera as pa
from pandera.typing import Series, DataFrame

from .base import BaseSalesforceSchema


class SickLeaveSchema(BaseSalesforceSchema):
    """Schema for hr2d__SickLeave__c entity in HR2Day. Represents a sick leave record."""
    
    # HR2Day fields
    LastActivityDate: Series[str] = pa.Field(nullable=True, description="Last activity date")
    hr2d__Employee__c: Series[str] = pa.Field(nullable=True, description="Employee")
    hr2d__CalendarDays__c: Series[float] = pa.Field(
        nullable=True, 
        description="Number of sick days from start to end or for open records from start to today",
    )
    hr2d__EndDate__c: Series[datetime] = pa.Field(
        nullable=True, 
        description="Last day of sick leave",
        coerce=True
    )
    hr2d__SickClassification__c: Series[str] = pa.Field(nullable=True, description="Type of sick leave")
    hr2d__StartDate__c: Series[datetime] = pa.Field(
        nullable=True, 
        description="First day of sick leave",
        coerce=True
    )
    hr2d__ArbrelVolgnr__c: Series[float] = pa.Field(
        nullable=True, 
        description="Sequence number of employment if sick leave only relates to one specific employment",
    )
    hr2d__Department__c: Series[str] = pa.Field(nullable=True, description="Department where employee works on first day of sick leave")
    hr2d__ClassificationPicked__c: Series[str] = pa.Field(nullable=True, description="Classification this sick leave falls under")
    hr2d__HoursFirstDay__c: Series[float] = pa.Field(
        nullable=True, 
        description="Hours if employee is sick part of the day",
    )
    hr2d__ExpectedEndDate__c: Series[datetime] = pa.Field(
        nullable=True, 
        description="Expected last day of sick leave",
        coerce=True
    )
    hr2d__RecordId__c: Series[str] = pa.Field(
        nullable=True, 
        description="Case insensitive id (18 characters) of this record",
        str_length=18
    )
        
    @pa.dataframe_check
    def validate_start_end_dates(cls, df: DataFrame) -> Series[bool]:
        """Validate that start date is before or equal to end date"""
        valid_dates = (
            ~df['hr2d__StartDate__c'].notna() | 
            ~df['hr2d__EndDate__c'].notna() | 
            (df['hr2d__StartDate__c'] <= df['hr2d__EndDate__c'])
        )
        return valid_dates
