import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import matplotlib as mpl
import os
from matplotlib.font_manager import FontProperties
from config.loader import (
    get_assets, 
    get_asset_names_en, 
    get_asset_descriptions_en, 
    get_risk_recommendation,
    get_risk_mapping,
    get_risk_category,
    get_welcome_text,
    get_behavior_questions,
    get_financial_personalities,
    get_financial_personality,
    get_experiment_groups,
    get_experiment_group,
    adjust_recommendation
)

# 定义全局英文标签映射字典 - 用于解决中文字体显示问题
CHINESE_TO_ENGLISH_LABELS = {
    # 资产类别
    '股票': 'Stocks', 
    '债券': 'Bonds', 
    '货币市场': 'Money Market', 
    '房地产': 'Real Estate', 
    '大宗商品': 'Commodities',
    
    # 图表标题
    '风险-收益分布': 'Risk-Return Distribution',
    '当前配置': 'Current Allocation',
    '推荐配置': 'Recommended Allocation',
    '最终配置': 'Final Allocation',
    '资产配置对比': 'Asset Allocation Comparison',
    '投资组合价值变化': 'Portfolio Value Change',
    '累计收益率变化': 'Cumulative Return Change',
    '日收益率分布': 'Daily Return Distribution',
    '金融性格雷达图': 'Financial Personality Radar',
    
    # 坐标轴标签
    '风险 (波动率) %': 'Risk (Volatility) %',
    '预期年化收益率 %': 'Expected Annual Return %',
    '日期': 'Date',
    '累计收益率 (%)': 'Cumulative Return (%)',
    '频率': 'Frequency',
    '日收益率': 'Daily Return',
    
    # 图例和标题
    '资产类别': 'Asset Class',
    '初始方案': 'Initial Plan',
    '推荐方案': 'Recommended Plan',
    '最终方案': 'Final Plan',
    '预期收益': 'Expected Return',
    '预期风险': 'Expected Risk',
    
    # 其他常用标签
    '收益/风险比': 'Return/Risk Ratio',
    '预期风险（波动率）': 'Expected Risk (Volatility)',
    '波动率': 'Volatility',
    '最大回撤': 'Max Drawdown',
    
    # 金融性格维度
    '收益目标': 'Return Target',
    '投资期限': 'Investment Horizon',
    '风险厌恶': 'Risk Aversion',
    '损失厌恶': 'Loss Aversion',
    '心理账户': 'Mental Accounting',
    '过度自信': 'Overconfidence'
}

# 标签转换函数
def get_en_label(zh_label):
    """将中文标签转换为英文标签，对于未定义的标签返回原始值"""
    return CHINESE_TO_ENGLISH_LABELS.get(zh_label, zh_label)

