from flask import Flask, request, render_template, url_for , jsonify
from pymongo import MongoClient
from bson import json_util
import pandas as pd 
import csv
# import logging

# app.logger.addHandler(logging.StreamHandler(sys.stdout))
# app.logger.setLevel(logging.ERROR)

app=Flask(__name__)

MONODB_URI="mongodb://login:topsecret1@ds245677.mlab.com:45677/training_db"
client=MongoClient(MONODB_URI)
db=client.get_database("training_db")    #training_dp is the name of the database
login_student = db.login_students        #login_students is the collection


#WelcomePage

@app.route('/')
def index():
		return render_template('index.html')
    	

#Login Page

@app.route('/login',methods=['POST'])
def login():
	username=request.form.get('email')
	password=request.form.get('password')
	login_user=login_student.find_one({'email-id':username})
	
	
	if login_user :
		student_name=login_user['name']
		student_branch=login_user['branch']
		student_enrollment= login_user['enroll']
		student_email=login_user['email-id']
		mobileNum=login_user['mobileNum']
		try:
			preference_df = pd.read_csv("data/preferences.csv")
			studentnum=int(student_enrollment)
			selected_df=preference_df[preference_df['Enrollment Number'] ==studentnum ]
		except:
			hyperlink_format='<a href="{link}">{text}</a>'
			link_text=hyperlink_format.format(link= url_for('details'), text='Please Update Here!')
		
			return "Your  Enrollment No. is Deleted! "+link_text

		if password == login_user['password']:
																			#or selected_df['Preference 1'] or selected_df['Preference 2'] or selected_df['Preference 3']
			
			
			# sorted_df=preference_df.sort_values("Receipt Number") 
			selected_df['Course']=selected_df['Preference 1']
			
			receiptNum=selected_df['Receipt Number'].values
			preferenceOne=selected_df['Preference 1'].values
			preferenceTwo=selected_df['Preference 2'].values
			preferenceThree=selected_df['Preference 3'].values
			slot=selected_df['Course'].values
			
			return  render_template('signed_in.html',student_name=student_name,student_branch=student_branch,student_enrollment=student_enrollment,student_email=student_email,mobileNum=mobileNum,receiptNum=receiptNum[0],preferenceOne=preferenceOne[0],preferenceTwo=preferenceTwo[0],preferenceThree=preferenceThree[0],slot=slot[0])
	
		else:
			return 'Invalid  username/password combination!'
	return 'Invalid  username/password combination!'


#Registration Form

@app.route('/register',methods=['GET','POST'])
def register():
	if request.method == 'POST':
		
		name=request.form.get('name') 
		branch=request.form.get('branch') 
		enroll=request.form.get('enroll')
		username=request.form.get('email-id')
		password=request.form.get('password')
		mobileNum=""
		existing_user=login_student.find_one({'email-id':username})
		
		if existing_user is None:
			

			if name and branch and enroll and username and password : 
				updated_df = pd.read_csv("data/preferences.csv")   
				updated_df=updated_df.append({'Enrollment Number':enroll,'Receipt Number':0,
				'Preference 1':'Nil',
				'Preference 2':'Nil',
				'Preference 3':'Nil'
				}, ignore_index=True)
				updated_df.to_csv('data/preferences.csv',index=False)

				login_student.insert({'name':name,'branch':branch,'enroll':enroll,'email-id':username,'password':password,'mobileNum':mobileNum})
				return render_template('RegisteredPleaseLogin.html',name=name,username=username)
			else:
				return "Required  Field(s) are Empty! "
		else :
			hyperlink_format='<a href="{link}">{text}</a>'
			link_text=hyperlink_format.format(link= url_for('index'), text='Please Login')

			return( "User  already registered with this Email-id! "+link_text )

	elif request.method=='GET': 
		branches=['CSE','IT','ECE']
		return render_template('registration_form.html',branches=branches)


#Buttons on Signed In page


# 1. To edit Preferences ,Receipyt no. and Fee Receipt Doc.

