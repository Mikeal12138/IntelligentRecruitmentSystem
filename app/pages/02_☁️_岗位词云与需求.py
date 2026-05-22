import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def main():
    st.title("☁️ 岗位词云与需求")
    
    st.header("技能词云")
    st.write("基于岗位描述提取的技能关键词云。")
    
    st.header("福利分布")
    st.write("企业福利标签统计分析。")
    
    st.header("学历要求分布")
    st.write("不同学历要求的岗位占比。")


if __name__ == "__main__":
    main()