# 设置中文字体的函数
def set_chinese_font():
    """配置matplotlib以显示中文字体，针对Streamlit Share环境优化"""
    try:
        # 检查字体文件是否存在 (支持TTF和OTF)
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        otf_path = os.path.join(font_dir, 'SourceHanSansCN-Normal.otf')
        ttf_path = os.path.join(font_dir, 'SourceHanSansCN-Normal.ttf')
        
        # 打印调试信息
        print(f"字体目录: {font_dir}")
        print(f"OTF字体路径存在: {os.path.exists(otf_path)}")
        print(f"TTF字体路径存在: {os.path.exists(ttf_path)}")
        
        # 使用第一个找到的字体文件
        if os.path.exists(ttf_path):
            font_path = ttf_path
            print(f"使用TTF字体文件: {ttf_path}")
        elif os.path.exists(otf_path):
            font_path = otf_path
            print(f"使用OTF字体文件: {otf_path}")
        else:
            font_path = None
            print("找不到任何可用的中文字体文件")
        
        if font_path:
            # 注册字体文件并设置字体
            from matplotlib.font_manager import fontManager
            fontManager.addfont(font_path)
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['font.sans-serif'] = ['Source Han Sans CN', 'Source Han Sans', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', 'sans-serif']
            print(f"成功加载字体文件: {font_path}")
            
            # 打印当前可用字体列表（调试用）
            from matplotlib.font_manager import findSystemFonts, FontProperties
            fonts = [FontProperties(fname=font).get_name() for font in findSystemFonts(fontpaths=[font_dir])]
            print(f"字体目录中可用字体: {fonts}")
        else:
            # 回退到英文字体并记录警告
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
            print("警告: 无法找到中文字体文件")
            
            # 在显著位置添加中文显示问题警告
            st.warning("⚠️ 中文字体无法正确加载，图表中的中文可能显示为方框。请在本地运行应用以获得最佳体验。", icon="⚠️")
    except Exception as e:
        # 出现异常时记录并使用系统字体
        print(f"设置中文字体时出错: {str(e)}")
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    
    # 统一设置负号显示
    plt.rcParams['axes.unicode_minus'] = False

# Set page config
st.set_page_config(
    page_title="智能投顾实验平台",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define session state variables if not present
if 'page' not in st.session_state:
    st.session_state.page = 0  # 0: welcome, 1: fund info+initial allocation, 2: personal info+questionnaire, 3: behavior quiz, 4: financial personality, 5: recommendations, 6: modification, 7: simulation, 8: link to real account, 9: satisfaction survey
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = 0
if 'initial_allocation' not in st.session_state:
    st.session_state.initial_allocation = None
if 'recommended_allocation' not in st.session_state:
    st.session_state.recommended_allocation = None
if 'final_allocation' not in st.session_state:
    st.session_state.final_allocation = None
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}
if 'language' not in st.session_state:
    st.session_state.language = "zh"  # Default language: Chinese
if 'financial_personality' not in st.session_state:
    st.session_state.financial_personality = None
if 'behavior_answers' not in st.session_state:
    st.session_state.behavior_answers = {}
if 'behavior_scores' not in st.session_state:
    st.session_state.behavior_scores = {
        "收益目标": 0,
        "投资期限": 0,
        "风险厌恶": 0,
        "损失厌恶": 0,
        "心理账户": 0,
        "过度自信": 0
    }
if 'finance_quiz_answers' not in st.session_state:
    st.session_state.finance_quiz_answers = []
if 'finance_quiz_correct' not in st.session_state:
    st.session_state.finance_quiz_correct = 0
if 'experiment_group' not in st.session_state:
    st.session_state.experiment_group = "control"  # 默认为控制组
if 'initial_alloc_values' not in st.session_state:
    st.session_state.initial_alloc_values = {}
if 'final_alloc_values' not in st.session_state:
    st.session_state.final_alloc_values = {}
if 'satisfaction_score' not in st.session_state:
    st.session_state.satisfaction_score = None
if 'satisfaction_feedback' not in st.session_state:
    st.session_state.satisfaction_feedback = ""
if 'real_account_linked' not in st.session_state:
    st.session_state.real_account_linked = False

# Load asset data from configuration
assets = get_assets()
asset_names_en = get_asset_names_en()
asset_descriptions_en = get_asset_descriptions_en()

# Function to calculate portfolio expected return and risk
def calculate_portfolio_metrics(allocation):
    portfolio_return = sum(allocation[asset] * assets[asset]["expected_return"] for asset in allocation)
    
    # Simplified risk calculation (not using correlation matrix for simplicity)
    portfolio_risk = np.sqrt(sum(allocation[asset]**2 * assets[asset]["risk"]**2 for asset in allocation))
    
    return portfolio_return, portfolio_risk

# Function to generate recommended allocation based on risk score
def generate_recommendation(risk_score):
    # 如果是控制组，直接使用用户的初始配置作为推荐配置
    if st.session_state.experiment_group == "control":
        return st.session_state.initial_allocation
    else:
        # 使用配置中的推荐函数
        return get_risk_recommendation(risk_score)

# Function to simulate investment returns
def simulate_returns(allocation, days=365, initial_investment=10000):
    np.random.seed(42)  # For reproducible results
    daily_returns = {}
    cumulative_returns = {}
    
    # Initialize with initial investment
    for asset in allocation:
        daily_returns[asset] = []
        cumulative_returns[asset] = [allocation[asset] * initial_investment]
    
    total_portfolio = [initial_investment]
    
    # Simulate daily returns
    for day in range(1, days + 1):
        daily_total = 0
        for asset in allocation:
            # Daily expected return (annualized/365)
            mu = assets[asset]["expected_return"] / 365
            # Daily volatility (annualized/sqrt(365))
            sigma = assets[asset]["risk"] / np.sqrt(365)
            
            # Generate random daily return
            daily_return = np.random.normal(mu, sigma)
            daily_returns[asset].append(daily_return)
            
            # Update cumulative return
            new_value = cumulative_returns[asset][-1] * (1 + daily_return)
            cumulative_returns[asset].append(new_value)
            daily_total += new_value
        
        total_portfolio.append(daily_total)
    
    return total_portfolio

# Helper function to translate asset names for charts
def get_asset_name_en(asset_zh):
    return asset_names_en.get(asset_zh, asset_zh)

# Welcome page
def welcome_page():
    # Get welcome text from configuration
    welcome_text = get_welcome_text()
    
    st.title("金融性格与模拟投资")
    st.write(welcome_text)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("查看基金信息", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    
    # Add a language selector in the sidebar
    with st.sidebar:
        st.caption("注意：图表将以英文显示以获得更好的兼容性")

# Fund information and initial allocation page (now first page)
def fund_info_allocation_page():
    st.title("资产配置方案")
    
    # Display asset information in a more attractive list format
    st.subheader("可投资基金列表")
    
    # 改为使用3x2网格布局展示基金，每行3个基金
    row1 = st.columns(3)
    row2 = st.columns(3)
    rows = [row1, row2]
    
    # 使用行和列的组合显示基金
    for i, (asset, info) in enumerate(assets.items()):
        row_idx = i // 3  # 每行显示3个基金
        col_idx = i % 3   # 列索引为0, 1, 2
        
        with rows[row_idx][col_idx]:
            st.markdown(f"""
            <div style='padding: 15px; border-radius: 5px; border: 1px solid #ddd; height: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                <h3 style='color: #1E88E5; font-size: 18px;'>{asset}</h3>
                <div style='font-size: 24px; font-weight: bold; color: #FF5722;'>{info["expected_return"]*100:.1f}%</div>
                <div style='font-size: 12px; color: #666;'>预期年化收益率</div>
                <div style='margin-top: 10px; font-size: 14px; font-weight: bold;'>风险指数: {info["risk"]*100:.1f}%</div>
                <div style='margin-top: 5px; font-size: 13px;'>{info["description"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show data table with more detailed information
    with st.expander("显示详细数据", expanded=False):
        # Display formatted data table with Chinese headers
        chinese_df = pd.DataFrame({
            "资产类别": [asset for asset in assets.keys()],
            "预期年化收益率 (%)": [assets[asset]["expected_return"] * 100 for asset in assets],
            "风险 (波动率) (%)": [assets[asset]["risk"] * 100 for asset in assets],
            "收益/风险比": [assets[asset]["expected_return"] / assets[asset]["risk"] for asset in assets]
        })
        
        st.dataframe(
            chinese_df.style.format({
                "预期年化收益率 (%)": "{:.1f}",
                "风险 (波动率) (%)": "{:.1f}",
                "收益/风险比": "{:.2f}"
            }),
            height=200,
            use_container_width=True
        )
        
        # Create risk-return scatter plot with proper Chinese font support
        fig, ax = plt.subplots(figsize=(8, 5))
        # 设置中文字体
        set_chinese_font()
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            plot_title = get_en_label("风险-收益分布") 
            x_label = get_en_label("风险 (波动率) %")
            y_label = get_en_label("预期年化收益率 %")
            # 准备资产名称的英文标签
            asset_labels = {asset: get_en_label(asset) for asset in assets}
        else:
            plot_title = "风险-收益分布"
            x_label = "风险 (波动率) %"
            y_label = "预期年化收益率 %"
            asset_labels = {asset: asset for asset in assets}
        
        # 使用不同的标记和颜色以提高可辨识度
        asset_markers = {'股票': 'o', '债券': 's', '货币市场': '^', '房地产': 'D', '大宗商品': 'P'}
        asset_colors = {'股票': 'red', '债券': 'blue', '货币市场': 'green', '房地产': 'purple', '大宗商品': 'orange'}
        
        # 绘制散点图并添加标签
        for asset, info in assets.items():
            plt.scatter(
                info["risk"] * 100, 
                info["expected_return"] * 100, 
                s=120, 
                alpha=0.7,
                marker=asset_markers.get(asset, 'o'),
                color=asset_colors.get(asset, 'gray'),
                label=asset_labels[asset]
            )
            
            # 添加标签
            plt.annotate(
                asset_labels[asset], 
                (info["risk"] * 100, info["expected_return"] * 100),
                xytext=(5, 5), 
                textcoords='offset points', 
                fontsize=10,
                fontweight='bold'
            )
        
        plt.title(plot_title, fontsize=14, fontweight='bold')
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
    
    # User allocation input
    st.subheader("请分配您的100,000元体验金")
    st.write("请为每个基金分配投资百分比（总计必须等于100%）")
    
    # 使用更新后的资产配置输入函数
    initial_allocation_inputs()

# Questionnaire page (now second page)
def questionnaire_page():
    st.title("个人信息与风险承受能力问卷")
    
    with st.form(key="questionnaire_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("姓名", placeholder="请输入您的姓名")
            age = st.number_input("年龄", min_value=18, max_value=100, value=30)
            gender = st.selectbox("性别", ["男", "女", "其他"])
            income = st.selectbox("年收入（人民币）", 
                ["10万以下", "10-30万", "30-50万", "50-100万", "100万以上"])
            
        with col2:
            investment_exp = st.selectbox("投资经验", 
                ["无经验", "1-3年", "3-5年", "5-10年", "10年以上"])
            
            st.subheader("风险承受能力评估")
            q1 = st.select_slider(
                "1. 您能接受的最大年度投资亏损是多少？",
                options=["不能接受亏损", "最多5%", "最多10%", "最多20%", "最多30%", "30%以上"],
                value="最多10%"
            )
            
            q2 = st.select_slider(
                "2. 如果您的投资在短期内下跌20%，您会：",
                options=["立即全部卖出", "卖出一部分", "不采取行动", "买入更多"],
                value="不采取行动"
            )
            
            q3 = st.select_slider(
                "3. 您更倾向于哪种类型的投资？",
                options=["保本型产品", "低风险理财产品", "混合型基金", "股票型基金", "个股"],
                value="混合型基金"
            )
            
            q4 = st.select_slider(
                "4. 您的投资目标是什么？",
                options=["保持资本价值", "获得高于通胀的稳定回报", "适度资本增长", "显著资本增长", "积极资本增长"],
                value="适度资本增长"
            )
            
            q5 = st.select_slider(
                "5. 您计划的投资期限是多久？",
                options=["1年以下", "1-3年", "3-5年", "5-10年", "10年以上"],
                value="3-5年"
            )
        
        submitted = st.form_submit_button("提交问卷")
        
        if submitted:
            # Calculate risk score (0-100)
            risk_mapping = get_risk_mapping()
            
            score = (risk_mapping["q1"][q1] + risk_mapping["q2"][q2] + 
                     risk_mapping["q3"][q3] + risk_mapping["q4"][q4] + 
                     risk_mapping["q5"][q5]) / 5
            
            # Store personal info and risk score
            st.session_state.personal_info = {
                "name": name,
                "age": age,
                "gender": gender,
                "income": income,
                "investment_exp": investment_exp
            }
            
            st.session_state.risk_score = score
            st.session_state.page = 3  # 进入行为问卷页面
            st.rerun()

# Behavior quiz page
def behavior_quiz_page():
    st.title("金融行为测试问卷")
    
    st.write("""
    感谢您完成了第一轮的资产配置！现在，请回答一些关于您投资行为偏好的问题，
    这将帮助我们分析您的金融性格，并提供更加个性化的建议。
    """)
    
    # 创建一个多步骤表单
    step = st.session_state.get("behavior_quiz_step", 1)
    
    if step == 1:
        # 第一部分：收益目标和投资期限
        with st.form(key="behavior_form_step1"):
            st.subheader("基本投资偏好")
            
            # 收益目标
            st.write("#### 收益目标")
            st.write("根据您目前对资产的投资偏好，您的收益目标更偏向以下哪个范围？")
            return_target = st.radio(
                "收益目标",
                options=["保障本金、对抗通胀（年收益0~3%）", 
                         "实现资产稳健增值（年收益3~7%）", 
                         "实现资产快速增长（年收益7%以上）"],
                label_visibility="collapsed"
            )
            
            # 投资期限
            st.write("#### 投资期限")
            st.write("根据您目前对资产的投资偏好，您的预期投资期限更偏向以下哪个？")
            investment_horizon = st.radio(
                "投资期限",
                options=["6个月及以内", 
                         "6个月以上且1年以内", 
                         "1年以上"],
                label_visibility="collapsed"
            )
            
            # 提交按钮
            submitted = st.form_submit_button("下一步", use_container_width=True)
            
            if submitted:
                # 计算收益目标得分
                if return_target == "保障本金、对抗通胀（年收益0~3%）":
                    st.session_state.behavior_scores["收益目标"] = 20
                elif return_target == "实现资产稳健增值（年收益3~7%）":
                    st.session_state.behavior_scores["收益目标"] = 50
                else:  # 实现资产快速增长
                    st.session_state.behavior_scores["收益目标"] = 80
                
                # 计算投资期限得分
                if investment_horizon == "6个月及以内":
                    st.session_state.behavior_scores["投资期限"] = 20
                elif investment_horizon == "6个月以上且1年以内":
                    st.session_state.behavior_scores["投资期限"] = 50
                else:  # 1年以上
                    st.session_state.behavior_scores["投资期限"] = 80
                
                # 保存回答
                st.session_state.behavior_answers["收益目标"] = return_target
                st.session_state.behavior_answers["投资期限"] = investment_horizon
                
                # 进入下一步
                st.session_state.behavior_quiz_step = 2
                st.rerun()
    
    elif step == 2:
        # 第二部分：风险厌恶
        with st.form(key="behavior_form_step2"):
            st.subheader("风险厌恶")
            st.write("""
            假设您现在有1万元资金可以投资，有A和B两种投资方式供选择。
            A在一年后将获得确定的收益，B在一年后将有50%的概率获得如下收益，50%的概率不获得收益。
            请您在以下每组中选择更偏好的投资方式。
            """)
            
            # 风险厌恶问题1-4
            risk_q1 = st.radio(
                "第1组",
                options=["A：100%收益400元", "B：50%收益760元，50%收益0元"],
            )
            
            risk_q2 = st.radio(
                "第2组",
                options=["A：100%收益400元", "B：50%收益960元，50%收益0元"],
            )
            
            risk_q3 = st.radio(
                "第3组",
                options=["A：100%收益400元", "B：50%收益1240元，50%收益0元"],
            )
            
            risk_q4 = st.radio(
                "第4组",
                options=["A：100%收益400元", "B：50%收益1600元，50%收益0元"],
            )
            
            # 提交按钮
            submitted = st.form_submit_button("下一步", use_container_width=True)
            
            if submitted:
                # 保存回答
                risk_answers = [risk_q1, risk_q2, risk_q3, risk_q4]
                st.session_state.behavior_answers["风险厌恶"] = risk_answers
                
                # 计算风险厌恶得分 - 找到第一个选B的题号
                risk_aversion_score = 20  # 默认值（所有题都选A）
                for i, answer in enumerate(risk_answers):
                    if "B" in answer:
                        if i == 0:  # 第1题
                            risk_aversion_score = 100
                        elif i == 1:  # 第2题
                            risk_aversion_score = 80
                        elif i == 2:  # 第3题
                            risk_aversion_score = 60
                        elif i == 3:  # 第4题
                            risk_aversion_score = 40
                        break
                
                st.session_state.behavior_scores["风险厌恶"] = risk_aversion_score
                
                # 进入下一步
                st.session_state.behavior_quiz_step = 3
                st.rerun()
    
    elif step == 3:
        # 第三部分：损失厌恶
        with st.form(key="behavior_form_step3"):
            st.subheader("损失厌恶")
            st.write("""
            假设您现在有1万元资金可以投资，有A和B两种投资方式供选择。
            A在一年后将获得确定的收益，B在一年后将有50%的概率获得如下收益，50%的概率产生如下损失。
            请您在以下每组中选择更偏好的投资方式。
            """)
            
            # 损失厌恶问题1-4
            loss_q1 = st.radio(
                "第1组",
                options=["A：100%收益200元", "B：50%收益800元，50%损失400元"],
            )
            
            loss_q2 = st.radio(
                "第2组",
                options=["A：100%收益200元", "B：50%收益1040元，50%损失400元"],
            )
            
            loss_q3 = st.radio(
                "第3组",
                options=["A：100%收益200元", "B：50%收益1280元，50%损失400元"],
            )
            
            loss_q4 = st.radio(
                "第4组",
                options=["A：100%收益200元", "B：50%收益1520元，50%损失400元"],
            )
            
            # 提交按钮
            submitted = st.form_submit_button("下一步", use_container_width=True)
            
            if submitted:
                # 保存回答
                loss_answers = [loss_q1, loss_q2, loss_q3, loss_q4]
                st.session_state.behavior_answers["损失厌恶"] = loss_answers
                
                # 计算损失厌恶得分 - 找到第一个选B的题号
                loss_aversion_score = 20  # 默认值（所有题都选A）
                for i, answer in enumerate(loss_answers):
                    if "B" in answer:
                        if i == 0:  # 第1题
                            loss_aversion_score = 100
                        elif i == 1:  # 第2题
                            loss_aversion_score = 80
                        elif i == 2:  # 第3题
                            loss_aversion_score = 60
                        elif i == 3:  # 第4题
                            loss_aversion_score = 40
                        break
                
                st.session_state.behavior_scores["损失厌恶"] = loss_aversion_score
                
                # 进入下一步
                st.session_state.behavior_quiz_step = 4
                st.rerun()
    
    elif step == 4:
        # 第四部分：心理账户
        with st.form(key="behavior_form_step4"):
            st.subheader("心理账户（组合投资）")
            st.write("""
            假设您目前同时持有两只股票A和B，根据您在下列问题的选择，
            它们会同时决定您的最终收益。
            """)
            
            # 心理账户问题1-2
            mental_q1 = st.radio(
                "股票A现在相比购入价赚了2400元，如果现在卖掉可以确定赚到2400元，如果持有到下一期50%的概率赚10000元，50%的概率不赚也不赔，请问您选择卖掉还是持有？",
                options=["现在卖掉", "持有到下一期"]
            )
            
            mental_q2 = st.radio(
                "股票B现在相比购入价赔了7500元，如果现在卖掉将会确定损失7500元，如果持有到下一期50%的概率会亏10000元，50%的概率不赚也不赔，请问您选择卖掉还是持有？",
                options=["现在卖掉", "持有到下一期"]
            )
            
            # 提交按钮
            submitted = st.form_submit_button("下一步", use_container_width=True)
            
            if submitted:
                # 保存回答
                st.session_state.behavior_answers["心理账户"] = [mental_q1, mental_q2]
                
                # 计算心理账户得分
                # 如果在第一题选"现在卖掉"且在第二题选"持有到下一期"，则组合投资待提高（30），否则组合投资优秀（80）
                if mental_q1 == "现在卖掉" and mental_q2 == "持有到下一期":
                    mental_accounting_score = 30
                else:
                    mental_accounting_score = 80
                
                st.session_state.behavior_scores["心理账户"] = mental_accounting_score
                
                # 进入下一步
                st.session_state.behavior_quiz_step = 5
                st.rerun()
    
    elif step == 5:
        # 第五部分：过度自信
        with st.form(key="behavior_form_step5"):
            st.subheader("金融知识测试")
            st.write("下面请您做3道金融知识小测试")
            
            # 金融知识问题1-3
            finance_q1 = st.radio(
                "问题1：10000元以3%的年利率续存10年，10年后可以取出多少钱？",
                options=["恰好10000元", "恰好10300元", "恰好13000元", "多于13000元"]
            )
            
            finance_q2 = st.radio(
                "问题2：通常情况下，下列哪一项投资回报率的风险最大？",
                options=["银行存款", "股票", "基金"]
            )
            
            finance_q3 = st.radio(
                "问题3：如果银行存款利率上升，债券利率一般会如何变化？",
                options=["上升", "不变", "下降"]
            )
            
            # 计算正确答案数量
            correct_answers = 0
            if finance_q1 == "多于13000元":  # 正确答案D
                correct_answers += 1
            if finance_q2 == "股票":  # 正确答案B
                correct_answers += 1
            if finance_q3 == "上升":  # 正确答案A
                correct_answers += 1
            
            # 保存答案和正确数量
            st.session_state.finance_quiz_answers = [finance_q1, finance_q2, finance_q3]
            st.session_state.finance_quiz_correct = correct_answers
            
            # 提交按钮
            submitted = st.form_submit_button("下一步", use_container_width=True)
            
            if submitted:
                # 进入下一步
                st.session_state.behavior_quiz_step = 6
                st.rerun()
    
    elif step == 6:
        # 第六部分：过度自信评估
        with st.form(key="behavior_form_step6"):
            st.subheader("自我评估")
            
            # 过度自信问题1-2
            overconfidence_q1 = st.number_input(
                "在上面的金融知识小测试的3道题中您认为自己答对了几道题？",
                min_value=0,
                max_value=3,
                value=2
            )
            
            overconfidence_q2 = st.slider(
                "您认为自己在这个测试的表现在填写问卷的人群中能排名在前百分之多少？",
                min_value=1,
                max_value=100,
                value=50,
                format="%d%%"
            )
            
            # 提交按钮
            submitted = st.form_submit_button("完成问卷", use_container_width=True)
            
            if submitted:
                # 保存回答
                st.session_state.behavior_answers["过度自信"] = [overconfidence_q1, overconfidence_q2]
                
                # 计算过度自信得分 - G1 = 认为自己答对了几道题 - 实际答对了几道题
                G1 = overconfidence_q1 - st.session_state.finance_quiz_correct
                
                # 根据G1确定过度自信得分
                if G1 <= 0:  # -3、-2、-1、0
                    overconfidence_score = 100
                elif G1 == 1:
                    overconfidence_score = 70
                elif G1 == 2:
                    overconfidence_score = 40
                else:  # G1 == 3
                    overconfidence_score = 20
                
                st.session_state.behavior_scores["过度自信"] = overconfidence_score
                
                # 确定金融性格
                personality = determine_financial_personality(st.session_state.behavior_scores)
                st.session_state.financial_personality = personality
                
                # 重置步骤计数器，以便下次从头开始
                st.session_state.behavior_quiz_step = 1
                
                # 进入金融性格页面
                st.session_state.page = 4
                st.rerun()
    
    # 显示当前进度
    progress = (step - 1) / 6  # 总共6步，从0到1的比例
    st.progress(progress)
    st.caption(f"第 {step}/6 部分")

# Financial personality page
def financial_personality_page():
    st.title("您的金融性格分析")
    
    # 显示问卷得分和金融性格
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # 显示雷达图
        fig = plt.figure(figsize=(8, 8))
        
        # 准备数据
        categories = list(st.session_state.behavior_scores.keys())
        values = list(st.session_state.behavior_scores.values())
        
        # 闭合雷达图需要首尾相连
        categories = categories + [categories[0]]
        values = values + [values[0]]
        
        # 计算角度
        N = len(categories) - 1
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # 闭合
        
        # 初始化雷达图
        ax = plt.subplot(111, polar=True)
        
        # 绘制多边形
        ax.fill(angles, values, 'b', alpha=0.1)
        
        # 绘制轮廓线
        ax.plot(angles, values, 'b', linewidth=2)
        
        # 添加标签
        if st.session_state.use_english_labels:
            chart_title = get_en_label("金融性格雷达图")
            label_map = {k: get_en_label(k) for k in categories}
            plt.xticks(angles[:-1], [label_map[cat] for cat in categories[:-1]], size=12)
        else:
            chart_title = "金融性格雷达图"
            plt.xticks(angles[:-1], categories[:-1], size=12)
        
        # 设置图表外观
        ax.set_rlabel_position(0)
        plt.yticks([0, 20, 40, 60, 80, 100], ["0", "20", "40", "60", "80", "100"], color="grey", size=10)
        plt.ylim(0, 100)
        
        plt.title(chart_title, size=16, y=1.1)
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("您的行为偏好得分")
        
        # 创建得分表格
        scores_df = pd.DataFrame({
            "维度": list(st.session_state.behavior_scores.keys()),
            "得分": list(st.session_state.behavior_scores.values())
        })
        
        # 设置条形图颜色映射
        cmap = plt.cm.get_cmap('coolwarm')
        norm = plt.Normalize(20, 100)  # 分数范围从20到100
        
        # 创建自定义条形图表格
        st.dataframe(
            scores_df,
            hide_index=True,
            column_config={
                "维度": st.column_config.TextColumn("维度"),
                "得分": st.column_config.ProgressColumn(
                    "得分",
                    min_value=0,
                    max_value=100,
                    format="%d",
                )
            },
            use_container_width=True
        )
    
    # 显示金融性格
    personality = st.session_state.financial_personality
    
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 10px; background-color: #f0f8ff; margin: 20px 0;'>
        <h2 style='color: #1E88E5;'>{personality["name"]}</h2>
        <p style='font-size: 16px;'>{personality["description"]}</p>
        <p style='font-size: 16px; font-weight: bold; color: #1E88E5;'>{personality["advice"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to continue to recommendations
    if st.button("查看投资建议", use_container_width=True):
        # 获取标准推荐配置
        standard_recommendation = generate_recommendation(st.session_state.risk_score)
        
        # 获取当前实验分组配置
        experiment_group = get_experiment_group(st.session_state.experiment_group)
        
        # 调整推荐配置
        adjusted_recommendation = adjust_recommendation(
            st.session_state.initial_allocation,
            standard_recommendation,
            experiment_group,
            st.session_state.behavior_scores
        )
        
        # 保存推荐配置
        st.session_state.recommended_allocation = adjusted_recommendation
        
        st.session_state.page = 5
        st.rerun()

# Helper function for initial allocation inputs
def initial_allocation_inputs():
    """处理初始资产配置输入"""
    # 初始化session状态
    if not st.session_state.initial_alloc_values:
        st.session_state.initial_alloc_values = {asset: 0.0 for asset in assets}
    
    # 使用常规输入控件代替表单，以支持实时更新
    st.write("请直接输入各资产配置比例：")
    
    # 使用3x2网格布局，每行显示3个资产输入
    row1 = st.columns(3)
    row2 = st.columns(3)
    rows = [row1, row2]
    
    # 创建用于处理输入变化的回调函数
    def update_allocation(asset):
        # 回调函数不需要实际操作，因为输入值已自动保存到session_state
        pass
    
    # 确保所有资产在session_state中都有初始值
    for asset in assets:
        if asset not in st.session_state.initial_alloc_values:
            st.session_state.initial_alloc_values[asset] = 0.0
    
    # 使用行和列的组合显示输入控件
    for i, asset in enumerate(assets):
        row_idx = i // 3  # 每行显示3个资产
        col_idx = i % 3   # 列索引为0, 1, 2
        
        with rows[row_idx][col_idx]:
            # 添加卡片式样式，使得输入字段更美观
            st.markdown(f"""<div style='margin-bottom: 5px; font-weight: bold; color: #333;'>{asset}</div>""", unsafe_allow_html=True)
            st.number_input(
                "配置比例 (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.initial_alloc_values.get(asset, 0.0)),
                step=1.0,
                key=f"initial_allocation_{asset}",
                on_change=update_allocation,
                args=(asset,),
                label_visibility="collapsed"
            )
            # 更新session_state中的值
            st.session_state.initial_alloc_values[asset] = st.session_state[f"initial_allocation_{asset}"]
    
    # 计算总和 - 这里会在每次界面刷新时重新计算，实现"实时"更新
    total = sum(st.session_state.initial_alloc_values.values())
    
    # 使用更醒目的样式显示总和状态
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # 添加间距
    if abs(total - 100.0) < 0.01:
        st.markdown(f"""
        <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 15px;'>
            总配置比例: {total:.1f}% ✓
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 15px;'>
            总配置比例: {total:.1f}% (应当等于100%)
        </div>
        """, unsafe_allow_html=True)
    
    # 提交按钮，使用更吸引人的样式
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # 添加间距
    if st.button("提交配置方案", use_container_width=True, type="primary"):
        # 检查总和是否接近100%
        if abs(total - 100.0) > 0.01:
            st.error(f"您的配置总计为{total:.1f}%，请确保总计等于100%")
        else:
            # 转换为小数格式用于内部计算
            initial_alloc = {asset: st.session_state.initial_alloc_values[asset] / 100.0 for asset in assets}
            st.session_state.initial_allocation = initial_alloc
            # 进入个人信息与风险问卷页面
            st.session_state.page = 2
            st.rerun()

# Simulation page (now at index 7)
def simulation_page():
    st.title("投资收益模拟")
    
    # Sidebar for simulation parameters
    with st.sidebar:
        st.header("模拟参数")
        initial_investment = st.number_input(
            "初始投资金额（人民币）", 
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=10000,
            format="%d"
        )
        
        simulation_period = st.slider(
            "模拟期限（天）",
            min_value=30,
            max_value=3650,
            value=365,
            step=30
        )
        
        st.caption("注意：本模拟使用蒙特卡洛方法基于历史数据和统计分布生成可能的投资路径。实际投资表现可能与模拟结果有显著差异。")
    
    # 设置中文字体
    set_chinese_font()
    
    # Run simulations
    initial_simulation = simulate_returns(
        st.session_state.initial_allocation, 
        days=simulation_period, 
        initial_investment=initial_investment
    )
    
    final_simulation = simulate_returns(
        st.session_state.final_allocation, 
        days=simulation_period, 
        initial_investment=initial_investment
    )
    
    # 只有非控制组才显示推荐方案的模拟
    is_control_group = st.session_state.experiment_group == "control"
    
    if not is_control_group:
        recommended_simulation = simulate_returns(
            st.session_state.recommended_allocation, 
            days=simulation_period, 
            initial_investment=initial_investment
        )
        recommended_return = (recommended_simulation[-1] - initial_investment) / initial_investment * 100
    
    # Calculate key metrics
    initial_return = (initial_simulation[-1] - initial_investment) / initial_investment * 100
    final_return = (final_simulation[-1] - initial_investment) / initial_investment * 100
    
    # Create dataframe for simulation results
    days = list(range(simulation_period + 1))
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in days]
    
    if is_control_group:
        sim_df = pd.DataFrame({
            'Date': dates,
            '初始方案': initial_simulation,
            '最终方案': final_simulation
        })
    else:
        sim_df = pd.DataFrame({
            'Date': dates,
            '初始方案': initial_simulation,
            '推荐方案': recommended_simulation,
            '最终方案': final_simulation
        })
    
    # 使用容器组织内容，更紧凑的布局
    with st.container():
        # 使用列布局展示关键指标 - 控制组只有两列
        if is_control_group:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("初始方案", f"{initial_simulation[-1]:,.0f}元", f"{initial_return:.1f}%")
            with col2:
                st.metric("最终方案", f"{final_simulation[-1]:,.0f}元", f"{final_return:.1f}%")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("初始方案", f"{initial_simulation[-1]:,.0f}元", f"{initial_return:.1f}%")
            with col2:
                st.metric("推荐方案", f"{recommended_simulation[-1]:,.0f}元", f"{recommended_return:.1f}%")
            with col3:
                st.metric("最终方案", f"{final_simulation[-1]:,.0f}元", f"{final_return:.1f}%")
    
    # 投资组合价值变化图表 - 使用更紧凑的尺寸
    st.subheader("投资组合价值变化")
    
    # 采样数据以避免过度拥挤 (大约每月)
    sample_freq = max(1, simulation_period // 30)
    
    # 使用更小的图表
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # 根据用户设置选择标签语言
    if st.session_state.use_english_labels:
        plot_title = get_en_label("投资组合价值变化")
        x_label = get_en_label("日期")
        y_label = "Portfolio Value (CNY)"  # 特殊处理货币单位
        legend_initial = get_en_label("初始方案")
        legend_recommended = get_en_label("推荐方案")
        legend_final = get_en_label("最终方案")
    else:
        plot_title = "资产价值变化"
        x_label = "日期"
        y_label = "投资组合价值 (元)"
        legend_initial = "初始方案"
        legend_recommended = "推荐方案"
        legend_final = "最终方案"
    
    # 绘制图表 - 控制组只有两条线
    plt.plot(dates[::sample_freq], initial_simulation[::sample_freq], 
             label=legend_initial, linewidth=2, linestyle='-', color='blue')
            
    if not is_control_group:
        plt.plot(dates[::sample_freq], recommended_simulation[::sample_freq], 
                 label=legend_recommended, linewidth=2, linestyle='--', color='green')
    
    plt.plot(dates[::sample_freq], final_simulation[::sample_freq], 
             label=legend_final, linewidth=2, linestyle='-.', color='red')
    
    plt.title(plot_title, fontsize=12, fontweight='bold')
    plt.xlabel(x_label, fontsize=10)
    plt.ylabel(y_label, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='best')
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    
    # 确保图例不重叠
    plt.tight_layout()
    st.pyplot(fig)
    
    # 所有详细分析放入标签页中
    tab1, tab2, tab3 = st.tabs(["收益分析", "风险分析", "累计收益"])
    
    with tab1:
        # 排列详细指标表格
        st.subheader("收益指标详情")
        
        # 计算更详细的绩效指标
        def calculate_metrics(daily_returns, total_return, period):
            volatility = np.std(daily_returns) * np.sqrt(252) * 100
            sharpe_ratio = (total_return / (period/365)) / volatility if volatility > 0 else 0
            max_drawdown = 0
            
            # 计算最大回撤
            if len(daily_returns) > 0:
                wealth_index = (1 + np.array(daily_returns)).cumprod()
                previous_peaks = np.maximum.accumulate(wealth_index)
                drawdowns = (wealth_index - previous_peaks) / previous_peaks
                max_drawdown = abs(min(drawdowns)) * 100 if len(drawdowns) > 0 else 0
            
            return {
                "年化收益率 (%)": f"{total_return / (period/365):.2f}",
                "波动率 (%)": f"{volatility:.2f}",
                "夏普比率": f"{sharpe_ratio:.2f}",
                "最大回撤 (%)": f"{max_drawdown:.2f}",
                "收益/风险比": f"{(total_return / (period/365)) / volatility if volatility > 0 else 0:.2f}"
            }
        
        # 计算日收益率用于指标计算
        daily_returns_initial = np.diff(initial_simulation) / initial_simulation[:-1]
        daily_returns_final = np.diff(final_simulation) / final_simulation[:-1]
        
        if not is_control_group:
            daily_returns_recommended = np.diff(recommended_simulation) / recommended_simulation[:-1]
        
        # 创建绩效指标表格
        metrics = {
            "初始方案": calculate_metrics(daily_returns_initial, initial_return/100, simulation_period),
            "最终方案": calculate_metrics(daily_returns_final, final_return/100, simulation_period)
        }
        
        if not is_control_group:
            metrics["推荐方案"] = calculate_metrics(daily_returns_recommended, recommended_return/100, simulation_period)
        
        # 转换为更易读的表格格式
        metrics_rows = []
        for metric_name in metrics["初始方案"].keys():
            row = {
                "指标": metric_name,
                "初始方案": metrics["初始方案"][metric_name]
            }
            
            if not is_control_group:
                row["推荐方案"] = metrics["推荐方案"][metric_name]
                
            row["最终方案"] = metrics["最终方案"][metric_name]
            metrics_rows.append(row)
        
        metrics_df = pd.DataFrame(metrics_rows)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with tab2:
        # 日收益率分布图
        st.subheader("日收益率分布")
        
        # 使用更小的图表
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            plot_title = get_en_label("日收益率分布")
            x_label = get_en_label("日收益率")
            y_label = get_en_label("频率")
            legend_initial = get_en_label("初始方案")
            legend_recommended = get_en_label("推荐方案")
            legend_final = get_en_label("最终方案")
        else:
            plot_title = "日收益率分布对比"
            x_label = "日收益率"
            y_label = "频率"
            legend_initial = "初始方案"
            legend_recommended = "推荐方案"
            legend_final = "最终方案"
        
        # 使用半透明直方图以便于比较 - 控制组只有两个直方图
        plt.hist(daily_returns_initial, bins=30, alpha=0.4, label=legend_initial, color='blue')
        
        if not is_control_group:
            plt.hist(daily_returns_recommended, bins=30, alpha=0.4, label=legend_recommended, color='green')
            
        plt.hist(daily_returns_final, bins=30, alpha=0.4, label=legend_final, color='red')
        
        plt.title(plot_title, fontsize=12, fontweight='bold')
        plt.xlabel(x_label, fontsize=10)
        plt.ylabel(y_label, fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=10)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        
        # 添加一个信息区域解释风险指标
        if st.session_state.use_english_labels:
            st.info("""
            **Volatility**: Measures the variability of portfolio returns. Higher values indicate higher risk.
            **Max Drawdown**: The maximum percentage loss from peak to trough during a specific period.
            **Sharpe Ratio**: Excess return per unit of risk. Higher values indicate better investment efficiency.
            """)
        else:
            st.info("""
            **波动率**: 衡量投资组合收益的波动程度，值越高表示风险越大。
            **最大回撤**: 投资组合在特定时期内从峰值到谷值的最大损失百分比。
            **夏普比率**: 每单位波动风险所获得的超额收益，值越高表示投资效率越高。
            """)
    
    with tab3:
        # 累计收益率图表
        st.subheader("累计收益率对比")
        
        # 计算累计收益率
        initial_cum_returns = [(val - initial_investment) / initial_investment * 100 for val in initial_simulation]
        final_cum_returns = [(val - initial_investment) / initial_investment * 100 for val in final_simulation]
        
        if not is_control_group:
            rec_cum_returns = [(val - initial_investment) / initial_investment * 100 for val in recommended_simulation]
        
        # 使用更小的图表
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            plot_title = get_en_label("累计收益率变化")
            x_label = get_en_label("日期")
            y_label = get_en_label("累计收益率 (%)")
            legend_initial = get_en_label("初始方案")
            legend_recommended = get_en_label("推荐方案")
            legend_final = get_en_label("最终方案")
        else:
            plot_title = "累计收益率变化"
            x_label = "日期"
            y_label = "累计收益率 (%)"
            legend_initial = "初始方案"
            legend_recommended = "推荐方案"
            legend_final = "最终方案"
        
        # 控制组只显示两条线    
        plt.plot(dates[::sample_freq], initial_cum_returns[::sample_freq], 
                 label=legend_initial, linewidth=2, color='blue')
        
        if not is_control_group:
            plt.plot(dates[::sample_freq], rec_cum_returns[::sample_freq], 
                     label=legend_recommended, linewidth=2, color='green')
                 
        plt.plot(dates[::sample_freq], final_cum_returns[::sample_freq], 
                 label=legend_final, linewidth=2, color='red')
        
        plt.title(plot_title, fontsize=12, fontweight='bold')
        plt.xlabel(x_label, fontsize=10)
        plt.ylabel(y_label, fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=10)
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
    
    # 数据下载选项
    with st.expander("数据下载", expanded=False):
        st.write("您可以下载模拟数据以便进一步分析：")
        
        # 准备可下载的CSV数据
        csv = sim_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="下载CSV数据",
            data=csv,
            file_name=f"模拟数据_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
        
        # 显示数据样本
        st.write("数据预览:")
        st.dataframe(sim_df.head(10), use_container_width=True)
    
    # 底部按钮区域
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # 链接实盘按钮
        if st.button("链接实盘账户", use_container_width=True):
            st.session_state.page = 8
            st.rerun()
    
    with col2:
        # 重新开始实验按钮
        if st.button("重新开始实验", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 0
            st.rerun()

# Add new Real Account Linking page
def link_real_account_page():
    st.title("链接实盘账户")
    
    st.write("""
    您已完成模拟投资体验。现在您可以选择将您的最终配置方案链接到实盘账户，
    开始真实的投资旅程。
    """)
    
    # 显示最终配置结果
    st.subheader("您的最终配置方案")
    
    final_allocation_data = {
        "资产": [asset for asset in assets],
        "配置比例 (%)": [st.session_state.final_allocation[asset] * 100 for asset in assets]
    }
    final_allocation_df = pd.DataFrame(final_allocation_data)
    st.dataframe(final_allocation_df, use_container_width=True, hide_index=True)
    
    # 链接实盘选项
    st.subheader("链接实盘账户")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        account_type = st.selectbox(
            "请选择您的账户类型",
            ["证券账户", "基金账户", "银行理财账户", "其他"]
        )
        
        account_number = st.text_input("请输入您的账户号码（选填）", placeholder="例如: 123456789")
        
    with col2:
        st.markdown("""
        <div style='background-color: #f0f8ff; padding: 20px; border-radius: 5px; margin-top: 30px;'>
            <h4 style='color: #1E88E5;'>安全提示</h4>
            <p>您的账户信息将被加密存储，仅用于配置关联。我们不会存储您的密码或进行任何未授权操作。</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("链接实盘账户", use_container_width=True):
        # 在实际应用中，这里会有账户验证和链接的功能逻辑
        st.session_state.real_account_linked = True
        st.success("您的账户已成功链接！配置方案将在工作日内同步到您的实盘账户。")
        
        # 自动进入满意度调查
        if st.button("继续完成满意度调查", use_container_width=True):
            st.session_state.page = 9
            st.rerun()
    
    # 跳过选项
    if st.button("暂不链接，直接进入满意度调查", use_container_width=True):
        st.session_state.page = 9
        st.rerun()

# Add new Satisfaction Survey page
def satisfaction_survey_page():
    st.title("用户满意度调查")
    
    # 检查是否已经提交过满意度调查
    if st.session_state.get('survey_submitted', False):
        # 显示感谢信息
        st.success("感谢您的反馈！我们将不断改进我们的服务。")
        
        # 提供重新开始的选项
        if st.button("重新开始体验", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 0
            st.rerun()
        return
    
    st.write("""
    感谢您使用我们的智能投顾服务！请花一点时间完成以下满意度调查，
    您的反馈对我们改进服务非常重要。
    """)
    
    with st.form(key="satisfaction_form"):
        st.subheader("整体满意度")
        satisfaction = st.slider(
            "您对本次智能投顾体验的总体满意度评分是？",
            min_value=1,
            max_value=10,
            value=8,
            help="1分表示非常不满意，10分表示非常满意"
        )
        
        st.subheader("具体反馈")
        col1, col2 = st.columns(2)
        
        with col1:
            interface_rating = st.select_slider(
                "界面易用性",
                options=["很差", "较差", "一般", "良好", "优秀"],
                value="良好"
            )
            
            recommendation_rating = st.select_slider(
                "推荐方案合理性",
                options=["很差", "较差", "一般", "良好", "优秀"],
                value="良好"
            )
        
        with col2:
            clarity_rating = st.select_slider(
                "信息清晰度",
                options=["很差", "较差", "一般", "良好", "优秀"],
                value="良好"
            )
            
            simulation_rating = st.select_slider(
                "模拟收益体验",
                options=["很差", "较差", "一般", "良好", "优秀"],
                value="良好"
            )
        
        feedback = st.text_area(
            "您对我们的服务有哪些建议或意见？",
            height=150,
            placeholder="请在此输入您的反馈意见..."
        )
        
        submit_button = st.form_submit_button("提交反馈", use_container_width=True)
        
        if submit_button:
            # 保存满意度评价
            st.session_state.satisfaction_score = satisfaction
            st.session_state.satisfaction_feedback = feedback
            # 标记调查已提交
            st.session_state.survey_submitted = True
            # 使用rerun来刷新页面显示感谢信息
            st.rerun()

# Main app logic
def main():
    # 初始化中文字体设置
    set_chinese_font()
    
    # 检查是否需要显示英文标签的提示
    if 'use_english_labels' not in st.session_state:
        # 默认使用英文标签以解决字体问题
        st.session_state.use_english_labels = True
    
    # Sidebar navigation
    with st.sidebar:
        st.title("金融性格与模拟投资")
        st.write("---")
        
        # 添加图表语言切换选项
        st.session_state.use_english_labels = st.checkbox(
            "在图表中使用英文标签 (解决中文显示问题)", 
            value=st.session_state.use_english_labels,
            help="默认选中以避免中文显示为方框，如果您的环境支持中文显示，可以取消选中"
        )
        
        # 实验分组选择 - 在每一页都显示
        experiment_group_selection()
        
        # Show progress in sidebar
        if st.session_state.page > 0:
            st.write("### 实验进度")
            progress_labels = ["开始", "基金信息与配置", "个人信息", "行为测试", "金融性格", 
                              "推荐方案", "修改方案", "收益模拟", "链接实盘", "满意度调查"]
            progress_value = st.session_state.page / (len(progress_labels) - 1)
            st.progress(progress_value)
            st.write(f"当前阶段: {progress_labels[st.session_state.page]}")
            
            # Navigation buttons
            if st.session_state.page > 1:
                if st.button("← 返回", use_container_width=True):
                    st.session_state.page -= 1
                    st.rerun()
            
            # 显示当前实验分组名称
            if st.session_state.page >= 4:  # 金融性格分析页及之后显示
                experiment_group = get_experiment_group(st.session_state.experiment_group)
                st.caption(f"当前实验组：{experiment_group['name']}")
    
    # Display appropriate page based on session state
    if st.session_state.page == 0:
        welcome_page()
    elif st.session_state.page == 1:
        fund_info_allocation_page()
    elif st.session_state.page == 2:
        questionnaire_page()
    elif st.session_state.page == 3:
        behavior_quiz_page()
    elif st.session_state.page == 4:
        financial_personality_page()
    elif st.session_state.page == 5:
        recommendation_page()
    elif st.session_state.page == 6:
        modification_page()
    elif st.session_state.page == 7:
        simulation_page()
    elif st.session_state.page == 8:
        link_real_account_page()
    elif st.session_state.page == 9:
        satisfaction_survey_page()

# 根据行为问卷得分确定金融性格
def determine_financial_personality(scores):
    """基于四个维度的分数确定金融性格类型"""
    # 确定每个维度的高低
    risk_aversion_level = "高" if scores["风险厌恶"] >= 50 else "低"
    loss_aversion_level = "高" if scores["损失厌恶"] >= 50 else "低"
    mental_accounting_level = "高" if scores["心理账户"] >= 50 else "低"
    overconfidence_level = "高" if scores["过度自信"] >= 50 else "低"
    
    # 构建金融性格类型的键
    personality_key = f"风险厌恶_{risk_aversion_level}_损失厌恶_{loss_aversion_level}_心理账户_{mental_accounting_level}_过度自信_{overconfidence_level}"
    
    # 从配置中获取对应的金融性格类型
    financial_personalities = get_financial_personalities()
    
    if personality_key in financial_personalities:
        return financial_personalities[personality_key]
    else:
        # 如果找不到对应的性格类型，返回一个默认值
        return {
            "name": "平衡投资者",
            "description": "您的投资性格比较平衡，兼具风险管理和收益追求的特点。",
            "advice": "建议您采用均衡的投资策略，合理配置不同风险的资产。"
        }

# Helper function to update experiment group selection
def experiment_group_selection():
    """在侧边栏显示实验分组选择器"""
    st.subheader("实验分组设置")
    experiment_groups = get_experiment_groups()
    group_options = {group_info["name"]: group_id for group_id, group_info in experiment_groups.items()}
    
    # 找到当前实验组对应的名称
    current_group_name = None
    for name, group_id in group_options.items():
        if group_id == st.session_state.experiment_group:
            current_group_name = name
            break
    
    # 如果找不到当前组名，使用控制组作为默认值
    if not current_group_name:
        current_group_name = "控制组" if "控制组" in group_options else list(group_options.keys())[0]
    
    # 找到当前组名在选项列表中的索引
    initial_index = list(group_options.keys()).index(current_group_name)
    
    # 使用固定的key，不再每个页面使用不同key
    selected_group_name = st.selectbox(
        "选择实验分组（开发用）",
        options=list(group_options.keys()),
        index=initial_index,
        key="experiment_group_select"
    )
    
    # 更新会话状态中的实验分组
    if st.session_state.experiment_group != group_options[selected_group_name]:
        st.session_state.experiment_group = group_options[selected_group_name]
        # 如果实验分组改变且已经生成了推荐配置，需要重新生成
        if st.session_state.page >= 5 and st.session_state.recommended_allocation is not None:
            # 获取标准推荐配置
            standard_recommendation = generate_recommendation(st.session_state.risk_score)
            
            # 获取当前实验分组配置
            experiment_group = get_experiment_group(st.session_state.experiment_group)
            
            # 调整推荐配置
            adjusted_recommendation = adjust_recommendation(
                st.session_state.initial_allocation,
                standard_recommendation,
                experiment_group,
                st.session_state.behavior_scores
            )
            
            # 保存推荐配置
            st.session_state.recommended_allocation = adjusted_recommendation
    
    st.caption("注意：此选项仅用于开发测试，实际使用时将随机分配实验组。")

# Recommendation page functions
def recommendation_page():
    st.title("投资推荐方案")
    
    # 检查是否为控制组
    is_control_group = st.session_state.experiment_group == "control"
    
    # 控制组只显示初始配置
    if is_control_group:
        st.subheader("您的资产配置方案")
        
        # 显示初始配置数据表格
        initial_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets]
        }
        initial_allocation_df = pd.DataFrame(initial_allocation_data)
        st.dataframe(initial_allocation_df, use_container_width=True, hide_index=True)
        
        # 显示初始配置的投资指标
        init_return, init_risk = calculate_portfolio_metrics(st.session_state.initial_allocation)
        
        st.write("#### 投资组合指标")
        metrics_data = {
            "指标": ["预期年化收益率", "预期风险（波动率）", "收益/风险比"],
            "数值": [
                f"{init_return * 100:.2f}%", 
                f"{init_risk * 100:.2f}%", 
                f"{(init_return / init_risk) if init_risk > 0 else 0:.2f}"
            ]
        }
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        # 可视化初始配置
        st.write("#### 资产配置可视化")
        
        # 设置中文字体
        set_chinese_font()
        
        # 创建饼图
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 准备数据
        labels = list(st.session_state.initial_allocation.keys())
        sizes = [st.session_state.initial_allocation[asset] * 100 for asset in labels]
        colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            chart_title = get_en_label("当前配置")
            chart_labels = [get_en_label(label) for label in labels]
        else:
            chart_title = "当前配置"
            chart_labels = labels
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=chart_labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # 设置字体大小
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        for text in texts:
            text.set_fontsize(10)
        
        # 添加标题
        ax.set_title(chart_title, fontsize=14, fontweight='bold')
        
        # 确保图像是圆形的
        ax.axis('equal')
        plt.tight_layout()
        
        st.pyplot(fig)
    
    # 非控制组显示初始配置和推荐配置
    else:
        experiment_group = get_experiment_group(st.session_state.experiment_group)
        st.subheader("您的资产配置方案分析")
        
        # 显示实验组描述
        st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin-bottom: 20px;'>{experiment_group['description']}</div>", unsafe_allow_html=True)
        
        # 使用垂直布局替代列布局，确保在非wide模式下也能完整显示
        st.subheader("您的初始配置")
        
        # 显示初始配置数据表格 - 加宽表格
        initial_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets]
        }
        initial_allocation_df = pd.DataFrame(initial_allocation_data)
        
        # 设置固定高度并使用use_container_width让表格自适应宽度
        st.dataframe(
            initial_allocation_df, 
            use_container_width=True, 
            hide_index=True,
            height=36 * (len(assets) + 1) # 根据资产数量动态调整高度
        )
        
        # 显示指标 - 使用水平指标布局
        init_return, init_risk = calculate_portfolio_metrics(st.session_state.initial_allocation)
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.metric("预期年化收益率", f"{init_return * 100:.2f}%")
        with metrics_col2:
            st.metric("预期风险（波动率）", f"{init_risk * 100:.2f}%")
        with metrics_col3:
            st.metric("收益/风险比", f"{(init_return / init_risk) if init_risk > 0 else 0:.2f}")
            
        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)  # 分隔线
        
        st.subheader("推荐配置")
        
        # 计算推荐配置指标
        rec_return, rec_risk = calculate_portfolio_metrics(st.session_state.recommended_allocation)
        
        # 显示推荐配置数据表格 - 加宽表格
        recommended_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.recommended_allocation[asset] * 100 for asset in assets],
            "变化 (%)": [(st.session_state.recommended_allocation[asset] - st.session_state.initial_allocation[asset]) * 100 for asset in assets]
        }
        recommended_allocation_df = pd.DataFrame(recommended_allocation_data)
        
        # 使用Pandas样式功能为变化值添加颜色
        def color_change(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'black'
            return f'color: {color}'
            
        styled_df = recommended_allocation_df.style.format({
            "配置比例 (%)": "{:.1f}",
            "变化 (%)": "{:+.1f}"  # 添加正负号
        }).applymap(color_change, subset=['变化 (%)'])
        
        # 设置固定高度并使用use_container_width让表格自适应宽度
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            height=36 * (len(assets) + 1) # 根据资产数量动态调整高度
        )
            
        # 显示指标 - 使用水平指标布局
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.metric("预期年化收益率", f"{rec_return * 100:.2f}%", f"{(rec_return - init_return) * 100:.2f}%")
        with metrics_col2:
            st.metric("预期风险（波动率）", f"{rec_risk * 100:.2f}%", f"{(rec_risk - init_risk) * 100:.2f}%")
        with metrics_col3:
            st.metric("收益/风险比", f"{(rec_return / rec_risk) if rec_risk > 0 else 0:.2f}", 
                    f"{(rec_return / rec_risk) - (init_return / init_risk) if init_risk > 0 and rec_risk > 0 else 0:.2f}")
        
        # 可视化配置对比
        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)  # 分隔线
        st.subheader("配置对比可视化")
        
        # 提供一个选项切换显示模式
        chart_display_mode = st.radio(
            "选择图表显示模式",
            ["并排显示", "垂直显示"],
            horizontal=True,
            index=1  # 默认垂直显示，更适合非wide模式
        )
        
        # 设置中文字体
        set_chinese_font()
        
        # 根据选择的显示模式调整图表布局
        if chart_display_mode == "并排显示":
            # 并排显示两个饼图
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # 饼图数据准备
            labels = list(st.session_state.initial_allocation.keys())
            init_sizes = [st.session_state.initial_allocation[asset] * 100 for asset in labels]
            rec_sizes = [st.session_state.recommended_allocation[asset] * 100 for asset in labels]
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
            
            # 根据用户设置选择标签语言
            if st.session_state.use_english_labels:
                init_title = get_en_label("当前配置")
                rec_title = get_en_label("推荐配置")
                chart_labels = [get_en_label(label) for label in labels]
            else:
                init_title = "当前配置"
                rec_title = "推荐配置"
                chart_labels = labels
            
            # 初始配置饼图
            wedges1, texts1, autotexts1 = ax1.pie(
                init_sizes, 
                labels=chart_labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # 推荐配置饼图
            wedges2, texts2, autotexts2 = ax2.pie(
                rec_sizes, 
                labels=chart_labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # 设置字体样式
            for autotext in autotexts1 + autotexts2:
                autotext.set_fontsize(9)
                autotext.set_color('black')
                autotext.set_fontweight('bold')
            
            for text in texts1 + texts2:
                text.set_fontsize(10)
            
            # 设置标题
            ax1.set_title(init_title, fontsize=12, fontweight='bold')
            ax2.set_title(rec_title, fontsize=12, fontweight='bold')
            
            # 确保图像是圆形的
            ax1.axis('equal')
            ax2.axis('equal')
            
            plt.tight_layout()
            st.pyplot(fig)
        else:
            # 垂直显示两个饼图（更适合非wide模式）
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
            
            # 饼图数据准备
            labels = list(st.session_state.initial_allocation.keys())
            init_sizes = [st.session_state.initial_allocation[asset] * 100 for asset in labels]
            rec_sizes = [st.session_state.recommended_allocation[asset] * 100 for asset in labels]
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
            
            # 根据用户设置选择标签语言
            if st.session_state.use_english_labels:
                init_title = get_en_label("当前配置")
                rec_title = get_en_label("推荐配置")
                chart_labels = [get_en_label(label) for label in labels]
            else:
                init_title = "当前配置"
                rec_title = "推荐配置"
                chart_labels = labels
            
            # 初始配置饼图
            wedges1, texts1, autotexts1 = ax1.pie(
                init_sizes, 
                labels=chart_labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # 推荐配置饼图
            wedges2, texts2, autotexts2 = ax2.pie(
                rec_sizes, 
                labels=chart_labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # 设置字体样式
            for autotext in autotexts1 + autotexts2:
                autotext.set_fontsize(9)
                autotext.set_color('black')
                autotext.set_fontweight('bold')
            
            for text in texts1 + texts2:
                text.set_fontsize(10)
            
            # 设置标题
            ax1.set_title(init_title, fontsize=12, fontweight='bold')
            ax2.set_title(rec_title, fontsize=12, fontweight='bold')
            
            # 确保图像是圆形的
            ax1.axis('equal')
            ax2.axis('equal')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    # 风险-收益对比图
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)  # 分隔线
    st.subheader("风险-收益分析")
    
    # 创建风险-收益散点图 - 调整大小更适合非wide模式
    fig, ax = plt.subplots(figsize=(8, 6))  # 减小宽度
    
    # 根据用户设置选择标签语言
    if st.session_state.use_english_labels:
        plot_title = get_en_label("风险-收益分布")
        x_label = get_en_label("风险 (波动率) %")
        y_label = get_en_label("预期年化收益率 %")
        legend_initial = get_en_label("初始方案")
        legend_recommended = get_en_label("推荐方案")
    else:
        plot_title = "风险-收益分布"
        x_label = "风险 (波动率) %"
        y_label = "预期年化收益率 %"
        legend_initial = "初始方案"
        legend_recommended = "推荐方案"
    
    # 绘制资产风险-收益散点图 - 减少数据标签重叠
    for asset, info in assets.items():
        asset_label = get_en_label(asset) if st.session_state.use_english_labels else asset
        
        plt.scatter(
            info["risk"] * 100, 
            info["expected_return"] * 100, 
            s=80,  # 略微减小点的大小
            alpha=0.5,
            label=asset_label
        )
        
        # 添加资产标签
        plt.annotate(
            asset_label, 
            (info["risk"] * 100, info["expected_return"] * 100),
            xytext=(5, 5), 
            textcoords='offset points', 
            fontsize=9,
            fontweight='normal'  # 减轻标签视觉重量
        )
    
    # 绘制投资组合风险-收益点
    plt.scatter(
        init_risk * 100, 
        init_return * 100, 
        s=120,  # 减小点的大小
        marker='*', 
        color='blue', 
        label=legend_initial
    )
    plt.scatter(
        rec_risk * 100, 
        rec_return * 100, 
        s=120,  # 减小点的大小
        marker='*', 
        color='green', 
        label=legend_recommended
    )
    
    # 连接初始方案和推荐方案的点
    plt.plot(
        [init_risk * 100, rec_risk * 100],
        [init_return * 100, rec_return * 100],
        'k--',  # 黑色虚线
        alpha=0.5,
        linewidth=1
    )
    
    # 添加投资组合标签，优化位置以减少重叠
    plt.annotate(
        legend_initial, 
        (init_risk * 100, init_return * 100),
        xytext=(10, 10), 
        textcoords='offset points', 
        fontsize=10,
        fontweight='bold',
        color='blue'
    )
    plt.annotate(
        legend_recommended, 
        (rec_risk * 100, rec_return * 100),
        xytext=(10, -15), 
        textcoords='offset points', 
        fontsize=10,
        fontweight='bold',
        color='green'
    )
    
    # 设置图表属性
    plt.title(plot_title, fontsize=14, fontweight='bold')
    plt.xlabel(x_label, fontsize=10)
    plt.ylabel(y_label, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # 将图例放在图表下方，避免与数据点重叠
    plt.legend(
        title=get_en_label("资产类别") if st.session_state.use_english_labels else "资产类别",
        loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,  # 图例显示3列
        fontsize=9
    )
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 添加按钮进入修改配置页面
    if st.button("修改配置方案", use_container_width=True):
        st.session_state.page = 6
        st.rerun()

# Modification page functions
def modification_page():
    st.title("修改您的投资方案")
    
    st.write("""
    在这里，您可以调整最终的投资方案。请根据您的需求修改各资产的配置比例。
    """)
    
    # 显示初始配置和推荐配置（如果不是控制组）
    is_control_group = st.session_state.experiment_group == "control"
    
    # 使用垂直布局替代列布局，确保在非wide模式下也能完整显示
    if is_control_group:
        # 控制组只显示初始配置
        st.subheader("您的初始配置")
        initial_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets]
        }
        init_df = pd.DataFrame(initial_allocation_data)
        
        # 设置固定高度并使用use_container_width让表格自适应宽度
        st.dataframe(
            init_df, 
            use_container_width=True, 
            hide_index=True,
            height=36 * (len(assets) + 1)  # 根据资产数量动态调整高度
        )
    else:
        # 非控制组显示初始和推荐配置
        st.subheader("您的初始配置")
        initial_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets]
        }
        init_df = pd.DataFrame(initial_allocation_data)
        
        # 设置固定高度并使用use_container_width让表格自适应宽度
        st.dataframe(
            init_df, 
            use_container_width=True, 
            hide_index=True,
            height=36 * (len(assets) + 1)  # 根据资产数量动态调整高度
        )
        
        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)  # 分隔线
        
        st.subheader("智能推荐配置")
        recommended_allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.recommended_allocation[asset] * 100 for asset in assets],
            "变化 (%)": [(st.session_state.recommended_allocation[asset] - st.session_state.initial_allocation[asset]) * 100 for asset in assets]
        }
        rec_df = pd.DataFrame(recommended_allocation_data)
        
        # 使用Pandas样式功能为变化值添加颜色
        def color_change(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'black'
            return f'color: {color}'
            
        styled_df = rec_df.style.format({
            "配置比例 (%)": "{:.1f}",
            "变化 (%)": "{:+.1f}"  # 添加正负号
        }).applymap(color_change, subset=['变化 (%)'])
        
        # 设置固定高度并使用use_container_width让表格自适应宽度
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            height=36 * (len(assets) + 1)  # 根据资产数量动态调整高度
        )
    
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)  # 分隔线
    
    # 初始化最终配置输入
    if not st.session_state.final_alloc_values:
        # 如果是首次访问，将最终配置设置为推荐配置的值（或控制组的初始配置）
        if is_control_group:
            st.session_state.final_alloc_values = {asset: st.session_state.initial_allocation[asset] * 100 for asset in assets}
        else:
            st.session_state.final_alloc_values = {asset: st.session_state.recommended_allocation[asset] * 100 for asset in assets}
    
    # 使用常规输入控件代替表单，以支持实时更新
    st.subheader("请输入您的最终配置")
    st.write("请直接输入各资产配置比例：")
    
    # 根据assets的数量动态决定每行显示几个资产
    # 窄屏幕（非wide模式）下每行显示2个，宽屏显示3个
    cols_per_row = 2
    rows_needed = (len(assets) + cols_per_row - 1) // cols_per_row  # 向上取整计算所需行数
    
    # 创建所有行
    all_rows = []
    for i in range(rows_needed):
        all_rows.append(st.columns(cols_per_row))
    
    # 创建用于处理输入变化的回调函数
    def update_final_allocation(asset):
        # 回调函数不需要实际操作，因为输入值已自动保存到session_state
        pass
    
    # 确保所有资产在session_state中都有初始值
    for asset in assets:
        if asset not in st.session_state.final_alloc_values:
            st.session_state.final_alloc_values[asset] = 0.0
    
    # 使用行和列的组合显示输入控件
    for i, asset in enumerate(assets):
        row_idx = i // cols_per_row
        col_idx = i % cols_per_row
        
        with all_rows[row_idx][col_idx]:
            # 添加卡片式样式，使得输入字段更美观
            st.markdown(f"""<div style='margin-bottom: 5px; font-weight: bold; color: #333;'>{asset}</div>""", unsafe_allow_html=True)
            st.number_input(
                "配置比例 (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.final_alloc_values.get(asset, 0.0)),
                step=1.0,
                key=f"final_allocation_{asset}",
                on_change=update_final_allocation,
                args=(asset,),
                label_visibility="collapsed"
            )
            # 更新session_state中的值
            st.session_state.final_alloc_values[asset] = st.session_state[f"final_allocation_{asset}"]
    
    # 计算总和 - 这里会在每次界面刷新时重新计算，实现"实时"更新
    total = sum(st.session_state.final_alloc_values.values())
    
    # 使用更醒目的样式显示总和状态
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # 添加间距
    if abs(total - 100.0) < 0.01:
        st.markdown(f"""
        <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 15px;'>
            总配置比例: {total:.1f}% ✓
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 15px;'>
            总配置比例: {total:.1f}% (应当等于100%)
        </div>
        """, unsafe_allow_html=True)
    
    # 计算实时指标
    if total > 0:
        temp_allocation = {asset: st.session_state.final_alloc_values[asset] / 100.0 for asset in assets}
        temp_return, temp_risk = calculate_portfolio_metrics(temp_allocation)
        
        # 显示实时指标
        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)  # 分隔线
        st.write("#### 当前方案指标预览")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预期年化收益率", f"{temp_return * 100:.2f}%")
        with col2:
            st.metric("预期风险（波动率）", f"{temp_risk * 100:.2f}%")
        with col3:
            st.metric("收益/风险比", f"{(temp_return / temp_risk) if temp_risk > 0 else 0:.2f}")
    
    # 提交按钮，使用更吸引人的样式
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # 添加间距
    if st.button("提交最终方案", use_container_width=True, type="primary"):
        # 检查总和是否接近100%
        if abs(total - 100.0) > 0.01:
            st.error(f"您的配置总计为{total:.1f}%，请确保总计等于100%")
        else:
            # 转换为小数格式用于内部计算
            final_alloc = {asset: st.session_state.final_alloc_values[asset] / 100.0 for asset in assets}
            st.session_state.final_allocation = final_alloc
            # 进入模拟页面
            st.session_state.page = 7
            st.rerun()

if __name__ == "__main__":
    main() 