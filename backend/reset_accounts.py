from app.db.base import SessionLocal, engine
from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.core.security import get_password_hash
from sqlalchemy import text
import uuid

def main():
    db = SessionLocal()
    try:
        if "mysql" in engine.url.drivername:
            db.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
            db.execute(text("TRUNCATE TABLE users;"))
            db.execute(text("TRUNCATE TABLE teaching_offices;"))
            db.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        else:
            db.execute(text("DELETE FROM users;"))
            db.execute(text("DELETE FROM teaching_offices;"))

        pw = get_password_hash("123456")

        offices = []
        for i in range(1, 7):
            o = TeachingOffice(id=uuid.uuid4(), name=f"教研室{i}", code=f"TR00{i}", department=f"学院{i}")
            offices.append(o)
            db.add(o)
        
        db.commit()

        users = []
        # 6 teaching office users
        for i in range(1, 7):
            u = User(
                username=f"office{i}",
                password_hash=pw,
                role="teaching_office",
                name=f"教研室端{i}",
                teaching_office_id=offices[i-1].id
            )
            users.append(u)

        # 2 eval teams
        for i in range(1, 3):
            u = User(
                username=f"eval_team{i}",
                password_hash=pw,
                role="evaluation_team",
                name=f"评教小组{i}"
            )
            users.append(u)

        # 1 eval office
        u_eval_office = User(
            username="eval_office_1",
            password_hash=pw,
            role="evaluation_office",
            name="评教小组办公室"
        )
        users.append(u_eval_office)

        # 1 president office
        u_president = User(
            username="president_office_1",
            password_hash=pw,
            role="president_office",
            name="校长办公室"
        )
        users.append(u_president)

        for u in users:
            db.add(u)
        
        db.commit()
        print("账号重置成功！所有账号密码为 123456")
        for u in users:
            print(f"{u.role}: {u.username}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
