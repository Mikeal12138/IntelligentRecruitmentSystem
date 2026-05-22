import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def plot_bar_chart(data, x, y, title):
    fig = px.bar(data, x=x, y=y, title=title)
    st.plotly_chart(fig)


def plot_line_chart(data, x, y, title):
    fig = px.line(data, x=x, y=y, title=title)
    st.plotly_chart(fig)


def plot_scatter_chart(data, x, y, title, color=None):
    fig = px.scatter(data, x=x, y=y, title=title, color=color)
    st.plotly_chart(fig)


def plot_pie_chart(data, names, values, title):
    fig = px.pie(data, names=names, values=values, title=title)
    st.plotly_chart(fig)
