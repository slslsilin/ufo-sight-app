import streamlit as st
import pandas as pd
import plotly.express as px

# 配置页面
st.set_page_config(page_title="UFO地理分析", layout="wide")
st.title("UFO目击地理分布分析 🛸")

# 从GitHub读取数据
@st.cache_data
def load_data():
    csv_url = "https://raw.githubusercontent.com/slslsilin/ufo-sight-app/main/ufo_sighting_data.csv"
    df = pd.read_csv(csv_url)
    
    # 数据清洗
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]
    return df

df = load_data()

# =========================================================================
# 问题1：目击最多的国家/地区
# =========================================================================
st.header("1. 目击最多的国家/地区")
country_counts = df["country"].value_counts().reset_index()
country_counts.columns = ["国家", "目击次数"]

# 双列布局
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("国家排名")
    st.dataframe(country_counts.head(10), height=400)

with col2:
    st.subheader("分布直方图")
    fig = px.bar(country_counts.head(10), 
                 x="国家", y="目击次数",
                 color="目击次数", 
                 labels={"国家": "国家", "目击次数": "报告数量"},
                 height=400)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 问题2：地理热点分析
# =========================================================================
st.header("2. 地理热点分布")

# 交互式地图
st.subheader("目击地点热力图")
st.map(df[["latitude", "longitude"]], zoom=1)

# 按州/省的目击密度
st.subheader("州/省级热点排名")
state_counts = df["state/province"].value_counts().reset_index()
state_counts.columns = ["州/省", "目击次数"]
fig = px.bar(state_counts.head(15), 
             x="目击次数", y="州/省", 
             orientation="h",
             labels={"州/省": "地区", "目击次数": "报告数量"},
             height=600)
st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 问题3：城乡分布分析
# =========================================================================
st.header("3. 城乡目击分布")

# 假设：通过城市目击频率推断城乡密度
city_counts = df["city"].value_counts().reset_index()
city_counts.columns = ["城市", "目击次数"]

# 定义城乡分类规则（示例）
city_counts["地区类型"] = pd.cut(city_counts["目击次数"],
                               bins=[0, 1, 5, float('inf')],
                               labels=["农村", "郊区", "城市"])

# 可视化
col3, col4 = st.columns(2)
with col3:
    st.subheader("城乡分布比例")
    urban_rural = city_counts["地区类型"].value_counts()
    fig = px.pie(urban_rural, 
                 values=urban_rural.values, 
                 names=urban_rural.index,
                 hole=0.4)
    st.plotly_chart(fig)

with col4:
    st.subheader("高频目击城市")
    st.dataframe(city_counts[city_counts["地区类型"] == "城市"].head(10))

# =========================================================================
# 添加筛选器
# =========================================================================
st.sidebar.header("筛选选项")
selected_countries = st.sidebar.multiselect("选择国家", df["country"].unique())
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
