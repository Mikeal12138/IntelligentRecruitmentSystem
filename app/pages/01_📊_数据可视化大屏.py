import streamlit as st
import pandas as pd


def main():
    st.title("📊 数据可视化大屏")
    
    st.header("薪资分析")
    st.write("薪资分布、行业薪资对比等分析内容。")
    
    st.header("企业分布")
    st.write("企业地域分布、行业分布等分析内容。")
    
    st.header("融资阶段分析")
    st.write("不同融资阶段的企业特征分析。")


if __name__ == "__main__":
    main()
