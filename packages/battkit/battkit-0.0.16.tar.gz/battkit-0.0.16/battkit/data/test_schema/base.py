

from abc import ABC, abstractmethod
from typing import Dict, Type
import pandas as pd

from battkit.logging_config import logger
from battkit.utils.typing_utils import types_match


class TestSchema(ABC):
	def __init__(self, test_name:str, required_schema:Dict[str, Type], optional_schema:Dict[str, Type]=None, summary_schema:Dict[str,Type]=None):
		self.test_name = test_name
		for k,v in required_schema.items(): assert type(v) == type, f"`required_schema` must contain str:type entries. {k}: {type(v).__name__} != {type.__name__}"
		self.req_schema = required_schema
		if optional_schema is not None:
			for k,v in optional_schema.items(): assert type(v) == type, f"`optional_schema` must contain str:type entries. {k}: {type(v).__name__} != {type.__name__}"
		self.opt_schema = optional_schema
		if summary_schema is not None:
			for k,v in summary_schema.items(): assert type(v) == type, f"`summary_schema` must contain str:type entries. {k}: {type(v).__name__} != {type.__name__}"
		self.sum_schema = summary_schema

	def _validate_data(self, data_schema:Dict[str, Type]) -> bool:
		"""Validate the provided data schema aginst the required properties for this test type"""
		
		missing_keys = [k for k in self.req_schema.keys() if k not in data_schema.keys()]
		invalid_types = {
			k:t for k,t in data_schema.items() \
			if (k in self.req_schema.keys() and not types_match(t, self.req_schema[k])) or \
			   (k in self.opt_schema.keys() and not types_match(t, self.opt_schema[k])) }

		if missing_keys:
			logger.error(f"Data validation failed. Missing required keys: {missing_keys}")
		if invalid_types:
			logger.error(f"Data validation failed. Invalid data types: {invalid_types}")

		if not missing_keys and not invalid_types:
			logger.info("Data validation successful.")
			return True

		return False
	
	@abstractmethod
	def validate_data(self, data_schema:Dict[str, Type]) -> bool:
		"""Validate the provided data schema aginst the required properties for this test type"""
		pass

	@abstractmethod
	def generate_summary(self, df_file:pd.DataFrame) -> dict:
		"""Extract summary information from a given dataframe specific to this test type."""
		pass


	
	

