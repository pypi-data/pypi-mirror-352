from typing import Optional, Union, List, Dict, Any
import json
from brynq_sdk_functions import Functions
from .schemas.cost_center import CostCenterUpdateSchema, CostCenterGetSchema

# Entity type constant
ENTITY_TYPE = "hr2d__CostCenter__c"


class CostCenter:
    """
    Handles cost center operations for HR2Day API.
    Cost center holds information about cost centers in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the CostCenter class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance

    def update(self, costcenters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sends a PUT request to the HR2Day API to update or create cost center information.
        
        Args:
            costcenters (List[Dict[str, Any]]): List of cost centers to update/create. Each cost center must include:
                For update:
                - costcenterId: 18 characters, case sensitive (e.g., a0M2G00011iDU9IAH)
                
                For create (insert):
                One of the following is required:
                - employerId: 18 characters, case sensitive (e.g., a04A000004eQcJIAU)
                - employerName: Max 80 characters, case sensitive
                - employerTaxId: 12 characters, case sensitive
                
                Fields that can be updated/created:
                - Name: Name of the cost center (max 80 characters, mandatory for insert)
                - hr2d__StartDate__c: Start date (format: yyyy-mm-dd)
                - hr2d__EndDate__c: End date (format: yyyy-mm-dd)
                - hr2d__Description__c: Description (max 75 characters)
                - hr2d__Dimension__c: Dimension (1 character: 1, 2, 3 or 9)
                - hr2d__Classification__c: Classification (max 20 characters)
                - hr2d__RecapChar__c: Verdichtings-kenmerk (max 20 characters)
                
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.HTTPError: When the HTTP request fails
            ValueError: When the request format is invalid or validation fails
        """
        
        try:
            # Validate each cost center update/create data
            valid_costcenters, invalid_costcenters = Functions.validate_pydantic_data(costcenters, CostCenterUpdateSchema)
        except Exception as e:
            # Add validation error to the cost center data
            raise ValueError(f"Cost center data validation failed:\n{str(e)}")

        # If there are invalid cost centers, raise an error
        if invalid_costcenters:
            error_messages = []
            for i, costcenter in enumerate(invalid_costcenters):
                error_messages.append(f"Cost center {i+1}: {costcenter.get('_validation_errors', 'Unknown error')}")
            
            error_summary = "\n".join(error_messages)
            raise ValueError(f"Cost center data validation failed:\n{error_summary}")
            
        # Check if there are valid cost centers
        if not valid_costcenters:
            raise ValueError("No valid cost centers to update/create")
            
        # Create request body
        request_body = {
            "request": {
                "requesterId": self.hr2day.requester_id,
                "costcenters": valid_costcenters
            }
        }
        
        # API endpoint URL
        url = f"{self.hr2day.base_url}/services/apexrest/hr2d/costcenter"
        json_body = json.dumps(request_body, default=self.hr2day.datetime_converter)

        # Send PUT request
        response = self.hr2day.session.put(
            url=url,
            data=json_body
        )
        
        # Error handling
        response.raise_for_status()
        
        # Return response as JSON
        return response.json() 