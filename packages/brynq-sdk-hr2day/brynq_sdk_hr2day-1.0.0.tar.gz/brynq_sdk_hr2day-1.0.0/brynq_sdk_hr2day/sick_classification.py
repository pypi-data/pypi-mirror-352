from typing import Optional, Union, List, Dict, Any
import pandas as pd
from .schemas.sick_classification import SickClassificationSchema

# Entity type constant
ENTITY_TYPE = "hr2d__SickClassification__c"


class SickClassification:
    """
    Handles sick classification operations for HR2Day API.
    SickClassification holds information about sick leave classifications in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the SickClassification class.

        Args:
            hr2day_instance: The HR2Day class instance.
        """
        self.hr2day = hr2day_instance

    def get(self,
            filter: Optional[str] = None,
            select_fields: Optional[Union[List[str], str]] = None,
            related: Optional[Dict[str, List[str]]] = None,
            orderby: Optional[Union[List[str], str]] = None,
            limit: Optional[int] = None,
            skip: Optional[int] = None) -> pd.DataFrame:
        """
        Get sick classification data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
                            Example: "Id = 'a08P500000USWDPIA5'"
            select_fields (Union[List[str], str], optional): Fields to select. If None, all fields will be selected.
                            Example (list): ["Id", "FirstName", "LastName"]
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                            Example: {"DepartmentToday": ["Name"]} will include department name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
                            Example (list): ["LastName ASC", "FirstName DESC"]
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
                            Example: 100
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
                            Example: 0
            validate (bool, optional): Whether to validate the data against the SickClassificationSchema. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing sick classification data
            
        Raises:
            ValueError: If validate is True and the data validation fails
        """
        return self.hr2day.get(
            entity_type=ENTITY_TYPE,
            select_fields=select_fields,
            related_fields=related,
            filter=filter,
            order_by=orderby,
            limit=limit,
            offset=skip,
            schema=SickClassificationSchema
        ) 