from app.db.base import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import text

def main() -> None:
    db = SessionLocal()
    try:
        # Delete all existing users as requested
        # First disable foreign key checks temporarily if possible (sqlite/mysql)
        engine_name = db.get_bind().dialect.name
        if engine_name == 'sqlite':
            db.execute(text("PRAGMA foreign_keys = OFF;"))
        elif engine_name == 'mysql':
            db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
        db.execute(text("DELETE FROM users;"))
        
        if engine_name == 'sqlite':
            db.execute(text("PRAGMA foreign_keys = ON;"))
        elif engine_name == 'mysql':
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            
        db.commit()

        password = get_password_hash("123456")

        new_users = [
            User(
                username=f"teaching_office_{i}",
                password_hash=password,
                role="teaching_office",
                name=f"教研室账号{i}",
                email=f"teaching_office_{i}@test.com",
            ) for i in range(1, 7)
        ] + [
            User(
                username=f"eval_team_{i}",
                password_hash=password,
                role="evaluation_team",
                name=f"评教小组账号{i}",
                email=f"eval_team_{i}@test.com",
            ) for i in range(1, 3)
        ] + [
            User(
                username="eval_office_1",
                password_hash=password,
                role="evaluation_office",
                name="评教小组办公室账号",
                email="eval_office_1@test.com",
            ),
            User(
                username="president_office_1",
                password_hash=password,
                role="president_office",
                name="校长办公室账号",
                email="president_office_1@test.com",
            )
        ]

        for u in new_users:
            db.add(u)

        db.commit()
        print("已成功删除所有旧账号，并重新设立以下账号（统一密码: 123456）：")
        for u in new_users:
            print(f" - {u.username} ({u.role})")

    except Exception as e:
        print(f"账号重置失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

