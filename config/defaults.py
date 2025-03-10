# 默认配置数据，当无法从配置文件加载时使用

# 默认资产数据
DEFAULT_ASSETS = {
    "股票": {"expected_return": 0.08, "risk": 0.20, "description": "高风险高回报，具有较高的长期增长潜力"},
    "债券": {"expected_return": 0.04, "risk": 0.05, "description": "中等风险，提供稳定的收入流"},
    "现金": {"expected_return": 0.015, "risk": 0.01, "description": "低风险低回报，具有高流动性"},
    "房地产": {"expected_return": 0.06, "risk": 0.12, "description": "中等风险，提供收入和增长潜力"},
    "黄金": {"expected_return": 0.03, "risk": 0.15, "description": "中等风险，对冲通胀的良好工具"}
}

# 默认资产名称翻译
DEFAULT_ASSET_NAMES_EN = {
    "股票": "Stocks",
    "债券": "Bonds",
    "现金": "Cash",
    "房地产": "Real Estate",
    "黄金": "Gold"
}

# 默认资产描述翻译
DEFAULT_ASSET_DESCRIPTIONS_EN = {
    "股票": "High risk with high return potential, offers significant long-term growth",
    "债券": "Medium risk, provides stable income flow",
    "现金": "Low risk with low returns, highly liquid",
    "房地产": "Medium risk, offers both income and growth potential",
    "黄金": "Medium risk, good hedge against inflation"
}

# 默认风险配置推荐
DEFAULT_RISK_RECOMMENDATIONS = {
    "very_conservative": {  # 风险评分 < 20
        "股票": 0.10,
        "债券": 0.50,
        "现金": 0.30,
        "房地产": 0.05,
        "黄金": 0.05
    },
    "conservative": {  # 风险评分 < 40
        "股票": 0.25,
        "债券": 0.45,
        "现金": 0.15,
        "房地产": 0.10,
        "黄金": 0.05
    },
    "moderate": {  # 风险评分 < 60
        "股票": 0.40,
        "债券": 0.30,
        "现金": 0.05,
        "房地产": 0.15,
        "黄金": 0.10
    },
    "aggressive": {  # 风险评分 < 80
        "股票": 0.60,
        "债券": 0.15,
        "现金": 0.05,
        "房地产": 0.15,
        "黄金": 0.05
    },
    "very_aggressive": {  # 风险评分 >= 80
        "股票": 0.75,
        "债券": 0.05,
        "现金": 0.00,
        "房地产": 0.15,
        "黄金": 0.05
    }
}

# 默认风险评分映射
DEFAULT_RISK_MAPPING = {
    "q1": {
        "不能接受亏损": 0,
        "最多5%": 20,
        "最多10%": 40,
        "最多20%": 60,
        "最多30%": 80,
        "30%以上": 100
    },
    "q2": {
        "立即全部卖出": 0,
        "卖出一部分": 33,
        "不采取行动": 67,
        "买入更多": 100
    },
    "q3": {
        "保本型产品": 0,
        "低风险理财产品": 25,
        "混合型基金": 50,
        "股票型基金": 75,
        "个股": 100
    },
    "q4": {
        "保持资本价值": 0,
        "获得高于通胀的稳定回报": 25,
        "适度资本增长": 50,
        "显著资本增长": 75,
        "积极资本增长": 100
    },
    "q5": {
        "1年以下": 0,
        "1-3年": 25,
        "3-5年": 50,
        "5-10年": 75,
        "10年以上": 100
    }
}

# 默认风险类别
DEFAULT_RISK_CATEGORIES = {
    "very_conservative": {
        "max_score": 20,
        "name": "非常保守型"
    },
    "conservative": {
        "max_score": 40,
        "name": "保守型"
    },
    "moderate": {
        "max_score": 60,
        "name": "平衡型"
    },
    "aggressive": {
        "max_score": 80,
        "name": "进取型"
    },
    "very_aggressive": {
        "max_score": 100,
        "name": "激进型"
    }
} 