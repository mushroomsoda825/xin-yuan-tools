import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# 页面配置
st.set_page_config(page_title="鑫圆小助手", layout="wide")

# 时区设置
TIMEZONE = pytz.timezone('Africa/Conakry')
now_gn = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

# 主标题
st.title("🤖 鑫圆小助手 - 综合管理控制台")
st.write(f"🌍 几内亚当前时间：`{now_gn}`")
st.divider()

# --- 证件汇总区域 ---
st.header("📊 证件到期汇总状态")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ 设备证件状态")
    if os.path.exists("设备证件清单.xlsx"):
        df_car = pd.read_excel("设备证件清单.xlsx")
        # 这里可以加入具体的过期逻辑计算，目前先显示总数
        st.metric("在册设备总数", f"{len(df_car)} 台")
        st.success("✅ 数据已连接")
    else:
        st.info("💡 尚未检测到设备数据，请在侧边栏录入。")
    st.caption("管理入口：左侧菜单 -> 车辆证件管理")

with col2:
    st.subheader("2️⃣ 人员证件状态")
    if os.path.exists("人员证件清单.xlsx"):
        df_per = pd.read_excel("人员证件清单.xlsx")
        st.metric("在职人员总数", f"{len(df_per)} 人")
        st.success("✅ 数据已连接")
    else:
        st.info("💡 尚未检测到人员数据，请在侧边栏录入。")
    st.caption("管理入口：左侧菜单 -> 人员证件管理")

st.divider()
st.info("📢 **使用提示**：点击左上角的“>”箭头可以展开菜单，进行具体的数字转换或证件数据录入。")