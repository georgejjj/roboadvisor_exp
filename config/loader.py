import os
import yaml
import logging
import streamlit as st
from config.defaults import (
    DEFAULT_ASSETS, 
    DEFAULT_ASSET_NAMES_EN, 
    DEFAULT_ASSET_DESCRIPTIONS_EN,
    DEFAULT_RISK_RECOMMENDATIONS,
    DEFAULT_RISK_MAPPING,
    DEFAULT_RISK_CATEGORIES,
    DEFAULT_WELCOME_TEXT,
    DEFAULT_BEHAVIOR_QUESTIONS,
    DEFAULT_FINANCIAL_PERSONALITIES,
    DEFAULT_EXPERIMENT_GROUPS
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_config_path(filename):
    """获取配置文件的完整路径"""
    # 在当前目录查找配置文件
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    config_path = os.path.join(config_dir, filename)
    
    if os.path.exists(config_path):
        return config_path
    
    # 备用路径：检查静态文件目录
    static_dir = os.path.join(base_dir, "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    static_config_path = os.path.join(static_dir, filename)
    
    if os.path.exists(static_config_path):
        return static_config_path
    
    # 如果都找不到，默认返回配置目录下的路径
    return config_path

@st.cache_data
def load_config(filename="assets.yaml"):
    """
    加载配置文件并缓存结果
    
    Parameters:
    ----------
    filename : str
        配置文件名称，默认为assets.yaml
        
    Returns:
    -------
    dict
        配置数据字典
    """
    try:
        config_path = get_config_path(filename)
        logger.info(f"尝试加载配置文件: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            logger.info(f"成功加载配置文件: {filename}")
            return config_data
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {filename}，将使用默认配置")
        # 如果文件不存在，返回默认的空配置
        return create_default_config()
    except yaml.YAMLError as e:
        logger.error(f"解析YAML配置文件出错: {e}，将使用默认配置")
        return create_default_config()
    except Exception as e:
        logger.error(f"加载配置文件时发生错误: {e}，将使用默认配置")
        return create_default_config()

def create_default_config():
    """创建默认配置"""
    return {
        "assets": DEFAULT_ASSETS,
        "asset_names_en": DEFAULT_ASSET_NAMES_EN,
        "asset_descriptions_en": DEFAULT_ASSET_DESCRIPTIONS_EN,
        "risk_recommendations": DEFAULT_RISK_RECOMMENDATIONS,
        "risk_mapping": DEFAULT_RISK_MAPPING,
        "risk_categories": DEFAULT_RISK_CATEGORIES,
        "welcome_text": DEFAULT_WELCOME_TEXT,
        "behavior_questions": DEFAULT_BEHAVIOR_QUESTIONS,
        "financial_personalities": DEFAULT_FINANCIAL_PERSONALITIES,
        "experiment_groups": DEFAULT_EXPERIMENT_GROUPS,
        "asset_risk_categories": {
            "风险资产": ["股票", "大宗商品"],
            "安全资产": ["债券", "货币市场", "房地产"]
        }
    }

def get_assets():
    """获取资产数据配置"""
    config = load_config()
    return config.get("assets", DEFAULT_ASSETS)

def get_asset_names_en():
    """获取资产名称英文翻译"""
    config = load_config()
    return config.get("asset_names_en", DEFAULT_ASSET_NAMES_EN)

def get_asset_descriptions_en():
    """获取资产描述英文翻译"""
    config = load_config()
    return config.get("asset_descriptions_en", DEFAULT_ASSET_DESCRIPTIONS_EN)

def get_risk_recommendation(risk_score):
    """
    根据风险评分获取推荐的资产配置
    
    Parameters:
    ----------
    risk_score : float
        风险评分，范围0-100
        
    Returns:
    -------
    dict
        资产配置字典
    """
    config = load_config()
    risk_recommendations = config.get("risk_recommendations", DEFAULT_RISK_RECOMMENDATIONS)
    
    if risk_score < 20:
        return risk_recommendations.get("very_conservative", DEFAULT_RISK_RECOMMENDATIONS["very_conservative"])
    elif risk_score < 40:
        return risk_recommendations.get("conservative", DEFAULT_RISK_RECOMMENDATIONS["conservative"])
    elif risk_score < 60:
        return risk_recommendations.get("moderate", DEFAULT_RISK_RECOMMENDATIONS["moderate"])
    elif risk_score < 80:
        return risk_recommendations.get("aggressive", DEFAULT_RISK_RECOMMENDATIONS["aggressive"])
    else:
        return risk_recommendations.get("very_aggressive", DEFAULT_RISK_RECOMMENDATIONS["very_aggressive"])

def get_risk_mapping():
    """获取问卷风险评分映射"""
    config = load_config()
    return config.get("risk_mapping", DEFAULT_RISK_MAPPING)

def get_risk_category(risk_score):
    """
    根据风险评分获取风险类型描述
    
    Parameters:
    ----------
    risk_score : float
        风险评分，范围0-100
        
    Returns:
    -------
    str
        风险类型描述
    """
    config = load_config()
    risk_categories = config.get("risk_categories", DEFAULT_RISK_CATEGORIES)
    
    for category, info in risk_categories.items():
        if risk_score < info.get("max_score", 100):
            return info.get("name", "未知类型")
    
    # 默认返回最高风险类型
    return DEFAULT_RISK_CATEGORIES["very_aggressive"]["name"]

def get_welcome_text():
    """获取欢迎语文本"""
    config = load_config()
    return config.get("welcome_text", DEFAULT_WELCOME_TEXT)

def get_behavior_questions():
    """获取行为测试问题"""
    config = load_config()
    return config.get("behavior_questions", DEFAULT_BEHAVIOR_QUESTIONS)

def get_financial_personalities():
    """获取金融性格类型"""
    config = load_config()
    return config.get("financial_personalities", DEFAULT_FINANCIAL_PERSONALITIES)

def get_financial_personality(risk_aversion, loss_aversion, mental_accounting):
    """
    根据风险厌恶、损失厌恶和心理账户的值获取对应的金融性格类型
    
    Parameters:
    ----------
    risk_aversion : str
        风险厌恶程度，可能的值为"高"或"低"
        
    loss_aversion : str
        损失厌恶程度，可能的值为"高"或"低"
    
    mental_accounting : str
        心理账户使用程度，可能的值为"高"或"低"
        
    Returns:
    -------
    dict
        金融性格类型信息，包含名称和描述
    """
    config = load_config()
    financial_personalities = config.get("financial_personalities", DEFAULT_FINANCIAL_PERSONALITIES)
    
    key = f"风险厌恶_{risk_aversion}_损失厌恶_{loss_aversion}_心理账户_{mental_accounting}"
    
    if key in financial_personalities:
        return financial_personalities[key]
    else:
        # 如果找不到对应的性格类型，返回一个默认值
        return {
            "name": "平衡投资者",
            "description": "您的投资性格比较平衡，兼具风险管理和收益追求的特点。"
        }

def get_experiment_groups():
    """获取实验分组配置"""
    config = load_config()
    return config.get("experiment_groups", DEFAULT_EXPERIMENT_GROUPS)

def get_experiment_group(group_id):
    """
    根据分组ID获取对应的实验分组配置
    
    Parameters:
    ----------
    group_id : str
        实验分组ID
        
    Returns:
    -------
    dict
        实验分组配置信息
    """
    config = load_config()
    experiment_groups = config.get("experiment_groups", DEFAULT_EXPERIMENT_GROUPS)
    
    if group_id in experiment_groups:
        return experiment_groups[group_id]
    else:
        # 如果找不到对应的分组，返回控制组
        return experiment_groups.get("control", DEFAULT_EXPERIMENT_GROUPS["control"])

def get_asset_risk_categories():
    """获取资产风险类别映射"""
    config = load_config()
    return config.get("asset_risk_categories", {
        "风险资产": ["股票", "大宗商品"],
        "安全资产": ["债券", "货币市场", "房地产"]
    })

def adjust_recommendation(initial_allocation, recommended_allocation, experiment_group, behavior_answers):
    """
    根据实验分组和行为特征调整推荐配置
    
    Parameters:
    ----------
    initial_allocation : dict
        初始资产配置
    recommended_allocation : dict
        标准推荐配置
    experiment_group : dict
        实验分组配置
    behavior_answers : dict
        行为测试答案
        
    Returns:
    -------
    dict
        调整后的推荐配置
    """
    # 如果是控制组或者没有调整规则，直接返回标准推荐
    if experiment_group.get("name") == "控制组" or not experiment_group.get("adjustment"):
        return recommended_allocation
    
    # 深拷贝推荐配置，避免修改原始配置
    import copy
    adjusted = copy.deepcopy(recommended_allocation)
    
    # 获取资产风险类别映射
    asset_categories = get_asset_risk_categories()
    risk_assets = asset_categories.get("风险资产", [])
    safe_assets = asset_categories.get("安全资产", [])
    
    # 获取调整规则
    adjustments = experiment_group.get("adjustment", {})
    
    # 根据行为特征和调整规则进行调整
    strategy = experiment_group.get("recommendation_strategy", "standard")
    
    if strategy == "accommodate":
        # 迎合策略：根据风险厌恶程度调整
        risk_aversion = behavior_answers.get("风险厌恶", "低")
        key = f"risk_aversion_{risk_aversion}"
        
        if key in adjustments:
            rule = adjustments[key]
            
            # 下调风险资产
            if "风险资产_下调" in rule:
                factor = rule["风险资产_下调"]
                for asset in risk_assets:
                    if asset in adjusted:
                        adjusted[asset] = max(0, adjusted[asset] - factor / len(risk_assets))
            
            # 上调风险资产
            if "风险资产_上调" in rule:
                factor = rule["风险资产_上调"]
                for asset in risk_assets:
                    if asset in adjusted:
                        adjusted[asset] = min(1, adjusted[asset] + factor / len(risk_assets))
            
            # 下调安全资产
            if "安全资产_下调" in rule:
                factor = rule["安全资产_下调"]
                for asset in safe_assets:
                    if asset in adjusted:
                        adjusted[asset] = max(0, adjusted[asset] - factor / len(safe_assets))
            
            # 上调安全资产
            if "安全资产_上调" in rule:
                factor = rule["安全资产_上调"]
                for asset in safe_assets:
                    if asset in adjusted:
                        adjusted[asset] = min(1, adjusted[asset] + factor / len(safe_assets))
    
    elif strategy == "educate":
        # 教育策略
        
        # 心理账户教育
        if "心理账户_高" in adjustments and behavior_answers.get("心理账户") == "高":
            rule = adjustments["心理账户_高"]
            
            # 提高分散度
            if "分散度_提高" in rule:
                factor = rule["分散度_提高"]
                # 计算平均配置
                avg_allocation = sum(adjusted.values()) / len(adjusted)
                # 向平均值靠拢
                for asset in adjusted:
                    adjusted[asset] = adjusted[asset] * (1 - factor) + avg_allocation * factor
        
        # 损失厌恶教育
        if "损失厌恶_高" in adjustments and behavior_answers.get("损失厌恶") == "高":
            rule = adjustments["损失厌恶_高"]
            
            # 上调风险资产
            if "风险资产_上调" in rule:
                factor = rule["风险资产_上调"]
                for asset in risk_assets:
                    if asset in adjusted:
                        adjusted[asset] = min(1, adjusted[asset] + factor / len(risk_assets))
            
            # 下调安全资产
            if "安全资产_下调" in rule:
                factor = rule["安全资产_下调"]
                for asset in safe_assets:
                    if asset in adjusted:
                        adjusted[asset] = max(0, adjusted[asset] - factor / len(safe_assets))
    
    # 归一化配置，确保总和为1
    total = sum(adjusted.values())
    if total > 0:
        for asset in adjusted:
            adjusted[asset] = adjusted[asset] / total
    
    return adjusted 