@app.route('/document',methods=['GET','POST'])
def document():
		
	if request.method =='GET' :
		branches=['CSE','IT','ECE']
		preferences=['Machine Learning(ML)','Internet Of Things(IOT)','Big Data(BD)']
		return render_template('editPreference_uploadDocument.html',branches=branches,preferences=preferences)

		
	elif request.method =='POST':
		
		password=request.form.get('password')
		login_user=login_student.find_one({'password':password})
		
		if login_user:

			student_enrollment=login_user['enroll']
			receipt=request.form.get('receipt')
			preference1=request.form.get('preference1')
			preference2=request.form.get('preference2')
			preference3=request.form.get('preference3')
			photo=request.files.get('photo')  
			if receipt or preference1 or preference2 or preference3 or photo :
				if receipt and preference1 and preference2 and preference3 and photo:					
					try:
						preference_df = pd.read_csv("data/preferences.csv",index_col="Enrollment Number")
						student_number=student_enrollment.split()
						studentnum=list(map(int,student_number))
						preference_df.drop(studentnum[0],inplace=True,axis=0)
						preference_df.to_csv('data/preferences.csv')

						updated_df = pd.read_csv("data/preferences.csv")   
						updated_df=updated_df.append({'Enrollment Number':student_enrollment,'Receipt Number':receipt,
						'Preference 1':preference1,
						'Preference 2':preference2,
						'Preference 3':preference3}, ignore_index=True)
						updated_df.to_csv('data/preferences.csv',index=False)    
						ext = photo.filename.split('.')[-1]
						photo.save("FeeReceipt/{}.{}".format(student_enrollment,ext))

						# hyperlink_format='<a href="{link}">{text}</a>'
						# link_text=hyperlink_format.format(link= url_for('homepage'), text='Go back to Home Page')
						return "Preferences,  Receipt Number and Fee Receipt is Sucessfully Uploaded! "#+link_text	

					except:
						hyperlink_format='<a href="{link}">{text}</a>'
						link_text=hyperlink_format.format(link= url_for('details'), text='Please Update Here!')
					
						return "Enrollment  No. is Deleted! "+link_text

				if receipt and preference1 and preference2 and preference3 :					
					
					preference_df = pd.read_csv("data/preferences.csv",index_col="Enrollment Number")
					student_number=student_enrollment.split()
					studentnum=list(map(int,student_number))
					preference_df.drop(studentnum[0],inplace=True,axis=0)
					preference_df.to_csv('data/preferences.csv')

					updated_df = pd.read_csv("data/preferences.csv")   
					updated_df=updated_df.append({'Enrollment Number':student_enrollment,'Receipt Number':receipt,
					'Preference 1':preference1,
					'Preference 2':preference2,
					'Preference 3':preference3}, ignore_index=True)
					updated_df.to_csv('data/preferences.csv',index=False)

					# hyperlink_format='<a href="{link}">{text}</a>'
					# link_text=hyperlink_format.format(link= url_for('homepage'), text='Go back to Home Page')
					return "Your  Preferences and Receipt Number are Sucessfully  Uploaded! "#+link_text	

				if not photo:
					return "Required  fields[Receipt No. and Preferences] are Empty!"

				    #save file with particular enrollment number
				
				if photo:
					try:    
						ext = photo.filename.split('.')[-1]
						photo.save("FeeReceipt/{}.{}".format(student_enrollment,ext))

						# hyperlink_format='<a href="{link}">{text}</a>'
						# link_text=hyperlink_format.format(link= url_for('homepage'), text='Go back to Home Page')
						return "Fee  Receipt is Sucessfully Uploaded! "#+link_text	

					except:
						hyperlink_format='<a href="{link}">{text}</a>'
						link_text=hyperlink_format.format(link= url_for('details'), text='Please Update Here!')
					
						return "Enrollment  No. is Deleted! "+link_text

			else:
				return "Required  fields are Empty! "			

		else:
			return 'Invalid  Password!'


# 2. To Edit Personal Details 

