import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from config.loader import (
    get_assets, 
    get_asset_names_en, 
    get_asset_descriptions_en, 
    get_risk_recommendation,
    get_risk_mapping,
    get_risk_category
)

# Set page config
st.set_page_config(
    page_title="智能投顾实验平台",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define session state variables if not present
if 'page' not in st.session_state:
    st.session_state.page = 0  # 0: welcome, 1: questionnaire, 2: initial allocation, 3: recommendations, 4: modification, 5: simulation
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
    # Use the configuration-based recommendation function
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
    st.title("欢迎使用智能投顾实验平台")
    st.write("""
    这个平台将帮助您了解自己的投资偏好，并提供个性化的投资建议。
    
    实验流程：
    1. 完成关于您个人情况和风险承受能力的问卷
    2. 查看不同资产的风险收益特征，并提供您的初始配置方案
    3. 查看系统推荐的资产配置方案
    4. 根据推荐修改您的配置
    5. 比较不同配置方案的模拟收益
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("开始实验", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    
    # Add a language selector in the sidebar
    with st.sidebar:
        st.caption("注意：图表将以英文显示以获得更好的兼容性")

# Questionnaire page
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
            st.session_state.page = 2
            st.rerun()

# Initial allocation page
def initial_allocation_page():
    st.title("资产配置方案")
    
    # Risk profile summary
    risk_category = get_risk_category(st.session_state.risk_score)
    
    st.write(f"根据您的问卷回答，您的风险承受能力评分为：**{st.session_state.risk_score:.1f}/100**")
    st.write(f"风险偏好类型：**{risk_category}**")
    
    # Display asset information
    st.subheader("资产风险收益特征")
    
    # Create dataframe with English translations for visualization
    asset_df = pd.DataFrame({
        "Asset Class": [asset_names_en[asset] for asset in assets.keys()],
        "Expected Annual Return (%)": [assets[asset]["expected_return"] * 100 for asset in assets],
        "Risk (Volatility) (%)": [assets[asset]["risk"] * 100 for asset in assets],
        "Return/Risk Ratio": [assets[asset]["expected_return"] / assets[asset]["risk"] for asset in assets],
        "Description": [asset_descriptions_en[asset] for asset in assets]
    })
    
    # Create more compact layout
    col1, col2 = st.columns([3, 3])
    
    with col1:
        # Display formatted data table with Chinese headers but English asset names
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
    
    with col2:
        # Create more compact chart with English labels
        fig, ax = plt.subplots(figsize=(6, 5))
        scatter = sns.scatterplot(
            x="Risk (Volatility) (%)", 
            y="Expected Annual Return (%)", 
            data=asset_df, 
            s=150, 
            ax=ax
        )
        
        # Add labels in English
        for i, asset in enumerate(assets):
            plt.annotate(
                asset_names_en[asset], 
                (assets[asset]["risk"] * 100, assets[asset]["expected_return"] * 100),
                xytext=(5, 5), 
                textcoords='offset points', 
                fontsize=10
            )
        
        plt.title("Asset Risk-Return Distribution", fontsize=12)
        plt.xlabel("Risk (Volatility) %", fontsize=10)
        plt.ylabel("Expected Annual Return %", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Display asset descriptions (using expander to save space)
    with st.expander("点击查看详细资产描述", expanded=False):
        for asset, info in assets.items():
            st.write(f"**{asset}**: {info['description']}")
    
    # User allocation input
    st.subheader("输入您的初始资产配置方案")
    st.write("请为每个资产类别分配投资百分比（总计必须等于100%）")
    
    # Initialize session state for initial allocations if not present
    if 'initial_alloc_values' not in st.session_state:
        st.session_state.initial_alloc_values = {asset: 0.0 for asset in assets}
    
    # Function to update total when any input changes
    def update_total():
        st.session_state.initial_total = sum(st.session_state.initial_alloc_values.values())
    
    # Function to update allocation value when input changes
    def update_allocation(asset):
        input_key = f"initial_input_{asset}"
        if input_key in st.session_state:
            st.session_state.initial_alloc_values[asset] = st.session_state[input_key]
            update_total()
    
    # Display direct inputs in a more compact layout
    st.write("请直接输入各资产配置比例：")
    cols = st.columns(5)
    
    for i, asset in enumerate(assets):
        with cols[i % 5]:
            # Initialize input key for this asset
            input_key = f"initial_input_{asset}"
            
            if input_key not in st.session_state:
                st.session_state[input_key] = st.session_state.initial_alloc_values.get(asset, 0.0)
                
            # Direct number input
            st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state[input_key],
                step=1.0,
                key=input_key,
                on_change=lambda asset=asset: update_allocation(asset)
            )
            
            # Update the allocation value from input
            st.session_state.initial_alloc_values[asset] = st.session_state[input_key]
    
    # Calculate and display total
    total = sum(st.session_state.initial_alloc_values.values())
    
    # Display total with color based on whether it equals 100%
    if abs(total - 100.0) < 0.01:
        st.success(f"总配置比例: **{total:.1f}%** ✓")
    else:
        st.warning(f"总配置比例: **{total:.1f}%** (应当等于100%)")
    
    # Submit button (outside of form)
    if st.button("提交配置方案"):
        # Check if total is close to 100%
        if abs(total - 100.0) > 0.01:
            st.error(f"您的配置总计为{total:.1f}%，请确保总计等于100%")
        else:
            # Convert to decimal format for internal calculations
            initial_alloc = {asset: st.session_state.initial_alloc_values[asset] / 100.0 for asset in assets}
            st.session_state.initial_allocation = initial_alloc
            st.session_state.recommended_allocation = generate_recommendation(st.session_state.risk_score)
            st.session_state.page = 3
            st.rerun()

# Recommendation page
def recommendation_page():
    st.title("智能投顾推荐方案")
    
    # Visualize comparison between initial and recommended allocations
    st.subheader("您的初始方案 vs 智能投顾推荐")
    
    # Calculate metrics for both allocations
    initial_return, initial_risk = calculate_portfolio_metrics(st.session_state.initial_allocation)
    rec_return, rec_risk = calculate_portfolio_metrics(st.session_state.recommended_allocation)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 您的初始方案")
        initial_df = pd.DataFrame({
            "资产": [asset for asset in st.session_state.initial_allocation.keys()],
            "配置比例": [f"{v*100:.1f}%" for v in st.session_state.initial_allocation.values()]
        })
        st.dataframe(initial_df, use_container_width=True)
        st.metric("预期年化收益率", f"{initial_return*100:.2f}%")
        st.metric("预期风险（波动率）", f"{initial_risk*100:.2f}%")
        st.metric("收益/风险比", f"{(initial_return/initial_risk):.2f}")
        
        # Pie chart for initial allocation with English labels
        fig, ax = plt.subplots(figsize=(6, 6))
        plt.pie(
            list(st.session_state.initial_allocation.values()), 
            labels=[asset_names_en[asset] for asset in st.session_state.initial_allocation.keys()],
            autopct='%1.1f%%',
            startangle=90,
            shadow=False
        )
        plt.title("Your Initial Asset Allocation")
        st.pyplot(fig)
    
    with col2:
        st.write("### 智能投顾推荐方案")
        rec_df = pd.DataFrame({
            "资产": [asset for asset in st.session_state.recommended_allocation.keys()],
            "配置比例": [f"{v*100:.1f}%" for v in st.session_state.recommended_allocation.values()]
        })
        st.dataframe(rec_df, use_container_width=True)
        st.metric("预期年化收益率", f"{rec_return*100:.2f}%")
        st.metric("预期风险（波动率）", f"{rec_risk*100:.2f}%")
        st.metric("收益/风险比", f"{(rec_return/rec_risk):.2f}")
        
        # Pie chart for recommended allocation with English labels
        fig, ax = plt.subplots(figsize=(6, 6))
        plt.pie(
            list(st.session_state.recommended_allocation.values()), 
            labels=[asset_names_en[asset] for asset in st.session_state.recommended_allocation.keys()],
            autopct='%1.1f%%',
            startangle=90,
            shadow=False
        )
        plt.title("Robo-Advisor Recommended Allocation")
        st.pyplot(fig)
    
    # Risk-return comparison plot
    st.subheader("风险收益对比")
    
    # Create a more compact visual for risk-return comparison
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        # Plot the two portfolios
        plt.scatter(initial_risk*100, initial_return*100, color='blue', s=150, label='Your Initial Plan')
        plt.scatter(rec_risk*100, rec_return*100, color='green', s=150, label='Robo-Advisor Recommendation')
        
        # Add individual assets
        for asset, info in assets.items():
            plt.scatter(info["risk"]*100, info["expected_return"]*100, s=80, alpha=0.6)
            plt.annotate(asset_names_en[asset], (info["risk"]*100, info["expected_return"]*100), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.title("Portfolio Risk-Return Comparison")
        plt.xlabel("Risk (Volatility) %")
        plt.ylabel("Expected Annual Return %")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Add a summary table for quick comparison
        comparison_df = pd.DataFrame({
            "指标": ["收益率 (%)", "风险 (%)", "收益/风险"],
            "初始方案": [f"{initial_return*100:.2f}", f"{initial_risk*100:.2f}", f"{(initial_return/initial_risk):.2f}"],
            "推荐方案": [f"{rec_return*100:.2f}", f"{rec_risk*100:.2f}", f"{(rec_return/rec_risk):.2f}"],
        })
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        if st.button("修改配置方案", use_container_width=True):
            st.session_state.page = 4
            st.rerun()

# Modification page
def modification_page():
    st.title("修改您的配置方案")
    
    st.write("""
    根据智能投顾的推荐，您可以调整您的资产配置方案。
    请在下方修改各个资产的百分比，并确认以进入收益模拟环节。
    """)
    
    # Initialize session state for final allocations if not present
    if 'final_alloc_values' not in st.session_state:
        st.session_state.final_alloc_values = {
            asset: 0.0 for asset in assets
        }
    
    # Function to update total when any input changes
    def update_final_total():
        st.session_state.final_total = sum(st.session_state.final_alloc_values.values())
    
    # Function to update allocation value when input changes
    def update_final_allocation(asset):
        input_key = f"final_input_{asset}"
        if input_key in st.session_state:
            st.session_state.final_alloc_values[asset] = st.session_state[input_key]
            update_final_total()
    
    # Show both initial and recommended values in a compact table first
    comparison_data = {
        "资产": [asset for asset in assets],
        "初始方案 (%)": [st.session_state.initial_allocation[asset] * 100 for asset in assets],
        "推荐方案 (%)": [st.session_state.recommended_allocation[asset] * 100 for asset in assets]
    }
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Now show direct inputs in a more compact layout
    st.write("请直接输入各资产配置比例：")
    cols = st.columns(5)
    
    for i, asset in enumerate(assets):
        recommended_value = st.session_state.recommended_allocation[asset] * 100
        initial_value = st.session_state.initial_allocation[asset] * 100
        
        with cols[i % 5]:
            # Initialize input key for this asset
            input_key = f"final_input_{asset}"
            
            if input_key not in st.session_state:
                st.session_state[input_key] = st.session_state.final_alloc_values.get(asset, 0.0)
                
            # Direct number input
            st.number_input(
                f"{asset} (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state[input_key],
                step=1.0,
                key=input_key,
                help=f"初始: {initial_value:.1f}%, 推荐: {recommended_value:.1f}%",
                on_change=lambda asset=asset: update_final_allocation(asset)
            )
            
            # Update the allocation value from input
            st.session_state.final_alloc_values[asset] = st.session_state[input_key]
    
    # Calculate and display total
    total = sum(st.session_state.final_alloc_values.values())
    
    # Display total with color based on whether it equals 100%
    if abs(total - 100.0) < 0.01:
        st.success(f"总配置比例: **{total:.1f}%** ✓")
    else:
        st.warning(f"总配置比例: **{total:.1f}%** (应当等于100%)")
    
    # Submit button (outside of form)
    if st.button("确认并进入收益模拟"):
        # Check if total is close to 100%
        if abs(total - 100.0) > 0.01:
            st.error(f"您的配置总计为{total:.1f}%，请确保总计等于100%")
        else:
            # Convert to decimal format for internal calculations
            final_alloc = {asset: st.session_state.final_alloc_values[asset] / 100.0 for asset in assets}
            st.session_state.final_allocation = final_alloc
            st.session_state.page = 5
            st.rerun()

# Simulation page
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
    
    # Run simulations
    initial_simulation = simulate_returns(
        st.session_state.initial_allocation, 
        days=simulation_period, 
        initial_investment=initial_investment
    )
    
    recommended_simulation = simulate_returns(
        st.session_state.recommended_allocation, 
        days=simulation_period, 
        initial_investment=initial_investment
    )
    
    final_simulation = simulate_returns(
        st.session_state.final_allocation, 
        days=simulation_period, 
        initial_investment=initial_investment
    )
    
    # Calculate key metrics
    initial_return = (initial_simulation[-1] - initial_investment) / initial_investment * 100
    recommended_return = (recommended_simulation[-1] - initial_investment) / initial_investment * 100
    final_return = (final_simulation[-1] - initial_investment) / initial_investment * 100
    
    # Create dataframe for simulation results
    days = list(range(simulation_period + 1))
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in days]
    
    sim_df = pd.DataFrame({
        'Date': dates,
        'Initial Plan': initial_simulation,
        'Recommended Plan': recommended_simulation,
        'Final Plan': final_simulation
    })
    
    # Display portfolio summary and comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("初始方案最终价值", f"{initial_simulation[-1]:,.2f} 元", 
                 f"{initial_return:.2f}%")
        
    with col2:
        st.metric("推荐方案最终价值", f"{recommended_simulation[-1]:,.2f} 元", 
                 f"{recommended_return:.2f}%")
        
    with col3:
        st.metric("最终方案最终价值", f"{final_simulation[-1]:,.2f} 元", 
                 f"{final_return:.2f}%")
    
    # Plot simulation results with improved layouts
    st.subheader("投资组合价值变化")
    
    tabs = st.tabs(["价值图表", "日收益率", "绩效指标"])
    
    with tabs[0]:
        # Create a more efficient layout for main chart
        fig, ax = plt.subplots(figsize=(10, 6))
        # Sample data to avoid overcrowding (roughly monthly)
        sample_freq = max(1, simulation_period // 30)
        plt.plot(dates[::sample_freq], initial_simulation[::sample_freq], label='Initial Plan', linewidth=2)
        plt.plot(dates[::sample_freq], recommended_simulation[::sample_freq], label='Recommended Plan', linewidth=2)
        plt.plot(dates[::sample_freq], final_simulation[::sample_freq], label='Final Plan', linewidth=2)
        
        plt.title("Simulated Returns of Different Allocation Plans")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value (CNY)")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    with tabs[1]:
        # Calculate daily returns
        daily_returns_initial = np.diff(initial_simulation) / initial_simulation[:-1]
        daily_returns_recommended = np.diff(recommended_simulation) / recommended_simulation[:-1]
        daily_returns_final = np.diff(final_simulation) / final_simulation[:-1]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.hist(daily_returns_initial, bins=50, alpha=0.3, label='Initial Plan')
        plt.hist(daily_returns_recommended, bins=50, alpha=0.3, label='Recommended Plan')
        plt.hist(daily_returns_final, bins=50, alpha=0.3, label='Final Plan')
        
        plt.title("Daily Returns Distribution Comparison")
        plt.xlabel("Daily Return")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
    
    with tabs[2]:
        # Show detailed metrics with improved formatting
        metrics_df = pd.DataFrame({
            '指标': ['年化收益率 (%)', '波动率 (%)', '夏普比率', '最大回撤 (%)', '收益/风险比'],
            '初始方案': [
                f"{initial_return / (simulation_period/365):.2f}",
                f"{np.std(daily_returns_initial) * np.sqrt(252) * 100:.2f}",
                f"{(initial_return / (simulation_period/365)) / (np.std(daily_returns_initial) * np.sqrt(252) * 100):.2f}",
                f"{(np.max(initial_simulation) - np.min(initial_simulation[np.argmax(initial_simulation):]))/ np.max(initial_simulation) * 100:.2f}",
                f"{initial_return / (np.std(daily_returns_initial) * np.sqrt(252) * 100):.2f}"
            ],
            '推荐方案': [
                f"{recommended_return / (simulation_period/365):.2f}",
                f"{np.std(daily_returns_recommended) * np.sqrt(252) * 100:.2f}",
                f"{(recommended_return / (simulation_period/365)) / (np.std(daily_returns_recommended) * np.sqrt(252) * 100):.2f}",
                f"{(np.max(recommended_simulation) - np.min(recommended_simulation[np.argmax(recommended_simulation):]))/ np.max(recommended_simulation) * 100:.2f}",
                f"{recommended_return / (np.std(daily_returns_recommended) * np.sqrt(252) * 100):.2f}"
            ],
            '最终方案': [
                f"{final_return / (simulation_period/365):.2f}",
                f"{np.std(daily_returns_final) * np.sqrt(252) * 100:.2f}",
                f"{(final_return / (simulation_period/365)) / (np.std(daily_returns_final) * np.sqrt(252) * 100):.2f}",
                f"{(np.max(final_simulation) - np.min(final_simulation[np.argmax(final_simulation):]))/ np.max(final_simulation) * 100:.2f}",
                f"{final_return / (np.std(daily_returns_final) * np.sqrt(252) * 100):.2f}"
            ]
        })
        
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Restart experiment button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("重新开始实验", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 0
            st.rerun()

# Main app logic
def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("智能投顾实验平台")
        st.write("---")
        
        # Show progress in sidebar
        if st.session_state.page > 0:
            st.write("### 实验进度")
            progress_labels = ["开始", "问卷", "初始配置", "推荐方案", "修改方案", "收益模拟"]
            progress_value = st.session_state.page / (len(progress_labels) - 1)
            st.progress(progress_value)
            st.write(f"当前阶段: {progress_labels[st.session_state.page]}")
            
            # Navigation buttons
            if st.session_state.page > 1:
                if st.button("← 返回", use_container_width=True):
                    st.session_state.page -= 1
                    st.rerun()
    
    # Display appropriate page based on session state
    if st.session_state.page == 0:
        welcome_page()
    elif st.session_state.page == 1:
        questionnaire_page()
    elif st.session_state.page == 2:
        initial_allocation_page()
    elif st.session_state.page == 3:
        recommendation_page()
    elif st.session_state.page == 4:
        modification_page()
    elif st.session_state.page == 5:
        simulation_page()

if __name__ == "__main__":
    main() 