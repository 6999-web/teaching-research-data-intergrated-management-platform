import sys
sys.path.insert(0, 'backend')

from app.models.user import User
from app.db.base import SessionLocal
from app.core.security import verify_password

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'director1').first()
    if user:
        print(f'Username: {user.username}')
        print(f'Role: {user.role}')
        print(f'Name: {user.name}')
        print(f'Teaching Office ID: {user.teaching_office_id}')
        print(f'Password verification: {verify_password("password123", user.password_hash)}')
    else:
        print('User director1 not found')
        # List all users
        all_users = db.query(User).all()
        print(f'\nAll users in database:')
        for u in all_users:
            print(f'  - {u.username}: {u.role}')
finally:
    db.close()