@app.route('/details',methods=['GET','POST'])
def details():
	if request.method== 'GET':
		branches=['CSE','IT','ECE']
		return render_template('editDetails_Password.html',branches=branches)

	elif request.method=='POST':
		name=request.form.get('name')
		password=request.form.get('password')
		mobileNo=request.form.get('mobileNo')
		name=request.form.get('name')
		branch=request.form.get('branch')
		enroll=request.form.get('enroll')
		email=request.form.get('email')
		old_password=request.form.get('oldPass')
		new_password=request.form.get('newPass')

		login_user=login_student.find_one({'password':password})
		
		   
		if login_user:
		
			if name:
				login_student.update_one({'password':password}, {'$set':{'name':name}})

			if branch:
				login_student.update_one({'password':password}, {'$set':{'branch':branch}})

			if enroll:
				login_student.update_one({'password':password}, {'$set':{'enroll':enroll}})

			if email:
				login_student.update_one({'password':password}, {'$set':{'email-id':email}})

			if mobileNo:
				login_student.update_one({'password':password}, {'$set':{'mobileNum':mobileNo}})

			if old_password==password:
				login_student.update_one( {'password':password},{'$set':{'password':new_password}})

			# hyperlink_format='<a href="{link}">{text}</a>'
			# link_text=hyperlink_format.format(link= url_for('homepage'), text='Go back to Home Page')
			return "Sucessfully  Uploaded! "#+link_text
		
		else:
		 	return "Either  verification password(old) or Current Password is Incorrect!!"


# 3. To Delate different Fields		

@app.route('/delete',methods=['GET','POST'])
def delete():
	if request.method == 'GET':
		return render_template('delete.html')
	elif request.method == 'POST':
		email=request.form.get('email')
		login_user=login_student.find_one({'email-id':email})
		
		if email:
			if login_user:
				filename=login_user['enroll']
				if request.form['action'] =='Delete Personal Details':
					login_student.update_one({'email-id':email},{'$set' : { 'name':"Obscure", 'branch' : "" ,'mobileNum' : "" }})
					return"Your Name, Branch, Mobile no. has been Deleted!"

				elif request.form['action'] == 'Delete Preferences':
					preference_df = pd.read_csv("data/preferences.csv",index_col="Enrollment Number")
					#select_df=preference_df[['Receipt Number','Preference 1','Preference 2','Preference 3']]                                       #if we want to select some colums

																																					# enrollmentNum="41196203117"
															# could do this as well	->																# student_number=enrollmentNum.split() 
																																					# studentnum=list(map(int,student_number))
																																					# studentnum=int(enrollmentNum)
																																					# select_df.drop(studentnum,inplace=True,axis=0)
					filenumber=filename.split()																			
					filenum=list(map(int,filenumber))
					preference_df.drop(filenum[0],inplace=True,axis=0)
					preference_df.to_csv('data/preferences.csv')

					updated_df = pd.read_csv("data/preferences.csv")   
					updated_df=updated_df.append({'Enrollment Number':filename,'Receipt Number':0,
					'Preference 1':'Nil',
					'Preference 2':'Nil',
					'Preference 3':'Nil'}, ignore_index=True)
					updated_df.to_csv('data/preferences.csv',index=False)


					return "Your  Preferences and receipt No. are Deleted!"
				    
				elif request.form['action'] == 'Delete Information':
					preference_df = pd.read_csv("data/preferences.csv",index_col="Enrollment Number")
					filenumber=filename.split()
					filenum=list(map(int,filenumber))
					try:
						preference_df.drop(filenum[0],inplace=True,axis=0)
						preference_df.to_csv('data/preferences.csv')

						updated_df = pd.read_csv("data/preferences.csv")   
						updated_df=updated_df.append({'Enrollment Number':filename,'Receipt Number':0,
						'Preference 1':'Nil',
						'Preference 2':'Nil',
						'Preference 3':'Nil'}, ignore_index=True)
						updated_df.to_csv('data/preferences.csv',index=False)


						login_student.update_one({'email-id':email},{'$set' : { 'name':"Obscure", 'branch' : "" ,'mobileNum' : "" ,'enroll':""}})
						return"Your  Information Details have been Deleted !"
					except:
						hyperlink_format='<a href="{link}">{text}</a>'
						link_text=hyperlink_format.format(link= url_for('details'), text='Please Update Here!')
					
						return "You  might have Already Deleted Enrollment Number!! "+link_text

				elif request.form['action'] == 'Delete Account':
					preference_df = pd.read_csv("data/preferences.csv",index_col="Enrollment Number")
					filenumber=filename.split()
					filenum=list(map(int,filenumber))
					try:
						login_student.delete_one({'email-id':email})
						preference_df.drop(filenum[0],inplace=True,axis=0)
						preference_df.to_csv('data/preferences.csv')
					except:
						hyperlink_format='<a href="{link}">{text}</a>'
						link_text=hyperlink_format.format(link= url_for('details'), text='Please Update Here!')
					
						return "You  might have Already Deleted Enrollment Number!! "+link_text

					                   #OR
					#login_student.update_one({'email-id':email},{'$unset' : { 'name':1, 'branch' : 1 ,'mobileNum' : 1 ,'enroll:1,"email-id":1,password:1}})
					hyperlink_format='<a href="{link}">{text}</a>'
					link_text=hyperlink_format.format(link= url_for('register'), text='Create New Account')
			
					return"Your  Account is Deleted! "+link_text
			
			else:
				return"User  Not Found!"	    
		else:
			return "Email-id  is Not Specified! "


