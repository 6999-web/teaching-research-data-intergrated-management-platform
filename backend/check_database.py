"""
快速查看MySQL数据库内容

使用方法：
    python check_database.py
"""

import pymysql
from app.core.config import settings

def check_database():
    """检查数据库连接和表结构"""
    
    print("=" * 80)
    print("MySQL数据库检查工具")
    print("=" * 80)
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=settings.MYSQL_SERVER,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset='utf8mb4'
        )
        
        print(f"\n✅ 成功连接到数据库: {settings.MYSQL_DB}")
        print(f"   服务器: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
        print(f"   用户: {settings.MYSQL_USER}")
        
        cursor = connection.cursor()
        
        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n📊 数据库中的表（共 {len(tables)} 个）:")
        print("-" * 80)
        
        table_info = []
        
        for (table_name,) in tables:
            # 获取表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # 获取表的列数
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_count = len(columns)
            
            table_info.append([table_name, count, column_count])
        
        # 打印表格
        print(f"{'表名':<30} {'记录数':<10} {'字段数':<10}")
        print("-" * 80)
        for name, count, cols in table_info:
            print(f"{name:<30} {count:<10} {cols:<10}")
        
        # 显示每个表的详细结构
        print("\n" + "=" * 80)
        print("表结构详情")
        print("=" * 80)
        
        for (table_name,) in tables:
            print(f"\n📋 表: {table_name}")
            print("-" * 80)
            
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"{'字段名':<25} {'类型':<20} {'NULL':<8} {'键':<8} {'默认值':<15} {'额外':<15}")
            print("-" * 80)
            for col in columns:
                field, type_, null, key, default, extra = col
                print(f"{field:<25} {type_:<20} {null:<8} {key:<8} {str(default or ''):<15} {str(extra or ''):<15}")
        
        # 显示外键关系
        print("\n" + "=" * 80)
        print("外键关系")
        print("=" * 80)
        
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE
                REFERENCED_TABLE_SCHEMA = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME
        """, (settings.MYSQL_DB,))
        
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print(f"{'表名':<30} {'字段':<30} {'引用':<40}")
            print("-" * 80)
            for fk in foreign_keys:
                table, column, ref_table, ref_column = fk
                print(f"{table:<30} {column:<30} {ref_table}.{ref_column:<40}")
        else:
            print("未找到外键关系")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 80)
        print("✅ 数据库检查完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n请检查:")
        print("  1. MySQL服务是否正在运行")
        print("  2. 数据库配置是否正确 (backend/.env)")
        print("  3. 用户名和密码是否正确")


if __name__ == "__main__":
    check_database()
