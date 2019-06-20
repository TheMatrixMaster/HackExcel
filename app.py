"""
Flask app file to be run to render web app
"""

# Import modules
from flask import Flask, flash, redirect, url_for, render_template, request, Response, send_file, make_response, abort, session
from werkzeug.utils import secure_filename

import glob
import os
import re

import pandas as pd
import datetime

from transform_functions import *

# configure Flask app
app = Flask(__name__)
app.secret_key = "zjd92kn"
ALLOWED_EXTENSIONS = set(['xlsx', 'xls', 'csv'])
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# variables 
excel_file = pd.DataFrame()
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

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
	submitted = "False"
	if request.method == 'POST':
		# check for excel file in user input
		if 'excel-file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['excel-file']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			# read input file and find recognized columns that correspond to output keywords
			filename = secure_filename(file.filename)
			df = read_file(file)
			global excel_file
			excel_file = df
			columns = list(df.columns.dropna())
			data_columns = find_data_columns(df, search_data)
			data_indexes = [x for x in list(data_columns.values()) if x != -1]
			selected_columns = [x for i, x in enumerate(columns) for index in data_indexes if i == index]
			other_columns = [x for x in columns if x not in selected_columns]
			submitted = "True"
			return render_template('home.html', selected_columns=selected_columns, other_columns=other_columns, key=submitted)

	return render_template('home.html', key=submitted)

@app.route('/export', methods=['GET', 'POST'])
def export_to_excel():
	if request.method == 'POST':
		print('exporting to excel')
		global excel_file
		columns = excel_file.columns.dropna()
		selected_columns = [x for x in columns if request.form.get(x) == 'on']
		column_names = [request.form.get(x + 'name') for x in selected_columns]
		required_data = column_names[:2]
		new_df = excel_file.loc[:, selected_columns]
		new_df.columns = column_names
		new_df.dropna(subset=required_data, inplace=True)

		strIO = style_header_and_save(new_df)
		return send_file(strIO, attachment_filename='output.xlsx', as_attachment=True)

	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)