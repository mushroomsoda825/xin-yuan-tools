import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="鑫圆办公系统", layout="wide")

# --- 2. 强力 CSS 修正：将侧边栏的 "app" 替换为 "首页" 并确保它不消失 ---
st.markdown("""
    <style>
        /* 定位侧边栏第一个项目 */
        [data-testid="stSidebarNav"] ul li:first-child span {
            font-size: 0 !important;
        }
        [data-testid="stSidebarNav"] ul li:first-child span::after {
            content: "首页";
            font-size: 1rem !important;
            visibility: visible !important;
        }
        /* 保持当前页选中状态的背景 */
        [data-testid="stSidebarNav"] ul li:first-child a {
            background-color: rgba(151, 166, 195, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏：预警阈值调整模块 ---
st.sidebar.header("预警时间设置")
red_days = st.sidebar.number_input("🔴 红色预警天数 (过期)", value=0, help="到期天数小于此值标记为红色")
yellow_days = st.sidebar.number_input("🟡 黄色预警天数 (临期)", value=30, help="到期天数小于等于此值标记为黄色")

st.sidebar.divider()
st.sidebar.caption("统计规则：\n1. 小于红区为过期\n2. 小于等于黄区为临期\n3. 其余为绿色正常")

# --- 4. 核心统计逻辑 ---
TIMEZONE = pytz.timezone('Africa/Conakry')
today = datetime.now(TIMEZONE).date()

def get_stats(file_path, date_columns, r_limit, y_limit):
    if not os.path.exists(file_path):
        return None
    try:
        # 读取 Excel，确保日期格式正确
        df = pd.read_excel(file_path)
        total = len(df)
        red, yellow, green = 0, 0, 0
        
        for _, row in df.iterrows():
            days_list = []
            for col in date_columns:
                if col in df.columns and pd.notna(row[col]):
                    # 转换日期并计算差距
                    d = (pd.to_datetime(row[col]).date() - today).days
                    days_list.append(d)
            
            if not days_list:
                green += 1 
                continue
            
            # 取该行所有证件中最紧迫的一个日期
            min_day = min(days_list)
            if min_day < r_limit:
                red += 1
            elif min_day <= y_limit:
                yellow += 1
            else:
                green += 1
        return {"total": total, "red": red, "yellow": yellow, "green": green}
    except:
        return None

# --- 5. 主界面展示 ---
st.title("控制台汇总")
st.write(f"几内亚时间: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("设备证件汇总")
    # 扫描车辆相关的三个日期列
    res_car = get_stats("设备证件清单.xlsx", ["灰卡有效期", "保险有效期", "车检有效期"], red_days, yellow_days)
    if res_car:
        st.metric("在册数量", f"{res_car['total']} 台")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {res_car['red']}")
        m2.warning(f"🟡 临期: {res_car['yellow']}")
        m3.success(f"🟢 正常: {res_car['green']}")
    else:
        st.info("暂无设备数据")

with col2:
    st.subheader("人员证件汇总")
    # 扫描人员相关的三个日期列
    res_per = get_stats("人员证件清单.xlsx", ["护照有效期", "签证有效期", "居住证有效期"], red_days, yellow_days)
    if res_per:
        st.metric("在册数量", f"{res_per['total']} 人")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {res_per['red']}")
        m2.warning(f"🟡 临期: {res_per['yellow']}")
        m3.success(f"🟢 正常: {res_per['green']}")
    else:
        st.info("暂无人员数据")