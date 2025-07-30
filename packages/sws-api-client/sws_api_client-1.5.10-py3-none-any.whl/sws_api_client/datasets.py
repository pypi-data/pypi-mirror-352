"""Datasets Module for SWS API.

This module provides functionality for managing datasets, including creation,
cloning, data import/export, and dimension management through the SWS API client.
"""

import logging
from time import sleep
import os
import zipfile
from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from sws_api_client.codelist import Codelists
from sws_api_client.generic_models import Code, Multilanguage
from sws_api_client.sws_api_client import SwsApiClient
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = logging.getLogger(__name__)

class Lifecycle(BaseModel):
    """Model representing the lifecycle state of a dataset.

    Attributes:
        state (str): Current state of the dataset
        type (str): Type of lifecycle
        previousState (Optional[str]): Previous state if applicable
        created (int): Creation timestamp
        lastModified (int): Last modification timestamp
        lastModifiedBy (str): User who last modified the dataset
    """
    state: str
    type: str
    previousState: Optional[str]
    created: int
    lastModified: int
    lastModifiedBy: str

class Domain(BaseModel):
    """Model representing a domain.

    Attributes:
        id (str): Domain identifier
        label (Multilanguage): Multilanguage labels
        description (Dict): Domain description in multiple languages
    """
    id: str
    label: Multilanguage
    description: Dict

class Binding(BaseModel):
    """Model representing column binding information.

    Attributes:
        joinColumn (str): Column used for joining
    """
    joinColumn: Optional[str] = None

class Dimension(BaseModel):
    """Model representing a dataset dimension.

    Attributes:
        id (str): Dimension identifier
        label (Multilanguage): Multilanguage labels
        description (Dict): Dimension description
        sdmxName (str): SDMX name
        codelist (str): Associated codelist
        roots (List[str]): Root codes
        binding (Binding): Column binding information
        checkValidityPeriod (bool): Whether to check validity period
        formulas (List): Associated formulas
        type (str): Dimension type
    """
    id: str
    label: Multilanguage
    description: Dict
    sdmxName: Optional[str] = None
    codelist: str
    roots: List[str]
    binding: Binding
    checkValidityPeriod: bool
    formulas: List
    type: str

class Dimensions(BaseModel):
    dimensions: List[Dimension]

class PivotingGrouped(BaseModel):
    id: str
    ascending: bool

class Pivoting(BaseModel):
    grouped: List[PivotingGrouped]
    row: PivotingGrouped
    cols: PivotingGrouped

class DatasetBinding(BaseModel):
    observationTable: Optional[str] = None
    coordinateTable: Optional[str] = None
    sessionObservationTable: Optional[str] = None
    metadataTable: Optional[str] = None
    metadataElementTable:  Optional[str] = None
    sessionMetadataTable: Optional[str] = None
    sessionMetadataElementTable: Optional[str] = None
    validationTable: Optional[str] = None
    sessionValidationTable: Optional[str] = None
    tagObservationTable: Optional[str] = None
    tags: Optional[List] = None

class Dataset(BaseModel):
    id: str
    label: Multilanguage
    description: Dict
    sdmxName: Optional[str] = None
    lifecycle: Lifecycle
    domain: Domain
    dimensions: Dimensions
    flags: Dict
    rules: Dict
    pivoting: Pivoting
    pluginbar: Dict
    showEmptyRows: bool
    showRealCalc: bool
    useApproveCycle: bool
    binding: Optional[DatasetBinding] = None

class Fingerprint(BaseModel):
    empty: bool
    sessions: int
    queries: int
    tags: int
    computationTags: int
    modules: int
class DataModel(BaseModel):
    dataset: Dataset
    fingerprint: Optional[Fingerprint] = None

class MappedCode(BaseModel):
    code: Code
    include: bool
