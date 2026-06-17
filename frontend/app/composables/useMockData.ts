// 统一模拟数据源 - 所有页面共用
import type { Brief, TopNews, BriefReport, IndustryNewsGroup, SentimentData } from '~/types/brief'
import type { Report } from '~/types/report'
import type { NewsCluster, ClusterNode, ClusterLink } from '~/types/cluster'
import type { WorkflowState, PipelineStep, AgentStatus, LogEntry } from '~/types/workflow'
import type { StatItem, TopicItem, DataSourceItem } from '~/types/common'

// ==================== Dashboard 统计卡片 ====================
export function getStats(): StatItem[] {
  return [
    { label: '今日采集', value: '1,234', icon: 'rss', iconBg: 'bg-blue-50', iconColor: 'text-blue-600', trend: '+12.5%', trendType: 'up', subLabel: 'vs 昨日' },
    { label: '今日去重', value: '856', icon: 'filter', iconBg: 'bg-green-50', iconColor: 'text-green-600', trend: '去重率 30.6%', trendType: 'neutral' },
    { label: '生成研报', value: '12', icon: 'file-text', iconBg: 'bg-purple-50', iconColor: 'text-purple-600', trend: '+2', trendType: 'up', subLabel: '篇待审核' },
    { label: '推送次数', value: '4', icon: 'send', iconBg: 'bg-orange-50', iconColor: 'text-orange-600', trend: '已推 3 / 待推 1', trendType: 'neutral' },
  ]
}

// ==================== Dashboard 趋势图数据 ====================
export function getTrendData() {
  return {
    dates: ['05-21', '05-22', '05-23', '05-24', '05-25', '05-26', '05-27'],
    collect: [980, 1050, 1120, 1180, 1200, 1150, 1234],
    dedup: [650, 720, 780, 820, 840, 810, 856],
    reports: [8, 9, 10, 11, 11, 10, 12],
  }
}

// ==================== 每日简报 ====================
export function getBrief(date?: string): Brief {
  return {
    date: date || '2026-05-27',
    topNews: getTopNews(),
    reports: getBriefReports(),
    industryNews: getIndustryNews(),
    sentimentData: getSentimentData(),
    tomorrowFocus: [
      '美国5月PCE物价指数发布',
      'NVIDIA股东大会',
      '中国6月PMI数据公布',
    ],
  }
}

export function getTopNews(): TopNews[] {
  return [
    
  ]
}

export function getBriefReports(): BriefReport[] {
  return [
    {
      id: 'report-1', title: 'AI监管政策动向深度分析',
      summary: '梳理全球主要经济体AI监管政策演变脉络，分析对中国科技企业的潜在影响...',
      sourceCount: 23, generatedAt: '2小时前', importance: 5,
      sections: ['事件背景', '现状分析', '趋势研判', '风险提示'],
    },
    {
      id: 'report-2', title: '半导体供应链重构趋势研判',
      summary: '全球半导体供应链加速重构，分析地缘政治对芯片产业格局的深远影响...',
      sourceCount: 15, generatedAt: '4小时前', importance: 4,
      sections: ['事件背景', '现状分析', '趋势研判', '风险提示'],
    },
  ]
}

export function getIndustryNews(): IndustryNewsGroup[] {
  return [
    { industry: '金融', icon: '🏦', items: ['央行降准释放万亿流动性', '银行净息差收窄至历史低位'] },
    { industry: '科技', icon: '💻', items: ['AI芯片管制新规', '大模型推理成本下降80%', '量子计算突破'] },
    { industry: '能源', icon: '🏭', items: ['光伏组件价格触底反弹', 'OPEC+减产延期'] },
    { industry: '汽车', icon: '🚗', items: ['Q2交付超预期', '欧盟反补贴调查'] },
  ]
}

export function getSentimentData(): SentimentData {
  return {
    sentiment: 72, sentimentLabel: '偏乐观', sentimentTrend: 'up',
    hotIndex: 85, hotLabel: '高', hotTrend: 'up',
    volatility: 45, volatilityLabel: '低', volatilityTrend: 'down',
  }
}

