import secrets
import os
from flask import Flask, render_template, redirect, request, session, url_for, flash,jsonify
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin,current_user
from bson import ObjectId  # Import ObjectId from bson module



app = Flask(__name__)

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
    return render_template('index.html')




# ------------- profile ------------- 

@app.route('/profile',methods = ['GET','POST'])
def profile():

    user_data = users_collection.find_one({'username':current_user.username})
    return render_template('profile.html',user_data= user_data)    





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
        print(doctor_name)
        print(doctor_description)
        print(image_url)
        # If the route is accessed with a GET request (e.g., when rendering a template)
        # You can render the template here
        return render_template('book_appointment.html',doctor_name=doctor_name, doctor_description=doctor_description, rating=rating, image_url=image_url,user_data=user_data)
        








# ----------- submit appointment ----------------
@app.route('/submit_appointment', methods=['POST','GET'])
def submit_appointment():

    if request.method == 'POST':
      username = request.form['username']
      time_slot = request.form['time_slot']
      concern = request.form['concern']
      print(username)
      print(time_slot)
      print(concern)
      # Insert the data into the appointment collection
      appointment_data = {
            'username': username,
            'time_slot': time_slot,
            'concern': concern
       }
      appointments_collection.insert_one(appointment_data)      

      user_data = users_collection.find_one({'username': username})

      


        # Pass the extracted data to the HTML template
    return render_template('profile.html',user_data=user_data)













if __name__ == '__main__':
    app.run(debug=True, port=5001)