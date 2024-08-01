import secrets
import os
from flask import Flask, render_template, redirect, request, session, url_for, flash,jsonify
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin,current_user
from bson import ObjectId  # Import ObjectId from bson module
from datetime import datetime

import uuid  # For generating unique IDs
import smtplib  # For sending emails
import joblib
import re
from urllib.parse import urlparse
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


app = Flask(__name__)


i1 = None
i2 = None
i3 = None
i4 = None
i5 = None

#sdfshh
# Generate a secure secret key
secret_key = secrets.token_hex(16)

# Set the secret key securely from environment variable or fallback to a default value
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secret_key)

client = MongoClient('mongodb://localhost:27017/')
db = client['MyHealth_Hero']
users_collection = db['users']
users_community = db['users_community']
appointments_collection = db['appointments_collection']
goals_collection = db['goals']
users_mental_data = db['users_mental_data']
mental_question_collection = db['mental_question']
goals_done = db['goals_done']


login_manager = LoginManager()
login_manager.init_app(app)



# ------ for prediction ------
# Load the trained model
model = joblib.load(r"D:\10_Projects\Main Projects\Decision support system (Mental Health)\My_Health_Hero\StressidentificationNLP")
# model = joblib.load(r"StressidentificationNLP")

# # Load the vectorizer
vectorizer = joblib.load(r"D:\10_Projects\Main Projects\Decision support system (Mental Health)\My_Health_Hero\TfidfVectorizer.joblib")
# vectorizer = joblib.load(r"TfidfVectorizer.joblib")

# Define preprocessing functions
def text_process(text):
    # Remove brackets
    text = re.sub('[][)(]', ' ', text)
    # Remove URLs
    text = [word for word in text.split() if not urlparse(word).scheme]
    text = ' '.join(text)
    # Remove escape characters
    text = re.sub(r'\@\w+', '', text)
    # Remove HTML tags
    text = re.sub(re.compile("<.*?>"), '', text)
    # Keep only alphanumeric characters
    text = re.sub("[^A-Za-z0-9]", ' ', text)
    # Convert to lowercase
    text = text.lower()
    # Tokenize text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Function to predict stress
def predictor(text):
    processed_text = text_process(text)
    # Vectorize the text
    processed_text_vectorized = vectorizer.transform([text])
    # Predict using the model
    prediction = model.predict(processed_text_vectorized)
    if prediction[0] == 1:
        return "Based on our assessment, it appears that you are currently experiencing stress. We recommend seeking support and exploring coping strategies to manage this effectively."
    elif prediction[0] == 0:
        return "Our evaluation indicates that you are not currently experiencing significant stress. However, it's essential to continue practicing self-care and maintaining healthy habits to sustain your mental well-being."








# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return str(self.username)    

# Load user from database
@login_manager.user_loader
def load_user(username):
    user_data = users_collection.find_one({'username': username})
    if user_data:
        return User(user_data['username'])
    else:
        return None
    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        dob = request.form['dob']
        mobile = request.form['mobile']

        if users_collection.find_one({'username': username}):
            flash('Username already taken. Please choose a different username.', 'error')
            return redirect(url_for('signup'))

        new_user = {
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'username': username,
            'email': email,
            'password': password,
            'address': address,
            'dob': dob,
            'mobile': mobile
        }
        users_collection.insert_one(new_user)
        flash('Signup successful. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = users_collection.find_one({'username': username, 'password': password})

        if user_data:
            user = User(user_data['username'])
            print(user)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))   



# ---------- home page ----------- 
@app.route('/',methods=['GET','POST'])
def home():
    user_data = None

    if current_user.is_authenticated:
        user_data = users_collection.find_one({'username': current_user.username})

    return render_template('index.html',user_data=user_data)




# ------------- profile ------------- 

