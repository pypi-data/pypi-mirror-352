
from pathlib import Path
import pandas as pd
import zipfile, xmltodict, warnings


def get_xlsx_sheet_ids(file:Path) -> list:
	"""
	A minimal-read function that returns a list of the sheet names present 
	in a given .xslx file.

	Args:
		file (Path): Path object to location of the .xlsx file

	Returns:
		list: A list of sheet names given as strings
	"""
	
	assert file.suffix == '.xlsx'
	sheet_names = []
	with zipfile.ZipFile(file, 'r') as zip_ref:
		xml = zip_ref.open(r'xl/workbook.xml').read()
		dictionary = xmltodict.parse(xml)
		if not isinstance(dictionary['workbook']['sheets']['sheet'], list):
			sheet_names.append(dictionary['workbook']['sheets']['sheet']['@name'])
		else:
			for sheet in dictionary['workbook']['sheets']['sheet']:
				sheet_names.append(sheet['@name'])
	return sheet_names

def get_csv_columns(file:Path, header_row:int=0):
    return list(pd.read_csv(file, header=header_row, nrows=0).columns)

def read_any_to_df(file:Path) -> pd.DataFrame:
	"""Converts any supported filetype to pandas dataframe"""
	with warnings.catch_warnings():
		warnings.simplefilter("ignore", UserWarning)
		if file.suffix in ['.csv', '.tsv']:
			df = pd.read_csv(file)
		elif file.suffix == '.json':
			df = pd.read_json(file)
		elif file.suffix == '.xml':
			df = pd.read_xml(file)
		elif file.suffix in ['.xls', '.xlsx']:
			df = pd.read_excel(file)
		elif file.suffix == '.hdf':
			df = pd.read_hdf(file)           
		elif file.suffix == '.sql':
			df = pd.read_sql(file)
		elif file.suffix == '.parquet':
			df = pd.read_parquet(file)
		else:
			raise ValueError(f'Unsupported filetype: {file}')
	return df