// ==================== 研报列表 ====================
export function getReports(): Report[] {
  return [
    {
      id: 'report-1', title: 'AI监管政策动向深度分析',
      subtitle: '全球AI监管进入加速期，多国政策密集出台，对科技行业影响深远',
      summary: '全球AI监管进入加速期。欧盟AI法案正式生效，美国发布对华AI芯片出口管制新规，中国加速推进人工智能法立法进程。本文从政策背景、影响范围、行业应对三个维度进行深度剖析...',
      generatedAt: '2小时前', sourceCount: 23, importance: 5, timeSpan: '3天',
      tags: ['AI监管', '政策', '芯片管制'], isFeatured: true, status: 'published',
      sections: getReportSections('report-1'),
      sources: getReportSources(),
    },
    {
      id: 'report-2', title: '半导体供应链重构趋势研判',
      subtitle: '全球半导体供应链加速重构，分析地缘政治对芯片产业格局的影响',
      summary: '全球半导体供应链加速重构，分析地缘政治对芯片产业格局的影响...',
      generatedAt: '4小时前', sourceCount: 15, importance: 4, timeSpan: '5天',
      tags: ['半导体', '供应链', '地缘政治'], isFeatured: false, status: 'published',
      sections: getReportSections('report-2'),
      sources: [],
    },
    {
      id: 'report-3', title: '新能源汽车出海战略风险提示',
      subtitle: '中国新能源车企出海面临反补贴调查、关税壁垒等多重挑战',
      summary: '中国新能源车企出海面临反补贴调查、关税壁垒等多重挑战...',
      generatedAt: '6小时前', sourceCount: 18, importance: 3, timeSpan: '4天',
      tags: ['新能源', '出海', '关税'], isFeatured: false, status: 'reviewing',
      sections: [],
      sources: [],
    },
    {
      id: 'report-4', title: '美联储利率政策路径展望',
      subtitle: '美联储维持利率不变，点阵图暗示年内两次降息',
      summary: '美联储维持利率不变，点阵图暗示年内两次降息，市场如何定价...',
      generatedAt: '8小时前', sourceCount: 12, importance: 3, timeSpan: '2天',
      tags: ['美联储', '利率', '货币政策'], isFeatured: false, status: 'published',
      sections: [],
      sources: [],
    },
    {
      id: 'report-5', title: '光伏产业周期拐点研判',
      subtitle: '多晶硅价格暴跌后企稳，行业是否迎来底部',
      summary: '多晶硅价格暴跌后企稳，组件端开工率回升，行业是否迎来底部...',
      generatedAt: '1天前', sourceCount: 20, importance: 4, timeSpan: '7天',
      tags: ['光伏', '新能源', '周期'], isFeatured: false, status: 'published',
      sections: [],
      sources: [],
    },
    {
      id: 'report-6', title: '数字货币监管框架国际比较',
      subtitle: '各国数字货币监管政策趋同演化',
      summary: '各国数字货币监管政策趋同演化，MiCA框架或成全球标准...',
      generatedAt: '1天前', sourceCount: 10, importance: 3, timeSpan: '14天',
      tags: ['数字货币', '监管', 'MiCA'], isFeatured: false, status: 'published',
      sections: [],
      sources: [],
    },
    {
      id: 'report-7', title: '医疗健康产业数字化转型',
      subtitle: 'AI+医疗投融资回暖，数字疗法获批提速',
      summary: 'AI+医疗投融资回暖，数字疗法获批提速，行业拐点已至...',
      generatedAt: '2天前', sourceCount: 8, importance: 2, timeSpan: '10天',
      tags: ['医疗', 'AI', '数字化'], isFeatured: false, status: 'published',
      sections: [],
      sources: [],
    },
  ]
}

export function getReportById(id: string): Report | undefined {
  return getReports().find(r => r.id === id)
}

