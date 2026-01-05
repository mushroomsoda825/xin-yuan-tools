import streamlit as st
from num2words import num2words

st.set_page_config(page_title="数字转换")

def to_chinese_upper(num):
    """转换数字为中文大写金额"""
    units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    digits = '零壹贰叁肆伍陆柒捌玖'
    try:
        s = str(int(num))[::-1]
        res = []
        for i, d in enumerate(s):
            if d != '0':
                res.append(units[i % 9])
                res.append(digits[int(d)])
            else:
                if not res or res[-1] != '零':
                    res.append('零')
        result = "".join(res[::-1]).rstrip('零')
        return result + "元整" if result else "零元整"
    except:
        return "转换出错"

st.title("数字转换助手")
num = st.number_input("输入数字", value=0, step=1)

if num > 0:
    st.divider()
    
    st.write("英语 (English):")
    st.code(num2words(num, lang='en').upper(), language='text')
    
    st.write("法语 (Français):")
    st.code(num2words(num, lang='fr').upper(), language='text')
    
    st.write("中文财务大写:")
    st.code(to_chinese_upper(num), language='text')