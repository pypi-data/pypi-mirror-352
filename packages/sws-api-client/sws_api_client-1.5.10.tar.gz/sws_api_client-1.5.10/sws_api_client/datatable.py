"""Datatables Module for SWS API.

This module provides functionality for managing datatables, including retrieving
information, exporting data, and handling CSV paths through the SWS API client.
"""

import logging
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from sws_api_client.sws_api_client import SwsApiClient
logger = logging.getLogger(__name__)
from datetime import datetime, time
from time import sleep

class LabelModel(BaseModel):
    """Model for multilingual labels.

    Attributes:
        en (str): English label text
    """
    en: str

class DescriptionModel(BaseModel):
    """Model for multilingual descriptions.

    Attributes:
        en (str): English description text
    """
    en: str

class ColumnModel(BaseModel):
    """Model representing a datatable column.

    Attributes:
        id (str): Column identifier
        label (LabelModel): Column labels in different languages
        description (DescriptionModel): Column descriptions in different languages
        type (str): Data type of the column
        constraints (List[Any]): List of column constraints
        defaultValue (Optional[Any]): Default value for the column
        facets (List[Any]): List of column facets
    """
    id: str
    label: LabelModel
    description: DescriptionModel
    type: str
    constraints: List[Any]
    defaultValue: Optional[Any]
    facets: List[Any]

class DataModel(BaseModel):
    """Model representing datatable data status.

    Attributes:
        url (Optional[str]): URL to access the data
        available (bool): Whether the data is available
        uptodate (bool): Whether the data is up to date
    """
    url: Optional[str]
    available: bool
    uptodate: bool

class DatatableModel(BaseModel):
    """Model representing a complete datatable.

    Attributes:
        id (str): Datatable identifier
        name (str): Name of the datatable
        label (LabelModel): Labels in different languages
        description (DescriptionModel): Descriptions in different languages
        schema_name (str): Schema name
        domains (List[str]): List of associated domains
        plugins (List[Any]): List of associated plugins
        columns (List[ColumnModel]): List of table columns
        facets (List[Any]): List of table facets
        last_update (datetime): Last update timestamp
        data (DataModel): Data status information
    """
    id: str
    name: str
    label: LabelModel
    description: DescriptionModel
    schema_name: str = Field(..., alias="schema")
    domains: List[str]
    plugins: List[Any]
    columns: List[ColumnModel]
    facets: List[Any]
    last_update: datetime
    data: DataModel

class Datatables:
    """Class for managing datatable operations through the SWS API.

    This class provides methods for retrieving datatable information
    and managing data exports.

    Args:
        sws_client (SwsApiClient): An instance of the SWS API client
    """

    def __init__(self, sws_client: SwsApiClient) -> None:
        """Initialize the Datatables manager with SWS client."""
        self.sws_client = sws_client
    
    def get_datatable_info(self, datatable_id: str) -> DatatableModel:
        """Retrieve information about a specific datatable.

        Args:
            datatable_id (str): The identifier of the datatable

        Returns:
            DatatableModel: Datatable information if found, None otherwise
        """
        url = f"/datatables/{datatable_id}"

        response = self.sws_client.discoverable.get('datatable_api', url)
        if(response.get('id') is not None):
            return DatatableModel(**response)
        else:
            return None
        
    def invoke_export_datatable(self, datatable_id: str) -> Dict:
        """Trigger an export operation for a datatable.

        Args:
            datatable_id (str): The identifier of the datatable

        Returns:
            Dict: Response containing export operation status
        """
        url = f"/datatables/{datatable_id}/invoke_export_2_s3"

        response = self.sws_client.discoverable.post('datatable_api', url)

        return response

    def get_datatable_csv_path(self, datatable, timeout=60*15, interval=2) -> HttpUrl:
        """Get the CSV file path for a datatable, waiting for export if necessary.

        Args:
            datatable: The datatable identifier
            timeout (int): Maximum time to wait for export in seconds (default: 15 minutes)
            interval (int): Time between checks in seconds (default: 2)

        Returns:
            HttpUrl: URL to the CSV file

        Raises:
            TimeoutError: If export doesn't complete within timeout period
        """
        info = self.get_datatable_info(datatable)
        if info.data.available and info.data.uptodate:
            return info.data.url
        else:
            self.invoke_export_datatable(datatable)
            # get the updated info every interval seconds until the data are available to a maximum of timeout seconds
            start = datetime.now()
            while (datetime.now() - start).seconds < timeout:
                info = self.get_datatable_info(datatable)
                if info.data.available:
                    return info.data.url
                sleep(interval)