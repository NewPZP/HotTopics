# 文本清洗器
import re
import html
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def clean_html(raw_html: str) -> str:
    """清洗 HTML，提取纯文本"""
    if not raw_html:
        return ""
    try:
        soup = BeautifulSoup(raw_html, "lxml")
        # 移除 script/style 标签
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
    except Exception:
        text = raw_html
    return text


def normalize_text(text: str) -> str:
    """标准化文本：去除多余空白、统一编码"""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def detect_language(text: str) -> str:
    """检测文本语言"""
    if not text:
        return "unknown"
    try:
        from langdetect import detect
        return detect(text[:500])
    except Exception:
        # 简单规则：CJK字符占比判断
        cjk_count = sum(1 for c in text[:200] if '\u4e00' <= c <= '\u9fff')
        return "zh" if cjk_count > 10 else "en"


def clean_article(article: dict) -> dict:
    """清洗单篇文章"""
    content = article.get("content", "")
    cleaned_content = normalize_text(clean_html(content))

    return {
        **article,
        "content": cleaned_content[:5000],  # 截断过长内容
        "language": detect_language(cleaned_content),
    }
