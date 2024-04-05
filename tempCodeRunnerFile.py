@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    username = data['username']

    
    # Save message to MongoDB users_community collection
    users_community.insert_one({'username': username, 'message': message})
    return redirect(url_for('community'))