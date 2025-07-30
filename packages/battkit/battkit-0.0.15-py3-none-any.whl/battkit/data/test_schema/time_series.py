

from typing import Dict, Type, List
import pandas as pd
import numpy as np

from battkit.logging_config import logger
from battkit.data.test_schema import TestSchema


class TimeSeriesSchema(TestSchema):
	test_name = 'TimeSeries'
	step_modes = [
		'CC CHG', 'CV CHG', 'CCCV CHG', 'CC DCHG', 'CV DCHG', 'CCCV DCHG',
		'CP CHG', 'CP DCHG', 'CR DCHG', 'REST',
		'UNDEFINED'
	]

	required_schema = {
		'RECORD_NUMBER':int, 				# unique for each sampled point (natural number)
		'TIME_S':float,                		# test time (in seconds)
		'CYCLE_NUMBER':int,          		# unique for each cycle number in protocol (natural number)
		'STEP_NUMBER':int, 					# unique for each step number in protocol (natural number)
		'STEP_MODE':str,					# see supported step modes below
		'VOLTAGE_V':float,					# cell voltage (in volts)
		'CURRENT_A':float,					# applied current (positive if charge step, negative if discharge step)
		'STEP_CAPACITY_AH':float,			# cumulative capacity since start of step number (can be negative)
	}
	optional_schema = {
		'CELL_TEMPERATURE_C':float,			# cell temperature (in deg C)
		'AMBIENT_TEMPERATURE_C':float, 		# ambient temperature (in deg C)
	}
	summary_schema = {
		'NUM_CYCLES':int,					# number of cycles performed
		'CAPACITY_CYCLE_DELTA_MAX_AH': float,	# max current throughput in a single cycle
		'CURRENT_MAX_A': float,				# max charge current 
		'CURRENT_MIN_A': float,				# min charge current 
		'CURRENT_THROUGHPUT_AH': float,		# total current throughput 
		'VOLTAGE_MAX_V': float,				# max voltage 
		'VOLTAGE_MIN_V': float,				# min voltage 
	}

	def __init__(self):
		super().__init__(self.test_name, self.required_schema, self.optional_schema, self.summary_schema)

	
	def validate_step_mode(self, step_modes:List[str]):
		invalid_modes = [m for m in step_modes if m not in self.step_modes]

		if invalid_modes:
			logger.error(f"Data validation failed. Invalid step modes found: {invalid_modes}")
		else:
			logger.info(f"Step mode validation successful.")
			return True
		
		return False
	
	def validate_data(self, data_schema:Dict[str, Type]) -> bool:
		# This subclass method allows for custom validation to be performed in addition to 
		# the direct schema validation that is performed in super()._validate_data() 
		if not super()._validate_data(data_schema): 
			return False
		
		return True
	
	def generate_summary(self, df_file:pd.DataFrame) -> dict:
		"""Generates summary informtion from a time-series dataframe. Must contain the following columns: \
			[CYCLE_NUMBER, STEP_NUMBER, STEP_MODE, VOLTAGE_V, CURRENT_A, STEP_CAPACITY_AH]"""
		if not self.validate_data({col: df_file[col].dtype for col in df_file.columns}):
			raise TypeError(f"Summary generation failed. Data does not match expected time-series schema.")

		if not 'FILE_ID' in df_file.columns:
			logger.info(f"The current data has no FILE_ID column. Only a single summary instance will be returned.")
			df_file['FILE_ID'] = -1
		elif df_file['FILE_ID'].unique() > 1:
			logger.warning(f"The current data contains multiple files. Only a single summary instance will be returned.")

		#region: calculate [NUM_CYCLES, CURRENT_MAX_A, CURRENT_MIN_A, VOLTAGE_MAX_V, VOLTAGE_MIN_V]
		agg_df = df_file.groupby('FILE_ID').agg({
			'CYCLE_NUMBER': 'max',
			'CURRENT_A': ['max', 'min'],
			'VOLTAGE_V': ['max', 'min']
		})
		# Flatten multi-index columns
		agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
		
		# Extract stats
		num_cycles = agg_df['CYCLE_NUMBER_max'].sum()
		current_max = agg_df['CURRENT_A_max'].max()
		current_min = agg_df['CURRENT_A_min'].min()
		voltage_max = agg_df['VOLTAGE_V_max'].max()
		voltage_min = agg_df['VOLTAGE_V_min'].min()
		#endregion

		#region: calculate [CURRENT_THROUGHPUT_AH, CAPACITY_CYCLE_DELTA_MAX_AH]
		q_throughput = 0
		q_delta_max = 0
		q_steps = [0]
		for _, df_gb in df_file.groupby(['CYCLE_NUMBER', 'STEP_NUMBER', 'STEP_MODE']):
			last_capacity = df_gb['STEP_CAPACITY_AH'].values[-1]
			q_steps.append(last_capacity)
			q_throughput += df_gb['STEP_CAPACITY_AH'].abs().max()

		# Record maximum difference in cumulative capacity
		q_cum = np.cumsum(q_steps)
		q_delta_max = max(q_cum) - min(q_cum)
		#endregion

		return {
			'NUM_CYCLES':int(num_cycles),
			'CAPACITY_CYCLE_DELTA_MAX_AH': float(q_delta_max),
			'CURRENT_MAX_A': float(current_max),
			'CURRENT_MIN_A': float(current_min),
			'CURRENT_THROUGHPUT_AH': float(q_throughput),
			'VOLTAGE_MAX_V': float(voltage_max), 
			'VOLTAGE_MIN_V': float(voltage_min),
		}



		

