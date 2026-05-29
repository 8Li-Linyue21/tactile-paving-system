import streamlit as st
import json
import os
from datetime import datetime

# ====== 页面配置 ======
st.set_page_config(
    page_title="异常上报 · 盲道帮扶系统",
    page_icon="⚠️",
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

.form-label {
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.5rem;
}

.info-box {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-left: 4px solid #f59e0b;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
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

def save_markers():
    with open('abnormal_markers.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.markers, f, ensure_ascii=False, indent=2)

# ====== 侧边栏 ======
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h2 style="font-size: 1.3rem; font-weight: 700; color: #1e293b;">⚠️ 异常上报</h2>
        <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
            请填写以下表单，上报发现的盲道问题
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 异常类型说明")
    type_descriptions = {
        "盲道被占用": "共享单车、摊位、杂物等占用盲道",
        "盲道损坏": "地砖破损、翘起、下沉等",
        "盲道缺失": "本应有盲道的区域没有铺设",
        "障碍物阻挡": "电杆、树池等阻挡盲道",
        "其他问题": "其他影响视障人士通行的问题"
    }
    
    for ab_type, desc in type_descriptions.items():
        st.markdown(f"""
        <div style="margin-bottom: 0.75rem; padding: 0.5rem; background: #f8fafc; border-radius: 6px;">
            <b style="color: #3b82f6;">{ab_type}</b>
            <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #64748b;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ====== 主内容 ======
st.markdown("""
<div style="padding: 1.5rem 0;">
    <h1 class="main-title">⚠️ 盲道异常上报</h1>
    <p style="color: #64748b; font-size: 1.1rem;">发现盲道问题？在此处上报，我们会及时处理</p>
</div>
""", unsafe_allow_html=True)

# 提示信息
st.markdown("""
<div class="info-box">
    <b>💡 温馨提示</b><br>
    1. 请先在「盲道地图」页面找到问题位置并点击获取坐标<br>
    2. 准确描述问题有助于快速处理<br>
    3. 上报后可在「异常列表」查看处理进度
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

with st.form("report_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="form-label">异常类型 *</p>', unsafe_allow_html=True)
        ab_type = st.selectbox(
            "异常类型",
            ["盲道被占用", "盲道损坏", "盲道缺失", "障碍物阻挡", "其他问题"],
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<p class="form-label">上报人</p>', unsafe_allow_html=True)
        ab_reporter = st.text_input(
            "上报人姓名",
            placeholder="可填写昵称",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown('<p class="form-label">位置坐标 *</p>', unsafe_allow_html=True)
        lat = st.number_input("纬度", value=35.6850, format="%.6f", step=0.000001, label_visibility="collapsed")
        lon = st.number_input("经度", value=139.7300, format="%.6f", step=0.000001, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        severity = st.selectbox(
            "严重程度",
            ["轻微", "一般", "严重", "紧急"],
            help="评估问题的紧急程度"
        )
    
    with col3:
        st.markdown('<p class="form-label">详细描述 *</p>', unsafe_allow_html=True)
        ab_description = st.text_area(
            "详细描述",
            placeholder="请描述具体情况，例如：共享单车占用了整个人行道的盲道...",
            height=140,
            label_visibility="collapsed"
        )
        
        if st.session_state.get('clicked_location'):
            lat_clicked, lon_clicked = st.session_state.clicked_location
            if st.button("📍 使用地图点击的位置", use_container_width=True):
                st.session_state.temp_lat = lat_clicked
                st.session_state.temp_lon = lon_clicked
                st.rerun()
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        submitted = st.form_submit_button("🚀 提交上报", use_container_width=True)

if submitted:
    if not ab_description.strip():
        st.error("❌ 请填写详细描述")
    else:
        new_marker = {
            "lat": float(lat),
            "lon": float(lon),
            "type": ab_type,
            "description": ab_description,
            "reporter": ab_reporter if ab_reporter else "匿名志愿者",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "待处理",
            "severity": severity
        }
        
        st.session_state.markers.append(new_marker)
        save_markers()
        
        st.success("✅ 上报成功！")
        st.balloons()
        
        # 显示刚才上报的信息
        st.markdown("""
        <div style="background: #ecfdf5; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
            <h4 style="margin: 0 0 10px 0; color: #059669;">已提交的信息</h4>
            <p><b>类型：</b>{}</p>
            <p><b>位置：</b>({:.6f}, {:.6f})</p>
            <p><b>描述：</b>{}</p>
            <p><b>时间：</b>{}</p>
        </div>
        """.format(ab_type, lat, lon, ab_description, new_marker['time']), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 相关链接
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🔗 相关操作")

col_link1, col_link2, col_link3 = st.columns(3)
with col_link1:
    if st.button("🗺️ 返回地图", use_container_width=True):
        st.switch_page("app.py")

with col_link2:
    if st.button("📋 异常列表", use_container_width=True):
        st.switch_page("pages/2_异常列表.py")

with col_link3:
    if st.button("📊 数据统计", use_container_width=True):
        st.switch_page("pages/3_数据统计.py")

st.markdown('</div>', unsafe_allow_html=True)