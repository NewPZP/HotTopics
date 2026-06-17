# ResearchAgent — RAG检索增强 + 深度摘要生成
import logging
import uuid
import asyncio
from datetime import datetime
from app.agents.state import PlatformState
from app.generators.summarizer import call_llm_async
from app.generators.prompts import (
    RESEARCH_REPORT_PROMPT, QUERY_REWRITE_PROMPT, REPORT_TAGS_PROMPT,
    BATCH_INSIGHT_PROMPT, BATCH_COMPOSE_PROMPT,
)

logger = logging.getLogger(__name__)


async def researcher_node(state: PlatformState) -> PlatformState:
    """RAG检索增强 + 深度研报生成"""
    state["current_step"] = "research"
    state["progress"] = 55.0

    clusters = state.get("clusters", [])
    if not clusters:
        logger.warning("[ResearchAgent] 无聚类结果，跳过研报生成")
        state["research_reports"] = []
        state["research_count"] = 0
        state["progress"] = 70.0
        return state

    # 按重要性排序，取前5个簇生成研报
    sorted_clusters = sorted(clusters, key=lambda c: c.get("importance", 0), reverse=True)
    target_clusters = sorted_clusters[:5]

    logger.info(f"[ResearchAgent] 开始为 {len(target_clusters)} 个主题生成研报")

    reports = []
    for idx, cluster in enumerate(target_clusters):
        cid = cluster.get("cluster_id", "?")
        logger.info(f"[ResearchAgent] 处理 {idx+1}/{len(target_clusters)} cluster={cid}")
        try:
            report = await _generate_report(cluster)
            reports.append(report)
            state["progress"] = 55.0 + (idx + 1) / len(target_clusters) * 15.0
            logger.info(f"[ResearchAgent] cluster={cid} 完成")
        except Exception as e:
            logger.error(f"[ResearchAgent] 研报生成失败 cluster={cluster.get('cluster_id')}: {e}")

    state["research_reports"] = reports
    state["research_count"] = len(reports)
    state["progress"] = 70.0

    # 持久化研报到数据库
    if reports:
        try:
            from app.repositories.report_repo import ReportRepo
            for report in reports:
                ReportRepo.upsert(report)
            logger.info(f"[ResearchAgent] 持久化到 DB: {len(reports)} 篇研报")
        except Exception as e:
            logger.warning(f"[ResearchAgent] DB 持久化失败: {e}")

    logger.info(f"[ResearchAgent] 研报生成完成: {len(reports)} 篇")
    return state


async def _generate_tags(topic_label: str, articles: list[dict]) -> list[str]:
    """通过 LLM 为研报生成精准分类标签"""
    titles = "\n".join(a["title"] for a in articles[:10])
    if not titles.strip():
        return [topic_label] if topic_label else ["综合"]

    try:
        prompt = REPORT_TAGS_PROMPT.format(title=topic_label, titles=titles)
        result = await call_llm_async(prompt)
        # 解析：每行一个标签
        tags = [line.strip() for line in result.strip().split("\n") if line.strip()]
        # 过滤过宽泛的标签
        blocked = {"金融", "经济", "综合", "财经", "新闻", "资讯", "市场"}
        tags = [t for t in tags if t not in blocked][:5]
        if tags:
            logger.info(f"[ResearchAgent] LLM 生成标签: {tags}")
            return tags
    except Exception as e:
        logger.warning(f"[ResearchAgent] 标签生成失败: {e}")

    # 回退：从文章标题提取关键词
    fallback = []
    for title in [a["title"] for a in articles[:5]]:
        for kw in ["AI", "芯片", "新能源", "光伏", "电池", "利率", "央行", "房地产",
                    "汽车", "互联网", "电商", "医疗", "教育", "消费", "贸易"]:
            if kw in title and kw not in fallback:
                fallback.append(kw)
                break
        if len(fallback) >= 4:
            break
    return fallback if fallback else [topic_label[:4] if topic_label else "综合"]


