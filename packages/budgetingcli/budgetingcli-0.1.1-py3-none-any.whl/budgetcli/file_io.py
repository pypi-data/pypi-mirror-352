import os, json, hashlib
from platformdirs import user_data_dir

APP_NAME = "budgetcli"
APP_AUTHOR = "budgetcli"

def get_user_file_path(username):
    data_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, f"{username}.json")

def get_user(username, password=None):
    """Get user from local JSON file"""
    user_file = get_user_file_path(username)
    if not os.path.exists(user_file):
        return None
    
    with open(user_file, 'r') as f:
        user_data = eval(f.read())  # Consider using json.load for safety

    if password:
        hash_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if user_data.get('password') == hash_password:
            return user_data
        else:
            return None
    return user_data

def create_user(username, password):
    """Create a user and store it locally"""
    hash_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user_data = {
        'username': username,
        'password': hash_password,
        'goals': {},
        'spending': {},
        'notes': [],
        'current_streak': 0,
        'max_streak': 0,
        'streak_phrases': [
            f"Good job {username} :D",
            f"WOOOOOOO {username}! LET'S GOOOOOOO!",
            f"Woowwwwww you are doing so well {username}!",
            f"Keep it up {username}!",
            f"Keep going {username}!",
        ],
        'streak_reset_phrases': [
            f"Don't worry {username}, you got this!",
            f"Keep trying {username}, you can do it!",
            f"Don't give up {username}!",
            f"If you did it once you can do it again {username}!",
        ]
    }
    user_file = get_user_file_path(username)
    with open(user_file, 'w') as f:
        f.write(str(user_data))  # Optional: switch to json.dump for stricter format
    return user_data

def update_user(username, user_data):
    """Update a user's data"""
    user_file = get_user_file_path(username)
    with open(user_file, 'w') as f:
        f.write(str(user_data))
