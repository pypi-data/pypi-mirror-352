
import os, time
from pathlib import Path
from typing import List, Optional
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial, wraps
from tqdm.auto import tqdm


from battkit.logging_config import logger
from battkit.data.data_converter import load_data_converter, DATA_CONVERTER_REGISTRY
from battkit.data.test_schema import load_test_schema, TEST_SCHEMA_REGISTRY

from functools import wraps


def safe_process(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			return {
				"error": str(e),
				"args": args,
				"kwargs": kwargs
			}
	return wrapper

@safe_process
def _extract_file_grouping_helper(file:Path, data_converter:str):
		converter = load_data_converter(data_converter)
		try:
			gb = converter.extract_group_by_data(file)
			if gb is None or len(gb) == 0:
				return {}
			gb['FILEPATH'] = str(file)
			gb['DATA_CONVERTER'] = data_converter
			return gb
		except Exception as e:
			logger.error(f"Error processing file {file}: {e}")
			raise e  # Reraise to propagate the error

@safe_process
def _standardize_files_helper(file:Path, data_converter:str, test_type:str, file_id:int, cell_id:int):
		converter = load_data_converter(data_converter)
		try:
			df = None
			if test_type == 'TimeSeries':
				df = converter.extract_timeseries_data(file)
			elif test_type == 'Frequency':
				df = converter.extract_frequency_data(file)
			else:
				logger.error(f"Test type ({test_type}) is not supported by {data_converter}.")
				raise ValueError(f"Test type ({test_type}) is not supported.")
			return df, file, test_type, file_id, cell_id
		except Exception as e:
			logger.error(f"Error processing {test_type} data from file {file}: {e}")
			raise e



def infer_data_converter(file:Path) -> str:
	"""Returns the name of the inferred DataConverter subclass. Inferred from the DATA_CONVERTER_REGISTRY."""
	valid_data_converters = []
	for dc_name in DATA_CONVERTER_REGISTRY:
		data_converter = load_data_converter(dc_name)
		if data_converter.validate_converter(file):
			valid_data_converters.append(dc_name)

	if not valid_data_converters:
		logger.error("Failed to find a suitable data converter.")
		raise RuntimeError("Failed to find a suitable data converter. Please manually specify one")

	elif len(valid_data_converters) > 1:
		logger.warning(f"Multiple valid data converters were detected. The first one will be used ({valid_data_converters[0]}).")

	return valid_data_converters[0]

def extract_file_grouping(file_list:List[Path], next_file_id:int, data_converter:str, group_by:Optional[List[str]]=None, n_jobs:int=-1, tqdm_pbar=None) -> pd.DataFrame:
	"""Extracts the meta data from all files in `file_list` and groups based on `group_by`

	Args:
		file_list (List[Path]): A list of Path objects.
		next_file_id (int): The next available file ID to assign to these files.
		data_converter (str): The name of a registered data converter.
		group_by (Optional[List[str]], optional): The key(s) to use to group files belonging to the 
			same cell (e.g., ['CHANNEL_ID']). If not specified, defaults keys defined by the 
			`data_converter` will be used. Defaults to None.
		n_jobs (int, optional): Number of parallel tasks. Defaults to -1 (as many as possible).
		tqdm_pbar (optional): Reference to tqdm progress bar. Defaults to None.

	Returns:
		pd.DataFrame: A dataframe of meta data extracted from each file.
	"""
	if n_jobs == -1: n_jobs = os.cpu_count()

	def _progress_wrapped_iterator(iterable, total):
		"""Internal: wrap the iterator and update an external tqdm bar (if provided)."""
		for item in iterable:
			yield item
			if tqdm_pbar is not None:
				tqdm_pbar.update(1)

	# 1. Process meta data from all files
	start_time = time.time()
	meta_list = None
	with ProcessPoolExecutor(max_workers=n_jobs) as executor:
		results = executor.map(
			partial(_extract_file_grouping_helper, data_converter=data_converter),
			file_list
		)
		if tqdm_pbar is not None:
			meta_list = list(_progress_wrapped_iterator(results, total=len(file_list)))
		else:
			meta_list = list(tqdm(results, total=len(file_list), desc="Extracting meta-data"))
	
	logger.info(f"Extracted meta-data from {len(file_list)} files in {round(time.time()-start_time, 4)} seconds.")
	df_meta = pd.DataFrame(meta_list).dropna(axis=0, how='all')		# drop any empty rows
	
	# 2. Group meta data by specified or default cols
	converter = load_data_converter(data_converter)
	if group_by is None:
		group_by = list(converter.default_group_by.keys())

	if not set(group_by).issubset(list(df_meta.columns)):
		raise ValueError(f"Missing group_by keys: {set(group_by) - set(list(df_meta.columns))}")

	# 3. Assign CELL_ID (and store group_by values for traceability) 
	df_meta['CELL_ID'] = df_meta.groupby(group_by).ngroup().fillna(0)
	df_meta['GROUP_BY'] = np.full(len(df_meta), fill_value=str(group_by))

	# 4. Assign FILE_ID
	df_meta = df_meta.sort_values(["CELL_ID",] + group_by).reset_index(drop=True)
	df_meta.index.name = 'FILE_ID'
	df_meta.reset_index(inplace=True)
	df_meta['FILE_ID'] += next_file_id

	# 5. Remove file extension from filename
	df_meta['FILENAME'] = df_meta['FILENAME'].apply(lambda x: Path(x).stem)
	
	return df_meta

def standardize_files(df_files:pd.DataFrame, data_converter:str, dir_save:Path, n_jobs:int=-1, tqdm_pbar=None) -> pd.DataFrame:
	"""
	Standardizes all files defined in the `df_files` dataframe. Processed files will be saved to \
	`dir_save` with the .parquet extension.

	Args:
		df_files (pd.DataFrame): A dataframe containing new files to process and their meta data.
		data_converter (str): The name of a registered data converter.
		dir_save (Path): The directory where all processed data should be saved.
		n_jobs (int, optional): Number of parallel tasks. Defaults to -1 (as many as possible).
		tqdm_pbar (optional): Reference to tqdm progress bar. Defaults to None.

	Returns:
		pd.DataFrame: A dataframe of the FILE_ID, TEST_TYPE, and summary information
	"""

	if n_jobs == -1: n_jobs = os.cpu_count()
	
	dir_standardized = dir_save.joinpath("standardized_raw_files")
	dir_standardized.mkdir(parents=True, exist_ok=True)

	# 1. Standardize all raw files and temporarily resave (stored as {dir_storage}/FILENAME.parquet)
	summary_results = []
	start_time = time.time()
	with ProcessPoolExecutor(max_workers=n_jobs) as executor:
		# 1a. Construct list of tasks
		futures = []
		for i in range(len(df_files)):
			file_id = df_files.iloc[i]['FILE_ID']
			cell_id = df_files.iloc[i]['CELL_ID']
			file = Path(df_files.iloc[i]['FILEPATH'])
			test_type = df_files.iloc[i]['TEST_TYPE']

			futures.append( 
				executor.submit(
					_standardize_files_helper, 
					file=file,
					data_converter=data_converter,
					test_type=test_type,
					file_id=file_id,
					cell_id=cell_id,
				)
			)
		
		# 1b. Execute tasks in parallel
		if tqdm_pbar is None:
			tqdm_pbar = tqdm(total=len(futures), desc="Standardizing files")
		for future in as_completed(futures):
			df, file, test_type, file_id, cell_id = future.result()
			if df is None or df.empty:
				logger.warning(f"Failed to extract data from file: {file}. File has been skipped.")
				continue
			filename = f"{file.stem}.parquet"
			save_path = dir_standardized.joinpath(filename)
			df.to_parquet(save_path)
			logger.debug(f"Successfully processed `{test_type}` data from {(filename)}: {(save_path)}")

			test_schema = load_test_schema(test_type)
			res = test_schema.generate_summary(df)

			res['FILE_ID'] = file_id
			res['CELL_ID'] = cell_id
			res['TEST_TYPE'] = test_type
			summary_results.append(res)
			logger.debug(f"Successfully processed summary data from {(filename)}.")

			tqdm_pbar.update(1)

	logger.info(f"Extracted data from {len(df_files)} files in {round(time.time()-start_time, 4)} seconds.")

	df_summary = pd.DataFrame(summary_results)
	return df_summary


