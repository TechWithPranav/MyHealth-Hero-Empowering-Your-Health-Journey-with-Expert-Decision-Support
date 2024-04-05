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







if __name__ == '__main__':
    app.run(debug=True, port=5001)