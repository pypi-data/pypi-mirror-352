
import shutil, os, ast
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
import pandas as pd
import numpy as np
import dask.dataframe as dd
import logging

from battkit.config import MAX_PARTITION_SIZE
from battkit.logging_config import logger, suppress_logging
from battkit.utils.dataframe_utils import dask_partition_file_naming_fnc, dask_partition_file_naming_sort_fnc, get_dask_partition_from_file_name


class TableManager():
	def __init__(self, dir_storage:Path):
		self._tables = {}
		self._dir_storage = dir_storage

	@property
	def available_tables(self):
		return self._tables.keys()


	def filter_new_files(self, dir_files:Union[Path, List[Path]]) -> Tuple[List[Path], int]:
		"""
		Compares all files in a given directory or list of files and returns a list of file not already in the
		'Files' table.

		Args:
			dir_files (Union[Path, List[Path]]): The directory or list of paths to search through.

		Returns:
			Tuple[List[Path], int]: A list of new filepaths and the integer of the next FILE_ID 
			avilable in the 'Files' table.
		"""

		# Get all files from folder (search recursively)
		files = None
		if hasattr(dir_files, '__len__'):							# Given a list of paths
			files = dir_files
		elif isinstance(dir_files, Path) and dir_files.is_file():	# Given a single path
			files = [dir_files]
		elif isinstance(dir_files, Path) and dir_files.is_dir():	# Given a directory
			files = [f for f in dir_files.rglob('*') if not f.name.startswith('.') and f.is_file()]
		else:
			logger.error(f"dir_files is not a file or directory: {dir_files}")
			raise TypeError("dir_files is not a directory or filepath.")
		
		next_file_id = 0
		df_files = None
		try:
			with suppress_logging(level=logging.ERROR, logger_name=logger.name):
				df_files = self.get_table('Files').compute()
		except:
			# Files table doesn't exist yet
			return files, 0

		old_files = [Path(f).stem for f in df_files['FILENAME'].values]
		new_files = [f for f in files if f.stem not in old_files]
		next_file_id = df_files['FILE_ID'].max() + 1

		return new_files, next_file_id

	def create_table(self, name:str, data:Union[pd.DataFrame, dd.DataFrame], overwrite_existing:bool=False):
		"""Creates a new table from the given dataframe."""

		if name in self._tables.keys() and not overwrite_existing:
			logger.error(f"Table (\'{name}\') already exists.")
			raise ValueError(f"Table (\'{name}\') already exists. Use `update_test_type_tables()` to add to it.")
		
		if not (isinstance(data, pd.DataFrame) or isinstance(data, dd.DataFrame)):
			logger.error("Data must be a Pandas or Dask Dataframe.")
			raise TypeError("Data must be a Pandas or Dask Dataframe.")

		if isinstance(data, pd.DataFrame):
			data = dd.from_pandas(data, npartitions=1)
		self._tables[name] = data
		logger.info(f"Table (\'{name}\') successfully added to Dataset.")
		self.save_table(name)
		self._tables[name] = self.get_table(name, reload=True)

	def update_files_table(self, df_group_by:pd.DataFrame, tags:Dict[str,Any]=None, reload:bool=False):
		"""Updates `Files` table and generates new `Files_Summary` data,

		Args:
			df_group_by (pd.DataFrame): New `Files` data. Must include columns: ['FILE_ID', 'CELL_ID', \
				'TEST_TYPE', 'PROTOCOL'].
			tags (Dict[str,Any], optional): Can choose to add a custom tags to the provided set of \
				files for future sorting. These appear as additional columns (defined by the dict keys) \
				with the assigned value (eg, custom_tags={'label':'diagnostics',}). Defaults to None.
			reload (bool, optional): Whether to force a reload from disk. Defaults to False.
		"""

		df_files_new = df_group_by.copy()
		
		# The CELL_ID values in df_group_by are created based on that specific batch of files
		# We need to check if those groupings exist in the `Files` table, and if so, reassign the cell ID
		if 'Files' in self.available_tables:
			df_files = self.get_table('Files').compute()

			# Parse group_by cols from first row of GROUP_BY (assumes consistent for all)
			group_by_cols = ast.literal_eval(df_files_new['GROUP_BY'].iloc[0])

			# Reconstruct grouping values for matching
			df_files_new['_GROUP_KEY'] = df_files_new.apply(
				lambda row: tuple(row[k] for k in group_by_cols), axis=1
			)
			df_files['_GROUP_KEY'] = df_files.apply(
				lambda row: tuple(row[k] for k in group_by_cols), axis=1
			)

			# Build a map from existing group key to existing CELL_ID
			group_to_cell_id = dict(df_files[['CELL_ID', '_GROUP_KEY']].drop_duplicates().set_index('_GROUP_KEY')['CELL_ID'])
			
			# Assign new CELL_IDs
			group_to_final_cell_id = {}
			max_cell_id = df_files['CELL_ID'].max()
			next_cell_id = max_cell_id + 1 if pd.notna(max_cell_id) else 0
			for group_key in df_files_new['_GROUP_KEY'].unique():
				if group_key in group_to_cell_id.keys():
					group_to_final_cell_id[group_key] = int(group_to_cell_id[group_key])
				else:
					group_to_final_cell_id[group_key] = next_cell_id
					next_cell_id += 1

			df_files_new['CELL_ID'] = df_files_new['_GROUP_KEY'].map(group_to_final_cell_id)
		
			# Clean up
			df_files_new.drop(columns=['_GROUP_KEY'], inplace=True)

			# Update FILE_ID
			max_file_id = df_files['FILE_ID'].max()
			next_file_id = max_file_id + 1 if pd.notna(max_file_id) else 0
			df_files_new['FILE_ID'] = df_files_new['FILE_ID'] - df_files_new['FILE_ID'].min() + next_file_id

		# 1. Add tags to new files data
		if not tags is None:
			for k,v in tags.items():
				df_files_new[k] = np.full(len(df_files_new), v)
		
		# 2. Generate file table summary
		cols = ['FILE_ID', 'CELL_ID', 'PROTOCOL', 'TEST_TYPE',]
		if not tags is None: cols += [k for k in tags.keys()]
		df_files_summary_new = df_files_new[cols].copy()
		if 'DATETIME_START' in df_files_new.columns and 'DATETIME_END' in df_files_new.columns:
			df_files_summary_new['DURATION_DAYS'] = (
				df_files_new['DATETIME_END'] - df_files_new['DATETIME_START']
			).dt.total_seconds() / 86400  # 86400 seconds in a day
		else:
			df_files_summary_new['DURATION_DAYS'] = np.full(len(df_files_summary_new), 'NA')

		# 3. Update saved table references
		for t_name, new_data in {'Files':df_files_new, 'Files_Summary':df_files_summary_new}.items():
			# Get saved table (if exists)
			try:
				with suppress_logging(level=logging.ERROR, logger_name=logger.name):
					ddf_prev = self.get_table(t_name)
			except:
				ddf_prev = None
		
			# Create new table (overwrite existing)
			if ddf_prev is None or reload:
				self.create_table(name=t_name, data=dd.from_pandas(new_data, npartitions=1), overwrite_existing=True)

			# Only append new data, don't regenerate entire table
			else:
				self._append_to_table(t_name, dd.from_pandas(new_data, npartitions=1))
				

	def update_test_type_tables(self, reload:bool=False):
		"""
		Update all test-type tables using the current state of the 'Files' table. \n
		*Note: By default, this only looks for and updates tables with missing FILE_IDs. \
		If reload equals True, then all tables and fully regenerated*

		Args:
			reload (bool, optional): Whether to force reload all tables. Defaults to False.
		"""
		
		df_files = self.get_table('Files').compute()
	
		# Find any unique test type in 'Files' table --> only need to update these tables
		for test_type in df_files['TEST_TYPE'].unique():
			logger.debug(f"Updating `{test_type}` table.")

			# Get all standardized files for this test type
			test_files = df_files.loc[
				(df_files['TEST_TYPE'] == test_type),
				['FILE_ID', 'CELL_ID', 'FILENAME']].copy()
			
			# Get table for this test type (if exists)
			try:
				with suppress_logging(level=logging.ERROR, logger_name=logger.name):
					ddf_t = self.get_table(test_type)
			except:
				ddf_t = None

			# Regenerate all files in table if reload or table doesn't exist yet 
			if reload or ddf_t is None:
				# Get all files
				if len(test_files) > 0:
					test_files['FILENAME_STANDARDIZED'] = test_files['FILENAME'].apply(lambda f: f"{Path(f).stem}.parquet")
					
					# For each row in test_files, read the file to dask dataframe and assign the file_id index
					ddfs = [dd.read_parquet(
						self._dir_storage.joinpath("standardized_raw_files", row.FILENAME_STANDARDIZED)).assign(
							FILE_ID=row.FILE_ID,
							CELL_ID=row.CELL_ID
						) for row in test_files.itertuples(index=False)]
					
					# Concatenate all DataFrames
					ddf = dd.concat(ddfs)
					reordered_keys = ['FILE_ID', 'CELL_ID'] + [k for k in ddf.columns if k not in ['FILE_ID', 'CELL_ID']]
					ddf = ddf[reordered_keys]

					# Create new table (overwrite existing)
					self.create_table(name=test_type, data=ddf, overwrite_existing=True)

					# Update summary table
					df_summary = self.get_table(f"{test_type}_Summary").compute()
					mapping = df_files[['FILE_ID', "CELL_ID"]].set_index('FILE_ID')['CELL_ID'].to_dict()
					df_summary['CELL_ID'] = df_summary['FILE_ID'].map(mapping).fillna(df_summary['CELL_ID'])
					df_summary.reset_index(drop=True, inplace=True)
					self.create_table(name=f"{test_type}_Summary", data=df_summary, overwrite_existing=True)

			# Only append missing file, don't regenerate entire table
			else:
				# Find missing FILE_IDs
				files_in_ddf = ddf_t['FILE_ID'].drop_duplicates().compute().values
				missing_test_files = test_files.loc[~test_files['FILE_ID'].isin(files_in_ddf)].copy()
		
				# Update table with missing files
				if len(missing_test_files) > 0:
					missing_test_files['FILENAME_STANDARDIZED'] = missing_test_files['FILENAME'].apply(lambda f: f"{Path(f).stem}.parquet")
					
					# For each row in missing_test_files, read the file to dask dataframe and assign the file_id index
					ddfs = [dd.read_parquet(
						self._dir_storage.joinpath("standardized_raw_files", row.FILENAME_STANDARDIZED)).assign(
							FILE_ID=row.FILE_ID,
							CELL_ID=row.CELL_ID
						) for row in missing_test_files.itertuples(index=False)]
					
					# Concatenate all DataFrames
					ddf = dd.concat(ddfs)
					reordered_keys = ['FILE_ID', 'CELL_ID'] + [k for k in ddf.columns if k not in ['FILE_ID', 'CELL_ID']]
					ddf = ddf[reordered_keys]

					# Append to existing table
					self._append_to_table(test_type, ddf)

			logger.debug(f"`{test_type}` table successfully updated.")
		
		logger.debug(f"All test-type tables have been updated.")

	def update_test_type_summary_tables(self, df_summary:pd.DataFrame):
		"""Update all test-type summary tables using the provided summary information.

		Args:
			df_summary (pd.DataFrame): A dataframe of the summary information to add. \
				Must contain the following columns: ['FILE_ID', 'TEST_TYPE']
		"""

		req_cols = ['FILE_ID', 'TEST_TYPE']
		if not set(req_cols).issubset(set(df_summary.columns)):
			raise ValueError(f"`df_summary` must contain the following columns: {req_cols}")
		
		# Any time a new file is standardized (using Dataset.add_files), a set of summary information
		# is also generated (see the utils.standardize_files function). This is passed in the form of 
		# a pandas dataframe where each row is a unique FILE_ID. The rows will extra columns for the 
		# additional summary information. Note that each test type has its own set of summary columns.
		# Therefore, we need to drop any empty columns for a given row.

		for test_type, df_t in df_summary.groupby('TEST_TYPE'):
			# Drop empty columns 	#TODO: could also drop TEST_TYPE column --> .drop(columns=['TEST_TYPE'])
			new_sum_data = df_t.dropna(axis=1, how='all') 

			# Get summary table for this test type
			ddf_summary = None
			try:
				with suppress_logging(level=logging.ERROR, logger_name=logger.name):
					ddf_summary = self.get_table(f"{test_type}_Summary")
			except:
				ddf_summary = None

			# Create new summary table for this test type
			if ddf_summary is None:
				self.create_table(f"{test_type}_Summary", new_sum_data)
			# Otherwise, append this to the existing summary table
			else:
				self._append_to_table(f"{test_type}_Summary", dd.from_pandas(new_sum_data, npartitions=1))
		
	def regroup(self, group_by:Union[str, List[str]]=None, mapping:Dict=None):
		"""Regroups cells and files based on a new set of group_by terms or an explicit mapping. 

		Args:
			group_by (Union[str, List[str]], optional): The new key(s) to use to group files belonging to the same cell (e.g., ['CHANNEL_ID', 'PROTOCOL', etc]). Defaults to None.
			mapping (Optional[dict], optional): An explicit mapping of \'FILE_ID\' to \'CELL_ID\'. Defaults to None.
		"""
		if (group_by is None) and (mapping is None):
			logger.error(f"\'group_by\' and \'mapping\' are both None.")
			raise ValueError("You must provide either new \'group_by\' terms or an explicit \'mapping\'.")
		if (not group_by is None) and (not mapping is None): 
			logger.error(f"\'group_by\' and \'mapping\' are both defined. Only one can be defined.")
			raise ValueError("Provide either a new \'group_by\' terms or an explicit \'mapping\', not both.")

		files_table = self.get_table('Files').compute().reset_index(drop=True)
		new_gb_term = 'USER DEFINED'

		# 1. Re-group all existing FILE_IDs based on new grouping terms (creates an explicit mapping)
		if mapping is None:
			new_gb_term = [group_by,] if isinstance(group_by, str) else group_by
			missing_keys = [k for k in group_by if k not in files_table.columns]
			if missing_keys:
				logger.error(f"Group_by keys ({missing_keys}) do not exist in the \'Files\' table.")
				raise ValueError(f"Group_by keys ({missing_keys}) do not exist in the \'Files\' table.  You must use a subset of the following keys: {files_table.columns}.")

			# Create mapping using new group_by terms: mapping={} (keys=existing FILE_ID, vals=new CELL_ID)
			gb = files_table.groupby(by=group_by)
			file_ids = files_table['FILE_ID'].loc[gb.ngroup().index].values
			cell_ids = gb.ngroup().values
			mapping = {int(file_ids[i]): int(cell_ids[i]) for i in range(len(file_ids))}

		# 2. Use explicit mapping (keys=existing FILE_ID, vals=new CELL_ID) to update tables
		# Ensure all FILE_IDs (only only those FILE_IDs) are defined in mapping
		valid_file_ids = files_table['FILE_ID'].values
		invalid_keys = [int(k) for k in mapping.keys() if k not in valid_file_ids]
		missing_keys = [int(k) for k in valid_file_ids if k not in mapping.keys()]
		if invalid_keys: 
			logger.error(f"Invalid FILE_IDs in mapping: {invalid_keys}.")
			raise ValueError(f"Invalid FILE_IDs in mapping: {invalid_keys}.")
		if missing_keys:
			logger.warning(f"The following FILE_IDs are missing from \'mapping\': {missing_keys}. The missing FILE_IDs will remain at the previously mapped CELL_ID.")

		# 3. Update Files table: rewrite CELL_ID and GROUP_BY columns
		files_table['CELL_ID'] = files_table['FILE_ID'].map(mapping).fillna(files_table['CELL_ID'])
		files_table.loc[files_table['FILE_ID'].isin(mapping), 'GROUP_BY'] = np.full(shape=len(mapping), fill_value=str(new_gb_term))
		files_table = files_table.sort_values('FILE_ID').reset_index(drop=True)
		self.create_table(name='Files', data=files_table, overwrite_existing=True)

		# 4. Updates Files_Summary tables: overwrite CELL_ID column
		files_table_summary = self.get_table('Files_Summary').compute()
		files_table_summary['CELL_ID'] = files_table_summary['FILE_ID'].map(mapping).fillna(files_table_summary['CELL_ID'])
		files_table_summary = files_table_summary.sort_values('FILE_ID').reset_index(drop=True)
		self.create_table(name='Files_Summary', data=files_table_summary, overwrite_existing=True)

		# 5. Update all test type tables
		self.update_test_type_tables(reload=True)

		logger.info(f"Re-mapped CELL_IDs. All tables have been regenerated.")

	def identify_table_type(self, headers:Union[str, List[str]]) -> Optional[str]:
		"""Identifies which table name the column names belong to.
		Args:
			headers (Union[str, List[str]]): A column name or list of columns names.
		Returns:
			Optional[str]: Returns the table name (str) if only one matching table exists. Else, returns None.
		"""

		matching_tables = []
		for table_name in self._tables.keys():
			ddf = self.get_table(table_name)
			# Check if all headers exist in this table
			if set(headers).issubset(set(ddf.columns)):  
				matching_tables.append(table_name)
		if len(matching_tables) > 1:
			logger.warning("Headers match multiple table. Cannot determine single-match.")
			raise ValueError("These column names match multiple tables. You will need to specify the table type.")
		elif len(matching_tables) == 0:
			return None
		else:
			return matching_tables[0]

	def get_table(self, name:str, reload:bool=False) -> dd.DataFrame:
		"""Retrieve the specified table. \n
		*Note:* The default index is the RECORD_NUMBER and thus repeats for each FILE_ID \
		(ie, **the default index is not unique**). If a unique index is needed, convert to Pandas and \
		use a multi-index with 'FILE_ID' & 'RECORD_NUMBER'. Multi-indices are not currently \
		supported in Dask. Ex: `df.set_index(['FILE_ID', 'RECORD_NUMBER'], drop=False, inplace=True)`

		Args:
			name (str): Name of table to retrieve.
			reload (optional, bool): Whether to force a reload from disk. Defaults to False.

		Returns:
			dd.DataFrame: A Dask dataframe.
		"""
		if reload:
			return self._read_table_from_disk(name)
		if name not in self._tables.keys():
			logger.error(f"Table ({name}) does not exist.")
			raise ValueError(f"Table ({name}) does not exist. Try adding it first.")
		return self._tables[name]

	def save_table(self, name:str, dir_save:Optional[Path]=None):
		"""
		Save the specified table. \n
		*Note: This regenerates all .parquet partitions and will overwrite any existing files in given \
			table directory.*

		Args:
			name (str): Name of table to save.
			dir_save (Optional[Path], optional): Optionally can specify a new save location to export \
				the table.This makes a physical copy of all .parquet files to `dir_save`. Defaults to None.
		"""

		# Get Path to where files should be saved
		if not dir_save:
			dir_save = self._dir_storage.joinpath("tables", name)
		dir_save.mkdir(exist_ok=True, parents=True)

		ddf_table = self.get_table(name)
		
		if isinstance(ddf_table, pd.DataFrame):
			filename = dask_partition_file_naming_fnc(
				partition_index=0, stem=name, file_type='parquet')
			ddf_table.to_parquet(dir_save.joinpath(filename))
		
		elif isinstance(ddf_table, dd.DataFrame):
			# Save to parquet
			ddf_table.to_parquet(
				dir_save, 
				name_function=lambda x: dask_partition_file_naming_fnc(
					partition_index=x, stem=name, file_type='parquet'
				))
			
			# Remove any old files (partition number greater than current)
			del_files = [f for f in dir_save.glob('*.parquet') \
				if dask_partition_file_naming_sort_fnc(f) > ddf_table.npartitions-1]
			for f in del_files: os.remove(f)
		
		self._tables[name] = self._read_table_from_disk(name)
		logger.debug(f"Updated cache for the \'{name}\' table. Saved to: {(dir_save)}.")

	def export(self, dir_save:Path, overwrite:bool=False):
		"""Export all TableManager data (and standardized files) to `dir_save`

		Args:
			dir_save (Path): Directory to export TableManager to. Defaults to None.
			overwrite (bool, optional): If True, overwrites an existing copy at `dir_save`. Defaults to False.
		"""

		# Create main folder to export Dataset
		dir_export = dir_save.joinpath(self._dir_storage.name)

		if dir_export.exists():
			if overwrite:
				shutil.rmtree(dir_export)
				dir_export.mkdir(exist_ok=False, parents=True)
			else:
				logger.error(f"Dataset already exists at {dir_export}")
				raise FileExistsError("Dataset already exists at this location. Set `overwrite` to True if you want to replace it.")
		dir_export.mkdir(exist_ok=True, parents=True)

		# Export all tables as parquet files
		for t_name in self._tables.keys():
			dir_table = dir_export.joinpath('tables', t_name)
			dir_table.mkdir(exist_ok=True, parents=True)
			self.save_table(t_name, dir_table)
		
		# Export all standardized data
		if self._dir_storage.joinpath("standardized_raw_files").is_dir():
			shutil.copytree(
				src=self._dir_storage.joinpath("standardized_raw_files"),
				dst=dir_export.joinpath("standardized_raw_files"))
		
	def _append_to_table(self, name:str, ddf:dd.DataFrame):
		"""
		Appends a new Dask DataFrame to an existing table.\n
		*Note: This does not repartition the existing table. It simply create new partitions \
		with the additional data. Use `get_table(reload=True)` to fully regenerate the data.*

		Args:
			name (str): Name of table to append to
			ddf (dd.DataFrame): New Dask DataFrame to append.
		"""

		# Get table path
		dir_table = self._dir_storage.joinpath("tables", name)
		
		# If table doesn't exist, create new one
		if not dir_table.exists():
			logger.warning("No existing table was found. Creating a new one.")
			self.create_table(name, ddf)
			return
		
		# Get last index of previous .parquet file
		next_partition_index = int(
			np.max([
				get_dask_partition_from_file_name(f) 
		   		for f in dir_table.glob('*') 
				if f.name.startswith(f'{name}')
			])) + 1

		# Save new subset
		ddf.to_parquet(
			dir_table, 
			name_function=lambda x: dask_partition_file_naming_fnc(
				partition_index=x+next_partition_index, stem=name, file_type='parquet'
			))
		
		# Update in-memory table reference (we are not doing a full re-partition)
		self._tables[name] = dd.concat([self._tables[name], ddf])



	def _repartition(self, name:str=None, partition_size=MAX_PARTITION_SIZE):
		"""Repartitions the specified table (or all tables if `name=None`)."""
		
		names = None
		if name is None: 
			names = self.available_tables
		elif name in self.available_tables:
			names = [name]
		else:
			raise ValueError(f"There is no table named `{name}`.")

		for table_name in names:
			ddf = self.get_table(table_name)

			# Compute ideal number of partitions
			est_size_bytes = ddf.memory_usage(deep=True).sum().compute()
			target_size_bytes = MAX_PARTITION_SIZE * 1e6  # MB --> bytes
			desired_parts = max(1, int(est_size_bytes / target_size_bytes))

			# Repartition and save
			ddf = ddf.repartition(npartitions=desired_parts)
			self._tables[table_name] = ddf
			self.save_table(table_name)


	def _read_table_from_disk(self, name:str) -> dd.DataFrame:
		"""Generate a Dask DataFrame for the given table from the .parquet files on disk."""

		dir_table = self._dir_storage.joinpath("tables", name)
		if not dir_table.exists():
			raise ValueError(f"There is no saved data available for the `{name}` table: {dir_table}")
		logger.debug(f"Reading `{name}` table from disk.")
		return dd.read_parquet(dir_table)

	def _load_existing(self):
		"""Load existing TableManager data."""

		# 1. Check that all files exist 
		dir_raw_files = self._dir_storage.joinpath("standardized_raw_files")
		raw_file_stems = [f.stem for f in dir_raw_files.glob('*.parquet')]
		logger.debug(f"Found {len(raw_file_stems)} standardized files.")

		# 2. Load all tables and check for missing file_ids. Missing files include:
		# 	2a. any FILE_IDs in 'Files' table that do not have a matching standardized data file
		#	2b. any FILE_IDs in other tables that don't exist in 'Files' table
		dir_tables = self._dir_storage.joinpath("tables")
		existing_tables = [f for f in dir_tables.glob('*') if f.is_dir()]
		logger.debug(f"Found existing tables: {[f.name for f in existing_tables]}")

		valid_file_ids = []
		num_missing_files = 0
		# 2a. Filter 'Files' table
		if 'Files' in [f.name for f in existing_tables]:
			df_files = self.get_table('Files', reload=True).compute()

			# Filter 'Files' table to only include files with existing standardized data
			new_df_files = df_files.loc[df_files['FILENAME'].apply(
				lambda f: Path(f).stem in raw_file_stems)]
			num_missing_files = len(df_files) - len(new_df_files)
			self._tables['Files'] = dd.from_pandas(new_df_files, npartitions=1)
			self.save_table('Files')
			logger.debug(f"Updated `Files` table. {num_missing_files} missing files detected.")

			# Record valid FILE_IDs
			valid_file_ids.extend(df_files['FILE_ID'].unique())

		# 2b. Filter all other tables
		for dir_t in [f for f in dir_tables.glob('*') if f.is_dir() and not f.name == 'Files']:
			table_name = dir_t.name
			ddf_table = self.get_table(table_name, reload=True)
			self._tables[table_name] = ddf_table
			logger.debug(f"Updated `{table_name}` table.")

			# Only filter table if files are missing
			if num_missing_files > 0:
				self._tables[table_name] = ddf_table.loc[ddf_table['FILE_ID'].isin(valid_file_ids)]
				self.save_table(table_name)
				logger.debug(f"Removed {num_missing_files} missing files from `{table_name}` table.")

		# 3. Re-number all FILE_IDs so there are no gaps
		if (num_missing_files > 0) or not (np.max(valid_file_ids) == len(valid_file_ids) - 1):
			id_map = {old_id:new_id for new_id,old_id in enumerate(valid_file_ids)}
			for table_name, ddf_table in self._tables.items():
				ddf_table = ddf_table.assign(
					FILE_ID=ddf_table['FILE_ID'].map(
						id_map,
						meta=('FILE_ID', 'int64')
					).astype('int64')
				)
				
				self._tables[table_name] = ddf_table
				self.save_table(table_name)
				logger.debug(f"Re-mapped FILE_IDs in `{table_name}` table.")


		# #region: check for any inconsistencies in Files table vs standardized files
		# #	- If interrupted during add_files, there may be files defined in Files that \
		# # 		were not standardized.
		# df_files = self.get_table('Files').compute()
		# # files_table_stems = [Path(f).stem for f in df_files['FILENAME'].unique()]
		# raw_file_stems = [f.stem for f in dir_raw_files.glob('*.parquet')]
		# missing_file_ids = df_files.loc[
		# 	~df_files['FILENAME'].apply(
		# 		lambda f: 
		# 		Path(f).stem in raw_file_stems
		# 	),
		# 	'FILE_ID'].unique()
		
		# # If there are missing FILE_IDs, we need to:
		# #	1. Remove data corresponding to that FILE_ID from all tables
		# #	2. Re-index all FILE_IDs so that there are no gaps in FILE_ID
		# if len(missing_file_ids) > 0:
		# 	logger.warning(f"`Files` table contains missing standardized data. These files are being dropped. Run `add_files` again.")

		# print(missing_file_ids)
		# raise RuntimeError
		# # missing_file_stems = [
		# # 	stem for stem in files_table_stems
		# # 	if not stem in raw_file_stems
		# # ]
		# # if len(missing_file_stems) > 0:
		# # 	logger.warning(f"`Files` tables contains missing standardized data. These files are being dropped. Run `add_files` again.")
		# # 	# Remove entries from Files table
		# # 	df_files = df_files[~df_files['FILENAME'].apply(lambda f: Path(f).stem in missing_file_stems)]
		# # 	# Save updated Files table
		# # 	self.create_table("Files", df_files, overwrite_existing=True)
		# # 	logger.warning(f"Removed {len(missing_file_stems)} entries from `Files` table and re-saved cleaned table.")
		
		# if len(missing_file_ids) > 0:
		# 	logger.warning(f"`Files` tables contains missing standardized data. These files are being dropped. Run `add_files` again.")

		# 	print(missing_file_ids)
		# 	raise RuntimeError
		# 	# Remove entries from Files table
		# 	df_files = df_files[~df_files['FILENAME'].apply(lambda f: Path(f).stem in missing_file_ids)]

		# 	# Save updated Files table
		# 	self.create_table("Files", df_files, overwrite_existing=True)

		# 	logger.warning(f"Removed {len(missing_file_ids)} entries from `Files` table and re-saved cleaned table.")
		
		
		# #endregion

		# self.update_test_type_tables()
