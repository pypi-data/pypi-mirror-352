from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

from .base import BaseSchema


class JubileeSchema(BaseModel):
    """Schema for jubilee categories and their counting flags"""
    hr2d__Cat1__c: Optional[str] = Field(None, description="Jubilee category 1 - Description of jubilee category 1")
    hr2d__Cat2__c: Optional[str] = Field(None, description="Jubilee category 2")
    hr2d__Cat3__c: Optional[str] = Field(None, description="Jubilee category 3")
    hr2d__Cat4__c: Optional[str] = Field(None, description="Jubilee category 4")
    hr2d__CountCat1__c: Optional[bool] = Field(None, description="Count in 1 - Check to include period in the relevant jubilee")
    hr2d__CountCat2__c: Optional[bool] = Field(None, description="Count in 2")
    hr2d__CountCat3__c: Optional[bool] = Field(None, description="Count in 3")
    hr2d__CountCat4__c: Optional[bool] = Field(None, description="Count in 4")


class EmploymentPeriodSchema(BaseModel):
    """Schema for employment period details"""
    hr2d__StartDate__c: Optional[date] = Field(None, description="Start date - First day of this period of employment history")
    hr2d__EndDate__c: Optional[date] = Field(None, description="End date - Last day of this period of employment history")
    hr2d__Years__c: Optional[float] = Field(None, description="Number of years - Calculated period (end date - start date) in years")
    hr2d__Afvloeiing__c: Optional[bool] = Field(None, description="Lay-off - Period counts in composing the redundancy list")


class ApprovalSchema(BaseModel):
    """Schema for approval information"""
    hr2d__Approved__c: Optional[bool] = Field(None, description="Approval employee - Check if employee has approved the registration of this period of employment history")
    hr2d__ApprovedDate__c: Optional[date] = Field(None, description="Approval date - The date on which the employee approved the registration of this period of employment history")


class WorkHistorySchema(BaseModel):
    """Schema for hr2d__Arbeidsverleden__c entity in HR2Day. Represents an employee's work history record."""
    base: BaseSchema = Field(None)
    jubilee: JubileeSchema = Field(None)
    employment_period: EmploymentPeriodSchema = Field(None)
    approval: ApprovalSchema = Field(None)
    
    hr2d__Employee__c: Optional[str] = Field(None, description="Employee")
    hr2d__Werkgever__c: Optional[str] = Field(None, description="Employer - The employer where the employee was employed during this period of employment history")
    hr2d__Notes__c: Optional[str] = Field(None, description="Notes")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 