# 4. To Allot Slot

@app.route('/slot',methods=['GET'])
def slot():
	if request.method=='GET':
		data_df = pd.read_csv("data/preferences.csv")  
		sorted_df=data_df.sort_values("Receipt Number") 
		sorted_df['Course']=sorted_df['Preference 1']
		
		sorted_df.loc[sorted_df['Course'] == "ML", 'Allotted Slot'] = "SLOT-I : 1st August 2019 - 15th August 2019"
		sorted_df.loc[sorted_df['Course'] == "BD", 'Allotted Slot'] = "SLOT-II : 10th August 2019 - 25th August 2019"
		sorted_df.loc[sorted_df['Course'] == "IOT", 'Allotted Slot'] = "SLOT-III : 15th August 2019 - 30th August 2019"

		sorted_df.loc[sorted_df['Course'] == "ML", 'Laboratory'] ="CS Computer Lab 2[ Block 1,I Floor ]"
		sorted_df.loc[sorted_df['Course'] == "BD", 'Laboratory'] ="IT Computer Lab 1[ Block 2,Ground Floor ]"
		sorted_df.loc[sorted_df['Course'] == "IOT", 'Laboratory'] ="ECE Computer Lab 3 [ Block 4,III Floor ]"
		
		Course=sorted_df['Course'].values
		AllottedSlot=sorted_df['Allotted Slot'].values
		Laboratory=sorted_df['Laboratory'].values
		return render_template('allottedSlot.html',Course=Course[0],AllottedSlot=AllottedSlot[0],Laboratory=Laboratory[0])


# 5. To logout

@app.route('/log_out',methods=['GET'])
def logOut():
	hyperlink_format='<a href="{link}">{text}</a>'
	link_text=hyperlink_format.format(link= url_for('index'), text='Register/Login here!')
	return " You  are Signed out. "+link_text


# Testing the API using Request Library

# GET and POST HTTP Request

@app.route('/students', methods=['GET', 'POST'])

def student_list():

	if request.method == 'GET':
		students = list(login_student.find({}))
		return json_util.dumps(students)
	elif request.method == 'POST':
		username=request.form.get('email-id')
		if login_student.find_one({"email-id":username}):
			return jsonify({"Error": "User already registered!"})
		student = {}
		student['name']=request.form.get('name') 
		student['branch']=request.form.get('branch') 
		student['enroll']=request.form.get('enroll')
		student['email-id']=username
		student['password']=request.form.get('password')
		student['mobileNum']=request.form.get('mobileNum')
		login_student.insert_one(student)
		return jsonify({"result": "User successfully registered!"})


# Patch and Delete HTTP Requests:

@app.route('/student/<username>',methods=['GET','PATCH','DELETE'])
def get_student(username):
	student=login_student.find_one({'email-id':username})
		
	if not student:
		return jsonify({"Error": "Incorrect Username!"}), 404

	if request.method == 'GET':

		return json_util.dumps(student)

	elif request.method == 'PATCH':

		login_student.update_one({'email-id':username}, {'$set':request.form})

		return jsonify({"Result": "Student record successfully updated!"})

	elif request.method == 'DELETE':
		try:
			login_student.delete_one({'email-id':username})

			return jsonify({"Result": "Student record successfully deleted!"})
		except:
			return jsonify({"Error": "User does not exist!"})
		
if __name__=="__main__" :
	app.run(debug=True,port=9000,use_reloader=True)