class Datasets:
    """Class for managing dataset operations through the SWS API.

    This class provides methods for creating, cloning, importing data,
    and managing dataset dimensions.

    Args:
        sws_client (SwsApiClient): An instance of the SWS API client
    """

    def __init__(self, sws_client: SwsApiClient) -> None:
        """Initialize the Datasets manager with SWS client."""
        self.sws_client = sws_client
        self.codelists = Codelists(sws_client)

    def get_dataset_export_details(self, dataset_id: str) -> dict:
        """Get export details for a dataset.

        Args:
            dataset_id (str): Dataset identifier

        Returns:
            dict: Dataset export information
        """
        url = f"/dataset/{dataset_id}/info"
        params = {"extended": "true"}

        response = self.sws_client.discoverable.get('session_api', url, params=params)

        return response
    
    def get_dataset_info(self, dataset_id: str) -> DataModel:
        """Retrieve dataset information.

        Args:
            dataset_id (str): Dataset identifier

        Returns:
            DataModel: Complete dataset information model
        """
        url = f"/admin/dataset/{dataset_id}"

        response = self.sws_client.discoverable.get('is_api', url)
        return DataModel(**response)

    def create_dataset(self, dataset: Dataset) -> DataModel:
        """Create a new dataset.

        Args:
            dataset (Dataset): Dataset configuration

        Returns:
            DataModel: Created dataset model
        """
        url = "/admin/dataset"

        response = self.sws_client.discoverable.post('is_api', url, data=dataset.model_dump())

        return response
    
    def clone_dataset(self, dataset_id: str, new_id: str) -> DataModel:
        """Clone an existing dataset with a new identifier.

        Args:
            dataset_id (str): Source dataset identifier
            new_id (str): New dataset identifier

        Returns:
            DataModel: Cloned dataset model
        """
        dataset = self.get_dataset_info(dataset_id)
        dataset.dataset.id = new_id
        new_dataset = self.create_dataset(dataset.dataset)
        return new_dataset
    
    def get_job_status(self, jobId: str) -> dict:
        """Check status of a job.

        Args:
            jobId (str): Job identifier

        Returns:
            dict: Job status information with result and success flags
        """
        url = f"/job/status/{jobId}"

        response = self.sws_client.discoverable.get('is_api', url)

        result:bool = response.get('result')
        success:bool = response.get('success')
        return dict(result=result, success=success)

    def import_data(self, dataset_id: str, file_path, sessionId = None, zip=False, data=True, metadata=False, separator=",", quote="\"" ) -> bool:
        """Import data into a dataset.

        Args:
            dataset_id (str): Target dataset identifier
            file_path: Path to data file
            sessionId (Optional[int]): Session identifier
            zip (bool): Whether to zip the file

        Returns:
            bool: True if import successful
        """
        return self.import_data_chunk(dataset_id, file_path, sessionId, data=data, metadata=metadata, separator=separator, quote=quote)
        

    def get_dataset_dimension_codes(self, dataset_id: str) -> Dict[str, List[Code]]:
        """Get codes for all dimensions in a dataset.

        Args:
            dataset_id (str): Dataset identifier

        Returns:
            Dict[str, List[Code]]: Dictionary mapping dimension IDs to their codes
        """
        dataset_info = self.get_dataset_info(dataset_id)
        dimensions = dataset_info.dataset.dimensions.dimensions

        # Fetch codelist codes for each dimension and use the dimension name for the CSV header
        dimensions_map:Dict[str, Dict[str, Dict[str, MappedCode]]] = {}
        for dimension in dimensions:
            logger.debug(f"Fetching codelist for dimension: {dimension}")
            codelist = self.codelists.get_codelist(dimension.codelist)
            # filter out codes that have more than 0 children
            
            dimensions_map[dimension.id] = {}
            for code in codelist.codes:
                dimensions_map[dimension.id][code.id] = {"code":code, "include":False}
        
        
        def include_children(code:Code, dimension_id:str):
            if dimensions_map[dimension_id][code.id]["include"] is False:
                dimensions_map[dimension_id][code.id]["include"] = True
            if len(code.children) > 0:
                for child in code.children:
                    if dimensions_map[dimension_id][child]["include"] is False:
                        dimensions_map[dimension_id][child]["include"] = True
                        include_children(dimensions_map[dimension_id][child]["code"], dimension_id)

        dimensions_codes = {}
        for dimension in dimensions:
            dimensions_codes[dimension.id] = []
            if len(dimension.roots) > 0:
                for root in dimension.roots:
                    include_children(dimensions_map[dimension.id][root]["code"], dimension.id)
                for code in dimensions_map[dimension.id]:
                    if dimensions_map[dimension.id][code]["include"]:
                        dimensions_codes[dimension.id].append(code)
            else:
                for code in dimensions_map[dimension.id]:
                    dimensions_codes[dimension.id].append(code)
        return dimensions_codes

    def import_data_chunk(self, dataset_id: str, file_path: str, sessionId: Optional[int] = None, data: Optional[bool] = True, metadata: Optional[bool] = False, separator: Optional[str] = ",", quote: Optional[str] = "\"") -> dict:
        """Import a single chunk of data, automatically handling file compression.

        Args:
            dataset_id (str): Target dataset identifier
            file_path (str): Path to data file
            sessionId (Optional[int]): Session identifier

        Returns:
            dict: Import job result

        Raises:
            OSError: If file operations fail
        """

        is_zip = zipfile.is_zipfile(file_path)
        zip_file_path = None
        
        if not is_zip:
            # Check file size and zip if greater than 10MB    
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB in bytes
                zip_file_path = f"{file_path}.zip"
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                file_path = zip_file_path  # Use zipped file for upload
                is_zip = True
            else:
                is_zip = False

        url = "/observations/import"
        dataset_info = self.get_dataset_info(dataset_id)

        scope = "DATA"

        if data == True and metadata == True:
            scope = ["DATA", "METADATA"]
        elif metadata == True:
            scope = "METADATA"

        dataPayload = {
            "domain": dataset_info.dataset.domain.id,
            "dataset": dataset_id,
            "sessionId": -1 if sessionId is None else sessionId,
            "format": "CSV",
            "scope": scope,
            "execution": "ASYNC",
            "fieldSeparator": separator,
            "quoteOptions": quote,
            "filedownload": "ASYNC",
            "lineSeparator": "\n",
            "headers": "CODE",
            "structure": "NORMALIZED",
        }
        
        file_name = os.path.basename(file_path)

        files = {"file": (file_name, open(file_path, 'rb'), "application/zip" if is_zip else "text/csv")}
        
        response = self.sws_client.discoverable.multipartpost('is_api', url, data=dataPayload, files=files)
        logger.debug(f"Import data response for chunk: {response}")

        # Clean up the zip file if it was created
        if zip_file_path:
            os.remove(zip_file_path)

        job_id = response['result']
        return self.get_job_result(job_id)

    def get_job_result(self, job_id: str) -> bool:
        """Poll for job completion and return result.

        Args:
            job_id (str): Job identifier

        Returns:
            bool: True if job completed successfully
        """
        while True:
            logger.debug(f"Checking job status for job ID {job_id}")
            job_status = self.get_job_status(job_id)
            if job_status['result']:
                return job_status['success']

            if not job_status['result'] and not job_status['success']:
                return False
            sleep(5)

    def chunk_csv_file(self, file_path: str, chunk_size: int) -> List[str]:
        """Split CSV file into smaller chunks while preserving data format.

        Args:
            file_path (str): Path to CSV file
            chunk_size (int): Number of rows per chunk

        Returns:
            List[str]: Paths to chunk files

        Raises:
            OSError: If file operations fail
            pd.errors.EmptyDataError: If CSV file is empty
        """
        temp_files = []
        
        # Load the data in chunks and process each chunk
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size, dtype=str)):
            # Convert 'value' column to numeric, allowing other columns to stay as strings to preserve leading zeros
            if 'value' in chunk.columns:
                chunk['value'] = pd.to_numeric(chunk['value'], errors='coerce')
            
            chunk_file = f"{file_path}_chunk_{i}.csv"
            chunk.to_csv(chunk_file, index=False, quoting=1)  # quoting=1 ensures quotes around strings to preserve zeros
            temp_files.append(chunk_file)
        
        return temp_files

    def import_data_concurrent(self, dataset_id: str, file_path: str, sessionId: Optional[int] = None, data=True, metadata=False, separator=",", quote="\"", chunk_size: int = 10000, max_workers: int = 5) -> None:
        """Import data in parallel using multiple threads.

        Args:
            dataset_id (str): Target dataset identifier
            file_path (str): Path to data file
            sessionId (Optional[int]): Session identifier
            chunk_size (int): Rows per chunk
            max_workers (int): Maximum number of concurrent imports

        Raises:
            OSError: If file operations fail
            Exception: If import operations fail
        """
        # Step 1: Split the file into chunks
        chunk_files = self.chunk_csv_file(file_path, chunk_size)
        total_chunks = len(chunk_files)  # Total number of chunks for progress tracking
        completed_chunks = 0  # Initialize counter for completed chunks
        
        logger.info(f"Importing chunks: started")
        # Step 2: Use ThreadPoolExecutor to manage parallel imports
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {executor.submit(self.import_data_chunk, dataset_id, chunk_file, sessionId, data, metadata, separator, quote): chunk_file for chunk_file in chunk_files}
            results = []

            # Step 3: Collect and manage job statuses
            for future in as_completed(future_to_chunk):
                chunk_file = future_to_chunk[future]
                try:
                    chunk_result = future.result()
                    result = {"result": chunk_result, "chunk_file": chunk_file}
                    results.append(result)
                    logger.debug(f"Chunk {chunk_file} ended successfully")
                except Exception as exc:
                    logger.error(f"Chunk {chunk_file} generated an exception: {exc}")
                finally:
                    # Update and log progress
                    completed_chunks += 1
                    logger.info(f"Importing chunks: {completed_chunks}/{total_chunks} cmopleted")
        
        # Step 4: Wait for all jobs to complete and clean up temporary files
        for result in results:
            success = result.get('result')
            if not success:
                logger.error(f"Chunk {result.get('chunk_file')} failed to import.")
            else:
                logger.debug(f"Chunk {result.get('chunk_file')} completed successfully.")
                os.remove(result.get('chunk_file'))

        logger.info("Importing chunks: completed")

    def convert_codes_to_ids(self, dataset: DataModel, codes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Convert codes to internal IDs for a dataset.

        Args:
            dataset_id (str): Dataset identifier
            codes (Dict[str, List[str]]): Dictionary mapping dimension IDs to lists of codelist codes

        Returns:
            Dict[str, List[str]]: Dictionary mapping dimension IDs to lists of internal IDs
        """
        
        dimensions = dataset.dataset.dimensions.dimensions

        # Convert codes to internal IDs
        codelists = {}
        for dimension in dimensions:
            dimension.codelist
            codelists[dimension.codelist] = codes.get(dimension.id, [])
        
        data = {
            "codelists": codelists
        }
        response = self.sws_client.discoverable.post('session_api', 'codelist/convert_codes_to_ids', data=data)
        logger.debug(f"Convert codes to IDs response: {response}")
        # Map the response to the original codes
        ids = {}
        for dimension in dimensions:
            ids[dimension.id] = response.get(dimension.codelist, [])
        return ids

    def convert_id_to_codes(self, dataset: DataModel, ids: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Convert internal IDs to codes for a dataset.

        Args:
            dataset_id (str): Dataset identifier
            ids (Dict[str, List[str]]): Dictionary mapping dimension IDs to lists of internal codelist codes IDs

        Returns:
            Dict[str, List[str]]: Dictionary mapping dimension IDs to lists of codelist codes
        """
        
        dimensions = dataset.dataset.dimensions.dimensions

        # Convert IDs to codes
        codelists = {}
        for dimension in dimensions:
            codelists[dimension.codelist] = ids.get(dimension.id, [])

        data = {
            "codelists": codelists
        }

        response = self.sws_client.discoverable.post('session_api', 'codelist/convert_ids_to_codes', data=data)
        logger.debug(f"Convert IDs to codes response: {response}")
        # Map the response to the original IDs
        codes = {}
        for dimension in dimensions:
            codes[dimension.id] = response.get(dimension.codelist, [])
        return codes
        

    





