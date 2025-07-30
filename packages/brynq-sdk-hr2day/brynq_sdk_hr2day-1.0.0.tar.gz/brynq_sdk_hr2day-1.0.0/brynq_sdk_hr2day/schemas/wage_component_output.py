from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from .base import BaseSchema


class CalculationSchema(BaseModel):
    """Schema for calculation related fields"""
    hr2d__Aantal__c: Optional[float] = Field(None, description="Amount")
    hr2d__Bedrag__c: Optional[float] = Field(None, description="Amount")
    hr2d__Factor__c: Optional[float] = Field(None, description="Factor for allowance calculation (1=no allowance)")
    hr2d__Tarief__c: Optional[float] = Field(None, description="Rate")
    hr2d__ProrataFactor__c: Optional[float] = Field(None, description="Pro-rata factor of the wage component")
    hr2d__Cumulatief__c: Optional[float] = Field(None, description="Cumulative")
    hr2d__Index__c: Optional[float] = Field(None, description="Indexing for display on screen, payslip etc.")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class RelationshipSchema(BaseModel):
    """Schema for relationship related fields"""
    hr2d__Account__c: Optional[str] = Field(None, description="Account")
    hr2d__Department__c: Optional[str] = Field(None, description="Department related to work activities")
    hr2d__Job__c: Optional[str] = Field(None, description="Job function related to work activities")
    hr2d__Declaration__c: Optional[str] = Field(None, description="Declaration on which this wage component is based")
    hr2d__Substitution__c: Optional[str] = Field(None, description="Relation to substitution if relevant")
    hr2d__Vervanging__c: Optional[str] = Field(None, description="Relation to substitution if relevant (old)")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class BankingSchema(BaseModel):
    """Schema for banking related fields"""
    hr2d__Bank__c: Optional[str] = Field(None, description="Specific bank account. Must pass 11-test if longer than 7 characters")
    hr2d__Bank_naam__c: Optional[str] = Field(None, description="Bank account holder name")
    hr2d__Bank_omschr__c: Optional[str] = Field(None, description="Description of specific bank payment")
    hr2d__BankBIC__c: Optional[str] = Field(None, description="Bank Identification Code (BIC) for IBAN")
    hr2d__BankIBAN__c: Optional[str] = Field(None, description="International Bank Account Number")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class PayrollSchema(BaseModel):
    """Schema for payroll related fields"""
    hr2d__Verloning__c: Optional[str] = Field(None, description="Payroll")
    hr2d__Loonstrook__c: Optional[str] = Field(None, description="Payslip")
    hr2d__Regeling__c: Optional[str] = Field(None, description="Scheme for specific processing in payroll calculation")
    hr2d__Datum__c: Optional[date] = Field(None, description="Date")
    hr2d__EndDate__c: Optional[date] = Field(None, description="Last day this wage component is valid")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class CostCenterSchema(BaseModel):
    """Schema for cost center related fields"""
    hr2d__CostCenter__c: Optional[str] = Field(None, description="Cost center for booking amount")
    hr2d__CostCenter_Dim2__c: Optional[str] = Field(None, description="Dimension 2 cost center for booking amount")
    hr2d__CostCenter_Dim3__c: Optional[str] = Field(None, description="Dimension 3 cost center for booking amount")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ReferenceSchema(BaseModel):
    """Schema for reference related fields"""
    hr2d__Contractkenmerk__c: Optional[str] = Field(None, description="Contract identification number")
    hr2d__Herkomst__c: Optional[str] = Field(None, description="Origin of wage component in payroll")
    hr2d__ImportId__c: Optional[str] = Field(None, description="ID used to undo an import")
    hr2d__ImportKey__c: Optional[str] = Field(None, description="Identification used to modify previously imported wage component")
    hr2d__Reden__c: Optional[str] = Field(None, description="Reason for this wage component")
    hr2d__Referentie__c: Optional[str] = Field(None, description="Free field for identification, assignment, characteristic")
    hr2d__Volgnr__c: Optional[float] = Field(None, description="Sequence number")
    hr2d__Wijzigingen__c: Optional[str] = Field(None, description="Fields of wage component changed after payroll creation")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class ComponentReferenceSchema(BaseModel):
    """Schema for component reference related fields"""
    hr2d__Looncomponent__c: Optional[str] = Field(None, description="Wage Component Definition")
    hr2d__LooncompArbrel__c: Optional[str] = Field(None, description="Original Wage Component (employment)")
    hr2d__LooncompOud__c: Optional[str] = Field(None, description="Old Wage Component (in case of change)")
    hr2d__LooncompOutputChange__c: Optional[str] = Field(None, description="Wage Component Change (output)")

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore"


class WageComponentOutputSchema(BaseModel):
    """Schema for hr2d__WageComponentOutput__c entity in HR2Day. Represents a wage component output record."""
    base: BaseSchema = Field(None)
    calculation: CalculationSchema = Field(None)
    relationships: RelationshipSchema = Field(None)
    banking: BankingSchema = Field(None)
    payroll: PayrollSchema = Field(None)
    cost_center: CostCenterSchema = Field(None)
    reference: ReferenceSchema = Field(None)
    component_reference: ComponentReferenceSchema = Field(None)

    class Config:
        """Pydantic configuration"""
        frozen = True
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "ignore" 