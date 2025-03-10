# 智能投顾实验平台

这是一个基于Streamlit开发的智能投顾实验平台，用于演示资产配置和投资组合管理的基本原理。

## 功能特点

- 风险承受能力评估问卷
- 用户自定义资产配置
- 智能投顾推荐配置
- 投资组合风险收益分析
- 投资收益模拟

## 安装与运行

1. 克隆仓库到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`streamlit run app.py`

## 配置文件

本项目使用YAML配置文件存储资产数据和风险评分映射，主要配置文件包括：

- `config/assets.yaml`: 资产数据、风险评分映射和资产配置推荐

配置文件结构如下：

```yaml
# 资产数据及参数配置
assets:
  股票:
    expected_return: 0.08
    risk: 0.20
    description: 高风险高回报，具有较高的长期增长潜力
  # 其他资产...

# 资产名称翻译
asset_names_en:
  股票: Stocks
  # 其他资产...

# 风险评分对应的资产配置推荐
risk_recommendations:
  very_conservative:  # 风险评分 < 20
    股票: 0.10
    # 其他资产...
  # 其他风险类别...

# 风险评分映射
risk_mapping:
  q1:
    不能接受亏损: 0
    # 其他选项...
  # 其他问题...

# 风险偏好类型
risk_categories:
  very_conservative:
    max_score: 20
    name: 非常保守型
  # 其他类别...
```

## 在线部署

本项目可以部署到Streamlit Share平台。部署时需要注意：

1. 确保`.streamlit/config.toml`文件存在，并启用静态文件服务：
   ```toml
   [server]
   enableStaticServing = true
   ```

2. 确保`static`目录存在，并包含备份的配置文件：
   ```
   static/assets.yaml
   ```

3. 部署到Streamlit Share时，配置文件会从以下位置按顺序查找：
   - `config/assets.yaml`
   - `static/assets.yaml`
   - 如果都找不到，将使用内置的默认配置

## 自定义配置

如需修改资产数据或风险评分映射，只需编辑`config/assets.yaml`文件，无需修改代码。

## 许可证

MIT 