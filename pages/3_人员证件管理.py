import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="小工具", layout="wide")

# --- 2. 侧边栏布局优化 ---
with st.sidebar:
    st.page_link("app.py", label="主页面")
    st.write("") 

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li:first-child { display: none !important; }
        [data-testid="stSidebarNav"] { padding-top: 0rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 预警时间设置 ---
st.sidebar.header("预警时间设置")
red_days = st.sidebar.number_input("🔴 红色预警天数", value=0)
yellow_days = st.sidebar.number_input("🟡 黄色预警天数", value=30)

# --- 4. 修正后的统计逻辑函数 ---
TIMEZONE = pytz.timezone('Africa/Conakry')
today = datetime.now(TIMEZONE).date()

def get_refined_stats(file_path, monitor_map, r_limit, y_limit):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        total_count = len(df)
        red_entities, yellow_entities, green_entities = 0, 0, 0
        detail_item_counts = {k: 0 for k in monitor_map.keys()}
        
        for _, row in df.iterrows():
            entity_status = "green" # 默认正常
            has_red = False
            has_yellow = False
            
            for label, col in monitor_map.items():
                if col in df.columns and pd.notna(row[col]):
                    try:
                        d = (pd.to_datetime(row[col]).date() - today).days
                        if d < r_limit:
                            detail_item_counts[label] += 1
                            has_red = True
                        elif d <= y_limit:
                            detail_item_counts[label] += 1
                            has_yellow = True
                    except:
                        continue
            
            # 确定该个体（人或车）的最终状态标签
            if has_red:
                red_entities += 1
            elif has_yellow:
                yellow_entities += 1
            else:
                green_entities += 1
                
        return {
            "total": total_count, 
            "red": red_entities, 
            "yellow": yellow_entities, 
            "green": green_entities, 
            "details": detail_item_counts
        }
    except:
        return None

# --- 5. 主界面展示 ---
st.title("控制台汇总")
st.write(f"几内亚时间: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

col1, col2 = st.columns(2)

# --- 设备证件模块 ---
with col1:
    st.subheader("设备证件监控")
    car_map = {
        "灰卡": "灰卡有效日期", "无抵押": "无抵押证明有效日期", 
        "保险": "保险有效期", "车检": "车检有效期", "有色车窗": "有色车窗证有效期"
    }
    res_car = get_refined_stats("设备证件清单.xlsx", car_map, red_days, yellow_days)
    
    if res_car:
        # 顶部：以“台”为单位的汇总
        st.metric("在册设备总数", f"{res_car['total']} 台")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {res_car['red']}")
        m2.warning(f"🟡 临期: {res_car['yellow']}")
        m3.success(f"🟢 正常: {res_car['green']}")
        
        # 底部：异常项分析
        anomaly_count = res_car['red'] + res_car['yellow']
        with st.expander(f"📋 异常设备总计: {anomaly_count} 台 (点击查看具体分类)", expanded=True):
            for label, count in res_car['details'].items():
                if count > 0:
                    st.write(f"⚠️ {label}类别共涉及: {count} 件异常")
    else:
        st.info("暂无设备数据")

# --- 人员证件模块 ---
with col2:
    st.subheader("人员证件监控")
    per_map = {
        "护照": "护照有效期", "身份证": "身份证有效期", "签证": "几内亚签证有效期",
        "工作证": "工作证有效期", "居住证": "居住证有效期", "驾照": "驾照有效期"
    }
    res_per = get_refined_stats("人员证件清单.xlsx", per_map, red_days, yellow_days)
    
    if res_per:
        # 顶部：以“人”为单位的汇总
        st.metric("在职总人数", f"{res_per['total']} 人")
        n1, n2, n3 = st.columns(3)
        n1.error(f"🔴 已过期: {res_per['red']}")
        n2.warning(f"🟡 临期: {res_per['yellow']}")
        n3.success(f"🟢 正常: {res_per['green']}")
        
        # 底部：异常项分析
        anomaly_per_count = res_per['red'] + res_per['yellow']
        with st.expander(f"📋 异常人员总计: {anomaly_per_count} 人 (点击查看具体分类)", expanded=True):
            for label, count in res_per['details'].items():
                if count > 0:
                    st.write(f"⚠️ {label}类别共涉及: {count} 人预警")
    else:
        st.info("暂无人员数据")