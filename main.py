import os
#import magic
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template ,url_for ,send_file
from werkzeug.utils import secure_filename
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def csv_reader(name):
			df = pd.read_csv(name)
			print(df.describe())
			print(df.columns)
			print(df.shape)
			#1. file 1 ->  Organization Group Name + OrganizationGroupId + Friendly Name + Device ID + ComplianceStatus + Last Seen
			#Read only the required columns
			df1 = df[['Organization Group ID', 'Organization Group Name','Friendly Name','Device ID','Compliance Status',
						'Last Seen','Enrollment Status','Display Name']]
			df1.head()
			#Remove AV /MPAD
			df1.set_index('Display Name',inplace=True)
			df1.head()
			df1.shape
			df1.drop("Panasonic AutoVerify User",inplace=True)
			#df1.drop("Zebra AutoVerify User",inplace=True)
			df1.drop("MPAD User",inplace=True)
			df1.shape

			#df1['Organization Group Name'].value_counts(ascending=True)
			df1.reset_index(inplace = True)
			df1.set_index('Organization Group Name',inplace=True)

			df1.shape

			df1.drop("Device Staging - EUR",inplace=True)
			df1.drop("China Device Staging HQ",inplace=True)
			df1.drop("Device Staging - LAC",inplace=True)
			#df1.drop("Device Staging APAC",inplace=True)
			df1.drop("Device Staging",inplace=True)
			#df1.drop("Device Staging - MEISA",inplace=True)

			df1.shape
			df1.head()

			df1.reset_index(inplace = True)
			df1['Organization Group Name'] = df1['Organization Group Name'].str.replace('TR-', '')

			df1.head()

			#rename COlumns
			df1.rename(columns = {"Organization Group Name": "orgGN"},inplace = True)
			df1.rename(columns = {"Enrollment Status": "enrl"},inplace = True)
			df1.rename(columns = {"Organization Group ID": "orgId"},inplace = True)
			df1.rename(columns = {"Friendly Name": "name"},inplace = True)
			df1.rename(columns = {"Device ID": "dId"},inplace = True)
			df1.rename(columns = {"Compliance Status": "comp"},inplace = True)
			df1.rename(columns = {"Last Seen": "lastS"},inplace = True)

			df1 = df1.drop(['Display Name'], axis = 1)

			df1.head()

			df1['orgGN'] = df1.orgGN.str.replace('-', '')
			df1['orgGN'] = df1.orgGN.str.replace("Alpha", '')
			df1['orgGN'] = df1.orgGN.str.replace("ALPHA", '')
			df1['orgGN'] = df1.orgGN.str.replace("3rd", '')
			df1['orgGN'] = df1.orgGN.str.replace("2nd", '')
			df1['orgGN'] = df1.orgGN.str.replace("1st", '')
			df1['orgGN'] = df1.orgGN.str.replace("2ND", '')
			df1['orgGN'] = df1.orgGN.str.replace("1ST", '')
			df1['orgGN'] = df1.orgGN.str.replace("Wave", '')

			df1.head()


			from sklearn import preprocessing
			le = preprocessing.LabelEncoder()
			df1['enrl'] = le.fit_transform(df1.enrl.values)



			df1['enrl'].describe()


			#Complient Calculation
			dfcomp = df1[['orgGN','comp']]

			dfcomp = pd.get_dummies(data=dfcomp,columns=['comp'])

			dfcomp.head(2)

			dfcomp = dfcomp.groupby('orgGN').sum()


			dfcomp.head(2)

			dfcomp["percent"] = (dfcomp['comp_Compliant'] / (dfcomp['comp_Compliant']+dfcomp['comp_NotAvailable']) )* 100

			dfcomp.head(10)

			dfcomp.reset_index(inplace = True)


			dfcomp['percent'] = dfcomp['percent'].astype('int32')


			dfcomp.head(10)

			dfcolor = dfcomp

			dfcolor.head()

			dfcolor['color'] = 'BBBBBB'

			dfcolor.loc[dfcolor['percent'] < 90, 'color'] = 'red'
			dfcolor.loc[((dfcolor['percent'] >= 90) & (dfcolor['percent'] < 95) ), 'color'] = 'yellow'
			dfcolor.loc[dfcolor['percent'] >= 95, 'color'] = 'green'

			# 95% Compliance 7      --green
			# 90-95% Compliance 2    --yellow
			# 90% Compliance 1      -- red


			dfcolor.head()
			dfcolor['percent'].nunique()
			dfcolor['color'].nunique()

			dfcomp = dfcolor

			df1.head(10)

			df12 = df1.merge(dfcomp, how='outer')

			df12.head(10)

			#FedEx_Gps_Data.csv

			# reading csv file
			df3 = pd.read_csv('FedEx_Gps_Data.csv')

			df3.shape

			df3.columns

			df3 =df3.dropna()

			df3.shape
			df12.head()
			df3.head()

			#df3["loc"] = df3['Address'] + " - " +df3['City'] + " - " +df3['State']
			df3["loc"] = df3['City'] + " - " +df3['State'] + " - " +df3['Address']

			df3 = df3.drop(['City'], axis = 1)
			df3 = df3.drop(['State'], axis = 1)
			df3 = df3.drop(['Address'], axis = 1)

			#rename COlumns
			df3.rename(columns = {"Groupname": "orgGN"},inplace = True)
			df3.rename(columns = {"Latitude": "lat"},inplace = True)
			df3.rename(columns = {"Longtitude": "long"},inplace = True)

			df3.head()

			df123 = df12.merge(df3, how='outer')

			df123.head()


			#df123.to_csv('.\Device_Inventory9_24\df123.csv',index=True)
			#df123.to_json('.\Device_Inventory9_24\df123.json',orient='records')

			df123 =df123.dropna()

			df123.dtypes

			from sklearn import preprocessing
			le = preprocessing.LabelEncoder()
			df123['comp'] = le.fit_transform(df123.comp.values)


			df123.rename(columns = {"comp_Compliant": "compc"},inplace = True)
			df123.rename(columns = {"comp_NotAvailable": "ncompc"},inplace = True)


			df123.orgGN   =df123.orgGN.astype('str')
			df123.orgId   =df123.orgId.astype('int64')
			df123.name    =df123.name.astype('str')
			df123.dId     =df123.dId.astype('int64')

			df123['comp'] = df123['comp'].replace([0,1],['c','n'])
			df123.comp    =df123.comp.astype('str')
			#df123.comp    =df123.comp.astype('int64')

			df123.lastS   =df123.lastS.astype('str')
			df123.percent =df123.percent.astype('int64')
			df123.lat     =df123.lat.astype('float64')
			df123.long    =df123.long.astype('float64')
			df123.enrl    =df123.enrl.astype('int64')
			#df123.loc     =df123.loc.astype('str')

			df123.compc    =df123.compc.astype('int64')
			df123.ncompc    =df123.ncompc.astype('int64')

			df123.dtypes


			df123.to_csv(uploads_dir +r'\Device.csv',index=True)
			print('csv file loaded')
			print(uploads_dir)
			df123.to_json(uploads_dir +r'\devicelist.json',orient='records')
			print('json file loaded')
			print(uploads_dir)
			return



@app.route('/')
def upload_form():
	return render_template('index.html')

@app.route('/', methods=['POST','GET'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(uploads_dir, filename))
			print(uploads_dir)
			print(os.path.join(uploads_dir, filename))
			print(filename)
			df = pd.read_csv(os.path.join(uploads_dir, filename))
			print(df.describe())
			print(df.columns)
			print(df.shape)
			csv_reader(os.path.join(uploads_dir, filename))
			flash('File successfully uploaded')
			return redirect('downloadfile')
		else:
			flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif, csv')
			return redirect(request.url)


@app.route("/downloadfile", methods = ['GET'])
def download_form():
	return render_template('download.html')

@app.route('/download')
def download_file():
	#path = "html2pdf.pdf"
	#path = "info.xlsx"
	filename = '\devicelist.json'
	path = uploads_dir + filename
	return send_file(path, as_attachment=True,attachment_filename='')

if __name__ == "__main__":
    app.run()
