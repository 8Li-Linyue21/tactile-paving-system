import streamlit as st
import json
import os
from collections import Counter
import pandas as pd

# ====== 页面配置 ======
st.set_page_config(
    page_title="数据统计 · 盲道帮扶系统",
    page_icon="📊",
    layout="wide"
)

# ====== 全局样式 ======
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
}

.big-stat {
    text-align: center;
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 16px;
    border: 1px solid #e2e8f0;
}

.big-stat-number {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.big-stat-label {
    font-size: 1rem;
    color: #64748b;
    margin-top: 0.5rem;
}

.progress-bar {
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 图表颜色 */
[data-testid="stHorizontalBlock"] [data-testid="element-container"] {
    background: white;
    border-radius: 12px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ====== 初始化 ======
if 'markers' not in st.session_state:
    if os.path.exists('abnormal_markers.json'):
        with open('abnormal_markers.json', 'r', encoding='utf-8') as f:
            st.session_state.markers = json.load(f)
    else:
        st.session_state.markers = []

# ====== 侧边栏 ======
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h2 style="font-size: 1.3rem; font-weight: 700; color: #1e293b;">📊 数据统计</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">
            系统运行数据概览
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快速跳转
    st.markdown("### 🔗 快速跳转")
    if st.button("🗺️ 盲道地图", use_container_width=True):
        st.switch_page("app.py")
    if st.button("⚠️ 异常上报", use_container_width=True):
        st.switch_page("pages/1_异常上报.py")
    if st.button("📋 异常列表", use_container_width=True):
        st.switch_page("pages/2_异常列表.py")
    
    st.markdown("---")
    
    # 数据说明
    st.markdown("""
    <div style="padding: 1rem; background: #eff6ff; border-radius: 10px; font-size: 0.85rem;">
        <b style="color: #1e40af;">📌 关于数据</b><br>
        <span style="color: #3b82f6;">盲道节点数</span> 和 <span style="color: #3b82f6;">盲道路径数</span> 
        数据来源于 OpenStreetMap 的 Tactile Paving 标签统计。
    </div>
    """, unsafe_allow_html=True)

# ====== 主内容 ======
st.markdown("""
<div style="padding: 1.5rem 0;">
    <h1 class="main-title">📊 数据统计</h1>
    <p style="color: #64748b; font-size: 1.1rem;">盲道系统运行数据概览</p>
</div>
""", unsafe_allow_html=True)

# 计算数据
total = len(st.session_state.markers)
pending = len([m for m in st.session_state.markers if m.get("status") == "待处理"])
resolved = total - pending
resolution_rate = (resolved / total * 100) if total > 0 else 0
type_counts = Counter([m['type'] for m in st.session_state.markers])

# 核心指标
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🎯 核心指标")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="big-stat">
        <div class="big-stat-number">{}</div>
        <div class="big-stat-label">总上报异常</div>
    </div>
    """.format(total), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="big-stat">
        <div class="big-stat-number" style="color: #f59e0b;">{}</div>
        <div class="big-stat-label">待处理</div>
    </div>
    """.format(pending), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="big-stat">
        <div class="big-stat-number" style="color: #22c55e;">{}</div>
        <div class="big-stat-label">已处理</div>
    </div>
    """.format(resolved), unsafe_allow_html=True)

with col4:
    rate_color = "#22c55e" if resolution_rate >= 70 else "#f59e0b" if resolution_rate >= 40 else "#ef4444"
    st.markdown("""
    <div class="big-stat">
        <div class="big-stat-number" style="color: {};">{:.1f}%</div>
        <div class="big-stat-label">处理率</div>
    </div>
    """.format(rate_color, resolution_rate), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 处理进度
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📈 处理进度")

col_progress1, col_progress2 = st.columns([3, 1])
with col_progress1:
    # 进度条
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #64748b;">处理进度</span>
            <span style="color: #475569;"><b>{}/{}</b></span>
        </div>
        <div class="progress-bar">
            <div style="width: {:.1f}%; height: 100%; background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%); border-radius: 4px;"></div>
        </div>
    </div>
    """.format(resolution_rate, resolved, total), unsafe_allow_html=True)

with col_progress2:
    resolution_color = "#22c55e" if resolution_rate >= 70 else "#f59e0b" if resolution_rate >= 40 else "#ef4444"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, {resolution_color}15 0%, {resolution_color}25 100%); border-radius: 12px;">
        <div style="font-size: 2rem; font-weight: 700; color: {resolution_color};">{resolution_rate:.0f}%</div>
        <div style="font-size: 0.85rem; color: #64748b;">处理率</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 异常类型分布
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🔍 异常类型分布")

if type_counts:
    # 类型数据
    df_types = pd.DataFrame([
        {"类型": k, "数量": v, "占比": f"{v/total*100:.1f}%"}
        for k, v in type_counts.most_common()
    ])
    
    col_chart, col_table = st.columns([2, 1])
    
    with col_chart:
        st.bar_chart(type_counts)
    
    with col_table:
        st.markdown("**类型详情**")
        for t, c in type_counts.most_common():
            pct = c / total * 100
            st.markdown(f"- **{t}**：{c} 条 ({pct:.1f}%)")
else:
    st.info("暂无异常数据")

st.markdown('</div>', unsafe_allow_html=True)

# 基础数据
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🗺️ 盲道基础数据")

col_base1, col_base2, col_base3, col_base4 = st.columns(4)

with col_base1:
    st.metric("📍 覆盖区域", "东京 (新宿-涩谷)")

with col_base2:
    st.metric("🧭 盲道节点数", "~3000 个")

with col_base3:
    st.metric("🛤️ 盲道路径数", "~1200 条")

with col_base4:
    st.metric("🔄 数据更新", "2026-05-29")

st.markdown('</div>', unsafe_allow_html=True)

# 底部操作
st.markdown("---")
col_bottom1, col_bottom2, col_bottom3 = st.columns(3)
with col_bottom1:
    if st.button("🗺️ 返回地图", use_container_width=True):
        st.switch_page("app.py")
with col_bottom2:
    if st.button("⚠️ 异常上报", use_container_width=True):
        st.switch_page("pages/1_异常上报.py")
with col_bottom3:
    if st.button("📋 异常列表", use_container_width=True):
        st.switch_page("pages/2_异常列表.py")