@app.route('/profile', methods=['GET', 'POST'])
def profile():
   
   user_data = None
   appointments_data = None
   goals_collection_main=None
   doctor_name = None
   time_slot = None
   concern = None
   google_meet_link = None  
     


   if current_user.is_authenticated:
     user_data = users_collection.find_one({'username': current_user.username})
     appointments_data = appointments_collection.find_one({'username': current_user.username})
     goals_collection_main = goals_collection.find_one({'username': current_user.username})

   if appointments_data:
         doctor_name = appointments_data.get('doctor_name')
         time_slot = appointments_data.get('time_slot')
         concern = appointments_data.get('concern')
         google_meet_link = appointments_data.get('google_meet_link')  

   g1 = None
   g2 = None
   g3 = None
   g4 = None
   g5 = None   
   goal_1 =None       
   goal_2 =None    
   goal_3=None      
   goal_4=None     
   goal_5= None 
   flag1 = None
   flag2 = None
   flag3 = None
   flag4 = None
   flag5 = None

   s1 = None
   s2 = None
   s3 = None
   s4 = None
   s5 = None


# Initialize index variables
   if 'i1' not in session:
       session['i1'] = 0
   if 'i2' not in session:
       session['i2'] = 0
   if 'i3' not in session:
       session['i3'] = 0
   if 'i4' not in session:
       session['i4'] = 0
   if 'i5' not in session:
       session['i5'] = 0    


# Handle GET requests
   if request.method == 'GET':
    # Reset index variables to 0 when the page is loaded
     


     session['i1'] = 0
     session['i2'] = 0
     session['i3'] = 0
     session['i4'] = 0
     session['i5'] = 0

    # Fetch goal data based on the current index
     if goals_collection_main:
        goal1 = goals_collection_main.get('goal1', [])
        goal2 = goals_collection_main.get('goal2', [])
        goal3 = goals_collection_main.get('goal3', [])
        goal4 = goals_collection_main.get('goal4', [])
        goal5 = goals_collection_main.get('goal5', [])

        goal_1 = goal1[session['i1']] if goal1 else None
        goal_2 = goal2[session['i2']] if goal2 else None
        goal_3 = goal3[session['i3']] if goal3 else None
        goal_4 = goal4[session['i4']] if goal4 else None
        goal_5 = goal5[session['i5']] if goal5 else None

        
        # Convert date string to datetime object
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_username = current_user.username
    
        # Query MongoDB based on username and date
        goal_done_per_date = goals_done.find_one({'username':current_username , 'current_date':current_date })
        print(goal_done_per_date)
        if goal_done_per_date == None:
            pass
        else:

         if goal_done_per_date.get('goal_assigned1'):
            s1 = True
         if goal_done_per_date.get('goal_assigned2'):
            s2 = True
         if goal_done_per_date.get('goal_assigned3'):
            s3 = True
         if goal_done_per_date.get('goal_assigned4'):
            s4 = True
         if goal_done_per_date.get('goal_assigned5'):
            s5 = True

        return render_template('profile.html', user_data=user_data, doctor_name=doctor_name, time_slot=time_slot, concern=concern, google_meet_link=google_meet_link,goal_1=goal_1,goal_2=goal_2,goal_3=goal_3,goal_4=goal_4,goal_5=goal_5,s1 = s1,s2=s2,s3=s3,s4=s4,s5=s5)

   # Handle POST requests
   if request.method == 'POST':
    # Increment index variables based on the form submission
    # Increment index variables based on the form submission

     g1 = request.form.get('goal1_main')

     g2 = request.form.get('goal2_main')

     g3 = request.form.get('goal3_main')

     g4 = request.form.get('goal4_main')
    
     g5 = request.form.get('goal5_main')



     
     
     
     

     if g1:
        session['i1'] += 1
     if g2:
        session['i2'] += 1
     if g3:
        session['i3'] += 1
     if g4:
        session['i4'] += 1
     if g5:
        session['i5'] += 1

# Fetch goal data based on the current index
     if goals_collection_main:
      goal1 = goals_collection_main.get('goal1', [])
      goal2 = goals_collection_main.get('goal2', [])
      goal3 = goals_collection_main.get('goal3', [])
      goal4 = goals_collection_main.get('goal4', [])
      goal5 = goals_collection_main.get('goal5', [])

      goal_1 = goal1[session['i1']] if goal1 and len(goal1) > session['i1'] else None
      goal_2 = goal2[session['i2']] if goal2 and len(goal2) > session['i2'] else None
      goal_3 = goal3[session['i3']] if goal3 and len(goal3) > session['i3'] else None
      goal_4 = goal4[session['i4']] if goal4 and len(goal4) > session['i4'] else None
      goal_5 = goal5[session['i5']] if goal5 and len(goal5) > session['i5'] else None



