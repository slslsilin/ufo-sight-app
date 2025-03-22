import streamlit as st
import pandas as pd

# 设置标题
st.title("UFO目击数据可视化应用 🛸")

# 从GitHub读取CSV数据
csv_url = "https://raw.githubusercontent.com/[你的GitHub用户名]/[仓库名]/main/ufo_sighting_data.csv"
df = pd.read_csv(csv_url)

# 显示原始数据
st.subheader("原始数据")
st.write(df)

# 基础统计信息
st.subheader("基础统计")
st.write(df.describe())

# 交互式筛选
st.sidebar.subheader("筛选条件")
selected_shape = st.sidebar.multiselect("选择UFO形状", df["UFO_shape"].unique())
selected_country = st.sidebar.multiselect("选择国家", df["country"].unique())

# 根据筛选条件过滤数据
filtered_df = df[
    (df["UFO_shape"].isin(selected_shape)) &
    (df["country"].isin(selected_country))
]

# 显示筛选结果
st.subheader("筛选后的数据")
st.write(filtered_df)

# 地图可视化（需有效经纬度）
if not filtered_df.empty:
    st.subheader("目击地点地图")
    st.map(filtered_df[["latitude", "longitude"]].dropna())
else:
    st.warning("无匹配数据，请调整筛选条件。")
