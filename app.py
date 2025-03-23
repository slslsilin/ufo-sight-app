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
    df["city"] = df["city"].astype(str).str.lower()
    return df

df = load_data()

# =========================================================================
# 问题1：目击最多的国家/地区
# =========================================================================
st.header("The most witnessed countries")
country_counts = df["country"].value_counts().reset_index()
country_counts.columns = ["Country", "Witeness times"]

# 双列布局
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Ranking")
    st.dataframe(country_counts, height=400)

with col2:
    st.subheader(" ")
    fig = px.bar(country_counts.head(20), 
                 x="Country", y="Witeness times",
                 color="Witeness times", 
                 labels={"Country": "Country", "Witeness times": "Witeness times"},
                 height=400)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 问题2：地理热点分析
# =========================================================================
st.header("Geographic hotspot distribution")

# 交互式地图
st.subheader("目击地点热力图")
st.map(df[["latitude", "longitude"]], zoom=1)

# 按州/省的目击密度
st.subheader("州/省级热点排名")
state_counts = df["state/province"].value_counts().reset_index()
state_counts.columns = ["State", "Witeness times"]
fig = px.bar(state_counts, 
             x="Witeness times", y="State", 
             orientation="h",
             labels={"State": "Region", "Witeness time": "Witeness time"},
             height=600)
st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# 城乡分类逻辑（基于城市名称关键词）
# =========================================================================
def classify_urban_rural(city_name):
    """根据城市名称中的关键词分类"""
    city_name = str(city_name).lower()
    if "country" in city_name:
        return "农村"
    elif "rural" in city_name:
        return "郊区"
    else:
        return "城市"

# 应用分类
df["地区类型"] = df["city"].apply(classify_urban_rural)

# =========================================================================
# 城乡分布可视化
# =========================================================================
st.header("城乡目击分布")

# 双列布局
col1, col2 = st.columns([1, 2])

with col1:
    # 饼图展示比例
    st.subheader("城乡比例")
    urban_rural_counts = df["地区类型"].value_counts().reset_index()
    urban_rural_counts.columns = ["地区类型", "目击次数"]
    fig_pie = px.pie(
        urban_rural_counts,
        names="地区类型",
        values="目击次数",
        color="地区类型",
        color_discrete_map={"农村": "#00CC96", "郊区": "#EF553B", "城市": "#636EFA"},
        hole=0.3
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # 表格展示分类示例
    st.subheader("分类示例")
    
    # 农村示例
    rural_examples = df[df["地区类型"] == "农村"]["city"].str.title().unique()[:10]
    # 郊区示例
    suburban_examples = df[df["地区类型"] == "郊区"]["city"].str.title().unique()[:10]
    
    # 用Expander折叠展示
    with st.expander("点击查看农村地区示例", expanded=True):
        st.write(pd.DataFrame({"农村地区": rural_examples}))
    
    with st.expander("点击查看郊区示例"):
        st.write(pd.DataFrame({"郊区": suburban_examples}))

# =========================================================================
# 地理分布验证地图
# =========================================================================
st.header("分类结果地理验证")
st.write("""
- **红色标记**: 郊区 (`city`名称含"rural")  
- **蓝色标记**: 城市  
- **绿色标记**: 农村 (`city`名称含"country")
""")

# 为地图添加颜色编码
df["color"] = df["地区类型"].map({
    "农村": "#00CC96",
    "郊区": "#EF553B",
    "城市": "#636EFA"
})

# 绘制交互式地图
fig_map = px.scatter_geo(
    df,
    lat="latitude",
    lon="longitude",
    color="color",
    hover_name="city",
    scope="world",
    projection="natural earth",
    title="城乡分类地理分布验证",
    opacity=0.7
)
fig_map.update_layout(showlegend=False)
st.plotly_chart(fig_map, use_container_width=True)
# =========================================================================
# 添加筛选器
# =========================================================================
st.sidebar.header("筛选选项")
selected_countries = st.sidebar.multiselect("选择国家", df["country"].unique())
if selected_countries:
    df = df[df["country"].isin(selected_countries)]
