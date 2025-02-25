import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

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

# Mock asset data
assets = {
    "股票": {"expected_return": 0.08, "risk": 0.20, "description": "高风险高回报，具有较高的长期增长潜力"},
    "债券": {"expected_return": 0.04, "risk": 0.05, "description": "中等风险，提供稳定的收入流"},
    "现金": {"expected_return": 0.015, "risk": 0.01, "description": "低风险低回报，具有高流动性"},
    "房地产": {"expected_return": 0.06, "risk": 0.12, "description": "中等风险，提供收入和增长潜力"},
    "黄金": {"expected_return": 0.03, "risk": 0.15, "description": "中等风险，对冲通胀的良好工具"}
}

# Function to calculate portfolio expected return and risk
def calculate_portfolio_metrics(allocation):
    portfolio_return = sum(allocation[asset] * assets[asset]["expected_return"] for asset in allocation)
    
    # Simplified risk calculation (not using correlation matrix for simplicity)
    portfolio_risk = np.sqrt(sum(allocation[asset]**2 * assets[asset]["risk"]**2 for asset in allocation))
    
    return portfolio_return, portfolio_risk

# Function to generate recommended allocation based on risk score
def generate_recommendation(risk_score):
    # Risk score ranges from 0-100
    if risk_score < 20:  # Very conservative
        return {
            "股票": 0.10,
            "债券": 0.50,
            "现金": 0.30,
            "房地产": 0.05,
            "黄金": 0.05
        }
    elif risk_score < 40:  # Conservative
        return {
            "股票": 0.25,
            "债券": 0.45,
            "现金": 0.15,
            "房地产": 0.10,
            "黄金": 0.05
        }
    elif risk_score < 60:  # Moderate
        return {
            "股票": 0.40,
            "债券": 0.30,
            "现金": 0.05,
            "房地产": 0.15,
            "黄金": 0.10
        }
    elif risk_score < 80:  # Aggressive
        return {
            "股票": 0.60,
            "债券": 0.15,
            "现金": 0.05,
            "房地产": 0.15,
            "黄金": 0.05
        }
    else:  # Very aggressive
        return {
            "股票": 0.75,
            "债券": 0.05,
            "现金": 0.00,
            "房地产": 0.15,
            "黄金": 0.05
        }

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

# Welcome page
def welcome_page():
    st.title("欢迎使用智能投顾实验平台")
    st.write("""
    这个平台将帮助您了解自己的投资偏好，并提供个性化的投资建议。
    
    实验流程：
    1. 完成个人基本情况与风险偏好问卷
    2. 查看不同资产的风险收益特征，提供您的初始配置方案
    3. 查看系统推荐的资产配置方案
    4. 根据推荐方案修改您的配置
    5. 比较不同配置方案的模拟收益情况
    """)
    
    if st.button("开始实验"):
        st.session_state.page = 1
        st.rerun()

