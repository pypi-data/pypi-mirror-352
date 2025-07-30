
from typing import List
from pathlib import Path
import re, sxl, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import warnings
from datetime import datetime
import NewareNDA

from battkit.logging_config import logger
from battkit.data.data_converter import DataConverter
from battkit.data.test_schema import load_test_schema
from battkit.utils.file_utils import get_xlsx_sheet_ids

class NewareDataConverter(DataConverter):

	# Use class variables and @staticmethod decorator to allow for efficient parallelization
	name = "Neware"
	file_types = ['.xlsx', '.ndax', '.nda']
	default_group_by = {
		"TESTER_ID":int, 
		"UNIT_ID":int,
		"CHANNEL_ID":int, 
	}

	def __init__(self):
		super().__init__(NewareDataConverter.name, NewareDataConverter.file_types)

	## REQUIRED METHOD DEFINITIONS ##
	@staticmethod
	def define_schema() -> dict:
		return {
			"TEST_TYPE":str,
			"TESTER_ID":int, 
			"UNIT_ID":int,
			"CHANNEL_ID":int, 
			"PROTOCOL":str, 
			"FILENAME":str,
			"DATETIME_START":datetime,
			"DATETIME_END":datetime,
		}

	@classmethod
	def validate_file_type(cls, file:Path) -> bool:
		"""Checks whether the provided file uses a file type supported by this DataConverter"""
		if file.suffix not in cls.file_types:
			logger.error(f"Validation failed. File type ({file.suffix}) is not supported by {cls.name}.")
			return False
		logger.debug(f"Validation successful. File type ({file.suffix}) is supported by {cls.name}.")
		return True

	@classmethod
	def validate_converter(cls, file:Path):
		# Check whether this file matches the Neware tester format 
		# Perform checks sorted by operation execution time (ie, check file suffix first, 
		# then sheet names is Excel file, etc)
		# Want to read the least amount of information necessary to determine if the file 
		# matches the Neware format

		# 1. Check that the file type is supported
		if not cls.validate_file_type(file):
			return False
		
		# 2. For xlsx files, check formatting
		if file.suffix.lower() == '.xlsx':
			sheet_names = get_xlsx_sheet_ids(file)
			if 'Info' not in sheet_names: 
				logger.error(f"Validation failed. Excel file is missing required {cls.name} sheet name (\'Info\').")
				return False
			
			# The 'Info' sheet has several fixed cell values, those are checked below
			info_fmt = sxl.Workbook(file).sheets['Info'].rows[7][0]
			expected_fmt = ['device', 'Unit', 'Channel', 'P/N', 'Step file', 'Starting time', 'End time', 'Sorting files', 'Class', 'Remarks']
			if not info_fmt == expected_fmt:
				logger.error(f"Validation failed. \'Info\' sheet does not match {cls.name} format.")
				return False
			
		# 3. For .nda or .ndax files, this is by default a Neware file
		elif file.suffix.lower() in ['.nda', '.ndax']:
			return True

		# 4. Other formats not yet supported
		else:
			logger.error(f"Validation failed. File type ({file.suffix}) is supported but not yet implemented.")
			return False

		logger.debug(f"Validation successful. File matches the {cls.name} format.")
		return True
	
	@classmethod
	def extract_group_by_data(cls, file:Path) -> dict:
		grouping_data = {k:None for k in cls().group_by_schema}
		
		if file.suffix.lower() == '.xlsx':
			grouping_data["TEST_TYPE"] = "TimeSeries"			# TODO: assuming all Neware data is TimeSeries (do they have EIS?)
			# Extract grouping data from this file
			data = sxl.Workbook(file).sheets['Info'].rows[8][0]
			grouping_data["TESTER_ID"] = int(data[0])
			grouping_data["UNIT_ID"] = int(data[1])
			grouping_data["CHANNEL_ID"] = int(data[2])
			grouping_data["PROTOCOL"] = str(data[4])
			grouping_data["FILENAME"] = file.name
			grouping_data["DATETIME_START"] = datetime.strptime(str(data[5]), "%Y-%m-%d %H:%M:%S")
			grouping_data["DATETIME_END"] = datetime.strptime(str(data[6]), "%Y-%m-%d %H:%M:%S")
			
		elif file.suffix.lower() in ['.nda', '.ndax']:
			grouping_data["TEST_TYPE"] = "TimeSeries"			# TODO: assuming all Neware data is TimeSeries (do they have EIS?)
			# Extract grouping data from this file
			with tempfile.TemporaryDirectory() as tmpdir:
				zf = zipfile.PyZipFile(file)
				test_info = zf.extract('TestInfo.xml', path=tmpdir)
				with open(test_info, 'r', encoding='gb2312') as f:
					et_test_info = ET.fromstring(f.read()).find(".//TestInfo")
					# Extract desired attributes
					fields = ["DevType", "DevID", "UnitID", "ChlID", "TestID", "StepName", "StartTime", "EndTime"]
					extracted = {field: et_test_info.attrib.get(field) for field in fields}

					grouping_data["TESTER_ID"] = int(extracted['DevID'])
					grouping_data["UNIT_ID"] = int(extracted['UnitID'])
					grouping_data["CHANNEL_ID"] = int(extracted['ChlID'])
					grouping_data["PROTOCOL"] = str(extracted['StepName'])
					grouping_data["FILENAME"] = file.name
					grouping_data["DATETIME_START"] = datetime.strptime(str(extracted['StartTime']), "%Y-%m-%d %H:%M:%S")
					grouping_data["DATETIME_END"] = datetime.strptime(str(extracted['EndTime']), "%Y-%m-%d %H:%M:%S")

		else:
			logger.error(f"File type ({file.suffix}) not currently supported.")
			raise TypeError(f"File type ({file.suffix}) not currently supported.")
		
		# Check if there are supported group_by terms that have no values
		missing_groups = [k for k,v in grouping_data.items() if v is None]
		if missing_groups:
			logger.debug(f"Following group_by terms are missing values: {missing_groups}")

		logger.debug(f"Group_by data extracted successfully.")
		return grouping_data
	
	@classmethod
	def extract_timeseries_data(cls, file:Path) -> pd.DataFrame:
		# Check file validation
		if not cls.validate_converter(file):
			raise ValueError(f"Validation failed for the {cls.name} DataConverter.")
		
		# Create dataframe to return using required columns from 
		schema = load_test_schema('TimeSeries')
		df_to_return = pd.DataFrame(columns=schema.req_schema.keys())

		# Format time-series data for each supported file type
		# For .xlsx files
		if file.suffix.lower() == '.xlsx':
			sheet_names = np.asarray(get_xlsx_sheet_ids(file))

			df = None
			#region: load details sheet
			sheet_name_details = sheet_names[np.where(np.char.find(sheet_names, 'Detail_') == 0)]
			assert len(sheet_name_details) == 1
			with warnings.catch_warnings():
				warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
				df = pd.read_excel(file, sheet_name=sheet_name_details[0], engine='openpyxl')
				df.rename(columns={'Date(h:min:s.ms)':'Date'}, inplace=True)
			#endregion

			#region: if has temperature information in separate sheet, merge sheets
			sheet_name_temp = sheet_names[np.where(np.char.find(sheet_names, 'DetailTemp_') == 0)]
			if len(sheet_name_temp) == 1:
				with warnings.catch_warnings():
					warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
					df_temp = pd.read_excel(file, sheet_name=sheet_name_temp[0], engine='openpyxl')
				df_temp.drop(columns=['Record number', 'Relative Time(h:min:s.ms)'], inplace=True)
				df_temp.rename(columns={'Aux.CH TU1 T(°C)':'Temperature'}, inplace=True)
				# merge temperature and fill any gaps with linear interpolation
				df = pd.merge(left=df, right=df_temp, how='inner', on=['Date', 'State'])
				df['Temperature'] = df['Temperature'].interpolate(method='linear', inplace=False)
				df.drop_duplicates(subset='Record number', inplace=True, ignore_index=True)
			#endregion
			
			df_to_return['RECORD_NUMBER'] = df['Record number'].astype(int).values
			df_to_return['CYCLE_NUMBER'] = df['Cycle'].astype(int).values
			df_to_return['STEP_NUMBER'] = df['Steps'].astype(int).values
			df_to_return['STEP_MODE'] = df['State'].str.upper().values

			#region: get units of voltage, current, and capacity columns
			headers = cls.extract_data_headers(file)
			v_key = headers[np.argwhere(np.char.find(headers, 'Voltage') == 0)[0][0]]
			v_modifier = 1 if (v_key.rfind('mV') == -1) else (1/1000)
			i_key = headers[np.argwhere(np.char.find(headers, 'Current') == 0)[0][0]]
			i_modifier = 1 if (i_key.rfind('mA') == -1) else (1/1000)
			q_key = headers[np.argwhere(np.char.find(headers, 'Capacity') == 0)[0][0]]
			q_modifier = 1 if (q_key.rfind('mAh') == -1) else (1/1000)
			#endregion
			
			df_to_return['VOLTAGE_V'] = df[v_key].astype(float).values * v_modifier
			df_to_return['CURRENT_A'] = df[i_key].astype(float).values * i_modifier

			# calculate the sign of current (-1 if DCHG step)
			signs = np.asarray([-1 if 'DCHG' in step_mode else 1 for step_mode in df_to_return['STEP_MODE'].values])
			df_to_return['STEP_CAPACITY_AH'] = df[q_key].astype(float).values * q_modifier * signs

			#region: calculate cumulative capacity
			# dqs = np.zeros(len(df_to_return['STEP_CAPACITY(AH)']), dtype=float)
			# for step_num in df_to_return['STEP NUMBER'].unique():
			# 	df_step = df_to_return.loc[(df_to_return['STEP_NUMBER'] == step_num)]
			# 	idxs = df_step.index.values
			# 	assert len(df_step['STEP MODE'].unique()) == 1
			# 	sign = -1 if 'DChg' in df_step['STEP MODE'].unique()[0] else 1
			# 	dqs[idxs[1:]] = df_step['STEP CAPACITY (AH)'].diff().values[1:] * sign
			# 	dqs[idxs[0]] = 0
			# q_cum = np.cumsum(dqs)
			# df_to_return['PROTOCOL_CAPACITY(AH)'] = q_cum.astype(float)
			#endregion

			#region: calculate time
			step_time = pd.to_timedelta(df['Relative Time(h:min:s.ms)'])
			rel_seconds = step_time.dt.total_seconds().values	# step times in seconds (resets to 0 for each new step) 
			d_seconds = np.hstack([0, np.diff(rel_seconds)])	# ensures each step starts at 0 seconds
			d_seconds[np.where(d_seconds < 0)] = 0
			cum_seconds = np.cumsum(d_seconds)					# cumulative time (ie, protocol time)
			df_to_return['TIME_S'] = cum_seconds.astype(float)
			# # convert total time to TIMESTAMP format
			# start_date = pd.to_datetime(df['Date'], format=r"%Y-%m-%d %H:%M:%S").values[0]
			# timestamps = (start_date + pd.to_timedelta(cum_seconds, unit='second')).strftime(r"%Y-%m-%d %H:%M:%S.%f")
			# df_to_return['TIMESTAMP'] = timestamps
			#endregion
			
			#region: add any optional parameters
			if 'Temperature' in df.columns:
				df_to_return['CELL_TEMPERATURE_C'] = df['Temperature'].astype(float).values
			#endregion

		elif file.suffix.lower() in ['.nda', '.ndax']:
			df = NewareNDA.read(str(file), log_level='ERROR')

			#region: combine separate charge and dsicharge capacity columns into one
			try:
				headers = list(df.columns)
				q_chg_key = headers[np.argwhere(np.char.find(headers, 'Charge_Capacity') == 0)[0][0]]
				q_chg_unit = q_chg_key[q_chg_key.rindex('Charge_Capacity') + len('Charge_Capacity'):]
				q_dchg_key = headers[np.argwhere(np.char.find(headers, 'Discharge_Capacity') == 0)[0][0]]
				q_dchg_unit = q_dchg_key[q_dchg_key.rindex('Discharge_Capacity') + len('Discharge_Capacity'):]
				
				#region: ensure charge and discharge capacities in same units
				dchg_modifier = 1
				# if chg in Ah and dchg in mAh: multiply dchg by 1000
				if (q_chg_unit.rfind('mAh') == -1) and (q_dchg_unit.rfind('mAh') != -1):
					dchg_modifier = 1000
				# if chg in mAh and dchg in Ah: multiple dchg by 1/1000
				elif (q_chg_unit.rfind('mAh') != -1) and (q_dchg_unit.rfind('mAh') == -1):
					dchg_modifier = 1/1000
				df[q_dchg_key] *= dchg_modifier
				# df = df.rename(columns={q_dchg_key: f'Discharge_Capacity{q_chg_unit}'})
				#endregion

				#region: combine charge and discharge capacities into a single columns
				mask = (df[q_chg_key] != 0) & (df[q_dchg_key] != 0)
				if mask.any(): raise ValueError("Found non-zero entries for both charge and discharge capacity.")
				df[f'Capacity{q_chg_unit}'] = df[q_chg_key].where(df[q_chg_key] != 0, df[q_dchg_key]).clip(lower=0)
				#endregion
			except:
				raise ValueError(f"Unexpected columns found in file: {headers}")
			#endregion

			#region: get units of voltage, current, and capacity columns
			headers = list(df.columns)
			v_key = headers[np.argwhere(np.char.find(headers, 'Voltage') == 0)[0][0]]
			v_modifier = 1 if (v_key.rfind('mV') == -1) else (1/1000)
			i_key = headers[np.argwhere(np.char.find(headers, 'Current') == 0)[0][0]]
			i_modifier = 1 if (i_key.rfind('mA') == -1) else (1/1000)
			q_key = headers[np.argwhere(np.char.find(headers, 'Capacity') == 0)[0][0]]
			q_modifier = 1 if (q_key.rfind('mAh') == -1) else (1/1000)
			#endregion

			df_to_return['RECORD_NUMBER'] = df['Index'].astype(int).values
			df_to_return['CYCLE_NUMBER'] = df['Cycle'].astype(int).values
			df_to_return['STEP_NUMBER'] = df['Step'].astype(int).values
			df_to_return['STEP_MODE'] = df['Status'].str.replace('_', ' ', regex=False).str.upper().values

			df_to_return['VOLTAGE_V'] = df[v_key].astype(float).values * v_modifier
			df_to_return['CURRENT_A'] = df[i_key].astype(float).values * i_modifier

			# calculate the sign of current (-1 if DCHG step)
			signs = np.asarray([-1 if 'DCHG' in step_mode else 1 for step_mode in df_to_return['STEP_MODE'].values])
			df_to_return['STEP_CAPACITY_AH'] = df[q_key].astype(float).values * q_modifier * signs

			#region: calculate time
			df['Timestamp'] = pd.to_datetime(df['Timestamp'])
			df_to_return['TIME_S'] = pd.to_timedelta(df['Timestamp'] - df['Timestamp'].iloc[0]).apply(lambda t: t.total_seconds()).astype(float)
			#endregion

			#region: add any optional parameters
			if 'T1' in df.columns:
				df_to_return['CELL_TEMPERATURE_C'] = df['T1'].astype(float).values
			#endregion

		else:
			logger.error(f"Time-series extraction failed. File type ({file.suffix}) is supported but not yet implemented.")
			raise ValueError(f"Time-series extraction failed. File type ({file.suffix}) is supported but not yet implemented.")

		#region: validate schema
		if not schema.validate_data({col: df_to_return[col].dtype for col in df_to_return.columns}):
			raise TypeError("Validation failed. Extracted time-series data does not match expected schema.")
		
		if not schema.validate_step_mode(df_to_return['STEP_MODE'].unique()):
			raise TypeError("Validation failed. Steps modes contain unsupported values.")
		#endregion

		return df_to_return

	## HELPER METHODS ##
	@classmethod
	def extract_data_headers(cls, file:Path) -> List[str]:
		"""Extracts the headers of the data contained in the file."""

		sheet_names = get_xlsx_sheet_ids(file)
		sheet_name_details = sheet_names[np.where(np.char.find(sheet_names, 'Detail_') == 0)[0][0]]

		headers = sxl.Workbook(file).sheets[sheet_name_details].rows[1][0]
		return headers
	