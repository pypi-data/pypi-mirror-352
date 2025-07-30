
import shutil, json
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype
import numpy as np
import dask.dataframe as dd
from tqdm import tqdm

from battkit.config import MEMORY_LIMIT
from battkit.logging_config import logger

from battkit.data.dataset import TableManager
from battkit.data.dataset.utils import extract_file_grouping, standardize_files, infer_data_converter

class Dataset:
	def __init__(self, name: str, dir_storage:Path, overwrite_existing:bool=False):
		self.name = name
		if not dir_storage.exists():
			logger.error(f"Directory ({dir_storage}) does not exist.")
			raise FileNotFoundError(f"Directory does not exist: {dir_storage}")
		
		self._dir_storage = dir_storage.joinpath(f"BattKitDataset {name}")
		self._table_manager = TableManager(self._dir_storage)
		
		if self._dir_storage.exists():
			if not overwrite_existing:
				logger.info(f"Dataset already exists at this location. Loading saved files.")
				try:
					self._load_existing()
				except Exception as e:
					logger.error(f"Could not load existing dataset at {self._dir_storage}")
					raise e
			else:
				shutil.rmtree(self._dir_storage)
				self._dir_storage.mkdir(exist_ok=False, parents=True)
		else:
			self._dir_storage.mkdir(exist_ok=False, parents=True)

	@property
	def existing_tables(self):
		return self._table_manager.available_tables


	def add_files(self, dir_files:Union[Path, List[Path]], group_by:Union[str, List[str]]=None, data_converter:str=None, custom_tags:Dict[str,Any]=None, n_jobs=-1, file_batch_size=100):
		"""
		Add raw files under the `dir_files` directory to the dataset. 
		Data will be standardized and appended to the corresponding key in the `tables` attribute.

		Args:
			dir_files (Path): Directory or list of filepaths containing the raw data to add.
			group_by (Union[str, List[str]], optional): The key(s) to use to group files belonging to the \
				same cell (e.g., ['CHANNEL_ID']). If not specified, defaults keys defined by the \
				DataConverter will be used. Defaults to None.
			data_converter (str, optional): Can specify the appropriate DataConverter name for these \
				files, if known. Otherwise, an appropriate DataConverter will be automatically selected. \
				Defaults to None.
			custom_tags (Dict[str,Any], optional): Can choose to add a custom tags to the provided set of \
				files for future sorting. These appear as additional columns (defined by the dict keys) \
				with the assigned value (eg, custom_tags={'label':'diagnostics',}). Defaults to None.
			n_jobs (int, optional): Can specify the number of parallel cores to use. 
				Defaults to -1 (all available CPU cores).
			file_batch_size (int, optional): Can specify the max number of files to process in a single batch. \
				Defaults to 100.
		"""
		
		# List and filter new files
		file_list, next_file_id = self._table_manager.filter_new_files(dir_files)
		if not file_list:
			logger.info("No new files to add.")
			return
		
		# Batch files
		n_batches = (len(file_list) // file_batch_size) + 1
		for i in range(n_batches):
			batch_files = file_list[i * file_batch_size : (i + 1) * file_batch_size]
			if len(batch_files) == 0: continue
			tqdm.write(f"\nProcessing Batch {i+1}/{n_batches}: {len(batch_files)} files")

			# 1. Get converter and extract metadata
			# TODO: assuming all files have the same data converter
			#	- this is more efficient than checking every file but not robust 
			with tqdm(total=len(batch_files), desc=" > Extracting meta-data", leave=True) as pbar1:
				data_converter = data_converter if data_converter else infer_data_converter(batch_files[0])
				df_group_by = extract_file_grouping(
					file_list=batch_files, 
					next_file_id=next_file_id, 
					data_converter=data_converter,
					group_by=group_by,
					n_jobs=n_jobs,
					tqdm_pbar=pbar1)
				
			# 2. Update Files table
			file_table_keys = ['FILE_ID', 'CELL_ID',] + [k for k in df_group_by.columns if k not in ['FILE_ID', 'CELL_ID', 'FILEPATH']]
			df_files_table = df_group_by[file_table_keys].copy()
			self._table_manager.update_files_table(df_files_table, tags=custom_tags)
			self._save_state()

			# 3. Extract and save raw standardized data
			with tqdm(total=len(batch_files), desc=" > Standardizing data", leave=True) as pbar2:
				df_summary = standardize_files(
					df_files=df_group_by, 
					data_converter=data_converter, 
					dir_save=self._dir_storage, 
					n_jobs=n_jobs,
					tqdm_pbar=pbar2
				)
			summary_table_keys = ['FILE_ID', 'CELL_ID',] + [k for k in df_summary.columns if k not in ['FILE_ID', 'CELL_ID']]
			df_summary = df_summary[summary_table_keys]
			self._save_state()

			# 4. Update Timeseries/Frequency tables
			self._table_manager.update_test_type_summary_tables(df_summary)
			self._table_manager.update_test_type_tables()
			self._save_state()

			# main_bar.update(1)

		# Repartition all tables to ensure optimal sizes
		self._table_manager._repartition()

			


	
	def regroup(self, group_by:Union[str, List[str]]=None, mapping:Dict=None):
		"""Regroups cells and files based on a new set of group_by terms or an explicit mapping. 

		Args:
			group_by (Union[str, List[str]], optional): The new key(s) to use to group files belonging to the same cell (e.g., ['CHANNEL_ID', 'PROTOCOL', etc]). Defaults to None.
			mapping (Optional[dict], optional): An explicit mapping of \'FILE_ID\' to \'CELL_ID\'. Defaults to None.
		"""
		self._table_manager.regroup(group_by, mapping)

	def get_summary(self, table_name:str='Files', level:str='CELL_ID') -> pd.DataFrame:
		"""Generates a summary of the specified table and grouping level.

		Args:
			table_name (str, optional): The table to summarize. Defaults to 'Files'.
			level (str, optional): The level of summary to provide: 'FILE_ID' or 'CELL_ID'. \
				Defaults to 'FILE_ID' (summary statistics for each unique FILE_ID)

		Returns:
			pd.DataFrame: A table of summary statistics with unique rows defined by `level`
		"""

		if not level in ['CELL_ID', 'FILE_ID']: raise ValueError(f"`level` must be in {['CELL_ID', 'FILE_ID']}")

		# Get summary for given table name
		try:
			df_summary = self.get_table(f"{table_name}_Summary").compute()
		except:
			logger.warning(f"{table_name} table has no summary. {table_name} must have a summary")
			return None
		
		# Has cols: 'FILE_ID', 'CELL_ID', ... all others are summary stats
		# Define aggregation method for each summary stat column

		df_grouped = None
		if table_name == 'Files':
			agg_dict = {}
			if level == 'CELL_ID':
				agg_dict['NUM_UNIQUE_FILES'] = ('FILE_ID', 'nunique')
				agg_dict['FILE_IDS'] = (
					'FILE_ID', 
					lambda x: (
						[int(v) if isinstance(v, np.integer) else v for v in np.unique(x)]
						if len(np.unique(x)) > 1
						else np.unique(x).item()
					)
				)
				
			elif level == 'FILE_ID':
				agg_dict['NUM_UNIQUE_CELLS'] = ('CELL_ID', 'nunique')
				agg_dict['CELL_IDS'] = (
					'CELL_ID', 
					lambda x: (
						[int(v) if isinstance(v, np.integer) else v for v in np.unique(x)]
						if len(np.unique(x)) > 1
						else np.unique(x).item()
					)
				)
				
			agg_dict['TIME_UNDER_TEST_DAYS'] = ('DURATION_DAYS', 'sum')
			
			for k in [k for k in df_summary.columns if k not in ['FILE_ID', 'CELL_ID', 'DURATION_DAYS']]:
				agg_dict[f"NUM_UNIQUE_{k}S"] = (k, 'nunique')
				agg_dict[f"{k}S"] = (k, 
					lambda x: (
						[str(v) if isinstance(v, np.str_) else v for v in np.unique(x)]
						if len(np.unique(x)) > 1
						else str(np.unique(x).item())
					)
				)

			df_grouped = df_summary.groupby(level).agg(**agg_dict).reset_index()

		else:
			agg_map = {}
			for col in df_summary.columns:
				if col == level or level[:str(level).rindex("_ID")] in col:  
					continue  # skip the grouping column
				elif col in ["FILE_ID", "CELL_ID"]:
					agg_map[col] = lambda x: (
						[int(v) if isinstance(v, np.integer) else v for v in np.unique(x)]
						if len(np.unique(x)) > 1
						else np.unique(x).item()
					)
				elif "MAX" in col:
					agg_map[col] = "max"
				elif "MIN" in col:
					agg_map[col] = "min"
				elif "NUM" in col or is_numeric_dtype(df_summary[col]):
					agg_map[col] = "sum"
				elif is_string_dtype(df_summary[col]) or df_summary[col].dtype == 'object':
					agg_map[col] = lambda x: (
						[str(v) if isinstance(v, np.str_) else v for v in np.unique(x)]
						if len(np.unique(x)) > 1
						else str(np.unique(x).item())
					)
				else:
					raise ValueError(f"Unknown column in `df_summary`: `{col}`")

			# Perform groupby with dynamic aggregation
			df_grouped = df_summary.groupby(level).agg(agg_map).reset_index()


		return df_grouped

	def get_table(self, name:str) -> dd.DataFrame:
		"""Retrieve the specified table. \n
		*Note:* The default index is the RECORD_NUMBER and thus repeats for each FILE_ID \
		(ie, **the default index is not unique**). If a unique index is needed, convert to Pandas and \
		use a multi-index with 'FILE_ID' & 'RECORD_NUMBER'. Multi-indices are not currently \
		supported in Dask. Ex: `df.set_index(['FILE_ID', 'RECORD_NUMBER'], drop=False, inplace=True)`

		Args:
			name (str): Name of table to retrieve.

		Returns:
			dd.DataFrame: A Dask dataframe.
		"""
		return self._table_manager.get_table(name)

	def create_table(self, name:str, data:Union[pd.DataFrame, dd.DataFrame], overwrite_existing:bool=False):
		"""Creates a new table from the given dataframe."""
		self._table_manager.create_table(name=name, data=data, overwrite_existing=overwrite_existing)

	def filter(self, table_name:Optional[str]=None, data:Optional[Union[pd.DataFrame, dd.DataFrame]]=None, **conditions) -> Union[pd.DataFrame, dd.DataFrame]:
		"""Filters the specified table or data based on conditions applied to the 'Files' table and the specified table.

		Args:
			table_name (Optional[str], optional): The name of the table to filter (eg, 'TimeSeries'). If not specified, the table type is automatically determined from the \'data\' schema.
			data (Optional[Union[pd.DataFrame, dd.DataFrame]], optional): The subset of data to filter. If None, the entire table specified by \'table_name\' is filtered.
			conditions (dict): Key-value pairs specifying filtering conditions. 

		Returns:
			Union[pd.DataFrame, dd.DataFrame] : A DataFrame comprising a filtered subset of the `table_name` or `data`.
		"""
		if table_name is None: assert data is not None, "Either \'table_name\' or \'data\' must be provided."
		if data is None: assert table_name is not None, "Either \'table_name\' or \'data\' must be provided."

		# determine table type if not specified
		if table_name is None and not data is None: 
			table_name = self._table_manager.identify_table_type(list(data.columns))

		avilable_tables = self._table_manager.available_tables
		if ('Files' not in avilable_tables) or (table_name not in avilable_tables):
			logger.error(f"Unknown table name: {table_name}")
			raise ValueError(f"Invalid table name: {table_name}")

		files_table = self.get_table('Files')
		target_table = self.get_table(table_name) if data is None else data

		# Step 1: separate conditions for File table and target table
		files_conditions = {k:v for k,v in conditions.items() if k in files_table.columns}
		target_conditions = {k:v for k,v in conditions.items() if k in target_table.columns}
		invalid_conditions = {k:v for k,v in conditions.items() if (k not in files_conditions) and (k not in target_conditions)}
		if invalid_conditions:
			logger.warning(f"Invalid keywords are being ignored: {invalid_conditions.keys()}")

		# Step 2: filter Files table first (if applicable)
		if files_conditions:
			# Apply File table conditions
			for k,v in files_conditions.items():
				# support for range functions like 'lambda x : x <= 4.2'
				if callable(v):
					if isinstance(files_table, dd.DataFrame):
						files_table = files_table[files_table[k].apply(v, meta=(k, 'bool'))]
					else:
						files_table = files_table[files_table[k].apply(v)]
				# support for multiple condition values
				elif isinstance(v, (list, tuple, set, np.ndarray)):	
					files_table = files_table[files_table[k].isin(v)]
				else:
					files_table = files_table[files_table[k] == v]

			# Get matching FILE_IDs
			file_ids = files_table['FILE_ID'].values
			# Filter target table by FILE_IDs
			target_table = target_table[target_table['FILE_ID'].isin(file_ids)]

		# Step 3: apply target table conditions
		if target_conditions:
			for k,v in target_conditions.items():
				# support for range functions like 'lambda x : x <= 4.2'
				if callable(v):
					if isinstance(target_table, dd.DataFrame):
						target_table = target_table[target_table[k].apply(v, meta=(k, 'bool'))]
					else:
						target_table = target_table[target_table[k].apply(v)]
				# support for multiple condition values
				elif isinstance(v, (list, tuple, set, np.ndarray)):	
					target_table = target_table[target_table[k].isin(v)]
				else:
					target_table = target_table[target_table[k] == v]

		return target_table

	def sort(self, sort_columns:List[str], table_name:Optional[str]=None, data:Optional[Union[pd.DataFrame, dd.DataFrame]]=None, ascending:Union[bool, List[bool]]=True) -> Union[pd.DataFrame, dd.DataFrame]:
		"""Sorts the specified table or data based on conditions applied to the 'Files' table and the specified table. *IMPORTANT: Sorting requires loading all specified data into memory. Ensure the data to be sorted is first filtered to only the required subset*.

		Args:
			sort_columns (List[str]): The column names to sort by. Can contain column name in the specified \'table_name\', \'data\', or the \'Files\' table.
			table_name (Optional[str], optional): The name of the table to sort (eg, 'TimeSeries'). If not specified, the table type is automatically determined from the \'data\' schema.
			data (Optional[Union[pd.DataFrame, dd.DataFrame]], optional): The subset of data to sort. If None, the entire table specified by \'table_name\' is sorted *(WARNING: This will load the entire table into memory!)* 
			ascending (Union[bool, List[bool]]=True). Sort order for all or each column in \'sort_columns\'. Defaults to True (ascending for all \'sort_columns\').
		
		Returns:
			Union[pd.DataFrame, dd.DataFrame]: A DataFrame comprising a sorted version of the specified table or data.
		"""

		if table_name is None: assert data is not None, "Either \'table_name\' or \'data\' must be provided."
		if data is None: assert table_name is not None, "Either \'table_name\' or \'data\' must be provided."

		# determine table type if not specified
		if table_name is None and data is None: 
			self._table_manager.identify_table_type(list(data.columns))

		avilable_tables = self._table_manager.available_tables
		if 'Files' not in avilable_tables or (table_name is not None and table_name not in avilable_tables):
			logger.error(f"Unknown table name: {table_name}")
			raise ValueError(f"Invalid table name: {table_name}")

		files_table = self.get_table('Files').compute()
		target_table = self.get_table(table_name) if data is None else data

		# Step 1: Determine which columns are in the specified data or table_name
		original_columns = target_table.columns
		available_columns = [col for col in sort_columns if col in target_table.columns]
		missing_columns = [col for col in sort_columns if col not in target_table.columns]

		# Step 2: If any columns are missing, check the 'Files' table
		if missing_columns:	
			# Ensure all missing columns exist in the 'Files' table
			for col in missing_columns:
				if col not in files_table.columns:
					raise ValueError(f"Column '{col}' not found in \'data\' or the {f'{table_name} and ' if table_name is not None else ''}'Files' tables.")

			# Merge the original table with 'Files' on FILE_ID
			target_table = target_table.merge(files_table[['FILE_ID'] + missing_columns], on='FILE_ID', how='left')

		# Step 3: If target_table is a dask dataframe, we will need to load it into memory
		if isinstance(target_table, dd.DataFrame):
			# Check if the approx. memory required exceeds the user's limit.
			approx_mem = target_table.memory_usage(deep=True).sum().compute()
			# If so, use set_index(sort=True). This is an approximate sort that doesn't require loading all data in memory at once (still a very expensive operation)
			if approx_mem > MEMORY_LIMIT * 10**9:
				logger.warning(f"Data exceeds in-memory limit ({MEMORY_LIMIT} Gb). The resulting sort is approximate (sorted within partition but not globally).")
				target_table = target_table.set_index(sort_columns, sorted=True)
			# Otherwise, load into memory and sort with sort_values
			else:
				target_table = target_table.compute()
		
		# Pandas df can be sorted with sort_values
		if isinstance(target_table, pd.DataFrame):
			target_table = target_table.sort_values(by=sort_columns, ascending=ascending)

		# Step 4: Drop extra columns from Files table
		target_table = target_table[target_table.columns.intersection(original_columns)]

		return target_table

	def export(self, dir_save:Path, overwrite:bool=False):
		"""Export a copy of Dataset to `dir_save`

		Args:
			dir_save (Path): Path to save location.
			overwrite (bool, optional): If True, overwrites existing copy at `dir_save`. Defaults to False.
		"""

		# 1. Export all table data and standardized files
		self._table_manager.export(self.name, dir_save, overwrite)

		# 2. Export config file
		self._save_state(dir_save)
	


	def _save_state(self, dir_save:Optional[Path]=None):
		"""Saves the Dataset config state (config.json)"""

		if dir_save is None: 
			dir_save = self._dir_storage
		else:
			dir_save = dir_save.joinpath(self._dir_storage.name)
			dir_save.mkdir(exist_ok=True, parents=True)

		with open(dir_save.joinpath("config.json"), "w") as f:
			json_data = {
				'name':self.name,
				#'TODO': ADD TO THIS DICT WITH FUTURE DATASET ATTRIBUTES
			}
			json.dump(json_data, f, indent=4)
		
	def _load_existing(self):
		"""Load existing Dataset at self._dir_storage"""

		# Load dataset config
		file_config = self._dir_storage.joinpath("config.json")
		with open(file_config, "r") as f:
			config_data = json.load(f)
			if not config_data.get('name') == self.name:
				raise ValueError("Conflicting values found in `config.json`.")
			# TODO: updated with future attributes to load

		self._table_manager._load_existing()
