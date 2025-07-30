import os
import requests
import pandas as pd
import warnings
from typing import Union, Optional, List, Dict, Type, get_type_hints, Literal
from datetime import datetime, date
from brynq_sdk_brynq import BrynQ
from brynq_sdk_functions import Functions
from pydantic import BaseModel
import pandera as pa
from .employee import Employee
from .cost_center import CostCenter
from .job import Job
from .leave import Leave
from .file import File
from .department import Department
from .employer import Employer
from .employment_conditions_cluster import EmploymentConditionsCluster
from .employment_relationship import EmploymentRelationship
from .sick_classification import SickClassification
from .sick_leave import SickLeave
from .sick_leave_period import SickLeavePeriod

class HR2Day(BrynQ):
    """
    A class to interact with HR2Day API.
    """


    def __init__(self, requester_id: str, debug: bool = False, api_version: str = "v63.0", system_type: Optional[Literal['source', 'target']] = None):
        """
        Initialize the HR2Day class.

        Args:
            domain (str): Salesforce domain name (e.g., "mycompany")
            interface_id (str): Interface ID for the HR2Day integration.
            system (str): System identifier.
            system_type (str): System type identifier.
            test_environment (bool, optional): Whether to use test environment. Defaults to False.
            debug (bool, optional): Whether to enable debug mode. Defaults to False.
        """

        super().__init__()
        self.timeout = 3600
        self.debug = debug
        self.API_VERSION = api_version
        self.requester_id = requester_id

        # Get authentication token
        credentials = self.interfaces.credentials.get(system='hr2day', system_type=system_type)
        self.access_token, self.base_url = self._get_access_token(credentials)

        # Initialize session with headers and retry strategy
        self.session = requests.Session()
        
        # Set default headers for all requests
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'X-PrettyPrint': '1'
        })
        
        # Initialize components
        self.employee = Employee(self)
        self.cost_center = CostCenter(self)
        self.leave = Leave(self)
        self.file = File(self)
        self.department = Department(self)
        self.employer = Employer(self)
        self.employment_conditions_cluster = EmploymentConditionsCluster(self)
        self.employment_relationship = EmploymentRelationship(self)
        self.job = Job(self)
        self.sick_classification = SickClassification(self)
        self.sick_leave = SickLeave(self)
        self.sick_leave_period = SickLeavePeriod(self)

    def _get_access_token(self, credentials):
        payload = {
            "grant_type": "password",
            "client_id": credentials["data"]["client_id"],
            "client_secret": credentials["data"]["client_secret"],
            "username": credentials["data"]["username"],
            "password": credentials["data"]["password"]
        }
        resp = requests.post(url='https://login.salesforce.com/services/oauth2/token',
                             data=payload)
        resp.raise_for_status()
        data = resp.json()

        return data.get('access_token'), data.get('instance_url')

    def _create_flexible_schema(self, original_schema, select_fields):
        """
        Creates a new schema from the original schema that includes only the selected fields.
        
        Args:
            original_schema: Original Pydantic schema
            select_fields: Selected fields (list or comma-separated string)
            
        Returns:
            Dynamically created new Pandera schema with only the selected fields
        """
        from pandera import DataFrameSchema, Column, Check
        from typing import Optional as OptionalType
        
        # Convert select fields to list format
        if isinstance(select_fields, str):
            selected = [field.strip() for field in select_fields.split(",")]
        else:
            selected = select_fields
        
        # Get existing model fields and types
        original_fields = {}
        try:
            # Compatible with Pydantic v2
            original_fields = original_schema.model_fields
        except AttributeError:
            try:
                # Compatible with Pydantic v1
                original_fields = original_schema.__fields__
            except AttributeError:
                # Get all class properties (fallback)
                type_hints = get_type_hints(original_schema)
                for field_name, field_type in type_hints.items():
                    original_fields[field_name] = {"type": field_type}
        
        # Create new Pandera schema with only the selected fields
        schema_columns = {}
        
        for field_name in selected:
            # Skip if field doesn't exist in original schema
            if field_name not in original_fields:
                if self.debug:
                    print(f"Warning: Field '{field_name}' not found in original schema")
                continue
                
            field_info = original_fields[field_name]
            
            # Get field type based on Pydantic version
            try:
                field_type = field_info.annotation  # Pydantic v2
            except AttributeError:
                try:
                    field_type = field_info.type_  # Pydantic v1
                except AttributeError:
                    field_type = field_info.get("type")  # Fallback
            
            # Map Pydantic type to Pandera type
            import pandas as pd
            import numpy as np
            from typing import get_origin, get_args
            
            # Default column settings
            column_args = {
                "nullable": True,  # All fields are nullable by default
                "coerce": True,    # Try to coerce types
            }
            
            # Determine Python type from annotation
            python_type = field_type
            
            # Handle Optional types
            if hasattr(field_type, "__origin__") and field_type.__origin__ is OptionalType:
                python_type = get_args(field_type)[0]
                column_args["nullable"] = True
            
            # Map Python type to Pandas dtype
            if python_type == str:
                pandas_type = pd.StringDtype()
            elif python_type == int:
                pandas_type = pd.Int64Dtype()
            elif python_type == float:
                pandas_type = float
            elif python_type == bool:
                pandas_type = bool
            elif python_type == dict or python_type == Dict:
                pandas_type = object
            elif python_type == list or python_type == List:
                pandas_type = object
            else:
                # Default to object for complex types
                pandas_type = object
            
            # Create Pandera column
            schema_columns[field_name] = Column(pandas_type, **column_args)
        
        # Create Pandera schema
        flexible_schema = DataFrameSchema(
            schema_columns,
            strict=False,  # Don't enforce schema on columns not in the schema
            coerce=True    # Try to coerce data types
        )
        
        return flexible_schema

    def _build_soql_query(self,
                         entity_type: str,
                         select_fields: Optional[Union[List[str], str]] = None,
                         related_fields: Optional[Dict[str, List[str]]] = None,
                         filter: Optional[str] = None,
                         order_by: Optional[Union[List[str], str]] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None,
                         schema: Optional[Type[BaseModel]] = Type[pa.DataFrameModel]) -> tuple[str, int]:
        """
        Builds a SOQL query.
        
        Args:
            entity_type (str): The entity type to query (e.g., "hr2d__Employee__c")
            select_fields (Union[List[str], str], optional): Fields to select.
            related_fields (Dict[str, List[str]], optional): Dictionary of fields to select from related objects.
            filter (str, optional): WHERE clause.
            order_by (Union[List[str], str], optional): Sorting criteria.
            limit (int, optional): Number of records to return.
            offset (int, optional): Number of records to skip.
            schema (Type[BaseModel], optional): Pydantic schema class for validation.
            
        Returns:
            tuple[str, int]: The generated SOQL query and limit value
        """
        # Create SELECT part
        if select_fields:
            if isinstance(select_fields, str):
                select_fields = [select_fields]
                
            query = f"SELECT {','.join(select_fields)}"
        else:
            if schema:
                try:
                    all_fields = []
                    

                    schema_fields = list(schema.to_schema().columns.keys())
                
                    for field in schema_fields:
                        if not any(hasattr(getattr(schema, field, None), attr) 
                                  for attr in ["model_fields", "__fields__"]):
                            all_fields.append(field)
                    
                    if not all_fields:
                        if self.debug:
                            warnings.warn("No fields found in schema. Using SELECT FIELDS(ALL) which limits results to 200 records.")
                        query = "SELECT FIELDS(ALL)"
                        limit = 200
                    else:
                        query = f"SELECT {','.join(all_fields)}"
                except Exception as e:
                    if self.debug:
                        print(f"Error getting schema fields: {str(e)}")
                    query = "SELECT FIELDS(ALL)"
                    limit = 200
                    if self.debug:
                        warnings.warn(f"Error in schema field extraction: {str(e)}. Using SELECT FIELDS(ALL) which limits results to 200 records.")
            else:
                query = "SELECT FIELDS(ALL)"
                limit = 200
                if self.debug:
                    warnings.warn("SELECT FIELDS(ALL) used without schema. This will limit results to 200 records. Provide a schema for better results.")
            
        # Add related fields
        if related_fields:
            related_query_parts = []
            for relation, fields in related_fields.items():
                for field in fields:
                    related_query_parts.append(f"hr2d__{relation}__r.{field}")
            if related_query_parts:
                query += "," + ",".join(related_query_parts)
                
        # Add FROM part
        query += f" FROM {entity_type}"
        
        # Add WHERE clause
        if filter:
            query += f" WHERE {filter}"
            
        # Add ORDER BY part
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            processed_order = []
            for field in order_by:
                processed_order.append(field)
            query += f" ORDER BY {','.join(processed_order)}"
            
        # Add LIMIT part
        if limit:
            query += f" LIMIT {limit}"
            
        # Add OFFSET part
        if offset:
            if offset > 2000:
                raise ValueError("OFFSET cannot exceed 2000")
            query += f" OFFSET {offset}"
            
        return query, limit

    def get(self, 
            entity_type: str,
            select_fields: Optional[Union[List[str], str]] = None,
            related_fields: Optional[Dict[str, List[str]]] = None,
            filter: Optional[str] = None,
            order_by: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            schema: Optional[Type[pa.DataFrameModel]] = None) -> pd.DataFrame:
        """
        Get data from HR2Day using Salesforce SOQL query.
        
        Args:
            entity_type (str): The full entity type name (e.g., "hr2d__Employee__c")
            select_fields (Union[List[str], str], optional): Fields to select. If None, FIELDS(ALL) will be used (requires limit <= 200).
            related_fields (Dict[str, List[str]], optional): Dictionary of related fields to select. 
                                                           Key is the relation field, value is list of fields to select from related object.
                                                           Example: {"DepartmentToday": ["Name", "Code"]} will add "hr2d__DepartmentToday__r.Name, hr2d__DepartmentToday__r.Code"
            filter (str, optional): WHERE clause for the query. Defaults to None.
            order_by (Union[List[str], str], optional): Fields to order by. Defaults to None.
            limit (int): Number of records to return (LIMIT clause). Defaults to 200. Must be <= 200 when select_fields is None.
            offset (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
            schema (Type[BaseModel], optional): Pydantic schema class for validation. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame containing the query results
            
        Raises:
            ValueError: If the data validation fails
        """
        # Build SOQL query
        query, limit = self._build_soql_query(
            entity_type=entity_type,
            select_fields=select_fields,
            related_fields=related_fields,
            filter=filter,
            order_by=order_by,
            limit=limit,
            offset=offset,
            schema=schema
        )
        
        # URL encode the query (only convert spaces to +)
        encoded_query = query.replace(" ", "+")
        
        # Make the request
        response = self.session.get(f"{self.base_url}/services/data/{self.API_VERSION}/query?q={encoded_query}")
        response.raise_for_status()
        
        # Convert response to DataFrame
        data = response.json()
        
        # Check if pagination is needed
        all_records = []
        while True:
            if not data.get("records"):
                break
                
            # Remove "attributes" field from records
            records = data["records"]
            for record in records:
                record.pop("attributes", None)
            
            all_records.extend(records)
            
            # Check if there are more records
            if data.get("nextRecordsUrl"):
                response = self.session.get(f"{self.base_url}{data['nextRecordsUrl']}")
                response.raise_for_status()
                data = response.json()
            else:
                break
                
        if not all_records:
            return pd.DataFrame()
            
        # Create DataFrame from all records
        df = pd.DataFrame(all_records)
        
        # Skip validation if related_fields is provided
        if related_fields:
            return df
            
        try:
            # If select_fields parameter is used, only validate those fields
            if select_fields:
                # Create a list of selected fields
                if isinstance(select_fields, str):
                    selected_fields_list = [field.strip() for field in select_fields.split(',')]
                else:
                    selected_fields_list = select_fields
                    
                # Remove "attributes" field if present
                if "attributes" in selected_fields_list:
                    selected_fields_list.remove("attributes")
                
                # Add fields from related objects
                if related_fields:
                    for relation, fields in related_fields.items():
                        for field in fields:
                            related_field = f"hr2d__{relation}__r.{field}"
                            if related_field not in selected_fields_list:
                                selected_fields_list.append(related_field)
                
                # Filter DataFrame to only include selected fields
                df = df[selected_fields_list]
                
                # If schema is provided, create a flexible schema with only the selected fields
                if schema:
                    flexible_schema = self._create_flexible_schema(schema, selected_fields_list)
                    # Use Pandera schema validation directly
                    try:
                        validated_df = flexible_schema.validate(df)
                        return validated_df
                    except Exception as e:
                        if self.debug:
                            print(f"Validation error: {str(e)}")
                        raise ValueError(f"Data validation failed: {str(e)}")
            
            # Validate DataFrame with original schema if no select_fields or if select_fields but no schema
            if schema:
                # Check schema type and validate accordingly
                try:
                    valid_data, _ = Functions.validate_data(df, schema)
                    return valid_data
                except Exception as e:
                    if self.debug:
                        print(f"Validation error: {str(e)}")
                    raise ValueError(f"Data validation failed: {str(e)}")
                
        except Exception as e:
            raise e
        
        return df

    @staticmethod
    def datetime_converter(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the session"""
        self.session.close() 