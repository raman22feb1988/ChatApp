import requests
import server_script

# Set the API endpoint URL
API_ENDPOINT = 'http://localhost:5000'

# Function to register a new user
def register(username, password):
    url = API_ENDPOINT + '/register'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    return response.json()

# Function to authenticate a user
def login(username, password):
    url = API_ENDPOINT + '/login'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    return response.json()

# Function to create a new group
def create_group(name, admin_id):
    url = API_ENDPOINT + '/groups'
    data = {'name': name, 'admin_id': admin_id}
    response = requests.post(url, json=data)
    return response.json()

# Function to add a user to a group
def add_user_to_group(group_id, user_id):
    url = API_ENDPOINT + f'/groups/{group_id}/users'
    data = {'user_id': user_id}
    response = requests.post(url, json=data)
    return response.json()

# Function to remove a user from a group
def remove_user_from_group(group_id, user_id):
    url = API_ENDPOINT + f'/groups/{group_id}/users/{user_id}'
    response = requests.delete(url)
    return response.json()

# Function to send a message to a user
def send_message(sender_id, receiver_id, content):
    url = API_ENDPOINT + f'/users/{receiver_id}/messages'
    data = {'sender_id': sender_id, 'content': content}
    response = requests.post(url, json=data)
    return response.json()

# Function to send a message to a group
def send_group_message(sender_id, group_id, content):
    url = API_ENDPOINT + f'/groups/{group_id}/messages'
    data = {'sender_id': sender_id, 'content': content}
    response = requests.post(url, json=data)
    return response.json()

# Function to get all groups
def get_groups():
    url = API_ENDPOINT + '/groups'
    response = requests.get(url)
    return response.json()

# Function to get group members
def get_group_members(group_id):
    url = API_ENDPOINT + f'/groups/{group_id}/users'
    response = requests.get(url)
    return response.json()

# Function to get user messages
def get_user_messages(user_id):
    url = API_ENDPOINT + f'/users/{user_id}/messages'
    response = requests.get(url)
    return response.json()

# Function to get group messages
def get_group_messages(group_id):
    url = API_ENDPOINT + f'/groups/{group_id}/messages'
    response = requests.get(url)
    return response.json()

# Example usage
if __name__ == '__main__':
    # Register a new user
    register('alice', 'password123')
    
    # Authenticate the user
    response = login('alice', 'password123')
    user_id = response['user_id']
    
    # Create a new group
    create_group('Group 1', user_id)
    
    # Add a user to the group
    add_user_to_group(1, 2)
    
    # Send a message to a user
    send_message(1, 2, 'Hello!')
    
    # Send a message to a group
    send_group_message(1, 1, 'Hello everyone!')
    
    # Get all groups
    groups = get_groups()
    print(groups)