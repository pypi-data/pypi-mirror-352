
import pandas as pd
import dask.dataframe as dd
from typing import Optional, Union
from pathlib import Path


def dataframe_to_dask(dataframe:Union[pd.DataFrame, dd.DataFrame]) -> dd.DataFrame:
	"""Converts a dataframe object (Dask or Pandas) to a Dask dataframe"""

	if isinstance(dataframe, dd.DataFrame): 
		return dataframe
	elif isinstance(dataframe, pd.DataFrame):
		return dd.from_pandas(dataframe)
	else:
		raise TypeError(f"Unknown dataframe instance: {type(dataframe)}")
	
def dataframe_to_pandas(dataframe:Union[pd.DataFrame, dd.DataFrame]) -> pd.DataFrame:
	"""Converts a dataframe object (Dask or Pandas) to a Pandas dataframe"""

	if isinstance(dataframe, pd.DataFrame): 
		return dataframe
	elif isinstance(dataframe, dd.DataFrame):
		return dataframe.compute()
	else:
		raise TypeError(f"Unknown dataframe instance: {type(dataframe)}")

def dask_partition_file_naming_fnc(partition_index:int, stem:Optional[str]=None, file_type:str='parquet') -> str:
	"""A default partition naming function for saving Dask dataframes"""
	if stem is None: stem = 'part'
	return f"{stem}_p{partition_index}.{file_type}"

def get_dask_partition_from_file_name(file:Path) -> int:
	"""Returns the partition number from a saved dask partition file."""
	temp = file.name
	return int(temp[temp.rindex('_p')+2 : temp.rindex('.')])

def dask_partition_file_naming_sort_fnc(path:str, file_type:str='parquet') -> int:
	path = str(path)
	return int(path[path.rindex('_p')+2 : path.rindex(f'.{file_type}')])


