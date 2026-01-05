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
def show_detailed_dashboard():
    TIMEZONE = pytz.timezone('Africa/Conakry')
    today = datetime.now(TIMEZONE).date()
    r_limit, y_limit = 0, 30 
    FILE_NAME = "设备证件清单.xlsx"
    
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME)
            red, yellow, green = 0, 0, 0
            # 定义需要监控的四个有效期类别
            monitor_cols = {
                "灰卡": "灰卡有效日期",
                "无抵押": "无抵押证明有效日期",
                "保险": "保险有效期",
                "车检": "车检有效期"
            }
            detail_stats = {k: 0 for k in monitor_cols.keys()}
            
            for _, row in df.iterrows():
                row_days = []
                for label, col in monitor_cols.items():
                    if col in df.columns and pd.notna(row[col]):
                        d = (pd.to_datetime(row[col]).date() - today).days
                        row_days.append(d)
                        if d <= y_limit: detail_stats[label] += 1
                
                if not row_days: green += 1
                else:
                    min_d = min(row_days)
                    if min_d < r_limit: red += 1
                    elif min_d <= y_limit: yellow += 1
                    else: green += 1
            
            # 顶部总览
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("在册设备总数", f"{len(df)} 台")
            c2.error(f"🔴 已过期: {red}")
            c3.warning(f"🟡 临期: {yellow}")
            c4.success(f"🟢 正常: {green}")
            
            # 具体类别预警明细
            if red + yellow > 0:
                st.write("📊 **异常证件类别分布：**")
                cols = st.columns(4)
                cols[0].write(f"灰卡预警: {detail_stats['灰卡']}")
                cols[1].write(f"无抵押预警: {detail_stats['无抵押']}")
                cols[2].write(f"保险预警: {detail_stats['保险']}")
                cols[3].write(f"车检预警: {detail_stats['车检']}")
            st.divider()
            return df
        except: return None
    return None

st.title("车辆证件管理")
df_main = show_detailed_dashboard()

# --- 4. 管理功能 ---
FILE_NAME = "设备证件清单.xlsx"
menu = st.tabs(["查看/编辑清单", "单条录入", "批量导入Excel"])

with menu[0]:
    if df_main is not None:
        st.dataframe(df_main, use_container_width=True)
    else: st.info("暂无数据，请先录入。")

with menu[1]:
    with st.form("add_car_form", clear_on_submit=True):
        st.write("**基本信息**")
        c1, c2, c3 = st.columns(3)
        idx = c1.text_input("序号")
        name = c2.text_input("设备名称")
        model = c3.text_input("设备型号")
        
        c4, c5 = st.columns(2)
        plate = c4.text_input("车牌")
        vin = c5.text_input("车架号")
        
        st.write("---")
        st.write("**证件详情**")
        d1, d2 = st.columns(2)
        gray_no = d1.text_input("灰卡证件号")
        gray_date = d2.date_input("灰卡有效日期")
        
        d3, d4 = st.columns(2)
        mort_no = d3.text_input("无抵押证明号")
        mort_date = d4.date_input("无抵押证明有效日期")
        
        st.write("**保险信息**")
        i1, i2, i3, i4 = st.columns(4)
        ins_no = i1.text_input("保险号")
        ins_comp = i2.text_input("保险公司名称")
        ins_type = i3.selectbox("保险类型", ["第三方责任险", "全险", "其他"])
        ins_date = i4.date_input("保险有效期")
        
        st.write("**车检信息**")
        t1, t2 = st.columns(2)
        test_no = t1.text_input("车检号")
        test_date = t2.date_input("车检有效期")
        
        if st.form_submit_button("保存设备信息"):
            new_row = {
                "序号": idx, "设备名称": name, "设备型号": model, "车牌": plate, "车架号": vin,
                "灰卡证件号": gray_no, "灰卡有效日期": gray_date.strftime("%Y-%m-%d"),
                "无抵押证明号": mort_no, "无抵押证明有效日期": mort_date.strftime("%Y-%m-%d"),
                "保险号": ins_no, "保险公司名称": ins_comp, "保险类型": ins_type,
                "保险有效期": ins_date.strftime("%Y-%m-%d"),
                "车检号": test_no, "车检有效期": test_date.strftime("%Y-%m-%d")
            }
            if os.path.exists(FILE_NAME):
                df = pd.concat([pd.read_excel(FILE_NAME), pd.DataFrame([new_row])], ignore_index=True)
            else:
                df = pd.DataFrame([new_row])
            df.to_excel(FILE_NAME, index=False)
            st.success("✅ 设备信息录入成功！")
            st.rerun()

with menu[2]:
    upl = st.file_uploader("上传车辆Excel文件", type="xlsx")
    if upl and st.button("确认导入"):
        pd.read_excel(upl).to_excel(FILE_NAME, index=False)
        st.success("数据导入成功！")
        st.rerun()