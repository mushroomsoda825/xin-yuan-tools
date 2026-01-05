import streamlit as st
from num2words import num2words

st.set_page_config(page_title="鑫圆办公-数字转换")
st.title("🔢 数字多语言转换助手")

num = st.number_input("请输入想要转换的数字/金额", value=0)

if num:
    st.write("### 转换结果 (点击右上角图标即可复制)")
    
    # 英语
    st.write("**🇺🇸 英语读法 (English):**")
    st.code(num2words(num, lang='en').upper(), language='text')
    
    # 法语
    st.write("**🇫🇷 法语读法 (Français):**")
    st.code(num2words(num, lang='fr').upper(), language='text')
    
    # 中文示例
    st.write("**🇨🇳 中文备注:**")
    st.code(f"人民币金额：{num} 元整", language='text')