export function getReportSections(reportId: string) {
  if (reportId === 'report-1') {
    return [
      {
        id: 'background',
        title: '一、事件背景',
        content: [
          '自2024年以来，全球主要经济体加速推进人工智能监管立法。欧盟《人工智能法案》于2025年8月正式生效，成为全球首部综合性AI监管法律。美国拜登政府签署行政令，要求对华AI芯片出口实施更严格的管制措施，并于2026年5月发布最新修订版。中国方面，《人工智能法》草案已进入全国人大常委会审议阶段，预计2026年下半年正式出台。',
          '本轮监管浪潮的核心驱动力包括：大模型技术的快速迭代引发安全担忧、中美科技竞争加剧、以及公众对AI伦理问题的关注度持续上升。特别是DeepSeek等国产大模型的崛起，使得西方国家加快了对华技术限制的步伐。',
        ],
        keyParticipants: ['欧盟委员会', '美国商务部BIS', '中国工信部', 'OpenAI', 'NVIDIA'],
      },
      {
        id: 'analysis',
        title: '二、现状分析',
        content: [
          '美国最新对华芯片出口管制新规将限制范围从高端GPU扩展至涵盖更多AI加速器品类，NVIDIA H20、B200等专为中国市场设计的芯片也受到波及。受此影响，多家中国云计算企业和AI创业公司面临算力供应紧张的局面。与此同时，华为昇腾910B芯片产能持续爬坡，国产替代方案逐步获得市场认可。',
          '欧盟AI法案按风险等级将AI应用分为四类，对高风险AI系统实施严格的市场准入制度。全球科技公司纷纷调整产品策略以符合合规要求，OpenAI、Google、Meta等均设立了专门的AI合规团队。',
        ],
        highlights: [
          { label: '受管制芯片市场规模', value: '$48B', color: 'amber' },
          { label: 'NVIDIA中国区营收降幅', value: '▼12%', color: 'red' },
          { label: '华为昇腾出货量增速', value: '300%', color: 'green' },
          { label: '推进AI立法的国家数', value: '37国', color: 'blue' },
        ],
      },
      {
        id: 'trend',
        title: '三、趋势研判',
        content: [],
        shortTerm: '中美芯片博弈进一步升级，美国可能将更多中国公司列入实体清单。中国将加速推进AI法立法，预计发布征求意见稿。全球AI企业合规成本上升10-15%。',
        longTerm: '全球AI监管格局趋于"三极分化"——美国模式（行业自律+出口管制）、欧盟模式（严格立法）、中国模式（安全可控+自主创新）。国产AI芯片市占率有望突破30%，但先进制程仍是瓶颈。AI合规将成为企业ESG评级的重要维度。',
        keyDrivers: ['美国大选结果', '中国AI法立法进度', '华为芯片产能', '欧盟执法细则'],
      },
      {
        id: 'risks',
        title: '四、风险提示',
        content: [],
        risks: [
          { category: '政策/监管', categoryColor: 'red', title: '政策/监管风险', description: '美国出口管制进一步扩大至AI云服务领域，可能限制中国公司使用海外云计算资源进行AI训练。欧盟AI法案执法细则存在较大不确定性。' },
          { category: '市场', categoryColor: 'orange', title: '市场波动风险', description: 'AI板块估值处于历史高位，监管政策变化可能导致板块大幅回调。芯片管制升级可能引发供应链相关个股剧烈波动。' },
          { category: '技术/运营', categoryColor: 'amber', title: '技术/运营风险', description: '国产替代芯片在软件生态、性能稳定性方面仍需时间验证。合规体系建设需要大量人力物力投入，中小企业面临较大压力。' },
        ],
      },
    ]
  }
  return []
}

export function getReportSources() {
  return [
    { index: 1, source: 'Reuters', title: '美国商务部公布对华AI芯片出口管制修订细则', date: '2026-05-27' },
    { index: 2, source: '新华社', title: '欧盟AI法案正式生效：全球AI监管进入新纪元', date: '2026-05-26' },
    { index: 3, source: '36氪', title: '华为昇腾910B产能爬坡，国产AI芯片迎来机遇窗口', date: '2026-05-26' },
    { index: 4, source: '新浪财经', title: '中国人工智能法草案进入审议阶段，预计下半年出台', date: '2026-05-25' },
    { index: 5, source: '东方财富', title: 'NVIDIA H20芯片出口受限，中国云计算企业面临算力缺口', date: '2026-05-25' },
  ]
}

