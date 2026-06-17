# ExportAgent — 格式导出 (Markdown / PDF)
import logging
import os
from app.agents.state import PlatformState
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def exporter_node(state: PlatformState) -> PlatformState:
    """导出节点：生成 Markdown 和 PDF"""
    state["current_step"] = "export"
    state["progress"] = 92.0

    brief = state.get("daily_brief", {})
    if not brief:
        logger.warning("[ExportAgent] 无日报数据，跳过导出")
        state["progress"] = 95.0
        return state

    # 生成 Markdown
    markdown = _generate_markdown(brief)
    state["markdown_content"] = markdown
    state["progress"] = 95.0

    # 尝试导出文件
    try:
        os.makedirs(settings.EXPORT_DIR, exist_ok=True)

        date = brief.get("date", "unknown")
        md_path = os.path.join(settings.EXPORT_DIR, f"brief_{date}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info(f"[ExportAgent] Markdown导出: {md_path}")

        # PDF 导出（可选）
        try:
            pdf_path = os.path.join(settings.EXPORT_DIR, f"brief_{date}.pdf")
            _generate_pdf(markdown, pdf_path)
            state["pdf_path"] = pdf_path
        except Exception as e:
            logger.warning(f"[ExportAgent] PDF导出失败: {e}")

    except Exception as e:
        logger.error(f"[ExportAgent] 文件导出异常: {e}")

    state["progress"] = 97.0
    logger.info("[ExportAgent] 导出完成")
    return state


def _generate_markdown(brief: dict) -> str:
    """生成 Markdown 格式日报"""
    lines = [
        f"# 每日智能简报 — {brief.get('date', '')}",
        "",
        brief.get("overview", ""),
        "",
        "## 今日要闻 TOP5",
        "",
    ]

    for news in brief.get("topNews", []):
        lines.append(f"{news['rank']}. **{news['title']}** — {news['summary']}")
        lines.append(f"   来源: {news['source']} | 热度: {news['hotIndex']}")
        lines.append("")

    lines.append("## 深度研报")
    lines.append("")
    for report in brief.get("reports", []):
        lines.append(f"### {report['title']}")
        lines.append(f"{report['summary']}")
        lines.append(f"> 引用 {report['sourceCount']} 篇 | 重要性 {'⭐' * report['importance']}")
        lines.append("")

    lines.append("## 行业动态速览")
    lines.append("")
    for group in brief.get("industryNews", []):
        items = " | ".join(group.get("items", []))
        lines.append(f"- **{group['icon']} {group['industry']}**: {items}")

    lines.append("")
    lines.append("## 明日关注")
    for item in brief.get("tomorrowFocus", []):
        lines.append(f"- {item}")

    sentiment = brief.get("sentimentData", {})
    lines.append("")
    lines.append("## 市场情绪")
    lines.append(f"- 情绪指数: {sentiment.get('sentiment', '-')} ({sentiment.get('sentimentLabel', '')})")
    lines.append(f"- 热度指数: {sentiment.get('hotIndex', '-')} ({sentiment.get('hotLabel', '')})")
    lines.append(f"- 波动指数: {sentiment.get('volatility', '-')} ({sentiment.get('volatilityLabel', '')})")

    lines.append("")
    lines.append("---")
    lines.append(f"*自动生成于 {brief.get('date', '')} | 智览平台*")

    return "\n".join(lines)


def _generate_pdf(markdown: str, output_path: str):
    """生成 PDF 文件（纯 reportlab，零系统依赖）"""
    import re
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 注册中文字体
    _register_chinese_font()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()
    font_name = _get_chinese_font()

    # 自定义样式
    title_style = ParagraphStyle(
        'CNTitle', parent=styles['Title'],
        fontName=font_name, fontSize=18, leading=24,
        textColor=HexColor('#1a1a2e'), spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        'CNH2', parent=styles['Heading2'],
        fontName=font_name, fontSize=14, leading=18,
        textColor=HexColor('#16213e'), spaceBefore=16, spaceAfter=8,
    )
    h3_style = ParagraphStyle(
        'CNH3', parent=styles['Heading3'],
        fontName=font_name, fontSize=12, leading=16,
        textColor=HexColor('#2d8eff'), spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'CNBody', parent=styles['Normal'],
        fontName=font_name, fontSize=10, leading=16,
        spaceAfter=4,
    )
    small_style = ParagraphStyle(
        'CNSmall', parent=styles['Normal'],
        fontName=font_name, fontSize=9, leading=13,
        textColor=HexColor('#888888'),
    )
    footer_style = ParagraphStyle(
        'CNFooter', parent=styles['Normal'],
        fontName=font_name, fontSize=9, leading=13,
        textColor=HexColor('#999999'), alignment=TA_CENTER,
    )

    elements = []
    lines = markdown.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # 标题 #
        if line.startswith('# ') and not line.startswith('## '):
            elements.append(Paragraph(_escape(line[2:]), title_style))
            # 标题下分割线
            elements.append(Spacer(1, 2))
            elements.append(_thin_line())
            elements.append(Spacer(1, 8))
            i += 1
            continue

        # H2
        if line.startswith('## '):
            elements.append(Paragraph(_escape(line[3:]), h2_style))
            i += 1
            continue

        # H3
        if line.startswith('### '):
            elements.append(Paragraph(_escape(line[4:]), h3_style))
            i += 1
            continue

        # 引用行
        if line.startswith('> '):
            elements.append(Paragraph(_escape(line[2:]), small_style))
            i += 1
            continue

        # 粗体新闻条目
        m = re.match(r'^(\d+)\.\s\*\*(.+?)\*\*\s—\s(.+)', line)
        if m:
            rank, title, summary = m.groups()
            elements.append(Paragraph(
                f'<b>{_escape(rank)}. {_escape(title)}</b> — {_escape(summary)}',
                body_style
            ))
            i += 1
            continue

        # 来源/热度
        m = re.match(r'^\s+来源:\s(.+?)\s\|\s热度:\s(.+)', line)
        if m:
            source, hot = m.groups()
            elements.append(Paragraph(
                f'来源: {_escape(source)} | 热度: {_escape(hot)}', small_style
            ))
            i += 1
            continue

        # 列表项 - **icon industry**: items
        m = re.match(r'^-\s\*\*(.+?)\*\*:\s(.+)', line)
        if m:
            label, items_text = m.groups()
            elements.append(Paragraph(
                f'• <b>{_escape(label)}</b>: {_escape(items_text)}', body_style
            ))
            i += 1
            continue

        # 列表项 - item
        if re.match(r'^-\s', line):
            elements.append(Paragraph(f'• {_escape(line[2:])}', body_style))
            i += 1
            continue

        # 分割线
        if line.strip() == '---':
            elements.append(Spacer(1, 6))
            elements.append(_thin_line())
            elements.append(Spacer(1, 6))
            i += 1
            continue

        # 空行
        if not line.strip():
            elements.append(Spacer(1, 4))
            i += 1
            continue

        # 普通段落
        elements.append(Paragraph(_escape(line), body_style))
        i += 1

    doc.build(elements)


# ---- 字体辅助 ----

_CHINESE_FONT_REGISTERED = False
_CHINESE_FONT_NAME = 'Helvetica'


def _register_chinese_font():
    """尝试注册系统中可用的中文字体（优先 .ttf，.ttc 需指定 subfontIndex）"""
    global _CHINESE_FONT_REGISTERED, _CHINESE_FONT_NAME
    if _CHINESE_FONT_REGISTERED:
        return
    _CHINESE_FONT_REGISTERED = True

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 优先 .ttf 单字体（更可靠），其次 .ttc 集合字体
    candidates = [
        # .ttf 单字体 — 无需 subfontIndex，首选
        ('C:/Windows/Fonts/simhei.ttf', 'SimHei', None),
        ('C:/Windows/Fonts/simkai.ttf', 'SimKai', None),
        ('C:/Windows/Fonts/simsunb.ttf', 'SimSunB', None),
        # .ttc 集合字体 — 需 subfontIndex=0
        ('C:/Windows/Fonts/msyh.ttc', 'MSYH', 0),
        ('C:/Windows/Fonts/msyhbd.ttc', 'MSYHBD', 0),
        ('C:/Windows/Fonts/simsun.ttc', 'SimSun', 0),
    ]
    for path, name, subfont in candidates:
        try:
            kwargs = {}
            if subfont is not None:
                kwargs['subfontIndex'] = subfont
            pdfmetrics.registerFont(TTFont(name, path, **kwargs))
            _CHINESE_FONT_NAME = name
            return
        except Exception:
            continue


def _get_chinese_font() -> str:
    return _CHINESE_FONT_NAME


def _thin_line():
    """创建细分割线"""
    from reportlab.lib.units import mm
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.colors import HexColor
    t = Table([['']], colWidths=[170*mm], rowHeights=[0.5])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, HexColor('#2d8eff')),
    ]))
    return t


def _escape(text: str) -> str:
    """转义 XML/HTML 特殊字符"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
