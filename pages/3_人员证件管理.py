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

st.markdown("""<style>[data-testid="stSidebarNav"] ul li:first-child { display: none !important; }</style>""", unsafe_allow_html=True)

# --- 3. 核心统计与分析逻辑 ---
def show_person_detailed_dashboard():
    TIMEZONE = pytz.timezone('Africa/Conakry')
    today = datetime.now(TIMEZONE).date()
    r_limit, y_limit = 0, 30 
    FILE_NAME = "人员证件清单.xlsx"
    
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME)
            red, yellow, green = 0, 0, 0
            
            # 定义需要监控的六个有效期类别
            monitor_map = {
                "护照": "护照有效期",
                "身份证": "身份证有效期",
                "签证": "几内亚签证有效期",
                "工作证": "工作证有效期",
                "居住证": "居住证有效期",
                "驾照": "驾照有效期"
            }
            detail_stats = {k: 0 for k in monitor_map.keys()}
            
            for _, row in df.iterrows():
                row_days = []
                for label, col in monitor_map.items():
                    if col in df.columns and pd.notna(row[col]):
                        d = (pd.to_datetime(row[col]).date() - today).days
                        row_days.append(d)
                        # 如果该单项证件进入预警期（<=30天），统计到分类数据中
                        if d <= y_limit: 
                            detail_stats[label] += 1
                
                # 判断该人员整体所属的状态颜色
                if not row_days:
                    green += 1
                else:
                    min_d = min(row_days)
                    if min_d < r_limit: red += 1
                    elif min_d <= y_limit: yellow += 1
                    else: green += 1
            
            # 顶部汇总展示
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("在职总人数", f"{len(df)} 人")
            c2.error(f"🔴 已过期: {red}")
            c3.warning(f"🟡 临期: {yellow}")
            c4.success(f"🟢 正常: {green}")
            
            # 异常证件类别分布
            if red + yellow > 0:
                st.write("📊 **具体证件预警分布（涵盖所有异常项）：**")
                # 分两行显示，每行3个类别
                m_cols1 = st.columns(3)
                m_cols1[0].write(f"护照预警: {detail_stats['护照']} 人")
                m_cols1[1].write(f"身份证预警: {detail_stats['身份证']} 人")
                m_cols1[2].write(f"签证预警: {detail_stats['签证']} 人")
                
                m_cols2 = st.columns(3)
                m_cols2[0].write(f"工作证预警: {detail_stats['工作证']} 人")
                m_cols2[1].write(f"居住证预警: {detail_stats['居住证']} 人")
                m_cols2[2].write(f"驾照预警: {detail_stats['驾照']} 人")
            st.divider()
            return df
        except: return None
    return None

st.title("人员证件管理")
df_person = show_person_detailed_dashboard()

# --- 4. 管理功能 ---
FILE_NAME = "人员证件清单.xlsx"
menu = st.tabs(["查看/编辑清单", "单条录入", "批量导入Excel"])

with menu[0]:
    if df_person is not None:
        st.dataframe(df_person, use_container_width=True)
    else: st.info("暂无人员数据，请先录入。")

with menu[1]:
    with st.form("add_person_form", clear_on_submit=True):
        st.write("**基本信息**")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("姓名")
        gender = c2.selectbox("性别", ["男", "女"])
        id_no = c3.text_input("身份证号")
        
        st.write("---")
        st.write("**核心证件**")
        c4, c5, c6 = st.columns(3)
        pass_no = c4.text_input("护照号")
        visa_no = c5.text_input("几内亚签证号")
        res_no = c6.text_input("居住证号")
        
        st.write("**其他证件**")
        c7, c8 = st.columns(2)
        work_no = c7.text_input("工作证号")
        lic_no = c8.text_input("驾照号")
        
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
        
        if st.form_submit_button("确认保存"):
            new_person = {
                "姓名": name, "性别": gender, "身份证号": id_no, "护照号": pass_no,
                "几内亚签证号": visa_no, "居住证号": res_no, "工作证号": work_no, "驾照号": lic_no,
                "护照有效期": date_p.strftime("%Y-%m-%d"), "身份证有效期": date_i.strftime("%Y-%m-%d"),
                "几内亚签证有效期": date_v.strftime("%Y-%m-%d"), "工作证有效期": date_w.strftime("%Y-%m-%d"),
                "居住证有效期": date_r.strftime("%Y-%m-%d"), "驾照有效期": date_l.strftime("%Y-%m-%d")
            }
            if os.path.exists(FILE_NAME):
                df = pd.concat([pd.read_excel(FILE_NAME), pd.DataFrame([new_person])], ignore_index=True)
            else:
                df = pd.DataFrame([new_person])
            df.to_excel(FILE_NAME, index=False)
            st.success(f"✅ {name} 的信息已成功保存！")
            st.rerun()

with menu[2]:
    upl = st.file_uploader("上传人员Excel文件", type="xlsx")
    if upl and st.button("确认导入数据"):
        pd.read_excel(upl).to_excel(FILE_NAME, index=False)
        st.success("人员清单导入成功！")
        st.rerun()