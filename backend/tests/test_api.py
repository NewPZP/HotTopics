# 智览平台 — API 基础测试
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "running"
    assert data["name"] == "智览平台"


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_dashboard_stats(client):
    """工作台统计 — 返回 StatItem 列表"""
    resp = await client.get("/api/v1/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert "label" in data[0]
    assert "value" in data[0]


@pytest.mark.asyncio
async def test_dashboard_top_news(client):
    """工作台今日要闻 — 返回 TopNews 列表"""
    resp = await client.get("/api/v1/dashboard/top-news")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5


@pytest.mark.asyncio
async def test_brief_list(client):
    """简报列表 — 返回 PaginatedResponse {data: [...], success: True}"""
    resp = await client.get("/api/v1/briefs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_report_list(client):
    """研报列表 — 返回 PaginatedResponse {data: [...], success: True}"""
    resp = await client.get("/api/v1/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_cluster_list(client):
    """聚类列表 — 返回 {data: [...]}"""
    resp = await client.get("/api/v1/clusters")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_topic_list(client):
    """主题列表 — 返回列表"""
    resp = await client.get("/api/v1/topics")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_monitor_status(client):
    """系统状态 — 返回 WorkflowState"""
    resp = await client.get("/api/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["isRunning"] is True


@pytest.mark.asyncio
async def test_monitor_logs(client):
    """实时日志 — 返回 LogEntry 列表"""
    resp = await client.get("/api/v1/logs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_config_sources(client):
    """数据源配置 — 返回 DataSourceItem 列表"""
    resp = await client.get("/api/v1/config/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_collect_trigger(client):
    """采集触发接口 — 返回 ApiResponse"""
    resp = await client.post("/api/v1/collect")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "采集" in data["message"]
