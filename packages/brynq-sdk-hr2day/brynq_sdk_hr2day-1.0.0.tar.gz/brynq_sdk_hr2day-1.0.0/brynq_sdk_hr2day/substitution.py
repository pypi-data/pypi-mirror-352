from typing import Optional, Union, List, Dict, Any
import pandas as pd
from .schemas.substitution import SubstitutionSchema

# Entity type constant
ENTITY_TYPE = "hr2d__Substitution__c"


class Substitution:
    """
    Handles substitution operations for HR2Day API.
    Substitution holds information about substitution records in the Salesforce system.
    """

    def __init__(self, hr2day_instance):
        """
        Initialize the Substitution class.

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
        Get substitution data from Salesforce.

        Args:
            filter (str, optional): Filter condition for the query (WHERE clause). Defaults to None.
            select_fields (Union[List[str], str], optional): Fields to select. If None, all fields will be selected.
            related (Dict[str, List[str]], optional): Dictionary of related fields to select.
                                                    Example: {"SickLeave": ["Name"]} will include sick leave name.
            orderby (Union[List[str], str], optional): Fields to order by. Defaults to None.
            limit (int, optional): Number of records to return (LIMIT clause). Max 200 when all_fields is True. Defaults to 200.
            skip (int, optional): Number of records to skip (OFFSET clause). Max 2000. Defaults to None.
            validate (bool, optional): Whether to validate the data against the SubstitutionSchema. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing substitution data
            
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
            schema=SubstitutionSchema
        ) 