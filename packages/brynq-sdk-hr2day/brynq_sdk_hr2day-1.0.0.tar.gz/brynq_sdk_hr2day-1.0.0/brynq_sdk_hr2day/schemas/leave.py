from typing import Optional, List, Union, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from pandera.typing import Series
import pandera as pa
import pandas as pd

from .base import BaseSalesforceSchema

class LeaveImportSchema(BaseModel):
    # API Fields
    hr2d__ExternalKey__c: Optional[str] = None
    hr2d__InternalId__c: Optional[str] = None
    hr2d__EmployeeId__c: Optional[str] = None
    hr2d__EmployeeNr__c: Optional[str] = None
    hr2d__Mode__c: Literal["online"]
    hr2d__Operation__c: Literal["insert", "update", "delete"]
    hr2d__EmployerId__c: Optional[str] = None
    hr2d__EmployerTaxId__c: Optional[str] = None
    hr2d__EmployerName__c: Optional[str] = None

    # Leave Fields
    hr2d__Hours__c: Optional[float] = Field(None, ge=0)
    hr2d__StartDate__c: Optional[date] = None
    hr2d__EndDate__c: Optional[date] = None
    hr2d__ArbrelVolgnr__c: Optional[int] = Field(None, ge=0)
    hr2d__Reason__c: Optional[str] = None
    hr2d__Details__c: Optional[str] = None
    hr2d__TvtType__c: Optional[Literal["Recording", "Retching"]] = None
    hr2d__Description__c: Optional[str] = None
    hr2d__LeaveCode__c: Optional[str] = None
    hr2d__Leave__c: Optional[str] = None
    hr2d__Changes__c: Optional[str] = None
    hr2d__Workflowstatus__c: Optional[Literal["Approved", "Withdrawn"]] = None

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False

class LeaveSchema(BaseSalesforceSchema):
    """Schema for hr2d__Leave__c entity in HR2Day."""
    
    # Base fields inherited from BaseSalesforceSchema include:
    # Id, IsDeleted, Name, CreatedDate, CreatedById, LastModifiedDate, LastModifiedById, SystemModstamp
    
    # Additional base fields
    LastActivityDate: Series[datetime] = pa.Field(nullable=True, description="Last Activity Date")
    
    # HR2Day specific fields
    hr2d__Annual__c: Series[bool] = pa.Field(nullable=True, description="Indicatie of het een collectieve verlofdag betreft")
    hr2d__ArbrelVolgnr__c: Series[float] = pa.Field(nullable=True, description="Employment sequence number", ge=0)
    hr2d__CalculatedHours__c: Series[float] = pa.Field(nullable=True, description="Aantal uren dat door HR2day berekend is op basis van aanvang en einddatum, het rooster en/of de deeltijdpercentage")
    hr2d__Employee__c: Series[str] = pa.Field(nullable=True, description="Employee")
    hr2d__EndDate__c: Series[datetime] = pa.Field(nullable=True, description="Laatste dag van de afwezigheid", coerce=True)
    hr2d__Hours__c: Series[float] = pa.Field(nullable=True, description="Aantal uren verlof", ge=0)
    hr2d__Leave__c: Series[str] = pa.Field(nullable=True, description="Dit is de verlofsoort waarop de aanvraag betrekking heeft")
    hr2d__StartDate__c: Series[datetime] = pa.Field(nullable=True, description="Eerste dag van de afwezigheid", coerce=True)
    hr2d__Workflowstatus__c: Series[str] = pa.Field(nullable=True, description="Geeft de status van het proces weer", isin=["Ingediend/In behandeling", "Goedgekeurd", "Afgewezen", "Ingetrokken"])

    class Config:
        """Schema configuration"""
        strict = True
        coerce = True