// ==================== 聚类数据 ====================
export function getClusters(): NewsCluster[] {
  return [
    {
      id: 'cluster-1', label: 'AI监管政策动向', icon: '📌', articleCount: 23,
      timeSpan: '3天', importance: 5,
      summary: '欧盟AI法案通过 → 美国出口管制 → 中国AI立法加速',
      tags: ['AI监管', '政策', '芯片管制'],
      timeline: [
        { date: '05-27 10:30', title: '美国商务部公布对华AI芯片出口管制修订细则', description: '限制范围扩展至更多AI加速器品类，NVIDIA H20、B200等芯片受波及', done: true },
        { date: '05-26 16:00', title: '欧盟AI法案正式生效', description: '全球首部综合性AI监管法律进入执行阶段', done: true },
        { date: '05-26 09:00', title: '华为昇腾910B产能爬坡突破', description: '国产AI芯片出货量同比增长300%', done: true },
        { date: '05-25 14:00', title: '中国AI法草案进入全国人大审议', description: '草案明确AI安全分级、数据合规、算法备案等核心制度框架', done: true },
        { date: '05-25 08:00', title: 'OpenAI、Google宣布成立AI合规联合工作组', description: '全球科技巨头主动应对监管趋势', done: true },
      ],
      articles: [
      ],
    },
    {
      id: 'cluster-2', label: '半导体供应链重构', icon: '🔗', articleCount: 15,
      timeSpan: '5天', importance: 4,
      summary: '台积电日本扩产 → 英特尔获补贴 → 中国自主替代加速',
      tags: ['半导体', '供应链', '地缘政治'],
      timeline: [],
      articles: [],
    },
    {
      id: 'cluster-3', label: '新能源汽车出海风险', icon: '🚗', articleCount: 18,
      timeSpan: '4天', importance: 3,
      summary: '欧盟反补贴调查 → 东南亚市场机遇 → 本地化建厂加速',
      tags: ['关税壁垒', '出海', '新能源车'],
      timeline: [],
      articles: [],
    },
  ]
}

export function getClusterById(id: string): NewsCluster | undefined {
  return getClusters().find(c => c.id === id)
}

export function getClusterGraphData(): { nodes: ClusterNode[]; links: ClusterLink[] } {
  return {
    nodes: [
      { name: 'AI监管', symbolSize: 45, category: 0, itemStyle: { color: '#ef4444' } },
      { name: '芯片管制', symbolSize: 32, category: 1, itemStyle: { color: '#f97316' } },
      { name: '欧盟AI法案', symbolSize: 28, category: 1 },
      { name: '科技公司', symbolSize: 30, category: 2, itemStyle: { color: '#2d8eff' } },
      { name: '半导体', symbolSize: 38, category: 3, itemStyle: { color: '#8b5cf6' } },
      { name: '供应链', symbolSize: 30, category: 3 },
      { name: '地缘政治', symbolSize: 33, category: 0, itemStyle: { color: '#ef4444' } },
      { name: '新能源车', symbolSize: 35, category: 4, itemStyle: { color: '#10b981' } },
      { name: '关税壁垒', symbolSize: 25, category: 4 },
      { name: '中美关系', symbolSize: 30, category: 0 },
      { name: '光伏', symbolSize: 28, category: 4 },
      { name: '数字货币', symbolSize: 22, category: 5, itemStyle: { color: '#ec4899' } },
    ],
    links: [
      { source: 'AI监管', target: '芯片管制' }, { source: 'AI监管', target: '欧盟AI法案' },
      { source: 'AI监管', target: '科技公司' }, { source: '芯片管制', target: '半导体' },
      { source: '芯片管制', target: '中美关系' }, { source: '半导体', target: '供应链' },
      { source: '半导体', target: '地缘政治' }, { source: '地缘政治', target: '中美关系' },
      { source: '中美关系', target: '关税壁垒' }, { source: '关税壁垒', target: '新能源车' },
      { source: '新能源车', target: '光伏' }, { source: '科技公司', target: '新能源车' },
      { source: '科技公司', target: '数字货币' },
    ],
  }
}

