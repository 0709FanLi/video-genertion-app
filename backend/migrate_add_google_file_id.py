#!/usr/bin/env python3
"""数据库迁移脚本：添加 google_file_id 字段到 user_videos 表."""

import sys
from sqlalchemy import text, inspect
from app.database.session import engine, Base
from app.models import UserVideo


def add_google_file_id_column():
    """添加 google_file_id 字段到 user_videos 表."""
    # 检查表是否存在
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'user_videos' not in tables:
        print("⚠️  user_videos 表不存在，将自动创建（包含 google_file_id 字段）")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        return
    
    # 检查字段是否已存在
    columns = [col['name'] for col in inspector.get_columns('user_videos')]
    
    if 'google_file_id' in columns:
        print("✅ google_file_id 字段已存在，跳过迁移")
        return
    
    # 添加字段
    print("开始添加 google_file_id 字段...")
    with engine.connect() as conn:
        try:
            # SQLite 语法
            conn.execute(text("ALTER TABLE user_videos ADD COLUMN google_file_id VARCHAR(100)"))
            conn.commit()
            print("✅ 字段添加成功")
            
            # 创建索引
            try:
                conn.execute(text("CREATE INDEX idx_user_videos_google_file_id ON user_videos(google_file_id)"))
                conn.commit()
                print("✅ 索引创建成功")
            except Exception as e:
                print(f"⚠️  索引创建失败（可能已存在）: {e}")
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移：添加 google_file_id 字段")
    print("=" * 50)
    add_google_file_id_column()
    print("=" * 50)
    print("迁移完成！")
    print("=" * 50)

