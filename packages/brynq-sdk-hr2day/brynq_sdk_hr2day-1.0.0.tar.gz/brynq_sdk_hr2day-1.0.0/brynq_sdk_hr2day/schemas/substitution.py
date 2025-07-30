from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from .base import BaseSchema


class DatesSchema(BaseModel):
    """Schema for date related fields"""
    hr2d__StartDate__c: Optional[date] = Field(None, description="First day of substitution")
    hr2d__EndDate__c: Optional[date] = Field(None, description="Last day of substitution")
    hr2d__DateTimeLastVerzamelakte__c: Optional[datetime] = Field(None, description="Date on which a collective document was last created for this substitution")
    hr2d__LastModifiedDateTimeAkte__c: Optional[datetime] = Field(None, description="Date when fields relevant for the (collective) document were last modified")
    hr2d__OriginalCreateddate__c: Optional[datetime] = Field(None, description="Creation date of the substitution")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class RelationshipSchema(BaseModel):
    """Schema for relationship fields"""
    hr2d__SickLeave__c: Optional[str] = Field(None, description="Sick leave record for which substitution takes place")
    hr2d__Leave__c: Optional[str] = Field(None, description="Leave record for which substitution takes place")
    hr2d__Vervanger__c: Optional[str] = Field(None, description="Employee performing the substitution")
    hr2d__Department__c: Optional[str] = Field(None, description="Department where substitution takes place")
    hr2d__CostCenter__c: Optional[str] = Field(None, description="Cost center where the amount of this substitution is booked")
    hr2d__CostCenter_Dim2__c: Optional[str] = Field(None, description="Cost center of Dimension 2 where the amount of this substitution is booked")
    hr2d__CostCenter_Dim3__c: Optional[str] = Field(None, description="Cost center of Dimension 3 where the amount of this substitution is booked")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class WorkTimeFactorSchema(BaseModel):
    """Schema for work time factor related fields"""
    hr2d__WtfEersteMaand__c: Optional[float] = Field(None, description="The wtf in the first month. For broken month, wtf is calculated by summing individual roster days wtf and multiplying by 3/13")
    hr2d__WtfLaatsteMaand__c: Optional[float] = Field(None, description="The wtf in the last month. For broken month, wtf is calculated by summing individual roster days wtf and multiplying by 3/13")
    hr2d__WtfMaand__c: Optional[float] = Field(None, description="Total wtf of substitution on monthly basis. Sum of individual wtf Monday through Sunday")
    hr2d__Rooster__c: Optional[str] = Field(None, description="Hours or Weekly time factor per day (Monday through Sunday) for this substitution")
    hr2d__CalDays__c: Optional[float] = Field(None, description="Number of days of substitution, from start through end. For open end through today")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class AdministrationSchema(BaseModel):
    """Schema for administration related fields"""
    hr2d__BlockTransfer__c: Optional[bool] = Field(None, description="If checked, this substitution is not included in payroll")
    hr2d__Declarabel__c: Optional[bool] = Field(None, description="If checked, this substitution is billable to the Substitution Fund")
    hr2d__FinBron__c: Optional[str] = Field(None, description="This feature blocks reporting of this substitution to the Substitution Fund. Empty means no blocking")
    hr2d__Processed__c: Optional[str] = Field(None, description="This field indicates whether the substitution has been processed in payroll after entry/modification")
    hr2d__SrtVervanger__c: Optional[str] = Field(None, description="01 = regular substitute 02 = pool substitute")
    hr2d__ArbrelVolgnr__c: Optional[float] = Field(None, description="Number of the employment relationship of the substitute employee")
    hr2d__Key__c: Optional[str] = Field(None, description="Key field substitution record, consisting of sick leave or leave key, substitute's BSN, start of substitution")
    hr2d__ExternalKey__c: Optional[str] = Field(None, description="Reference to key of external data exchange")
    hr2d__RecordId__c: Optional[str] = Field(None, description="Case insensitive id (18 characters) of this record")
    hr2d__OriginalName__c: Optional[str] = Field(None, description="Name of the old substitution object, for coupling purposes")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class SubstitutionSchema(BaseModel):
    """Schema for hr2d__Substitution__c entity in HR2Day. Represents a substitution record."""
    base: BaseSchema = Field(None)
    dates: DatesSchema = Field(None)
    relationships: RelationshipSchema = Field(None)
    work_time_factor: WorkTimeFactorSchema = Field(None)
    administration: AdministrationSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 