// ==================== 工作流监控 ====================
export function getWorkflowState(): WorkflowState {
  return {
    isRunning: true,
    lastCollectTime: '10分钟前',
    nextCollectTime: '1小时50分后',
    totalProgress: 67,
    estimatedRemaining: '8分钟',
    pipelineSteps: [
      { name: 'collect', label: '采集', status: 'done', count: '1,234篇' },
      { name: 'preprocess', label: '预处理', status: 'done', count: '1,180篇' },
      { name: 'dedup', label: '去重', status: 'done', count: '856篇' },
      { name: 'cluster', label: '聚类', status: 'done', count: '42簇' },
      { name: 'research', label: '摘要', status: 'running', count: '67%', progress: 67 },
      { name: 'review', label: '审核', status: 'pending', count: '等待' },
      { name: 'compose', label: '组装', status: 'pending', count: '等待' },
      { name: 'dispatch', label: '推送', status: 'pending', count: '等待' },
    ],
    agents: [
      { name: 'CollectorAgent', label: 'CollectorAgent', status: 'idle', detail: '处理1,234篇' },
      { name: 'DedupAgent', label: 'DedupAgent', status: 'idle', detail: '去重856篇' },
      { name: 'ClusterAgent', label: 'ClusterAgent', status: 'idle', detail: '42个主题簇' },
      { name: 'ResearchAgent', label: 'ResearchAgent', status: 'running', detail: '67%' },
      { name: 'ReviewAgent', label: 'ReviewAgent', status: 'pending', detail: '等待中' },
      { name: 'DispatchAgent', label: 'DispatchAgent', status: 'pending', detail: '等待中' },
    ],
    logs: [
      { timestamp: '14:32:15', level: 'INFO', agent: 'ResearchAgent', message: '生成研报 3/5...' },
      { timestamp: '14:32:10', level: 'INFO', agent: 'ClusterAgent', message: '完成聚类，共42个主题簇' },
      { timestamp: '14:31:45', level: 'INFO', agent: 'DedupAgent', message: '去重完成，移除324篇重复文章' },
      { timestamp: '14:30:00', level: 'INFO', agent: 'CollectorAgent', message: '采集完成，共1,234篇' },
      { timestamp: '14:28:30', level: 'WARN', agent: 'NewsAPI', message: '请求超时，第2次重试中...' },
      { timestamp: '14:28:15', level: 'INFO', agent: 'CollectorAgent', message: '启动多源采集任务' },
      { timestamp: '14:28:00', level: 'INFO', agent: 'Scheduler', message: 'Cron触发采集' },
    ],
    metrics: { cpu: 45, memory: { used: 2.3, total: 8 }, redis: 156, dbConnections: 1.2 },
  }
}

// ==================== 配置数据 ====================
export function getTopics(): TopicItem[] {
  return [
    { id: 'topic-1', name: 'AI监管与政策', keywords: ['AI', '监管', '政策', '芯片管制'], enabled: true },
    { id: 'topic-2', name: '半导体供应链', keywords: ['半导体', '芯片', '供应链', '台积电'], enabled: true },
    { id: 'topic-3', name: '新能源汽车', keywords: ['新能源', '电动汽车', '出海', '电池'], enabled: true },
    { id: 'topic-4', name: '宏观经济', keywords: ['GDP', 'CPI', 'PMI', '央行', '利率'], enabled: false },
  ]
}

export function getDataSources(): DataSourceItem[] {
  return [
    { id: 'ds-1', name: 'NewsAPI', icon: 'rss', iconColor: 'text-blue-500', subLabel: 'API Key: 已配置', enabled: true },
    { id: 'ds-2', name: '自定义爬虫', icon: 'globe', iconColor: 'text-orange-500', subLabel: '3个站点', enabled: true },
    { id: 'ds-3', name: 'RSS订阅', icon: 'radio', iconColor: 'text-purple-500', subLabel: '5个源', enabled: true },
    { id: 'ds-4', name: '财报PDF解析', icon: 'file-text', iconColor: 'text-red-500', subLabel: 'A股+港股', enabled: false },
  ]
}