# Questionnaire page
def questionnaire_page():
    st.title("个人基本情况与风险偏好问卷")
    
    with st.form(key="questionnaire_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("姓名", placeholder="请输入您的姓名")
            age = st.number_input("年龄", min_value=18, max_value=100, value=30)
            gender = st.selectbox("性别", ["男", "女", "其他"])
            income = st.selectbox("年收入 (人民币)", 
                ["10万以下", "10-30万", "30-50万", "50-100万", "100万以上"])
            
        with col2:
            investment_exp = st.selectbox("投资经验", 
                ["无经验", "1-3年", "3-5年", "5-10年", "10年以上"])
            
            st.subheader("风险承受能力评估")
            q1 = st.select_slider(
                "1. 您能接受的最大年度投资损失是多少？",
                options=["不能接受任何损失", "最多5%", "最多10%", "最多20%", "最多30%", "超过30%"],
                value="最多10%"
            )
            
            q2 = st.select_slider(
                "2. 如果您的投资在短期内下跌20%，您会：",
                options=["立即全部卖出", "卖出部分", "不做任何操作", "买入更多"],
                value="不做任何操作"
            )
            
            q3 = st.select_slider(
                "3. 您更倾向于哪种类型的投资？",
                options=["保本保息的储蓄产品", "低风险理财产品", "混合型基金", "股票型基金", "个股投资"],
                value="混合型基金"
            )
            
            q4 = st.select_slider(
                "4. 您的投资目标是什么？",
                options=["保存资金价值", "略高于通胀的稳定收益", "适度的资本增长", "显著的资本增长", "积极的资本增长"],
                value="适度的资本增长"
            )
            
            q5 = st.select_slider(
                "5. 您计划的投资期限是多久？",
                options=["1年以内", "1-3年", "3-5年", "5-10年", "10年以上"],
                value="3-5年"
            )
        
        submitted = st.form_submit_button("提交问卷")
        
        if submitted:
            # Calculate risk score (0-100)
            risk_mapping = {
                "q1": {"不能接受任何损失": 0, "最多5%": 20, "最多10%": 40, "最多20%": 60, "最多30%": 80, "超过30%": 100},
                "q2": {"立即全部卖出": 0, "卖出部分": 33, "不做任何操作": 67, "买入更多": 100},
                "q3": {"保本保息的储蓄产品": 0, "低风险理财产品": 25, "混合型基金": 50, "股票型基金": 75, "个股投资": 100},
                "q4": {"保存资金价值": 0, "略高于通胀的稳定收益": 25, "适度的资本增长": 50, "显著的资本增长": 75, "积极的资本增长": 100},
                "q5": {"1年以内": 0, "1-3年": 25, "3-5年": 50, "5-10年": 75, "10年以上": 100}
            }
            
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
    risk_category = ""
    if st.session_state.risk_score < 20:
        risk_category = "非常保守型"
    elif st.session_state.risk_score < 40:
        risk_category = "保守型"
    elif st.session_state.risk_score < 60:
        risk_category = "平衡型"
    elif st.session_state.risk_score < 80:
        risk_category = "进取型"
    else:
        risk_category = "激进型"
    
    st.write(f"根据您的问卷回答，您的风险承受能力得分为: **{st.session_state.risk_score:.1f}/100**")
    st.write(f"风险偏好类型: **{risk_category}**")
    
    # Display asset information
    st.subheader("资产风险收益特征")
    
    # 创建数据表格和可视化的单行布局
    asset_df = pd.DataFrame({
        "资产类别": list(assets.keys()),
        "预期年化收益率 (%)": [assets[asset]["expected_return"] * 100 for asset in assets],
        "风险 (波动率) (%)": [assets[asset]["risk"] * 100 for asset in assets],
        "风险收益比": [assets[asset]["expected_return"] / assets[asset]["risk"] for asset in assets],
        "描述": [assets[asset]["description"] for asset in assets]
    })
    
    # 创建更紧凑的布局
    col1, col2 = st.columns([3, 3])
    
    with col1:
        # 显示格式化的数据表格
        st.dataframe(
            asset_df[["资产类别", "预期年化收益率 (%)", "风险 (波动率) (%)", "风险收益比"]].style.format({
                "预期年化收益率 (%)": "{:.1f}",
                "风险 (波动率) (%)": "{:.1f}",
                "风险收益比": "{:.2f}"
            }),
            height=200,
            use_container_width=True
        )
    
    with col2:
        # 创建更紧凑的图表
        fig, ax = plt.subplots(figsize=(6, 5))
        scatter = sns.scatterplot(
            x="风险 (波动率) (%)", 
            y="预期年化收益率 (%)", 
            data=asset_df, 
            s=150, 
            ax=ax
        )
        
        # 添加标签
        for i, asset in enumerate(assets):
            plt.annotate(
                asset, 
                (assets[asset]["risk"] * 100, assets[asset]["expected_return"] * 100),
                xytext=(5, 5), 
                textcoords='offset points', 
                fontsize=10
            )
        
        plt.title("资产风险-收益分布", fontsize=12)
        plt.xlabel("风险 (波动率) %", fontsize=10)
        plt.ylabel("预期年化收益率 %", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
    
    # 显示资产描述信息 (使用一行文本代替多行显示)
    st.expander("点击查看资产详细描述", expanded=False).write(
        "\n".join([f"**{asset}**: {info['description']}" for asset, info in assets.items()])
    )
    
    # User allocation input
    st.subheader("请输入您的初始资产配置方案")
    st.write("请为每种资产类别分配投资比例 (总和需等于100%)")
    
    initial_alloc = {}
    total = 0
    
    col1, col2 = st.columns(2)
    
    with st.form(key="initial_allocation_form"):
        for i, asset in enumerate(assets):
            if i % 2 == 0:
                with col1:
                    initial_alloc[asset] = st.slider(
                        f"{asset} (%)", 
                        min_value=0.0, 
                        max_value=100.0, 
                        value=20.0,
                        step=1.0,
                        key=f"initial_{asset}"
                    )
            else:
                with col2:
                    initial_alloc[asset] = st.slider(
                        f"{asset} (%)", 
                        min_value=0.0, 
                        max_value=100.0, 
                        value=20.0,
                        step=1.0,
                        key=f"initial_{asset}"
                    )
        
        # Convert percentages to decimals
        for asset in initial_alloc:
            initial_alloc[asset] = initial_alloc[asset] / 100.0
            total += initial_alloc[asset]
        
        submitted = st.form_submit_button("提交配置方案")
        
        if submitted:
            # Check if total is close to 1.0 (100%)
            if abs(total - 1.0) > 0.01:
                st.error(f"您的配置总和为 {total*100:.1f}%，请确保总和为100%")
            else:
                st.session_state.initial_allocation = initial_alloc
                st.session_state.recommended_allocation = generate_recommendation(st.session_state.risk_score)
                st.session_state.page = 3
                st.rerun()

# Recommendation page
def recommendation_page():
    st.title("智能投顾推荐方案")
    
    # Visualize comparison between initial and recommended allocations
    st.subheader("您的初始方案 vs 智能投顾推荐方案")
    
    # Calculate metrics for both allocations
    initial_return, initial_risk = calculate_portfolio_metrics(st.session_state.initial_allocation)
    rec_return, rec_risk = calculate_portfolio_metrics(st.session_state.recommended_allocation)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 您的初始方案")
        initial_df = pd.DataFrame({
            "资产": list(st.session_state.initial_allocation.keys()),
            "配置比例": [f"{v*100:.1f}%" for v in st.session_state.initial_allocation.values()]
        })
        st.dataframe(initial_df)
        st.metric("预期年化收益率", f"{initial_return*100:.2f}%")
        st.metric("预期风险 (波动率)", f"{initial_risk*100:.2f}%")
        st.metric("收益风险比", f"{(initial_return/initial_risk):.2f}")
        
        # Pie chart for initial allocation
        fig, ax = plt.subplots(figsize=(8, 8))
        plt.pie(
            list(st.session_state.initial_allocation.values()), 
            labels=list(st.session_state.initial_allocation.keys()),
            autopct='%1.1f%%',
            startangle=90,
            shadow=False
        )
        plt.title("您的初始资产配置")
        st.pyplot(fig)
    
    with col2:
        st.write("### 智能投顾推荐方案")
        rec_df = pd.DataFrame({
            "资产": list(st.session_state.recommended_allocation.keys()),
            "配置比例": [f"{v*100:.1f}%" for v in st.session_state.recommended_allocation.values()]
        })
        st.dataframe(rec_df)
        st.metric("预期年化收益率", f"{rec_return*100:.2f}%")
        st.metric("预期风险 (波动率)", f"{rec_risk*100:.2f}%")
        st.metric("收益风险比", f"{(rec_return/rec_risk):.2f}")
        
        # Pie chart for recommended allocation
        fig, ax = plt.subplots(figsize=(8, 8))
        plt.pie(
            list(st.session_state.recommended_allocation.values()), 
            labels=list(st.session_state.recommended_allocation.keys()),
            autopct='%1.1f%%',
            startangle=90,
            shadow=False
        )
        plt.title("智能投顾推荐资产配置")
        st.pyplot(fig)
    
    # Risk-return comparison plot
    st.subheader("风险-收益对比")
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.scatter(initial_risk*100, initial_return*100, color='blue', s=200, label='您的初始方案')
    plt.scatter(rec_risk*100, rec_return*100, color='green', s=200, label='智能投顾推荐方案')
    
    # Add individual assets
    for asset, info in assets.items():
        plt.scatter(info["risk"]*100, info["expected_return"]*100, s=100, alpha=0.6)
        plt.annotate(asset, (info["risk"]*100, info["expected_return"]*100), 
                    xytext=(5, 5), textcoords='offset points')
    
    plt.title("投资组合风险-收益对比")
    plt.xlabel("风险 (波动率) %")
    plt.ylabel("预期年化收益率 %")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    st.pyplot(fig)
    
    if st.button("修改配置方案"):
        st.session_state.page = 4
        st.rerun()

# Modification page
def modification_page():
    st.title("修改您的配置方案")
    
    st.write("""
    基于智能投顾的推荐，您可以调整您的资产配置方案。
    请在下面修改各资产的配置比例，完成后点击确认进入收益模拟环节。
    """)
    
    # Show initial values from recommended allocation
    final_alloc = {}
    total = 0
    
    col1, col2 = st.columns(2)
    
    with st.form(key="final_allocation_form"):
        for i, asset in enumerate(assets):
            recommended_value = st.session_state.recommended_allocation[asset] * 100
            initial_value = st.session_state.initial_allocation[asset] * 100
            
            if i % 2 == 0:
                with col1:
                    final_alloc[asset] = st.slider(
                        f"{asset} (%)", 
                        min_value=0.0, 
                        max_value=100.0, 
                        value=float(recommended_value),
                        step=1.0,
                        key=f"final_{asset}",
                        help=f"初始方案: {initial_value:.1f}%, 推荐方案: {recommended_value:.1f}%"
                    )
            else:
                with col2:
                    final_alloc[asset] = st.slider(
                        f"{asset} (%)", 
                        min_value=0.0, 
                        max_value=100.0, 
                        value=float(recommended_value),
                        step=1.0,
                        key=f"final_{asset}",
                        help=f"初始方案: {initial_value:.1f}%, 推荐方案: {recommended_value:.1f}%"
                    )
        
        # Convert percentages to decimals
        for asset in final_alloc:
            final_alloc[asset] = final_alloc[asset] / 100.0
            total += final_alloc[asset]
        
        submitted = st.form_submit_button("确认并进入收益模拟")
        
        if submitted:
            # Check if total is close to 1.0 (100%)
            if abs(total - 1.0) > 0.01:
                st.error(f"您的配置总和为 {total*100:.1f}%，请确保总和为100%")
            else:
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
            "初始投资金额 (元)", 
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=10000
        )
        
        simulation_period = st.slider(
            "模拟期限 (天)",
            min_value=30,
            max_value=3650,
            value=365,
            step=30
        )
        
        st.caption("注: 本模拟使用蒙特卡洛方法，基于历史数据和统计分布生成可能的投资路径。实际投资表现可能与模拟结果有显著差异。")
    
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
        '日期': dates,
        '初始方案': initial_simulation,
        '推荐方案': recommended_simulation,
        '最终方案': final_simulation
    })
    
    # Display portfolio summary and comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("初始方案最终收益", f"{initial_simulation[-1]:,.2f} 元", 
                 f"{initial_return:.2f}%")
        
    with col2:
        st.metric("推荐方案最终收益", f"{recommended_simulation[-1]:,.2f} 元", 
                 f"{recommended_return:.2f}%")
        
    with col3:
        st.metric("最终方案最终收益", f"{final_simulation[-1]:,.2f} 元", 
                 f"{final_return:.2f}%")
    
    # Plot simulation results
    st.subheader("投资组合价值变化")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(dates[::30], initial_simulation[::30], label='初始方案', linewidth=2)
    plt.plot(dates[::30], recommended_simulation[::30], label='推荐方案', linewidth=2)
    plt.plot(dates[::30], final_simulation[::30], label='最终方案', linewidth=2)
    
    plt.title("不同资产配置方案的模拟收益对比")
    plt.xlabel("日期")
    plt.ylabel("组合价值 (元)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show histogram of daily returns
    st.subheader("日收益率分布")
    
    # Calculate daily returns
    daily_returns_initial = np.diff(initial_simulation) / initial_simulation[:-1]
    daily_returns_recommended = np.diff(recommended_simulation) / recommended_simulation[:-1]
    daily_returns_final = np.diff(final_simulation) / final_simulation[:-1]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.hist(daily_returns_initial, bins=50, alpha=0.3, label='初始方案')
    plt.hist(daily_returns_recommended, bins=50, alpha=0.3, label='推荐方案')
    plt.hist(daily_returns_final, bins=50, alpha=0.3, label='最终方案')
    
    plt.title("日收益率分布对比")
    plt.xlabel("日收益率")
    plt.ylabel("频率")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)
    
    # Show detailed metrics
    st.subheader("详细绩效指标")
    
    metrics_df = pd.DataFrame({
        '指标': ['年化收益率', '波动率', '夏普比率', '最大回撤', '收益风险比'],
        '初始方案': [
            f"{initial_return / (simulation_period/365):.2f}%",
            f"{np.std(daily_returns_initial) * np.sqrt(252) * 100:.2f}%",
            f"{(initial_return / (simulation_period/365)) / (np.std(daily_returns_initial) * np.sqrt(252) * 100):.2f}",
            f"{(np.max(initial_simulation) - np.min(initial_simulation[np.argmax(initial_simulation):]))/ np.max(initial_simulation) * 100:.2f}%",
            f"{initial_return / (np.std(daily_returns_initial) * np.sqrt(252) * 100):.2f}"
        ],
        '推荐方案': [
            f"{recommended_return / (simulation_period/365):.2f}%",
            f"{np.std(daily_returns_recommended) * np.sqrt(252) * 100:.2f}%",
            f"{(recommended_return / (simulation_period/365)) / (np.std(daily_returns_recommended) * np.sqrt(252) * 100):.2f}",
            f"{(np.max(recommended_simulation) - np.min(recommended_simulation[np.argmax(recommended_simulation):]))/ np.max(recommended_simulation) * 100:.2f}%",
            f"{recommended_return / (np.std(daily_returns_recommended) * np.sqrt(252) * 100):.2f}"
        ],
        '最终方案': [
            f"{final_return / (simulation_period/365):.2f}%",
            f"{np.std(daily_returns_final) * np.sqrt(252) * 100:.2f}%",
            f"{(final_return / (simulation_period/365)) / (np.std(daily_returns_final) * np.sqrt(252) * 100):.2f}",
            f"{(np.max(final_simulation) - np.min(final_simulation[np.argmax(final_simulation):]))/ np.max(final_simulation) * 100:.2f}%",
            f"{final_return / (np.std(daily_returns_final) * np.sqrt(252) * 100):.2f}"
        ]
    })
    
    st.dataframe(metrics_df)
    
    # Restart experiment
    if st.button("重新开始实验"):
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
            progress_labels = ["开始", "问卷", "初始配置", "推荐方案", "方案修改", "收益模拟"]
            progress_value = st.session_state.page / (len(progress_labels) - 1)
            st.progress(progress_value)
            st.write(f"当前阶段: {progress_labels[st.session_state.page]}")
            
            # Navigation buttons
            if st.session_state.page > 1:
                if st.button("← 返回上一步"):
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