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
    '最大回撤': 'Max Drawdown'
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
    st.session_state.behavior_answers = {
        "风险厌恶": None,
        "损失厌恶": None,
        "心理账户": None
    }
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
    
    # Create a more visual and modern asset display
    cols = st.columns(len(assets))
    for i, (asset, info) in enumerate(assets.items()):
        with cols[i]:
            st.markdown(f"""
            <div style='padding: 15px; border-radius: 5px; border: 1px solid #ddd; height: 100%;'>
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
    
    # Get behavior questions from configuration
    behavior_questions = get_behavior_questions()
    
    with st.form(key="behavior_form"):
        # Create questions for each behavior dimension
        for dimension, question_data in behavior_questions.items():
            st.subheader(question_data["question"])
            options = list(question_data["options"].keys())
            selected_option = st.radio(
                f"问题_{dimension}",
                options,
                label_visibility="collapsed"
            )
            # Store the value (high/mid/low) for the selected option
            st.session_state.behavior_answers[dimension] = question_data["options"][selected_option]
        
        submitted = st.form_submit_button("提交问卷")
        
        if submitted:
            # Map medium value to high or low for simplicity in personality mapping
            for dim, value in st.session_state.behavior_answers.items():
                if value == "中":
                    # For simplicity, treat "中" as "低" (could also randomly assign or use other logic)
                    st.session_state.behavior_answers[dim] = "低"
            
            # Get the financial personality based on answers
            risk_aversion = st.session_state.behavior_answers["风险厌恶"]
            loss_aversion = st.session_state.behavior_answers["损失厌恶"]
            mental_accounting = st.session_state.behavior_answers["心理账户"]
            
            # Get the personality from configuration
            personality = get_financial_personality(risk_aversion, loss_aversion, mental_accounting)
            st.session_state.financial_personality = personality
            
            # Move to financial personality page
            st.session_state.page = 4
            st.rerun()

# Financial personality page
def financial_personality_page():
    st.title("您的金融性格分析")
    
    # Display risk profile information
    risk_category = get_risk_category(st.session_state.risk_score)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("您的风险承受能力")
        st.write(f"根据您的问卷回答，您的风险承受能力评分为：**{st.session_state.risk_score:.1f}/100**")
        st.write(f"风险偏好类型：**{risk_category}**")
    
    with col2:
        st.subheader("您的金融行为特征")
        risk_aversion = st.session_state.behavior_answers["风险厌恶"]
        loss_aversion = st.session_state.behavior_answers["损失厌恶"]
        mental_accounting = st.session_state.behavior_answers["心理账户"]
        
        st.write(f"风险厌恶程度：**{risk_aversion}**")
        st.write(f"损失厌恶程度：**{loss_aversion}**")
        st.write(f"心理账户倾向：**{mental_accounting}**")
    
    # Display financial personality
    personality = st.session_state.financial_personality
    
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 10px; background-color: #f0f8ff; margin: 20px 0;'>
        <h2 style='color: #1E88E5;'>{personality["name"]}</h2>
        <p style='font-size: 16px;'>{personality["description"]}</p>
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
            st.session_state.behavior_answers
        )
        
        # 保存推荐配置
        st.session_state.recommended_allocation = adjusted_recommendation
        
        st.session_state.page = 5
        st.rerun()

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
                st.session_state.behavior_answers
            )
            
            # 保存推荐配置
            st.session_state.recommended_allocation = adjusted_recommendation
    
    st.caption("注意：此选项仅用于开发测试，实际使用时将随机分配实验组。")

# Updated recommendation page (now at index 5)
def recommendation_page():
    st.title("智能投顾推荐方案")
    
    # 获取当前实验分组配置
    experiment_group = get_experiment_group(st.session_state.experiment_group)
    
    # 显示实验分组文案
    st.markdown(f"""
    <div style='padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>
        <p style='font-size: 16px;'>{experiment_group["description"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 计算初始配置的指标
    initial_return, initial_risk = calculate_portfolio_metrics(st.session_state.initial_allocation)
    
    # 控制组和实验组显示不同内容
    if st.session_state.experiment_group == "control":
        # 控制组只显示初始配置
        st.subheader("您的资产配置方案")
        
        # 创建配置表格
        allocation_data = {
            "资产": [asset for asset in assets],
            "配置比例 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets]
        }
        allocation_df = pd.DataFrame(allocation_data)
        st.dataframe(allocation_df, use_container_width=True, hide_index=True)
        
        # 投资组合指标
        st.subheader("投资组合指标")
        metrics_data = {
            "指标": ["预期年化收益率", "预期风险（波动率）", "收益/风险比"],
            "当前配置": [f"{initial_return*100:.2f}%", f"{initial_risk*100:.2f}%", f"{(initial_return/initial_risk):.2f}"]
        }
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        # 配置可视化 - 饼图
        st.subheader("配置可视化")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        set_chinese_font()
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            title = get_en_label("当前配置")
            assets_labels = {asset: get_en_label(asset) for asset in assets}
            legend_title = get_en_label("资产类别")
        else:
            title = "当前配置"
            assets_labels = {asset: asset for asset in assets}
            legend_title = "资产类别"
        
        # 配置环形图
        wedges, texts, autotexts = ax.pie(
            [st.session_state.initial_allocation[asset] * 100 for asset in assets],
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.5)
        )
        ax.set_title(title)
        
        # 添加图例
        ax.legend(
            [assets_labels[asset] for asset in assets],
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # 设置字体颜色
        plt.setp(autotexts, size=10, weight="bold", color="white")
        
        # 调整布局和间距
        plt.tight_layout()
        st.pyplot(fig)
        
    else:
        # 非控制组显示对比分析
        # 计算推荐配置的指标
        rec_return, rec_risk = calculate_portfolio_metrics(st.session_state.recommended_allocation)
        
        # 创建调整前后对比表格
        asset_comparison = []
        for asset in assets:
            initial_pct = st.session_state.initial_allocation[asset] * 100
            recommended_pct = st.session_state.recommended_allocation[asset] * 100
            change = recommended_pct - initial_pct
            change_direction = "↑" if change > 0 else "↓" if change < 0 else "→"
            
            asset_comparison.append({
                "类型": asset,
                "当前": f"{initial_pct:.1f}%",
                "调整后": f"{recommended_pct:.1f}%",
                "变化": f"{change_direction} {abs(change):.1f}%"
            })
        
        comparison_df = pd.DataFrame(asset_comparison)
        
        # 垂直堆叠布局 - 资产配置表格
        st.subheader("资产配置对比")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # 投资组合指标对比
        st.subheader("投资组合指标对比")
        metrics_comparison = pd.DataFrame({
            "指标": ["预期年化收益率", "预期风险（波动率）", "收益/风险比"],
            "当前配置": [f"{initial_return*100:.2f}%", f"{initial_risk*100:.2f}%", f"{(initial_return/initial_risk):.2f}"],
            "推荐配置": [f"{rec_return*100:.2f}%", f"{rec_risk*100:.2f}%", f"{(rec_return/rec_risk):.2f}"],
        })
        st.dataframe(metrics_comparison, use_container_width=True, hide_index=True)
        
        # 配置可视化 - 环形图
        st.subheader("配置可视化对比")
        
        # 创建两个环形图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        set_chinese_font()
        
        # 根据用户设置选择标签语言
        if st.session_state.use_english_labels:
            title1 = get_en_label("当前配置")
            title2 = get_en_label("推荐配置")
            assets_labels = {asset: get_en_label(asset) for asset in assets}
            legend_title = get_en_label("资产类别")
        else:
            title1 = "当前配置"
            title2 = "推荐配置"
            assets_labels = {asset: asset for asset in assets}
            legend_title = "资产类别"
        
        # 当前配置环形图
        wedges1, texts1, autotexts1 = ax1.pie(
            [st.session_state.initial_allocation[asset] * 100 for asset in assets],
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.5)
        )
        ax1.set_title(title1)
        
        # 添加图例
        ax1.legend(
            [assets_labels[asset] for asset in assets],
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # 推荐配置环形图
        wedges2, texts2, autotexts2 = ax2.pie(
            [st.session_state.recommended_allocation[asset] * 100 for asset in assets],
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.5)
        )
        ax2.set_title(title2)
        
        # 添加图例
        ax2.legend(
            [assets_labels[asset] for asset in assets],
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # 设置字体颜色
        plt.setp(autotexts1, size=10, weight="bold", color="white")
        plt.setp(autotexts2, size=10, weight="bold", color="white")
        
        # 调整布局和间距
        plt.tight_layout()
        st.pyplot(fig)
        
        # 风险收益散点图 - 使用expander使其可折叠
        with st.expander("点击查看风险收益分布图", expanded=False):
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 根据用户设置选择标签语言
            if st.session_state.use_english_labels:
                plot_title = get_en_label("风险-收益分布")
                x_label = get_en_label("风险 (波动率) %")
                y_label = get_en_label("预期年化收益率 %")
                
                # 创建图例标签映射
                legend_labels = {}
                for asset in assets:
                    legend_labels[asset] = get_en_label(asset)
                legend_labels['当前配置'] = get_en_label('初始方案')
                legend_labels['推荐配置'] = get_en_label('推荐方案')
            else:
                plot_title = "风险-收益分布"
                x_label = "风险 (波动率) %"
                y_label = "预期年化收益率 %"
                legend_labels = {asset: asset for asset in assets}
                legend_labels.update({'当前配置': '当前配置', '推荐配置': '推荐配置'})
            
            # 绘制所有资产点
            asset_markers = {'股票': 'o', '债券': 's', '货币市场': '^', '房地产': 'D', '大宗商品': 'P'}
            asset_colors = {'股票': 'red', '债券': 'blue', '货币市场': 'green', '房地产': 'purple', '大宗商品': 'orange'}
            
            for asset, info in assets.items():
                plt.scatter(
                    info["risk"]*100, 
                    info["expected_return"]*100, 
                    s=100, 
                    alpha=0.7, 
                    label=legend_labels.get(asset, asset),
                    marker=asset_markers.get(asset, 'o'),
                    color=asset_colors.get(asset, 'gray')
                )
            
            # 绘制两个投资组合点
            plt.scatter(initial_risk*100, initial_return*100, color='blue', s=200, marker='*', 
                        label=legend_labels.get('当前配置', '当前配置'))
            plt.scatter(rec_risk*100, rec_return*100, color='green', s=200, marker='*', 
                        label=legend_labels.get('推荐配置', '推荐配置'))
            
            # 连接两点
            plt.plot([initial_risk*100, rec_risk*100], [initial_return*100, rec_return*100], 
                    'k--', alpha=0.5, linewidth=1)
            
            plt.title(plot_title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend(loc='best')
            plt.tight_layout()
            st.pyplot(fig)
    
    # 修改配置按钮
    if st.button("修改配置方案", use_container_width=True):
        st.session_state.page = 6  # Updated index for modification page
        st.rerun()

# Modification page
def modification_page():
    st.title("修改您的配置方案")
    
    st.write("""
    根据智能投顾的推荐，您可以调整您的资产配置方案。
    请在下方修改各个资产的百分比，并确认以进入收益模拟环节。
    """)
    
    # 初始化最终配置值为0
    if not st.session_state.final_alloc_values:
        st.session_state.final_alloc_values = {asset: 0.0 for asset in assets}
    
    # 显示对比表格
    comparison_data = {
        "资产": [asset for asset in assets],
        "初始方案 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets],
        "推荐方案 (%)": [st.session_state.recommended_allocation[asset] * 100 for asset in assets]
    }
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # 修改配置输入区 - 使用常规输入控件代替表单，以支持实时更新
    st.write("请直接输入各资产配置比例：")
    cols = st.columns(5)
    
    # 创建用于处理输入变化的回调函数
    def update_final_allocation(asset):
        # 回调函数不需要实际操作，因为输入值已自动保存到session_state
        pass
    
    # 确保所有资产在session_state中都有初始值
    for asset in assets:
        if asset not in st.session_state.final_alloc_values:
            st.session_state.final_alloc_values[asset] = 0.0
    
    for i, asset in enumerate(assets):
        recommended_value = st.session_state.recommended_allocation[asset] * 100
        initial_value = st.session_state.initial_allocation[asset] * 100
        
        with cols[i % 5]:
            st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.final_alloc_values[asset]),
                step=1.0,
                key=f"final_allocation_{asset}",
                on_change=update_final_allocation,
                args=(asset,),
                help=f"初始: {initial_value:.1f}%, 推荐: {recommended_value:.1f}%"
            )
            # 更新session_state中的值
            st.session_state.final_alloc_values[asset] = st.session_state[f"final_allocation_{asset}"]
    
    # 计算总和 - 这里会在每次界面刷新时重新计算，实现"实时"更新
    total = sum(st.session_state.final_alloc_values.values())
    
    # 显示总和状态
    if abs(total - 100.0) < 0.01:
        st.success(f"总配置比例: **{total:.1f}%** ✓")
    else:
        st.warning(f"总配置比例: **{total:.1f}%** (应当等于100%)")
    
    # 提交按钮
    if st.button("确认并进入收益模拟", use_container_width=True):
        # 检查总和是否接近100%
        if abs(total - 100.0) > 0.01:
            st.error(f"您的配置总计为{total:.1f}%，请确保总计等于100%")
        else:
            # 转换为小数形式
            final_alloc = {asset: st.session_state.final_alloc_values[asset] / 100.0 for asset in assets}
            st.session_state.final_allocation = final_alloc
            st.session_state.page = 7  # 进入模拟页面
            st.rerun()

# Helper function for initial allocation inputs
def initial_allocation_inputs():
    """处理初始资产配置输入"""
    # 初始化session状态
    if not st.session_state.initial_alloc_values:
        st.session_state.initial_alloc_values = {asset: 0.0 for asset in assets}
    
    # 使用常规输入控件代替表单，以支持实时更新
    st.write("请直接输入各资产配置比例：")
    cols = st.columns(5)
    
    # 创建用于处理输入变化的回调函数
    def update_allocation(asset):
        # 回调函数不需要实际操作，因为输入值已自动保存到session_state
        pass
    
    # 确保所有资产在session_state中都有初始值
    for asset in assets:
        if asset not in st.session_state.initial_alloc_values:
            st.session_state.initial_alloc_values[asset] = 0.0
    
    # 使用列布局显示输入控件
    for i, asset in enumerate(assets):
        with cols[i % 5]:
            st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.initial_alloc_values.get(asset, 0.0)),
                step=1.0,
                key=f"initial_allocation_{asset}",
                on_change=update_allocation,
                args=(asset,)
            )
            # 更新session_state中的值
            st.session_state.initial_alloc_values[asset] = st.session_state[f"initial_allocation_{asset}"]
    
    # 计算总和 - 这里会在每次界面刷新时重新计算，实现"实时"更新
    total = sum(st.session_state.initial_alloc_values.values())
    
    # 显示总和状态
    if abs(total - 100.0) < 0.01:
        st.success(f"总配置比例: **{total:.1f}%** ✓")
    else:
        st.warning(f"总配置比例: **{total:.1f}%** (应当等于100%)")
    
    # 提交按钮
    if st.button("提交配置方案", use_container_width=True):
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
    plt.legend(fontsize=10, loc='upper left')
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

if __name__ == "__main__":
    main() 