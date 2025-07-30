
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Type
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Optional

REQUIRED_GROUP_BY_SCHEMA = {
	"CELL_ID":Union[int, str],
	"TEST_TYPE":str,
	"PROTOCOL":str, 
	"FILENAME":str,
	"DATETIME_START":datetime,
	"DATETIME_END":datetime,
}

class DataConverter(ABC):
	group_by_schema : dict

	def __init__(self, name:str, file_types:List[str]):
		"""_summary_

		Args:
			name (str): Name of this DataConverter instance
			file_types (List[str]): A list of file types supported by this DataConverter
			group_by (Optional, Dict[str,Type]): A schema of group_by terms supported by this DataConverter. Defaults to all GROUP_BY_TERMS
		"""

		self.name = name
		self.file_types = file_types
		self.group_by_schema = {**self.define_schema(), **REQUIRED_GROUP_BY_SCHEMA,}

	def __repr__(self):
		return f"{self.name} DataConverter"
	
	@staticmethod
	@abstractmethod
	def define_schema() -> dict:
		"""Subclasses must implement this method to return their specific schema."""
		pass

	@classmethod
	@abstractmethod
	def validate_file_type(cls, file:Path) -> bool:
		"""Checks whether the provided file uses a file type supported by this DataConverter"""
		pass

	@classmethod
	@abstractmethod
	def validate_converter(cls, file:Path) -> bool:
		"""Checks whether the provided file matches this DataConverter"""
		pass

	@classmethod
	@abstractmethod
	def extract_group_by_data(cls, file:Path) -> dict:
		"""Extracts group_by terms from the provided file using a light-weight read operation"""
		# This should use a light-weight file read to extract data corresponding to each supported
		# group_by term. For example, if "CELL_ID" is supported by this DataConverter, this method 
		# should extract the "CELL_ID" defined in this file without loading the entire file.
		# See the sub-class NewareDataConverter for an example
		pass

	@classmethod
	@abstractmethod
	def extract_timeseries_data(cls, file:Path) -> pd.DataFrame:
		"""Extracts data using the time-series test schema."""
		pass