# -------- for goals done or not for theripist giving ---------

      donebtn = None
      
      flag1 = None
      flag2 = None
      flag3 = None
      flag4 = None
      flag5 = None
      donebtn = request.form.get('done_btn')  # Get the value or None if not found

      print(donebtn)

  
      if donebtn:
  

        if g1:
         session['i1'] -= 1
         print(session['i1'])
        if g2:
         session['i2'] -= 1
         print(session['i2'])
        if g3:
         session['i3'] -= 1
         print(session['i3'])
        if g4:
         session['i4'] -= 1
         print(session['i4'])
        if g5:
         session['i5'] -= 1
         print(session['i5'])

        goal_1 = goal1[session['i1']] if goal1 and len(goal1) > session['i1'] else None
        goal_2 = goal2[session['i2']] if goal2 and len(goal2) > session['i2'] else None
        goal_3 = goal3[session['i3']] if goal3 and len(goal3) > session['i3'] else None
        goal_4 = goal4[session['i4']] if goal4 and len(goal4) > session['i4'] else None
        goal_5 = goal5[session['i5']] if goal5 and len(goal5) > session['i5'] else None

        if g1: 
         
         print(g1) 
         print(goal_1)
         current_date = datetime.now().strftime("%Y-%m-%d")
         current_time = datetime.now().strftime("%H:%M:%S")

        #  current_date = '2024-04-08'
        #  current_time = '04:23:06'
         print(current_date)
         print(current_time)

         username = current_user.username
  
        # Check if a document exists for the current username and current date
         existing_goal_doc = goals_done.find_one({'username': username, 'current_date': current_date})
            
         if existing_goal_doc:
             # Update the existing document with the new goal
             goals_done.update_one(
                 {'_id': existing_goal_doc['_id']},
                 {'$set': {'goal1': g1, 'goal_assigned1': goal_1}}
             )
         else:
             # Insert a new document with the new goal
             goals_finish = {
                 'username': username,
                 'current_date': current_date,
                 'goal1': g1,
                 'goal_assigned1': goal_1,
                 'current_time': current_time
             }
             goals_done.insert_one(goals_finish)
             flag1 = True





        if g2:
         print(g2) 
         print(goal_2)
         current_date = datetime.now().strftime("%Y-%m-%d")
         current_time = datetime.now().strftime("%H:%M:%S")

        #  current_date = '2024-04-08'
        #  current_time = '04:23:06'         
         #    return f"Current time and date: {current_time}"
         print(current_date)
         print(current_time)
     
         username = current_user.username
  
           # Check if a document exists for the current username and current date
         existing_goal_doc = goals_done.find_one({'username': username, 'current_date': current_date})
                
         if existing_goal_doc:
               # Update the existing document with the new goal
               goals_done.update_one(
                  {'_id': existing_goal_doc['_id']},
                   {'$set': {'goal2': g2, 'goal_assigned2': goal_2}}
               )
         else:
            # Insert a new document with the new goal
             goals_finish = {
                    'username': username,
                    'current_date': current_date,
                    'goal2': g2,
                    'goal_assigned2': goal_2,
                    'current_time': current_time
                }
             goals_done.insert_one(goals_finish)
             flag2 = True
     



        if g3: 
            print(g3)
            print(goal_3)
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")

            # current_date = '2024-04-08'
            # current_time = '04:23:06'
            print(current_date)
            print(current_time)
     
            username = current_user.username
           # Check if a document exists for the current username and current date
            existing_goal_doc = goals_done.find_one({'username': username, 'current_date': current_date})
                
            if existing_goal_doc:
                  # Update the existing document with the new goal
                   goals_done.update_one(
                      {'_id': existing_goal_doc['_id']},
                      {'$set': {'goal3': g3, 'goal_assigned3': goal_3}}
                   )
            else:
                   # Insert a new document with the new goal
                   goals_finish = {
                       'username': username,
                       'current_date': current_date,
                       'goal3': g3,
                       'goal_assigned3': goal_3,
                       'current_time': current_time
                   }
                   goals_done.insert_one(goals_finish)
                   flag3 = True





        if g4: 
            print(g4)
            print(goal_4)
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
            # current_date = '2024-04-08'
            # current_time = '04:23:06'


            print(current_date)
            print(current_time)

            username = current_user.username
           # Check if a document exists for the current username and current date
            existing_goal_doc = goals_done.find_one({'username': username, 'current_date': current_date})
                
            if existing_goal_doc:
                  # Update the existing document with the new goal
                   goals_done.update_one(
                      {'_id': existing_goal_doc['_id']},
                       {'$set': {'goal4': g4, 'goal_assigned4': goal_4}}
                   )
            else:
                   # Insert a new document with the new goal
                   goals_finish = {
                       'username': username,
                       'current_date': current_date,
                       'goal4': g4,
                       'goal_assigned4': goal_4,
                       'current_time': current_time
                   }
                   goals_done.insert_one(goals_finish)
                   flag4 = True




        if g5: 
            
            print(g5)
            print(goal_5)
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
         #    return f"Current time and date: {current_time}"
            print(current_date)
            print(current_time)

            username = current_user.username
           # Check if a document exists for the current username and current date
            existing_goal_doc = goals_done.find_one({'username': username, 'current_date': current_date})
                
            if existing_goal_doc:
                  # Update the existing document with the new goal
                   goals_done.update_one(
                      {'_id': existing_goal_doc['_id']},
                       {'$set': {'goal5': g5, 'goal_assigned5': goal_5}}
                   )
            else:
                   # Insert a new document with the new goal
                   goals_finish = {
                       'username': username,
                       'current_date': current_date,
                       'goal5': g5,
                       'goal_assigned5': goal_5,
                       'current_time': current_time
                   }
                   goals_done.insert_one(goals_finish)
                   flag5 = True
          
      else:
        pass


     # --------- for done tick ---------     

        # Convert date string to datetime object
     current_date = datetime.now().strftime("%Y-%m-%d")
     current_username = current_user.username  

        # Query MongoDB based on username and date
     goal_done_per_date = goals_done.find_one({'username': current_username, 'current_date': current_date})
     print(goal_done_per_date)
     if goal_done_per_date.get('goal_assigned1'):
            s1 = True
     if goal_done_per_date.get('goal_assigned2'):
            s2 = True
     if goal_done_per_date.get('goal_assigned3'):
            s3 = True
     if goal_done_per_date.get('goal_assigned4'):
            s4 = True
     if goal_done_per_date.get('goal_assigned5'):
            s5 = True




   return render_template('profile.html', user_data=user_data, doctor_name=doctor_name, time_slot=time_slot, concern=concern, google_meet_link=google_meet_link,goal_1=goal_1,goal_2=goal_2,goal_3=goal_3,goal_4=goal_4,goal_5=goal_5,flag1=flag1,flag2=flag2,flag3=flag3,flag4=flag4,flag5=flag5,s1 = s1,s2=s2,s3=s3,s4=s4,s5=s5)
  

    



