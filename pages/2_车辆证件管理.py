import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- 1. 页面配置 ---
st.set_page_config(page_title="车辆证件管理", layout="wide")

# --- 2. 核心统计函数 (用于顶部汇总) ---
def show_top_dashboard():
    TIMEZONE = pytz.timezone('Africa/Conakry')
    today = datetime.now(TIMEZONE).date()
    
    # 预警阈值（此处与主页逻辑保持一致）
    r_limit = 0  # 小于0天算红
    y_limit = 30 # 小于等于30天算黄
    
    FILE_NAME = "设备证件清单.xlsx"
    
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME)
            total = len(df)
            red, yellow, green = 0, 0, 0
            date_cols = ["灰卡有效期", "保险有效期", "车检有效期"]
            
            for _, row in df.iterrows():
                days_list = []
                for col in date_cols:
                    if col in df.columns and pd.notna(row[col]):
                        d = (pd.to_datetime(row[col]).date() - today).days
                        days_list.append(d)
                
                if not days_list:
                    green += 1
                    continue
                
                min_day = min(days_list)
                if min_day < r_limit: red += 1
                elif min_day <= y_limit: yellow += 1
                else: green += 1
            
            # 横向显示统计信息
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("在册总数", f"{total} 台")
            c2.error(f"🔴 已过期: {red}")
            c3.warning(f"🟡 临期: {yellow}")
            c4.success(f"🟢 正常: {green}")
            st.divider()
        except:
            st.error("读取统计数据失败，请检查Excel文件格式。")
    else:
        st.info("💡 暂无数据，请在下方录入第一条车辆信息。")

# --- 3. 业务逻辑开始 ---
st.title("🚜 车辆证件管理")

# 先显示顶部统计
show_top_dashboard()

# 数据文件定义
FILE_NAME = "设备证件清单.xlsx"

# 侧边栏：单条录入/管理功能（保持你原有的功能不变）
menu = st.tabs(["查看/编辑清单", "➕ 单条录入", "📥 批量导入Excel"])

# --- 选项卡1：查看与编辑 ---
with menu[0]:
    if os.path.exists(FILE_NAME):
        df_display = pd.read_excel(FILE_NAME)
        st.dataframe(df_display, use_container_width=True)
        
        if st.button("刷新数据"):
            st.rerun()
    else:
        st.write("暂无文件，请先录入数据。")

# --- 选项卡2：单条录入 ---
with menu[1]:
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            plate = st.text_input("车牌号/设备号")
            model = st.text_input("品牌型号")
        with col2:
            owner = st.text_input("所有人/责任人")
            cat = st.selectbox("类别", ["皮卡", "自卸车", "挖掘机", "其他"])
            
        st.write("--- 证件有效期设置 ---")
        c1, c2, c3 = st.columns(3)
        date1 = c1.date_input("灰卡有效期")
        date2 = c2.date_input("保险有效期")
        date3 = c3.date_input("车检有效期")
        
        submit = st.form_submit_button("保存到清单")
        
        if submit:
            new_data = {
                "车牌号": plate,
                "型号": model,
                "责任人": owner,
                "类别": cat,
                "灰卡有效期": date1.strftime("%Y-%m-%d"),
                "保险有效期": date2.strftime("%Y-%m-%d"),
                "车检有效期": date3.strftime("%Y-%m-%d"),
                "更新时间": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            if os.path.exists(FILE_NAME):
                old_df = pd.read_excel(FILE_NAME)
                df_final = pd.concat([old_df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df_final = pd.DataFrame([new_data])
            
            df_final.to_excel(FILE_NAME, index=False)
            st.success(f"✅ {plate} 录入成功！请刷新页面查看汇总。")
            st.rerun()

# --- 选项卡3：批量导入 ---
with menu[2]:
    uploaded_file = st.file_uploader("上传Excel文件 (需包含对应表头)", type="xlsx")
    if uploaded_file:
        if st.button("确认导入此文件"):
            df_upload = pd.read_excel(uploaded_file)
            df_upload.to_excel(FILE_NAME, index=False)
            st.success("🎉 批量数据导入成功！")
            st.rerun()