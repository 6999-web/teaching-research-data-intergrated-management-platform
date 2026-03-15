"""
修复教研室用户与教研室的关联

将 teaching_office_1 ~ teaching_office_6 分别关联到 教研室1 ~ 教研室6
"""

from app.db.base import SessionLocal
from app.models.user import User
from app.models.teaching_office import TeachingOffice
from sqlalchemy import text

def main():
    db = SessionLocal()
    try:
        # 获取所有教研室，按名称排序
        offices = db.query(TeachingOffice).order_by(TeachingOffice.name.asc()).all()
        print(f"找到 {len(offices)} 个教研室:")
        for o in offices:
            print(f"  {o.name}: {o.id}")

        if len(offices) < 6:
            print("教研室数量不足6个，需要先创建教研室！")
            return

        # 获取所有 teaching_office 角色用户，按用户名排序
        users = db.query(User).filter(User.role == "teaching_office").order_by(User.username.asc()).all()
        print(f"\n找到 {len(users)} 个教研室用户:")
        for u in users:
            print(f"  {u.username}: teaching_office_id={u.teaching_office_id}")

        # 尝试按名字匹配（teaching_office_1 -> 教研室1，teaching_office_2 -> 教研室2 ...）
        office_map = {}
        for o in offices:
            # 提取数字，例如 "教研室1" 中的 "1"
            import re
            match = re.search(r'\d+', o.name)
            if match:
                num = int(match.group())
                office_map[num] = o

        print(f"\n教研室映射: {[(k, v.name) for k, v in office_map.items()]}")

        # 更新每个用户
        for u in users:
            match = re.search(r'\d+', u.username)
            if match:
                num = int(match.group())
                if num in office_map:
                    old_id = u.teaching_office_id
                    u.teaching_office_id = office_map[num].id
                    print(f"  {u.username}: {old_id} -> {office_map[num].id} ({office_map[num].name})")
                else:
                    print(f"  警告：未找到匹配的教研室(num={num}) for {u.username}")
            else:
                print(f"  警告：无法从用户名提取数字: {u.username}")

        db.commit()
        print("\n✅ 关联成功！")

        # 验证
        print("\n验证结果：")
        users = db.query(User).filter(User.role == "teaching_office").order_by(User.username.asc()).all()
        for u in users:
            print(f"  {u.username}: teaching_office_id={u.teaching_office_id}")

    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import re
    main()
