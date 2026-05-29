-- 招聘数据库初始化脚本
-- 执行此脚本创建数据库和表结构

-- 创建数据库（指定utf8mb4避免中文乱码）
CREATE DATABASE IF NOT EXISTS recruitment_db 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 切换到目标数据库
USE recruitment_db;

-- 创建招聘数据表
CREATE TABLE IF NOT EXISTS recruitment_data (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    企业名称 VARCHAR(255) COMMENT '企业名称',
    招聘岗位 VARCHAR(255) COMMENT '招聘岗位',
    工作城市 VARCHAR(100) COMMENT '工作城市',
    最低月薪 DECIMAL(10,2) COMMENT '最低月薪',
    最高月薪 DECIMAL(10,2) COMMENT '最高月薪',
    职位描述 TEXT COMMENT '职位描述',
    学历要求 VARCHAR(50) COMMENT '学历要求',
    要求经验 VARCHAR(50) COMMENT '要求经验',
    招聘类别 VARCHAR(50) COMMENT '招聘类别',
    初级分类 VARCHAR(100) COMMENT '初级分类',
    招聘发布日期 VARCHAR(50) COMMENT '招聘发布日期',
    招聘发布年份 INT COMMENT '招聘发布年份',
    来源 VARCHAR(100) COMMENT '数据来源',
    学历要求_排序 INT COMMENT '学历要求排序',
    要求经验_排序 INT COMMENT '要求经验排序',
    平均月薪 DECIMAL(10,2) COMMENT '平均月薪',
    薪资浮动 DECIMAL(10,2) COMMENT '薪资浮动',
    薪资等级 VARCHAR(50) COMMENT '薪资等级',
    企业规模 VARCHAR(100) COMMENT '企业规模',
    行业类型 VARCHAR(100) COMMENT '行业类型',
    年终奖估算 DECIMAL(10,2) COMMENT '年终奖估算',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据导入时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='招聘数据总表';

-- 创建索引优化查询性能
CREATE INDEX idx_company ON recruitment_data(企业名称);
CREATE INDEX idx_position ON recruitment_data(招聘岗位);
CREATE INDEX idx_city ON recruitment_data(工作城市);
CREATE INDEX idx_education ON recruitment_data(学历要求);
CREATE INDEX idx_experience ON recruitment_data(要求经验);
CREATE INDEX idx_industry ON recruitment_data(行业类型);
CREATE INDEX idx_salary ON recruitment_data(平均月薪);

-- 显示表结构
DESCRIBE recruitment_data;

-- 显示创建成功信息
SELECT '数据库和表创建成功！' AS message;
