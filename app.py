import secrets
import os
from flask import Flask, render_template, redirect, request, session, url_for, flash,jsonify
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin,current_user
from bson import ObjectId  # Import ObjectId from bson module

import uuid  # For generating unique IDs
import smtplib  # For sending emails


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



login_manager = LoginManager()
login_manager.init_app(app)

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

     return render_template('profile.html', user_data=user_data, doctor_name=doctor_name, time_slot=time_slot, concern=concern, google_meet_link=google_meet_link,goal_1=goal_1,goal_2=goal_2,goal_3=goal_3,goal_4=goal_4,goal_5=goal_5)

   # Handle POST requests
   if request.method == 'POST':
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

   return render_template('profile.html', user_data=user_data, doctor_name=doctor_name, time_slot=time_slot, concern=concern, google_meet_link=google_meet_link,goal_1=goal_1,goal_2=goal_2,goal_3=goal_3,goal_4=goal_4,goal_5=goal_5)
  

    # goal_1 =None       
    # goal_2 =None    
    # goal_3=None      
    # goal_4=None     
    # goal_5 =None  



    # g1 = None
    # g2 = None
    # g3 = None
    # g4 = None
    # g5 = None


    # # Initialize index variables
    # if 'i1' not in session:
    #     session['i1'] = 0
    # if 'i2' not in session:
    #     session['i2'] = 0
    # if 'i3' not in session:
    #     session['i3'] = 0
    # if 'i4' not in session:
    #     session['i4'] = 0
    # if 'i5' not in session:
    #     session['i5'] = 0    

    # if current_user.is_authenticated:
    #     user_data = users_collection.find_one({'username': current_user.username})
    #     appointments_data = appointments_collection.find_one({'username': current_user.username})
    #     goals_collection_main = goals_collection.find_one({'username': current_user.username})

    # doctor_name = None
    # time_slot = None
    # concern = None
    # google_meet_link = None

    # g1 = request.form.get('goal1_main')

    # g2 = request.form.get('goal2_main')

    # g3 = request.form.get('goal3_main')

    # g4 = request.form.get('goal4_main')
    
    # g5 = request.form.get('goal5_main')

    # print(i1)
    # print(i2)
    # print(i3)
    # print(i4)
    # print(i5)

    # if g1:
    #     session['i1'] += 1
    # if g2:
    #     session['i2'] += 1
    # if g3:
    #     session['i3'] += 1
    # if g4:
    #     session['i4'] += 1
    # if g5:
    #     session['i5'] += 1


    
    # if appointments_data:
    #     doctor_name = appointments_data.get('doctor_name')
    #     time_slot = appointments_data.get('time_slot')
    #     concern = appointments_data.get('concern')
    #     google_meet_link = appointments_data.get('google_meet_link')

    # if goals_collection_main:
    #     # Fetch goal1 and get the first goal from the array
    #     goal1 = goals_collection_main.get('goal1', [])
    #     goal2 = goals_collection_main.get('goal2', [])
    #     goal3 = goals_collection_main.get('goal3', [])
    #     goal4 = goals_collection_main.get('goal4', [])
    #     goal5 = goals_collection_main.get('goal5', [])

    #     if goal1 and len(goal1) > session['i1']:
    #      goal_1 = goal1[session['i1']]
    #     if goal2 and len(goal2) > session['i2']:
    #         goal_2 = goal2[session['i2']]
    #     if goal3 and len(goal3) > session['i3']:
    #         goal_3 = goal3[session['i3']]
    #     if goal4 and len(goal4) > session['i4']:
    #         goal_4 = goal4[session['i4']]
    #     if goal5 and len(goal5) > session['i5']:
    #         goal_5 = goal5[session['i5']]


    # # print(goal_1)  # Print goal for debugging        
    # # print(goal_2)  # Print goal for debugging        
    # # print(goal_3)  # Print goal for debugging        
    # # print(goal_4)  # Print goal for debugging        
    # # print(goal_5)  # Print goal for debugging        

    # # print(appointments_data)  # Print appointments_data for debugging
  
    # return render_template('profile.html', user_data=user_data, doctor_name=doctor_name, time_slot=time_slot, concern=concern, google_meet_link=google_meet_link,goal_1=goal_1,goal_2=goal_2,goal_3=goal_3,goal_4=goal_4,goal_5=goal_5)
  





# ---------- mental test ----------- 
@app.route('/mental',methods=['GET','POST'])
def mental():
    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})

    return render_template('mental.html',user_data= user_data)



# ---------- Analysis ----------- 
@app.route('/analysis',methods=['GET','POST'])
def analysis():
    user_data = None  # Initialize user_data to None

    if current_user.is_authenticated:  # Check if the user is authenticated
        user_data = users_collection.find_one({'username': current_user.username})


    return render_template('analysis.html',user_data= user_data)




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

    # Prepare patient data as JSON
    patient_details = {
        'name': patient_data.get('username', ''),
        'concern': patient_data.get('concern', '')
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










if __name__ == '__main__':
    app.run(debug=True, port=5001)