# ---------- mental test ----------- 
@app.route('/mental',methods=['GET','POST'])
def mental():
#     user_data = None  # Initialize user_data to None

#     if current_user.is_authenticated:  # Check if the user is authenticated
#         user_data = users_collection.find_one({'username': current_user.username})

#     return render_template('mental.html',user_data= user_data)

    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})

    # Fetch questions from the database
    questions_cursor = mental_question_collection.find({}, {'_id': 0, 'question_text': 1})

    # Extract the questions from the cursor
    questions = [question['question_text'] for question in questions_cursor]

    return render_template('mental.html', user_data=user_data, questions=enumerate(questions, start=1))







# ---------- Analysis ----------- 
@app.route('/analysis',methods=['GET','POST'])
def analysis():

    user_data = None  # Initialize user_data to None
    user = None
    user_data1 = None
    current_date_time = datetime.now()
    formatted_date = current_date_time.strftime("%d%m%Y")
    if request.method=='POST':
     answers = []
     prefix = 'question'
     for i in range(1,21):
        answers.append(request.form[prefix+str(i)])

     explanation = request.form['explanation']
     user = request.form['user_name']
     
     print(user)
    
     user_data1 = {
        formatted_date: answers,
        'explanation': explanation,
        'user_data' : user,
        'dob':formatted_date
     }
     users_mental_data.insert_one(user_data1)

     
     if current_user.is_authenticated:  # Check if the user is authenticated
    
            
            user = current_user.username
            questions = mental_question_collection.find()
            
            print('hello')
            print(current_user.username)
            user_answers = users_mental_data.find_one({'user_data':current_user.username}) 
            if user_answers != None:
                explanation = user_answers['explanation']
                stressed = predictor(user_answers['explanation'])
                user_answers = user_answers[formatted_date] 
                
                user_data1 = {
                    'questions' : questions,
                    'answers': user_answers,
                    'explanation': explanation,
                    'stressed': stressed,
                    'user_data' : user
                }
    else:
        if current_user.is_authenticated:  # Check if the user is authenticated
            user = current_user.username
            questions = mental_question_collection.find()
            user = current_user.username
            questions = mental_question_collection.find()
            print('hello')
            print(current_user.username)
            user_answers = users_mental_data.find_one({'user_data':current_user.username}) 
            if user_answers != None:
                explanation = user_answers['explanation']
                stressed = predictor(user_answers['explanation'])
                user_answers = user_answers[formatted_date] 
                
                user_data1 = {
                    'questions' : questions,
                    'answers': user_answers,
                    'explanation': explanation,
                    'stressed': stressed,
                    'user_data' : user
                }
                print(user_data)
    print(user_data)
    print('hi')

    return render_template('analysis.html',user_data1= user_data1,user_data=user_data)





