import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

st.set_page_config(page_title="鑫圆小助手", layout="wide")
TIMEZONE = pytz.timezone('Africa/Conakry')
today = datetime.now(TIMEZONE).date()

st.title("🤖 鑫圆小助手 - 综合管理控制台")
st.write(f"🌍 几内亚当前时间：`{datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}`")
st.divider()

def get_counts(file_path, date_cols):
    """计算 Excel 中的预警统计"""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        total = len(df)
        red, yellow, green = 0, 0, 0
        
        for _, row in df.iterrows():
            min_days = 9999
            has_date = False
            for col in date_cols:
                if col in df.columns and pd.notna(row[col]):
                    has_date = True
                    expiry = pd.to_datetime(row[col]).date()
                    days = (expiry - today).days
                    if days < min_days: min_days = days
            
            if not has_date: continue
            if min_days < 0: red += 1
            elif min_days <= 30: yellow += 1
            else: green += 1
        return {"total": total, "red": red, "yellow": yellow, "green": green}
    except:
        return None

# --- 数据展示 ---
c1, c2 = st.columns(2)

# 1. 设备证件汇总
with c1:
    st.markdown("### 🚜 设备证件汇总")
    stats = get_counts("设备证件清单.xlsx", ["灰卡有效期", "保险有效期", "车检有效期"])
    if stats:
        st.metric("在册总数", f"{stats['total']} 台")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {stats['red']}")
        m2.warning(f"🟡 临期: {stats['yellow']}")
        m3.success(f"🟢 正常: {stats['green']}")
    else:
        st.info("暂无车辆数据")

# 2. 人员证件汇总
with c2:
    st.markdown("### 👤 人员证件汇总")
    # 假设人员表格包含这些有效期列
    stats = get_counts("人员证件清单.xlsx", ["护照有效期", "签证有效期", "居住证有效期"])
    if stats:
        st.metric("在职总数", f"{stats['total']} 人")
        m1, m2, m3 = st.columns(3)
        m1.error(f"🔴 已过期: {stats['red']}")
        m2.warning(f"🟡 临期: {stats['yellow']}")
        m3.success(f"🟢 正常: {stats['green']}")
    else:
        st.info("暂称人员数据")

st.divider()
st.caption("💡 统计逻辑：红色(<0天)，黄色(≤30天)，绿色(>30天)。具体录入请使用左侧菜单。")