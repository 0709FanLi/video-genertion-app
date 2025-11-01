-- 添加 google_file_id 字段到 user_videos 表
-- 如果字段已存在，会报错但不会影响功能

ALTER TABLE user_videos 
ADD COLUMN IF NOT EXISTS google_file_id VARCHAR(100) NULL;

-- 创建索引以加快查询速度
CREATE INDEX IF NOT EXISTS idx_user_videos_google_file_id 
ON user_videos(google_file_id);