async def _generate_report(cluster: dict) -> dict:
    """为单个聚类生成深度研报（≥6篇文章时分批提取洞察，避免单次 LLM 超时）"""
    articles = cluster.get("articles", [])
    topic_label = cluster.get("topic_label", "综合资讯")

    # 构建来源引用
    sources = []
    for i, article in enumerate(articles[:15]):
        sources.append({
            "index": i + 1,
            "source": article.get("author", article.get("source", "未知来源")),
            "title": article["title"],
            "date": (article.get("published_at", ""))[:10],
            "url": article.get("url"),
        })

    BATCH_SIZE = 5
    target_articles = articles[:15]

    if len(target_articles) <= BATCH_SIZE:
        # 文章少，直接生成
        context_parts = []
        for i, article in enumerate(target_articles):
            context_parts.append(f"[来源{i+1}] {article['title']}\n{article.get('content', '')[:300]}")
        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"[ResearchAgent] 直接生成 topic={topic_label}, 文章数={len(target_articles)}, prompt长度={len(context)}")
        prompt = RESEARCH_REPORT_PROMPT.format(
            title=topic_label, context=context, timestamp=datetime.utcnow().isoformat())
        markdown_content = await call_llm_async(prompt, system_prompt="你是一位资深行业分析师，请生成专业、客观、结构化的研究报告。")
    else:
        # 分批提取洞察
        batches = [target_articles[i:i + BATCH_SIZE] for i in range(0, len(target_articles), BATCH_SIZE)]
        logger.info(f"[ResearchAgent] 分批生成 topic={topic_label}, 文章数={len(target_articles)}, 批次={len(batches)}")

        async def _batch_insight(batch_idx: int, batch: list[dict]) -> str:
            parts = []
            for i, article in enumerate(batch):
                parts.append(f"[篇{i+1}] {article['title']}\n{article.get('content', '')[:300]}")
            ctx = "\n\n".join(parts)
            prompt = BATCH_INSIGHT_PROMPT.format(title=topic_label, context=ctx)
            logger.info(f"[ResearchAgent] 批次{batch_idx+1}/{len(batches)}: {len(batch)}篇, prompt长度={len(ctx)}")
            return await call_llm_async(prompt)

        # 并行处理各批次（每个批次独立，互不依赖）
        batch_results = await asyncio.gather(
            *[_batch_insight(i, b) for i, b in enumerate(batches)],
            return_exceptions=True,
        )

        insights_parts = []
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.warning(f"[ResearchAgent] 批次{i+1} 洞察提取失败: {result}")
                insights_parts.append(f"## 批次{i+1}\n（提取失败）")
            else:
                insights_parts.append(f"## 批次{i+1}\n{result}")

        insights = "\n\n".join(insights_parts)
        prompt = BATCH_COMPOSE_PROMPT.format(
            title=topic_label, insights=insights, timestamp=datetime.utcnow().isoformat())
        logger.info(f"[ResearchAgent] 汇总生成 topic={topic_label}, 洞察长度={len(insights)}")
        markdown_content = await call_llm_async(prompt, system_prompt="你是一位资深行业分析师，请生成专业、客观、结构化的研究报告。")

    # 通过 LLM 生成研报专属标签
    tags = await _generate_tags(topic_label, articles)

    report_id = f"report-{uuid.uuid4().hex[:8]}"

    return {
        "id": report_id,
        "cluster_id": cluster.get("cluster_id"),
        "title": topic_label,
        "subtitle": cluster.get("summary", ""),
        "summary": markdown_content[:200] if markdown_content else "",
        "generated_at": "刚刚",
        "source_count": len(sources),
        "importance": cluster.get("importance", 3),
        "time_span": cluster.get("time_span", "1天"),
        "tags": tags,
        "is_featured": cluster.get("importance", 0) >= 4,
        "status": "published",
        "sections": _parse_sections(markdown_content),
        "sources": sources,
        "markdown_content": markdown_content,
    }


def _parse_sections(markdown: str) -> list[dict]:
    """将Markdown研报解析为结构化sections"""
    import re
    sections = []
    section_map = {
        "事件背景": "background",
        "现状分析": "analysis",
        "趋势研判": "trend",
        "风险提示": "risks",
        "关键数据": "data",
    }

    current_section = None
    current_content = []

    for line in markdown.split("\n"):
        match = re.match(r"^#{1,3}\s*(.+)$", line)
        if match:
            if current_section:
                sections.append({
                    "id": section_map.get(current_section, current_section),
                    "title": current_section,
                    "content": current_content,
                })
            current_section = match.group(1).strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections.append({
            "id": section_map.get(current_section, current_section),
            "title": current_section,
            "content": current_content,
        })

    return sections if sections else [
        {"id": "content", "title": "正文", "content": markdown.split("\n") if markdown else []}
    ]
