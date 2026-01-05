import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面配置 ---
st.set_page_config(page_title="小工具", layout="wide")

# --- 2. 侧边栏统一修正 ---
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

# --- 3. 顶部汇总模块 ---
def show_top_dashboard():
    TIMEZONE = pytz.timezone('Africa/Conakry')
    today = datetime.now(TIMEZONE).date()
    r_limit, y_limit = 0, 30 
    
    FILE_NAME = "设备证件清单.xlsx"
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME)
            red, yellow, green = 0, 0, 0
            date_cols = ["灰卡有效期", "保险有效期", "车检有效期"]
            for _, row in df.iterrows():
                days = [ (pd.to_datetime(row[c]).date() - today).days for c in date_cols if c in df.columns and pd.notna(row[c]) ]
                if not days: green += 1
                else:
                    min_d = min(days)
                    if min_d < r_limit: red += 1
                    elif min_d <= y_limit: yellow += 1
                    else: green += 1
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("在册总数", f"{len(df)} 台")
            c2.error(f"🔴 已过期: {red}")
            c3.warning(f"🟡 临期: {yellow}")
            c4.success(f"🟢 正常: {green}")
            st.divider()
        except: pass

st.title("车辆证件管理")
show_top_dashboard()

# --- 4. 录入功能 ---
FILE_NAME = "设备证件清单.xlsx"
menu = st.tabs(["查看/编辑清单", "单条录入", "批量导入Excel"])

with menu[0]:
    if os.path.exists(FILE_NAME):
        st.dataframe(pd.read_excel(FILE_NAME), use_container_width=True)
    else: st.write("暂无数据。")

with menu[1]:
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        plate = col1.text_input("车牌号/设备号")
        owner = col2.text_input("所有人/责任人")
        st.write("证件有效期设置")
        c1, c2, c3 = st.columns(3)
        date1 = c1.date_input("灰卡有效期")
        date2 = c2.date_input("保险有效期")
        date3 = c3.date_input("车检有效期")
        if st.form_submit_button("保存"):
            new_data = {"车牌号": plate, "责任人": owner, "灰卡有效期": date1.strftime("%Y-%m-%d"), 
                        "保险有效期": date2.strftime("%Y-%m-%d"), "车检有效期": date3.strftime("%Y-%m-%d")}
            df = pd.concat([pd.read_excel(FILE_NAME), pd.DataFrame([new_data])]) if os.path.exists(FILE_NAME) else pd.DataFrame([new_data])
            df.to_excel(FILE_NAME, index=False)
            st.success("录入成功！")
            st.rerun()

with menu[2]:
    upl = st.file_uploader("导入Excel", type="xlsx")
    if upl and st.button("确认导入"):
        pd.read_excel(upl).to_excel(FILE_NAME, index=False)
        st.success("导入成功！")
        st.rerun()