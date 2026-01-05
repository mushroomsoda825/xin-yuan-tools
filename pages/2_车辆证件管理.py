import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz
import io

# --- 基础配置 ---
VERSION = "v1.3.0"
DEVICE_FILE = "设备证件清单.xlsx"
TIMEZONE = pytz.timezone('Africa/Conakry')

st.set_page_config(page_title="设备管理协作系统", layout="wide")

# 标准字段定义
DEVICE_COLUMNS = [
    "设备名称", "车辆品牌", "设备型号", "车牌", "车架号", 
    "灰卡号", "灰卡有效期", "无抵押号", "无抵押有效期", 
    "保险号", "保险公司", "险种", "保险有效期", 
    "车检号", "车检有效期", "有色车窗号", "有色车窗有效期"
]
DATE_FIELDS = ["灰卡有效期", "无抵押有效期", "保险有效期", "车检有效期", "有色车窗有效期"]

# --- 功能函数 ---
def load_data():
    if os.path.exists(DEVICE_FILE):
        df = pd.read_excel(DEVICE_FILE)
        for col in DEVICE_COLUMNS:
            if col not in df.columns: df[col] = None
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

# --- 顶部状态栏 ---
now_gn = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**系统版本:** `{VERSION}` | **几内亚时间:** `{now_gn}` | **状态:** 🛰️ 局域网服务已启动")

st.title("🚜 设备证件协作管理系统")

# --- 3个独立统计窗口 ---
df = load_data()
if not df.empty:
    stats = df.apply(get_status, axis=1)
    expired = sum(1 for s in stats if s[1] < 0)
    warning = sum(1 for s in stats if 0 <= s[1] <= 30)
    safe = sum(1 for s in stats if 30 < s[1] < 9999)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 已过期", f"{expired} 台")
    c2.metric("🟠 30天内到期", f"{warning} 台")
    c3.metric("🟢 状态正常", f"{safe} 台")

# --- 功能选项卡 ---
tab_view, tab_add, tab_import = st.tabs(["📋 查看/编辑清单", "➕ 单条录入", "📥 批量导入Excel"])

with tab_view:
    if not df.empty:
        status_col = [s[0] for s in stats]
        display_df = df.copy()
        display_df.insert(0, "⏰ 预警状态", status_col)
        
        # 搜索
        search = st.text_input("搜索车牌/名称/品牌")
        if search:
            display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search)).any(axis=1)]
        
        edited_df = st.data_editor(display_df, use_container_width=True, num_rows="dynamic", disabled=["⏰ 预警状态"])
        
        if st.button("💾 保存表格修订"):
            save_df = edited_df[DEVICE_COLUMNS]
            save_df.to_excel(DEVICE_FILE, index=False)
            st.success("数据已同步！")
            st.rerun()
    else:
        st.info("暂无数据。")

with tab_add:
    with st.form("add_form", clear_on_submit=True):
        # ... (此处保留之前的录入表单代码，保持 DEVICE_COLUMNS 顺序即可)
        st.write("请在下方输入单条设备信息...")
        # 简化版示例，你可以把之前的录入逻辑放回这里
        new_data = [st.text_input(col) if "有效期" not in col else st.date_input(col, value=None) for col in DEVICE_COLUMNS]
        if st.form_submit_button("提交保存"):
            new_df = pd.DataFrame([new_data], columns=DEVICE_COLUMNS)
            pd.concat([df, new_df]).to_excel(DEVICE_FILE, index=False)
            st.rerun()

with tab_import:
    st.subheader("批量导入中心")
    st.write("1. 先下载模板 -> 2. 在 Excel 中填入 -> 3. 上传文件")
    
    # 下载模板
    template_df = pd.DataFrame(columns=DEVICE_COLUMNS)
    tmp_buffer = io.BytesIO()
    template_df.to_excel(tmp_buffer, index=False)
    st.download_button("📥 下载 Excel 导入模板", tmp_buffer.getvalue(), "导入模板.xlsx")
    
    # 上传文件
    uploaded_file = st.file_uploader("选择填好的 Excel 文件", type=["xlsx"])
    if uploaded_file:
        up_df = pd.read_excel(uploaded_file)
        # 检查列名是否正确
        if all(col in up_df.columns for col in DEVICE_COLUMNS):
            st.success("文件格式正确！")
            if st.button("🚀 确认合并到系统数据库"):
                # 统一日期格式后合并
                for col in DATE_FIELDS:
                    up_df[col] = pd.to_datetime(up_df[col]).dt.date
                combined_df = pd.concat([df, up_df], ignore_index=True).drop_duplicates()
                combined_df.to_excel(DEVICE_FILE, index=False)
                st.success(f"成功导入 {len(up_df)} 条数据！")
                st.rerun()
        else:
            st.error("文件列名不匹配，请使用下载的模板。")