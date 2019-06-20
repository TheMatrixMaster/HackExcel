import pandas as pd
import io
import win32com.client as win32

# step 1: Read Excel Input and determine header row by searching for key word
def read_file(file):
	df = pd.read_excel(file, header=None)
	header_row = find_header_row(df)
	df = pd.read_excel(file, header=header_row)
	return df

# Find header row by searching for keyword, 'employeeid', TODO: add functionality for user specification
def find_header_row(file):
	header_row = 8
	for index, row in file.iterrows():
		for col, val in enumerate(row):
			try:
				if "employeeid" in str(val).lower() or "address" in str(val).lower(): 
					header_row = index
					break
			except: print("Something went wrong!")
	return header_row

def removeSpaces(string): 
    string = string.replace(' ','') 
    return string

def search_joined(joined, search_data):
	for key in search_data.keys():
		searchKey = removeSpaces(key.lower().strip())
		for index, join in enumerate(joined):
			if searchKey == join: search_data[key] = index
			elif searchKey in join: search_data[key] = index
	return search_data

def search_splitted(splitted, search_data):
	for key in search_data.keys():
		searchKey = removeSpaces(key.lower().strip())
		for index, list_ in enumerate(splitted):
			for split in list_:
				if searchKey == split: search_data[key] = index
	return search_data

# step 2: find columns in input file that correspond to required output data keywords
def find_data_columns(df, search_data):
	column_names = df.columns 
	column_names.dropna()
	splitted_column_names = [x.lower().strip().split(" ") for x in column_names]
	joined_column_names = [removeSpaces(x.lower().strip()) for x in column_names]
	search_data = search_joined(joined_column_names, search_data)
	search_data = search_splitted(splitted_column_names, search_data)
	return search_data

# step 3: Create new output dataframe with pulled data from input file 
def create_new_df(df, data_columns, required_data):
	new_df = df.iloc[:, list(data_columns.values())]
	new_df.columns = data_columns.keys()
	new_df.dropna(subset=required_data, inplace=True)
	return new_df

# step 4: Change header style and save to excel file
def style_header_and_save(new_df):
	strIO = io.BytesIO()
	writer = pd.ExcelWriter(strIO, engine='xlsxwriter')
	new_df.to_excel(writer, sheet_name='converted', startrow=1, header=False, index=False)
	workbook = writer.book
	worksheet = writer.sheets['converted']
	header_format = workbook.add_format({
		'bold': True,
		'font_size': 12,
		'bg_color': '#C0C0C0'
		})

	for col_num, value in enumerate(new_df.columns.values):
		worksheet.write(0, col_num, value, header_format)

	writer.save()
	excel_data = strIO.getvalue()
	strIO.seek(0)
	return strIO

	'''
	# open with windows client to auto-adjust column width
	excel = win32.gencache.EnsureDispatch('Excel.Application')
	wb = excel.Workbooks.Open()
	ws = wb.Worksheets("converted")
	ws.Columns.AutoFit()
	wb.Save()
	excel.Application.Quit()
	'''


'''
file = "D:/TransformerHacks/Sample1_Input2.xlsx"

search_data = {"LastName": -1, 
				"FirstName": -1, 
				"Title": -1, 
				"BirthDate": -1, 
				"Address": -1, 
				"City": -1, 
				"Region": -1, 
				"PostalCode": -1, 
				"Country": -1, 
				"HomePhone": -1, 
				"Extension": -1, 
				"Notes": -1}

required_data = list(search_data.keys())[:2]

df = read_file(file)
data_columns = find_data_columns(df, search_data)
new_df = create_new_df(df, data_columns, required_data)
style_header_and_save(new_df, file)
'''