# --------- doctor anaylysis ------------- 
@app.route('/analysis_doctor',methods=['GET','POST'])
def analysis_doctor():
    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})


    return render_template('analysis_doctor.html',user_data= user_data)




@app.route('/record',methods=['GET','POST'])
def record():
    user_data = None  # Initialize user_data to None
    
    date = request.form.get('d')
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d%m%Y")
    
    user_data1 = None
    # print('Ho')
    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})
        patient = request.form.get('patient')
        
        
        user_answers = users_mental_data.find({'dob':formatted_date}) 
        user_answer1 = user_answers[0] 
        user_answer2 = user_answers[1]
        print(user_answer1)
        print(user_answer2)
        # print(user_answers)
        if user_answers!=None:
            questions = mental_question_collection.find()
            q = []
            for question in questions:
               q.append(question['question_text'])
            
            user_data1 = {
                'answers':user_answer1[formatted_date],
                'question' : q,
                'user_data': patient,
                'date':formatted_date
            }
            user_data2 = {
                'answers':user_answer2[formatted_date],
                'question' : q,
                'user_data': patient,
                'date':formatted_date
            }
            print(user_answers)
            # Iterate over the cursor to access each document
            
             
            
        
        return render_template('record.html',user_data1 = user_data1,user_data= user_data,user_data2 = user_data2)








# ---------- Clinians ----------- 
@app.route('/clinitians',methods=['GET','POST'])
def clinitians():
    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})


    return render_template('clinitians.html',user_data= user_data)



# ---------- community ----------- 
@app.route('/community',methods=['GET','POST'])
def community():

    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})


    # Fetch all messages from users_community collection
    messages = users_community.find()

    return render_template('community.html', messages=messages,user_data=user_data)




@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    username = data['username']

    
    # Save message to MongoDB users_community collection
    users_community.insert_one({'username': username, 'message': message})
    return redirect(url_for('community'))










# --------- for handling booking ---------- 

@app.route('/handling_booking', methods=['POST','GET'])
def handle_booking():
    user_data = None  # Initialize user_data to None
    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})


    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data sent from the client-side JavaScript
        doctor_name = data.get('doctorName')  # Extract the doctor's name
        doctor_description = data.get('doctorDescription')  # Extract the doctor's description
        rating = data.get('rating')  # Extract the rating
        image_url = data.get('imageUrl')  # Extract the image URL


        # Pass the extracted data to the HTML template
        return render_template('book_appointment.html', doctor_name=doctor_name, doctor_description=doctor_description, rating=rating, image_url=image_url,user_data=user_data)

    elif request.method == 'GET':
        doctor_name = request.args.get('doctorName')
        doctor_description = request.args.get('doctorDescription')
        rating = request.args.get('rating')
        image_url = request.args.get('imageUrl')
        # print(doctor_name)
        # print(doctor_description)
        # print(image_url)
        # If the route is accessed with a GET request (e.g., when rendering a template)
        # You can render the template here
        return render_template('book_appointment.html',doctor_name=doctor_name, doctor_description=doctor_description, rating=rating, image_url=image_url,user_data=user_data)
        








