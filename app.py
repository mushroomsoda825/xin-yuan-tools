import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="小工具", layout="wide")

# --- 2. 侧边栏导航：修正名称并隐藏原生标签 ---
with st.sidebar:
    st.page_link("app.py", label="主页面")
    st.divider()

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. 预警时间设置 ---
st.sidebar.header("预警时间设置")
red_days = st.sidebar.number_input("🔴 红色预警天数", value=0)
yellow_days = st.sidebar.number_input("🟡 黄色预警天数", value=30)

# --- 4. 核心统计逻辑函数 ---
TIMEZONE = pytz.timezone('Africa/Conakry')
today = datetime.now(TIMEZONE).date()

def get_detailed_stats(file_path, monitor_map, r_limit, y_limit):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        total = len(df)
        red, yellow, green = 0, 0, 0
        detail_counts = {k: 0 for k in monitor_map.keys()}
        
        for _, row in df.iterrows():
            row_days = []
            for label, col in monitor_map.items():
                if col in df.columns and pd.notna(row[col]):
                    d = (pd.to_datetime(row[col]).date() - today).days
                    row_days.append(d)
                    if d <= y_limit: # 统计具体证件类型的预警数
                        detail_counts[label] += 1
            
            if not row_days:
                green += 1
            else:
                min_d = min(row_days)
                if min_d < r_limit: red += 1
                elif min_d <= y_limit: yellow += 1
                else: green += 1
        return {"total": total, "red": red, "yellow": yellow, "green": green, "details": detail_counts}
    except:
        return None

# --- 5. 主界面展示 ---
st.title("控制台汇总")
st.write(f"几内亚时间: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

col1, col2 = st.columns(2)

# --- 设备证件模块 ---
with col1:
    st.subheader("设备证件全局监控")
    car_map = {"灰卡": "灰卡有效日期", "无抵押": "无抵押证明有效日期", "保险": "保险有效期", "车检": "车检有效期"}
    res_car = get_detailed_stats("设备证件清单.xlsx", car_map, red_days, yellow_days)
    
    if res_car:
        st.metric("在册设备", f"{res_car['total']} 台")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {res_car['red']}")
        m2.warning(f"🟡 临期: {res_car['yellow']}")
        m3.success(f"🟢 正常: {res_car['green']}")
        
        # 显示具体分类统计
        with st.expander("查看设备预警详情"):
            for label, count in res_car['details'].items():
                st.write(f"{label}类别: {count} 件预警")
    else:
        st.info("暂无设备数据")

# --- 人员证件模块 ---
with col2:
    st.subheader("人员证件全局监控")
    per_map = {
        "护照": "护照有效期", "身份证": "身份证有效期", "签证": "几内亚签证有效期",
        "工作证": "工作证有效期", "居住证": "居住证有效期", "驾照": "驾照有效期"
    }
    res_per = get_detailed_stats("人员证件清单.xlsx", per_map, red_days, yellow_days)
    
    if res_per:
        st.metric("在职人数", f"{res_per['total']} 人")
        n1, n2, n3 = st.columns(3)
        n1.error(f"🔴 已过期: {res_per['red']}")
        n2.warning(f"🟡 临期: {res_per['yellow']}")
        n3.success(f"🟢 正常: {res_per['green']}")
        
        # 显示具体分类统计
        with st.expander("查看人员预警详情"):
            for label, count in res_per['details'].items():
                st.write(f"{label}类别: {count} 人预警")
    else:
        st.info("暂无人员数据")