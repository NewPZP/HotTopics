-- 智览平台 — 数据库初始化 SQL
-- 用法: mysql -u root -p < configs/init.sql

CREATE DATABASE IF NOT EXISTS wisdom_view CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wisdom_view;

-- ============================================
-- 表结构
-- ============================================

CREATE TABLE IF NOT EXISTS raw_articles (
    id VARCHAR(64) PRIMARY KEY,
    source VARCHAR(64) NOT NULL COMMENT '来源: newsapi / crawler / rss',
    title VARCHAR(512) NOT NULL,
    content TEXT,
    url VARCHAR(1024),
    published_at DATETIME,
    author VARCHAR(128),
    language VARCHAR(16),
    topic_tags JSON,
    raw_data JSON,
    url_hash VARCHAR(64) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(32) DEFAULT 'raw' COMMENT 'raw / processed / discarded',
    INDEX idx_url_hash (url_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS processed_articles (
    id VARCHAR(64) PRIMARY KEY,
    raw_article_id VARCHAR(64),
    source VARCHAR(64),
    title VARCHAR(512) NOT NULL,
    content TEXT,
    url VARCHAR(1024),
    published_at DATETIME,
    author VARCHAR(128),
    language VARCHAR(16),
    topic_tags JSON,
    cluster_id VARCHAR(64),
    simhash_value VARCHAR(64),
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of VARCHAR(64),
    embedding JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_raw_article_id (raw_article_id),
    INDEX idx_cluster_id (cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS clusters (
    id VARCHAR(64) PRIMARY KEY,
    topic_label VARCHAR(256) COMMENT '聚类主题标签',
    icon VARCHAR(16),
    article_count INT DEFAULT 0,
    time_span VARCHAR(64),
    importance INT DEFAULT 3 COMMENT '重要性 1-5',
    summary TEXT,
    tags JSON,
    timeline JSON COMMENT '事件时间线',
    representative_article_id VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cluster_date VARCHAR(16),
    INDEX idx_cluster_date (cluster_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cluster_articles (
    id VARCHAR(64) PRIMARY KEY,
    cluster_id VARCHAR(64),
    title VARCHAR(512),
    source VARCHAR(128),
    date VARCHAR(32),
    views VARCHAR(32),
    url VARCHAR(1024),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cluster_id (cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    subtitle VARCHAR(512),
    summary TEXT,
    generated_at VARCHAR(128),
    source_count INT DEFAULT 0,
    importance INT DEFAULT 3,
    time_span VARCHAR(64),
    tags JSON,
    is_featured BOOLEAN DEFAULT FALSE,
    status VARCHAR(32) DEFAULT 'draft' COMMENT 'published / reviewing / draft',
    cluster_id VARCHAR(64),
    sections JSON COMMENT 'ReportSection 列表',
    sources JSON COMMENT 'SourceCitation 列表',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cluster_id (cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS briefs (
    id VARCHAR(64) PRIMARY KEY,
    date VARCHAR(16) UNIQUE COMMENT '简报日期 YYYY-MM-DD',
    top_news JSON,
    reports JSON,
    industry_news JSON,
    sentiment_data JSON,
    tomorrow_focus JSON,
    markdown_content TEXT,
    pdf_path VARCHAR(512),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(32) DEFAULT 'draft' COMMENT 'draft / published',
    UNIQUE INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS topics (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    keywords JSON,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS data_sources (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    icon VARCHAR(32),
    icon_color VARCHAR(32),
    sub_label VARCHAR(256),
    enabled BOOLEAN DEFAULT TRUE,
    config_json JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS crawler_sites (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '站点名称',
    url VARCHAR(1024) NOT NULL COMMENT '站点首页URL',
    selector VARCHAR(512) NOT NULL COMMENT 'CSS选择器',
    link_attr VARCHAR(32) DEFAULT 'href' COMMENT '链接属性名',
    category VARCHAR(64) DEFAULT '综合' COMMENT '分类标签',
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_configs (
    `key` VARCHAR(128) PRIMARY KEY,
    `value` TEXT,
    value_type VARCHAR(32) DEFAULT 'string',
    description VARCHAR(256),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_runs (
    id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(32) DEFAULT 'running' COMMENT 'running / completed / failed',
    step VARCHAR(64) COMMENT '当前执行步骤',
    progress FLOAT DEFAULT 0.0,
    error_message TEXT,
    input_state JSON,
    output_state JSON,
    checkpoints JSON,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
