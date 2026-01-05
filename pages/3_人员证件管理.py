import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面配置 ---
st.set_page_config(page_title="小工具", layout="wide")

# --- 2. 侧边栏统一修正 (确保显示“主页面”并隐藏“app”) ---
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

# --- 3. 顶部汇总模块 (保留🔴🟡🟢图标) ---
def show_top_dashboard():
    TIMEZONE = pytz.timezone('Africa/Conakry')
    today = datetime.now(TIMEZONE).date()
    r_limit, y_limit = 0, 30 
    
    FILE_NAME = "人员证件清单.xlsx"
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME)
            red, yellow, green = 0, 0, 0
            # 统计所有涉及有效期的列
            date_cols = [
                "护照有效期", "身份证有效期", "几内亚签证有效期", 
                "工作证有效期", "居住证有效期", "驾照有效期"
            ]
            for _, row in df.iterrows():
                days = [ (pd.to_datetime(row[c]).date() - today).days for c in date_cols if c in df.columns and pd.notna(row[c]) ]
                if not days: green += 1
                else:
                    min_d = min(days)
                    if min_d < r_limit: red += 1
                    elif min_d <= y_limit: yellow += 1
                    else: green += 1
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("在职总数", f"{len(df)} 人")
            c2.error(f"🔴 已过期: {red}")
            c3.warning(f"🟡 临期: {yellow}")
            c4.success(f"🟢 正常: {green}")
            st.divider()
        except: pass

st.title("人员证件管理")
show_top_dashboard()

# --- 4. 业务功能 ---
FILE_NAME = "人员证件清单.xlsx"
menu = st.tabs(["查看/编辑清单", "单条录入", "批量导入Excel"])

with menu[0]:
    if os.path.exists(FILE_NAME):
        st.dataframe(pd.read_excel(FILE_NAME), use_container_width=True)
    else: st.write("暂无人员数据。")

with menu[1]:
    with st.form("person_add_form", clear_on_submit=True):
        st.write("**基本信息**")
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("姓名")
        gender = col2.selectbox("性别", ["男", "女"])
        id_card = col3.text_input("身份证号")
        
        st.write("---")
        st.write("**证件号登记**")
        ca, cb, cc = st.columns(3)
        passport_no = ca.text_input("护照号")
        visa_no = cb.text_input("几内亚签证号")
        residence_no = cc.text_input("居住证号")
        
        cd, ce, cf = st.columns(3)
        work_no = cd.text_input("工作证号")
        license_no = ce.text_input("驾照号")
        
        st.write("---")
        st.write("**有效期设置**")
        d1, d2, d3 = st.columns(3)
        date_p = d1.date_input("护照有效期")
        date_i = d2.date_input("身份证有效期")
        date_v = d3.date_input("几内亚签证有效期")
        
        d4, d5, d6 = st.columns(3)
        date_w = d4.date_input("工作证有效期")
        date_r = d5.date_input("居住证有效期")
        date_l = d6.date_input("驾照有效期")
        
        if st.form_submit_button("确认保存人员信息"):
            new_person = {
                "姓名": name, "性别": gender, "身份证号": id_card, "护照号": passport_no,
                "几内亚签证号": visa_no, "居住证号": residence_no, "工作证号": work_no, "驾照号": license_no,
                "护照有效期": date_p.strftime("%Y-%m-%d"), "身份证有效期": date_i.strftime("%Y-%m-%d"),
                "几内亚签证有效期": date_v.strftime("%Y-%m-%d"), "工作证有效期": date_w.strftime("%Y-%m-%d"),
                "居住证有效期": date_r.strftime("%Y-%m-%d"), "驾照有效期": date_l.strftime("%Y-%m-%d"),
                "更新时间": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            if os.path.exists(FILE_NAME):
                df = pd.concat([pd.read_excel(FILE_NAME), pd.DataFrame([new_person])], ignore_index=True)
            else:
                df = pd.DataFrame([new_person])
            df.to_excel(FILE_NAME, index=False)
            st.success(f"✅ {name} 的信息已成功保存！")
            st.rerun()

with menu[2]:
    upl = st.file_uploader("导入人员Excel", type="xlsx")
    if upl and st.button("确认导入数据"):
        pd.read_excel(upl).to_excel(FILE_NAME, index=False)
        st.success("人员清单导入成功！")
        st.rerun()