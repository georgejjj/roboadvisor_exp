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
    DEFAULT_RISK_CATEGORIES
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
        "risk_categories": DEFAULT_RISK_CATEGORIES
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