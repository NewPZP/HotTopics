# 智览平台 — Agent 工作流测试
import pytest


# ── State 测试 ──

def test_platform_state_defaults():
    """测试 PlatformState 默认值"""
    from app.agents.state import PlatformState
    state = PlatformState()
    assert state.get("raw_articles", []) == []
    assert isinstance(state.get("clusters", []), list)


# ── Collector Agent 测试 ──

@pytest.mark.asyncio
async def test_collector_mock():
    """采集 Agent — 无 API Key 时返回模拟数据"""
    from app.agents.collector import collector_node
    from app.agents.state import PlatformState
    state = PlatformState(topics=["AI", "金融"])
    result = await collector_node(state)
    assert "raw_articles" in result
    assert len(result["raw_articles"]) > 0
    assert result["collect_count"] > 0


# ── Preprocessor Agent 测试 ──

@pytest.mark.asyncio
async def test_preprocessor():
    """预处理 Agent — 清洗文本"""
    from app.agents.preprocessor import preprocessor_node
    from app.agents.state import PlatformState

    state = PlatformState(raw_articles=[{
        "id": "test-1",
        "title": "  测试文章  \n",
        "content": "<p>这是<b>HTML</b>内容</p>",
        "source": "test",
        "url": "http://example.com/1",
        "url_hash": "abc123",
        "topic_tags": ["AI"],
    }])
    result = await preprocessor_node(state)
    assert "cleaned_articles" in result
    assert len(result["cleaned_articles"]) > 0
    # 检查 HTML 是否被清理
    article = result["cleaned_articles"][0]
    assert "<b>" not in article.get("content", "")
    assert "<p>" not in article.get("content", "")


# ── Dedup Agent 测试 ──

@pytest.mark.asyncio
async def test_deduplicator():
    """去重 Agent — URL去重"""
    from app.agents.dedup import dedup_node
    from app.agents.state import PlatformState

    state = PlatformState(cleaned_articles=[
        {"id": "a1", "url": "http://example.com/a", "title": "Article A", "url_hash": "h1"},
        {"id": "a2", "url": "http://example.com/a", "title": "Article A Dup", "url_hash": "h1"},
        {"id": "a3", "url": "http://example.com/b", "title": "Article B", "url_hash": "h2"},
    ])
    result = await dedup_node(state)
    assert "unique_articles" in result
    assert "duplicates_removed" in result
    # 重复URL的应该被移除
    assert len(result["unique_articles"]) <= 2


# ── Cluster Agent 测试 ──

@pytest.mark.asyncio
async def test_clusterer_small():
    """聚类 Agent — 少量数据"""
    from app.agents.cluster import cluster_node
    from app.agents.state import PlatformState

    state = PlatformState(unique_articles=[
        {"id": "1", "title": "AI 突破", "content": "大模型新的突破...", "topic_tags": ["AI"]},
        {"id": "2", "title": "芯片新闻", "content": "台积电3nm量产...", "topic_tags": ["半导体"]},
        {"id": "3", "title": "深度学习进展", "content": "神经网络训练新方法...", "topic_tags": ["AI"]},
    ])
    result = await cluster_node(state)
    assert "clusters" in result
    # 少量数据可能跳过聚类（需>=3篇）
    assert isinstance(result["clusters"], list)


# ── Summarizer 测试 ──

def test_mock_summarizer():
    """LLM 摘要生成器 — 无 API Key Mock 模式"""
    from app.generators.summarizer import call_llm
    result = call_llm("请生成文章摘要")
    assert isinstance(result, str)
    assert len(result) > 0


def test_call_llm_with_system_prompt():
    """LLM — 带系统提示"""
    from app.generators.summarizer import call_llm
    result = call_llm("分析", system_prompt="你是一个助手")
    assert isinstance(result, str)


# ── Deduplicator (processor) 测试 ──

def test_exact_dedup():
    """精确去重 — URL + 标题哈希"""
    from app.processors.deduplicator import exact_dedup
    articles = [
        {"title": "AI突破", "content": "...", "url": "http://x.com/1", "url_hash": "hash_a"},
        {"title": "AI突破", "content": "...", "url": "http://x.com/1", "url_hash": "hash_a"},
        {"title": "芯片新闻", "content": "...", "url": "http://x.com/2", "url_hash": "hash_b"},
    ]
    result, removed = exact_dedup(articles)
    assert removed >= 1
    assert len(result) <= 2


# ── Text Cleaner 测试 ──

def test_clean_html():
    """HTML清洗"""
    from app.processors.text_cleaner import clean_html
    raw = "<p>Hello <b>World</b>!</p>"
    cleaned = clean_html(raw)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "Hello" in cleaned


def test_normalize_text():
    """文本标准化"""
    from app.processors.text_cleaner import normalize_text
    raw = "  Hello\n\n\nWorld  "
    cleaned = normalize_text(raw)
    assert "Hello" in cleaned
    assert "World" in cleaned


# ── Clusterer 测试 ──

def test_cluster_articles():
    """聚类器 — 关键词回退"""
    from app.processors.clusterer import cluster_articles
    articles = [
        {"id": "1", "title": "AI 新突破", "content": "人工智能进展", "topic_tags": ["AI"]},
        {"id": "2", "title": "芯片制造", "content": "半导体新闻", "topic_tags": ["半导体"]},
        {"id": "3", "title": "深度学习模型", "content": "AI模型", "topic_tags": ["AI"]},
        {"id": "4", "title": "AI 应用场景", "content": "人工智能场景", "topic_tags": ["AI"]},
    ]
    clusters = cluster_articles(articles)
    assert isinstance(clusters, list)


