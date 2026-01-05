import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz
import io

# --- 基础配置 ---
TIMEZONE = pytz.timezone('Africa/Conakry')
DEVICE_FILE = "设备证件清单.xlsx"

# 证件字段定义
DEVICE_COLUMNS = [
    "设备名称", "车辆品牌", "设备型号", "车牌", "车架号", 
    "灰卡号", "灰卡有效期", "无抵押号", "无抵押有效期", 
    "保险号", "保险公司", "险种", "保险有效期", 
    "车检号", "车检有效期", "有色车窗号", "有色车窗有效期"
]
DATE_FIELDS = ["灰卡有效期", "无抵押有效期", "保险有效期", "车检有效期", "有色车窗有效期"]

st.set_page_config(page_title="鑫圆办公-车辆管理", layout="wide")

# --- 核心功能函数 ---
def load_data():
    if os.path.exists(DEVICE_FILE):
        df = pd.read_excel(DEVICE_FILE)
        # 确保列齐全
        for col in DEVICE_COLUMNS:
            if col not in df.columns: df[col] = None
        # 转换日期格式
        for col in DATE_FIELDS:
            df[col] = pd.to_datetime(df[col]).dt.date
        return df[DEVICE_COLUMNS]
    return pd.DataFrame(columns=DEVICE_COLUMNS)

def get_status(row):
    today = datetime.now(TIMEZONE).date()
    urgent_days = 9999
    msg = "⚪ 未录入"
    for field in DATE_FIELDS:
        expiry = row.get(field)
        if pd.notna(expiry):
            days = (expiry - today).days
            if days < urgent_days:
                urgent_days = days
                if days < 0: msg = f"🔴 过期{abs(days)}天({field})"
                elif days <= 30: msg = f"🟠 临期{days}天({field})"
                else: msg = f"🟢 正常{days}天({field})"
    return msg, urgent_days

# --- 界面开始 ---
st.title("🚜 车辆证件管理系统")

df = load_data()

# 选项卡：查看、录入、导入
tab_view, tab_add, tab_import = st.tabs(["📋 清单明细与编辑", "➕ 单条手动录入", "📥 批量导入 Excel"])

# --- Tab 1: 清单明细 ---
with tab_view:
    if not df.empty:
        # 计算状态
        status_data = df.apply(get_status, axis=1)
        display_df = df.copy()
        display_df.insert(0, "⏰ 预警状态", [s[0] for s in status_data])
        
        # 搜索框
        search = st.text_input("🔍 搜索车牌或设备名称")
        if search:
            display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search)).any(axis=1)]
        
        # 可编辑表格
        edited_df = st.data_editor(
            display_df, 
            use_container_width=True, 
            num_rows="dynamic",
            disabled=["⏰ 预警状态"]
        )
        
        if st.button("💾 保存表格所有修订"):
            # 只保存原始字段，不保存预警状态列
            final_save_df = edited_df[DEVICE_COLUMNS]
            final_save_df.to_excel(DEVICE_FILE, index=False)
            st.success("数据已成功保存至本地 Excel！")
            st.rerun()
    else:
        st.info("目前还没有车辆数据，请尝试手动录入或批量导入。")

# --- Tab 2: 手动录入 ---
with tab_add:
    st.subheader("填写车辆信息")
    with st.form("car_form"):
        col1, col2 = st.columns(2)
        form_data = {}
        for i, col in enumerate(DEVICE_COLUMNS):
            with (col1 if i % 2 == 0 else col2):
                if "有效期" in col:
                    form_data[col] = st.date_input(col, value=None)
                else:
                    form_data[col] = st.text_input(col)
        
        if st.form_submit_button("✅ 确认提交"):
            new_row = pd.DataFrame([form_data])
            combined_df = pd.concat([df, new_row], ignore_index=True)
            combined_df.to_excel(DEVICE_FILE, index=False)
            st.success("新车辆已添加！")
            st.rerun()

# --- Tab 3: 批量导入 ---
with tab_import:
    st.subheader("Excel 批量操作")
    
    # 1. 下载模板
    template_df = pd.DataFrame(columns=DEVICE_COLUMNS)
    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 下载标准导入模板",
        data=buffer.getvalue(),
        file_name="车辆导入模板.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    st.divider()
    
    # 2. 上传并合并
    uploaded_file = st.file_uploader("选择填写好的 Excel 文件", type=["xlsx"])
    if uploaded_file:
        up_df = pd.read_excel(uploaded_file)
        if all(c in up_df.columns for c in DEVICE_COLUMNS):
            st.success("格式校验通过！")
            if st.button("🚀 开始批量合并数据"):
                # 处理日期
                for col in DATE_FIELDS:
                    up_df[col] = pd.to_datetime(up_df[col]).dt.date
                # 合并去重
                final_df = pd.concat([df, up_df]).drop_duplicates(subset=["车牌", "车架号"], keep='last')
                final_df.to_excel(DEVICE_FILE, index=False)
                st.success(f"成功导入 {len(up_df)} 条数据！")
                st.rerun()
        else:
            st.error("上传的表格列名不符，请使用下载的模板。")