# ----------- submit appointment ----------------
@app.route('/submit_appointment', methods=['POST','GET'])
def submit_appointment():

    time_slot = None
    concern = None
    google_meet_link = None
    doctor_name = None

    if request.method == 'POST':
      username = request.form['username']
      doctor_name = request.form['doctor_name']
      time_slot = request.form['time_slot']
      concern = request.form['concern']
    #   print(username)
    #   print(time_slot)
    #   print(concern)
      # Insert the data into the appointment collection
      # Generate a unique Google Meet link
      google_meet_link = f'https://meet.google.com/{uuid.uuid4()}'
      appointment_data = {
            'username': username,
            'time_slot': time_slot,
            'concern': concern,
            'google_meet_link': google_meet_link,
            'doctor_name': doctor_name
       }
      appointments_collection.insert_one(appointment_data)      

      user_data = users_collection.find_one({'username': username})



      # Send the Google Meet link to the user's email
      user_data = users_collection.find_one({'username': username})
      if user_data and 'email' in user_data:
            send_email(user_data['email'], google_meet_link)    
      


        # Pass the extracted data to the HTML template
    return render_template('profile.html',user_data=user_data,time_slot=time_slot,concern=concern,google_meet_link=google_meet_link,doctor_name=doctor_name)


def send_email(receiver_email, google_meet_link):
    # Configure SMTP server settings
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'pranavkolhe44@gmail.com'  # Admin email address
    sender_password = 'rwlw qkfk xwqe jeir'  # Update with your email password

    # Create SMTP server object
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Compose email message
    subject = 'Google Meet Link for Appointment'
    body = f'Here is your Google Meet link for the appointment: {google_meet_link}'
    message = f'Subject: {subject}\n\n{body}'

    # Send email
    server.sendmail(sender_email, receiver_email, message)

    # Close SMTP server connection
    server.quit()









# --------------- set goals by admin ------ 
@app.route('/set_goals',methods = ['POST','GET'])
def set_goals():
    user_data = None

    if current_user.is_authenticated:
        user_data = users_collection.find_one({'username': current_user.username})
    return render_template('set_goals.html',user_data=user_data)



# --------------- search patient by doctor ------ 
@app.route('/search_patient', methods=['POST', 'GET'])
def search_patient():
    user_data = None
    patient_data = None

    if current_user.is_authenticated:
        user_data = users_collection.find_one({'username': current_user.username})

    if request.method == 'POST':
        username = request.form['username']
        patient_data = appointments_collection.find_one({'username': username})

    if patient_data:
        # Prepare patient data as JSON
        patient_details = {
            'name': patient_data.get('username', ''),
            'concern': patient_data.get('concern', '')
        }
    else:
        # Handle the case where the patient is not found
        patient_details = {
            'error': 'Patient not found'
        }

    # Return patient details as JSON response
    return jsonify(patient_details)










# -------------- add_goals------------
@app.route('/add_goal', methods=['POST'])
def add_goal():
    # Retrieve data from the AJAX request
    username = request.form['username']
    goal_text = request.form['goal_text']
    goal_id = request.form['goal_id']

    # Assuming you have a collection named 'goals'
    # You will need to update this to match your actual collection name
    goals_collection = db.goals

    # Update the document in the goals collection, or insert it if it doesn't exist
    result = goals_collection.update_one(
        {'username': username},
        {'$push': {goal_id: goal_text}},
        upsert=True
    )

    if result.upserted_id is not None:
        message = 'Goal inserted successfully'
    else:
        message = 'Goal updated successfully'

    return jsonify({'message': message})










# ----------- search track goals done by user ---------- 
@app.route('/search', methods=['POST','GET'])
def search():
    user_data = None

    if current_user.is_authenticated:
        user_data = users_collection.find_one({'username': current_user.username})
    if request.method=='POST':
     username = request.form.get('username')
     user_data = goals_done.find({'username': username})
    #  for temp in user_data:
    #   print(temp)
     return render_template('results.html', username=username, user_data=user_data)
    if request.method=='GET':
     return render_template('search.html',user_data=user_data)







if __name__ == '__main__':
    app.run(debug=True, port=5001)