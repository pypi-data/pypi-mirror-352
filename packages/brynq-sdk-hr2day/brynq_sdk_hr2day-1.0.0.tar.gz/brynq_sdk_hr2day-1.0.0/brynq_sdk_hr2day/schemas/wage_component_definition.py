from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseSchema


class CalculationSchema(BaseModel):
    """Schema for calculation related fields"""
    hr2d__Aantal__c: Optional[float] = Field(None, description="Standard amount for calculation")
    hr2d__AantalMaxPara__c: Optional[str] = Field(None, description="Reference to Parameter for maximum amount")
    hr2d__AantalPara__c: Optional[str] = Field(None, description="Parameter for determining standard amount")
    hr2d__Factor__c: Optional[float] = Field(None, description="Standard factor for allowance calculation")
    hr2d__FactorPara__c: Optional[str] = Field(None, description="Parameter for determining standard factor")
    hr2d__Tarief__c: Optional[float] = Field(None, description="Standard rate/basis for amount calculation")
    hr2d__TariefMaxPara__c: Optional[str] = Field(None, description="Reference to Parameter for maximum rate")
    hr2d__TariefPara__c: Optional[str] = Field(None, description="Parameter for determining rate/calculation basis")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ConfigurationSchema(BaseModel):
    """Schema for configuration related fields"""
    hr2d__Code__c: Optional[str] = Field(None, description="Code for unique identification")
    hr2d__Type__c: Optional[str] = Field(None, description="Type of wage component regarding data input")
    hr2d__Status__c: Optional[str] = Field(None, description="Status of the wage component definition")
    hr2d__Index__c: Optional[float] = Field(None, description="Indexing of wage component for display")
    hr2d__MaintenanceCode__c: Optional[str] = Field(None, description="Code for unique identification for maintenance")
    hr2d__RegelingCode__c: Optional[str] = Field(None, description="Code for recognition in wage component regulations")
    hr2d__Reference__c: Optional[str] = Field(None, description="Reference to parent wage component definition")
    hr2d__Key__c: Optional[str] = Field(None, description="Key field consisting of Name and Definition")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class AccountingSchema(BaseModel):
    """Schema for accounting related fields"""
    hr2d__Kosten__c: Optional[str] = Field(None, description="Characteristic of how component counts in total costs")
    hr2d__KostVerd__c: Optional[str] = Field(None, description="Cost distribution characteristic")
    hr2d__Rubr_Grootbk__c: Optional[str] = Field(None, description="Categorization for general ledger account assignment")
    hr2d__Grondslag__c: Optional[str] = Field(None, description="Bases in which this wage component participates")
    hr2d__KenmerkAangifte__c: Optional[str] = Field(None, description="Code/Characteristic for wage tax return")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class DisplaySchema(BaseModel):
    """Schema for display related fields"""
    hr2d__HelpTekst__c: Optional[str] = Field(None, description="Help text shown on payslip")
    hr2d__Omschrijving__c: Optional[str] = Field(None, description="Description")
    hr2d__LoonstrookOpties__c: Optional[str] = Field(None, description="Specific options for payslip display")
    hr2d__Notities__c: Optional[str] = Field(None, description="Notes/background information")
    hr2d__LooncompNr__c: Optional[str] = Field(None, description="Options for external communication")
    hr2d__Rapportagegroep__c: Optional[str] = Field(None, description="Reporting group for HR Analytics")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ProcessingSchema(BaseModel):
    """Schema for processing related fields"""
    hr2d__Prorata__c: Optional[str] = Field(None, description="Pro-rata calculation method")
    hr2d__Blokkeren__c: Optional[str] = Field(None, description="Blocking of wage component data")
    hr2d__IndicatieUitbetaling__c: Optional[str] = Field(None, description="Settings for payment checks")
    hr2d__Veldsturing__c: Optional[str] = Field(None, description="Field control settings")
    hr2d__AfwijkendSVTarief__c: Optional[str] = Field(None, description="Indication for deviating SV rates")
    hr2d__AlertAssignment__c: Optional[str] = Field(None, description="Alert assignment code")
    hr2d__SplitLC__c: Optional[str] = Field(None, description="Component for split portion")
    hr2d__SplitOpties__c: Optional[str] = Field(None, description="Options for splitting component")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class WageComponentDefinitionSchema(BaseModel):
    """Schema for hr2d__WageComponentDefinition__c entity in HR2Day. Represents a wage component definition record."""
    base: BaseSchema = Field(None)
    calculation: CalculationSchema = Field(None)
    configuration: ConfigurationSchema = Field(None)
    accounting: AccountingSchema = Field(None)
    display: DisplaySchema = Field(None)
    processing: ProcessingSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 