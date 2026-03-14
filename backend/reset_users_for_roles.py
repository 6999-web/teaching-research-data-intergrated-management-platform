from app.db.base import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def main() -> None:
  """
  Create / ensure a minimal set of role-based accounts for local development.

  This script will NOT delete existing users (以免破坏外键约束和历史日志)，
  只会在当前库中补充一组标准账号，方便你登录不同端口进行测试：

  - teaching_office_1      (role=teaching_office)
  - eval_team_1, eval_team_2   (role=evaluation_team)
  - eval_office_1          (role=evaluation_office)
  - president_office_1     (role=president_office)

  所有账号默认密码：123456
  """
  db = SessionLocal()
  try:
    password = get_password_hash("123456")

    new_users = [
      User(
        username="teaching_office_1",
        password_hash=password,
        role="teaching_office",
        name="教研室账号",
        email="teaching_office_1@test.com",
      ),
      User(
        username="teaching_office_2",
        password_hash=password,
        role="teaching_office",
        name="教研室账号2",
        email="teaching_office_2@test.com",
      ),
      User(
        username="eval_team_1",
        password_hash=password,
        role="evaluation_team",
        name="评教小组账号1",
        email="eval_team_1@test.com",
      ),
      User(
        username="eval_team_2",
        password_hash=password,
        role="evaluation_team",
        name="评教小组账号2",
        email="eval_team_2@test.com",
      ),
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
      ),
    ]

    created_or_updated = []
    for u in new_users:
      existing = db.query(User).filter(User.username == u.username).first()
      if existing:
        # 更新角色和密码，保证可用
        existing.role = u.role
        existing.password_hash = password
        existing.name = u.name
        existing.email = u.email
        created_or_updated.append(existing)
      else:
        db.add(u)
        created_or_updated.append(u)

    db.commit()
    print("标准账号已创建/更新成功（密码均为: 123456）")
    for u in created_or_updated:
      print(f" - {u.username} ({u.role})")

  finally:
    db.close()


if __name__ == "__main__":
  main()

