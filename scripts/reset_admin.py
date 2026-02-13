import sys
import os
import logging
from pathlib import Path

# Add backend to sys.path
current_dir = Path(os.getcwd())
backend_dir = current_dir / "backend"
sys.path.append(str(backend_dir))

# Suppress logging
logging.getLogger("open_webui").setLevel(logging.ERROR)
logging.getLogger("multipart").setLevel(logging.ERROR)
logging.getLogger("uvicorn").setLevel(logging.ERROR)

from open_webui.internal.db import get_db
from open_webui.models.users import Users
from open_webui.models.auths import Auths
from open_webui.utils.auth import get_password_hash

def main():
    email_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    # We use a single session
    with get_db() as db:
        if email_arg:
            user = Users.get_user_by_email(email_arg, db=db)
            if not user:
                print(f"Error: User with email '{email_arg}' not found.")
                return

            print(f"Found user: {user.name} ({user.email}) Role: {user.role}")
            new_password = "password"
            hashed = get_password_hash(new_password)
            
            # Update password
            if Auths.update_user_password_by_id(user.id, hashed, db=db):
                print(f"Successfully reset password for '{user.email}' to '{new_password}'")
            else:
                print("Failed to update password in Auth table.")
                
        else:
            print("No email provided. Listing all users:")
            users_data = Users.get_users(db=db)
            users = users_data.get('users', [])
            
            if not users:
                print("No users found in database.")
                return
                
            for u in users:
                print(f"- Name: {u.name}, Email: {u.email}, Role: {u.role}, ID: {u.id}")
            
            print("\nUsage: python scripts/reset_admin.py <email> to reset password to 'password'")

if __name__ == "__main__":
    main()
