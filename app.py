import streamlit as st
import pandas as pd

st.title("UFO目击数据在线应用 🛸")

# 从GitHub读取数据
csv_url = "https://raw.githubusercontent.com/slslsilin/ufo-sight-app/main/ufo_sighting_data.csv"
df = pd.read_csv(csv_url)

# 清洗数据：确保经纬度为数值且在合理范围内
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
valid_df = df.dropna(subset=["latitude", "longitude"])
valid_df = valid_df[
    (valid_df["latitude"].between(-90, 90)) &
    (valid_df["longitude"].between(-180, 180))
]

# 显示数据
st.write("有效数据总览：", valid_df)

# 显示地图
if not valid_df.empty:
    st.map(valid_df[["latitude", "longitude"]])
else:
    st.warning("无有效经纬度数据可供显示。")
