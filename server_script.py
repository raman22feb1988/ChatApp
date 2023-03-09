from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to database
conn = sqlite3.connect('C:\\Python27\\chat.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create groups table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        admin_id INTEGER NOT NULL,
        FOREIGN KEY (admin_id) REFERENCES users(id)
    )
''')

# Create group_users table to track group memberships
cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_users (
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create messages table to store chat messages
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        group_id INTEGER,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id),
        FOREIGN KEY (group_id) REFERENCES groups(id)
    )
''')

# Function to create a new user
def create_user(username, password):
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to authenticate a user
def authenticate_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user is not None:
        return user[0] # Return user id
    else:
        return None

# Function to create a new group
def create_group(name, admin_id):
    try:
        cursor.execute('INSERT INTO groups (name, admin_id) VALUES (?, ?)', (name, admin_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to add a user to a group
def add_user_to_group(group_id, user_id):
    try:
        cursor.execute('INSERT INTO group_users (group_id, user_id) VALUES (?, ?)', (group_id, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to remove a user from a group
def remove_user_from_group(group_id, user_id):
    cursor.execute('DELETE FROM group_users WHERE group_id = ? AND user_id = ?', (group_id, user_id))
    conn.commit()

# Function to send a message
def send_message(sender_id, receiver_id, content):
    cursor.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)', (sender_id, receiver_id, content))
    conn.commit()

# Function to send a group message
def send_group_message(sender_id, group_id, content):
    cursor.execute('SELECT user_id FROM group_users WHERE group_id = ?', (group_id,))
    for row in cursor.fetchall():
        receiver_id = row[0]
        cursor.execute('INSERT INTO messages (sender_id, receiver_id, group_id, content) VALUES (?, ?, ?, ?)', (sender_id, receiver_id, group_id, content))
    conn.commit()

# Function to get all groups
def get_groups():
    cursor.execute('SELECT * FROM groups')
    return cursor.fetchall()

# Function to get group members
def get_group_members(group_id):
    cursor.execute('SELECT users.id, users.username FROM users JOIN group_users ON users.id = group_users.user_id WHERE group_users.group_id = ?', (group_id,))
    return cursor.fetchall()

# Function to get user messages
def get_user_messages(user_id):
    cursor.execute('SELECT messages.id, users.username, messages.content, messages.timestamp FROM messages JOIN users ON messages.sender_id = users.id WHERE messages.receiver_id = ?', (user_id,))
    return cursor.fetchall()

# Function to get group messages
def get_group_messages(group_id):
    cursor.execute('SELECT messages.id, users.username, messages.content, messages.timestamp FROM messages JOIN users ON messages.sender_id = users.id WHERE messages.group_id = ?', (group_id,))
    return cursor.fetchall()

# API endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    if create_user(username, password):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Username already exists'})

# API endpoint to authenticate a user
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user_id = authenticate_user(username, password)
    if user_id is not None:
        return jsonify({'success': True, 'user_id': user_id})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})

# API endpoint to create a new group
@app.route('/groups', methods=['POST'])
def create_group_endpoint():
    name = request.json['name']
    admin_id = request.json['admin_id']
    if create_group(name, admin_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Group name already exists'})

# API endpoint to add a user to a group
@app.route('/groups/int:group_id/users', methods=['POST'])
def add_user_to_group_endpoint(group_id):
    user_id = request.json['user_id']
    if add_user_to_group(group_id, user_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'User already in group'})

# API endpoint to remove a user from a group
@app.route('/groups/int:group_id/users/int:user_id', methods=['DELETE'])
def remove_user_from_group_endpoint(group_id, user_id):
    remove_user_from_group(group_id, user_id)
    return jsonify({'success': True})

# API endpoint to send a message to a user
@app.route('/users/int:receiver_id/messages', methods=['POST'])
def send_message_endpoint(receiver_id):
    sender_id = request.json['sender_id']
    content = request.json['content']
    send_message(sender_id, receiver_id, content)
    return jsonify({'success': True})

# API endpoint to send a message to a group
@app.route('/groups/int:group_id/messages', methods=['POST'])
def send_group_message_endpoint(group_id):
    sender_id = request.json['sender_id']
    content = request.json['content']
    send_group_message(sender_id, group_id, content)
    return jsonify({'success': True})

# API endpoint to get all groups
@app.route('/groups', methods=['GET'])
def get_groups_endpoint():
    groups = get_groups()
    return jsonify(groups)

# API endpoint to get group members
@app.route('/groups/int:group_id/users', methods=['GET'])
def get_group_members_endpoint(group_id):
    members = get_group_members(group_id)
    return jsonify(members)

# API endpoint to get user messages
@app.route('/users/int:user_id/messages', methods=['GET'])
def get_user_messages_endpoint(user_id):
    messages = get_user_messages(user_id)
    return jsonify(messages)

# API endpoint to get group messages
@app.route('/groups/int:group_id/messages', methods=['GET'])
def get_group_messages_endpoint(group_id):
    messages = get_group_messages(group_id)
    return jsonify(messages)

if __name__ == '__main__':
    app.run()