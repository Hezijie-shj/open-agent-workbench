"""演示数据."""

AGENTS = [
    {
        "id": 1,
        "name": "流水解析助手",
        "description": (
            "演示多格式流水文件的结构化解析, "
            "输出可复核的交易明细和基础统计指标."
        ),
        "department": "财务运营",
        "scene": "数据解析",
        "views": 368,
        "favorites": 1,
        "likes": 0,
        "route": "/bank/projects",
    },
    {
        "id": 2,
        "name": "制度文档比对",
        "description": "对示例制度文本和通用规则库进行差异比对, 输出风险项、条款差异和修订建议.",
        "department": "合规风控",
        "scene": "文档比对",
        "views": 92,
        "favorites": 3,
        "likes": 1,
        "route": "/regulations",
    },
    {
        "id": 3,
        "name": "文档差异比对",
        "description": "演示标准文档与多个版本文档的条款差异提取、风险分级和历史追踪.",
        "department": "法务支持",
        "scene": "文档比对",
        "views": 60,
        "favorites": 0,
        "likes": 0,
        "route": "/document-diff",
    },
]

PROJECTS = [
    {
        "id": 1,
        "name": "示例项目 A",
        "date_range": "2025-07-02 11:09:42 至 2025-07-31 18:26:23",
        "amount": "¥37,325,491.05",
        "created_at": "2026-07-06 15:49:41",
        "creator": "demo",
        "status": "待审核",
    },
    {
        "id": 2,
        "name": "批量解析样例",
        "date_range": "2025-07-02 11:09:42 至 2025-08-29 18:03:51",
        "amount": "¥60,517,599.59",
        "created_at": "2026-07-02 17:51:38",
        "creator": "demo",
        "status": "待审核",
    },
    {
        "id": 3,
        "name": "连续性核查样例",
        "date_range": "2025-01-01 09:10:00 至 2025-01-15 16:35:00",
        "amount": "¥11,900",
        "created_at": "2026-07-01 13:56:58",
        "creator": "demo",
        "status": "已完成",
    },
    {
        "id": 4,
        "name": "空白页识别样例",
        "date_range": "-",
        "amount": "-",
        "created_at": "2026-07-02 15:14:33",
        "creator": "demo",
        "status": "解析中",
    },
]

ANALYSIS_RESULTS = {
    1: {
        1: [
            {"id": 101, "date": "2025-07-02 11:09:42", "type": "支出", "amount": "-18433.57", "balance": "257872.82"},
            {"id": 102, "date": "2025-07-02 11:11:42", "type": "支出", "amount": "-120000.00", "balance": "137872.82"},
            {"id": 103, "date": "2025-07-02 11:23:22", "type": "支出", "amount": "-50000.00", "balance": "87872.82"},
            {
                "id": 104,
                "date": "2025-07-02 15:16:46",
                "type": "收入",
                "amount": "+2710000.00",
                "balance": "2782872.82",
            },
            {"id": 105, "date": "2025-07-03 13:16:03", "type": "收入", "amount": "+15000.00", "balance": "122015.16"},
            {"id": 106, "date": "2025-07-03 16:57:22", "type": "支出", "amount": "-54664.59", "balance": "67350.57"},
        ]
    },
    3: {
        1: [
            {"id": 301, "date": "2025-01-01 09:10:00", "type": "收入", "amount": "+5000.00", "balance": "15000.00"},
            {"id": 302, "date": "2025-01-03 10:20:00", "type": "支出", "amount": "-1200.00", "balance": "13800.00"},
            {"id": 303, "date": "2025-01-06 09:05:00", "type": "支出", "amount": "-1000.00", "balance": "11150.00"},
            {"id": 304, "date": "2025-01-07 10:40:00", "type": "收入", "amount": "+2500.00", "balance": "13650.00"},
        ]
    },
}

REPORTS = {
    3: {
        "project_name": "连续性核查样例",
        "date_range": "2025-01-01 09:10:00 至 2025-01-15 16:35:00",
        "overview": {
            "subject": "星河样例科技有限公司",
            "account": "6222 0000 0000 0000",
            "avg_balance": "12,676.67",
            "income": "8,300.00",
            "expense": "-3,600.00",
        },
        "integrity": {
            "period": "2025-01-01 09:10:00~2025-01-15 16:35:00",
            "duration": "1个月",
            "status": "不连续",
        },
        "composition": {
            "income": [
                {"type": "经营收入", "amount": "4,900.00", "ratio": "59.0361%"},
                {"type": "其他收入", "amount": "3,300.00", "ratio": "39.7590%"},
                {"type": "非经营性收入", "amount": "100.00", "ratio": "1.2048%"},
            ],
            "expense": [
                {"type": "其他支出", "amount": "-2,600.00", "ratio": "72.2222%"},
                {"type": "租金支出", "amount": "-1,000.00", "ratio": "27.7778%"},
            ],
        },
        "counterparties": [
            {
                "name": "晨星材料样例有限公司",
                "related": True,
                "suspicious": False,
                "income": "2,500.00",
                "expense": "-0.00",
            },
            {
                "name": "北桥工程样例有限公司",
                "related": False,
                "suspicious": True,
                "income": "2,000.00",
                "expense": "-0.00",
            },
            {
                "name": "云舟信息样例有限公司",
                "related": False,
                "suspicious": False,
                "income": "1,200.00",
                "expense": "-0.00",
            },
        ],
    }
}

REGULATION_TASKS = [
    {
        "id": 1,
        "name": "采购管理制度比对样例",
        "standard": "通用制度规则库 V2026",
        "uploaded_at": "2026-07-07 09:20:11",
        "status": "已完成",
        "risk_count": 8,
        "summary": "发现条款缺失 3 项, 表述不一致 5 项, 建议补充审批流程和资料留痕要求.",
    },
    {
        "id": 2,
        "name": "合同用印制度比对样例",
        "standard": "通用合规规则库 V2026",
        "uploaded_at": "2026-07-06 16:43:21",
        "status": "比对中",
        "risk_count": 2,
        "summary": "正在进行条款语义比对.",
    },
]
