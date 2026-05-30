import streamlit as st
import json
import os

# ====== 页面配置 ======
st.set_page_config(
    page_title="异常列表 · 盲道帮扶系统",
    page_icon="📋",
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

.status-badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.status-pending {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    color: #b45309;
}

.status-resolved {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #047857;
}

.ab-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border-left: 4px solid;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.ab-type-占用 { border-color: #f59e0b; }
.ab-type-损坏 { border-color: #ef4444; }
.ab-type-缺失 { border-color: #6366f1; }
.ab-type-阻挡 { border-color: #8b5cf6; }
.ab-type-其他 { border-color: #64748b; }

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

def get_card_class(ab_type):
    if "占用" in ab_type: return "ab-type-占用"
    if "损坏" in ab_type: return "ab-type-损坏"
    if "缺失" in ab_type: return "ab-type-缺失"
    if "阻挡" in ab_type: return "ab-type-阻挡"
    return "ab-type-其他"

# ====== 侧边栏 ======
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h2 style="font-size: 1.3rem; font-weight: 700; color: #1e293b;">📋 异常列表</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 统计
    total = len(st.session_state.markers)
    pending = len([m for m in st.session_state.markers if m.get("status") == "待处理"])
    resolved = total - pending
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.75rem 0; color: #64748b; font-size: 0.9rem;">📊 统计概览</h4>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>总计：</span><b style="color: #3b82f6;">{total}</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>待处理：</span><b style="color: #f59e0b;">{pending}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>已处理：</span><b style="color: #22c55e;">{resolved}</b>
        </div>
    </div>
    """.format(total=total, pending=pending, resolved=resolved), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 筛选
    st.markdown("### 🔍 筛选")
    filter_status = st.selectbox(
        "处理状态",
        ["全部", "待处理", "已处理"],
        label_visibility="collapsed"
    )
    
    if st.button("📝 新增上报", use_container_width=True):
        st.switch_page("pages/1_异常上报.py")

# ====== 主内容 ======
st.markdown("""
<div style="padding: 1.5rem 0;">
    <h1 class="main-title">📋 异常列表</h1>
    <p style="color: #64748b; font-size: 1.1rem;">
        共发现 <b style="color: #3b82f6;">{total}</b> 个盲道异常，已处理 <b style="color: #22c55e;">{resolved}</b> 个
    </p>
</div>
""".format(total=len(st.session_state.markers), resolved=len([m for m in st.session_state.markers if m.get("status") == "已处理"])), unsafe_allow_html=True)

# 筛选逻辑
display_markers = st.session_state.markers.copy()
if filter_status != "全部":
    display_markers = [m for m in display_markers if m.get("status") == filter_status]

# 空状态
if not display_markers:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: white; border-radius: 16px;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
        <h3 style="color: #64748b; margin-bottom: 0.5rem;">暂无异常记录</h3>
        <p style="color: #94a3b8;">暂时没有找到{filter_status}的异常记录</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # 显示异常列表
    for i, marker in enumerate(reversed(display_markers)):
        card_class = get_card_class(marker['type'])
        status_class = "status-pending" if marker.get('status') == "待处理" else "status-resolved"
        status_text = marker.get('status', '待处理')
        severity = marker.get('severity', '一般')
        
        # 严重程度颜色
        severity_colors = {
            "轻微": "#22c55e",
            "一般": "#3b82f6",
            "严重": "#f59e0b",
            "紧急": "#ef4444"
        }
        severity_color = severity_colors.get(severity, "#3b82f6")
        
        st.markdown(f'<div class="card {card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            col_header = st.columns([4, 1])
            with col_header[0]:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">⚠️</span>
                    <div>
                        <h3 style="margin: 0; color: #1e293b;">{marker['type']}</h3>
                        <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #64748b;">
                            👤 {marker['reporter']} · ⏰ {marker['time']}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_header[1]:
                st.markdown(f"""
                <div style="text-align: right;">
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"""
            <div style="margin-bottom: 0.75rem;">
                <b style="color: #475569;">📝 描述：</b>
                <span style="color: #64748b;">{marker['description']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #64748b;">
                <span>📍 <b style="color: #475569;">位置：</b>({marker['lat']:.4f}, {marker['lon']:.4f})</span>
                <span>🔶 <b style="color: #475569;">严重程度：</b><span style="color: {severity_color};">{severity}</span></span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if marker.get('status') == "待处理":
                if st.button("✓ 已处理", key=f"resolve_{i}", use_container_width=True):
                    # 找到原始索引
                    original_idx = len(st.session_state.markers) - 1 - i
                    st.session_state.markers[original_idx]['status'] = "已处理"
                    save_markers()
                    st.success("✅ 已标记为处理")
                    st.rerun()
        
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🗺️ 定位", key=f"goto_{i}", use_container_width=True):
                st.session_state.goto_location = (marker['lat'], marker['lon'])
                st.switch_page("app.py")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 底部操作
st.markdown("---")
col_bottom1, col_bottom2, col_bottom3 = st.columns(3)
with col_bottom1:
    if st.button("🗺️ 返回地图", use_container_width=True):
        st.switch_page("app.py")
with col_bottom2:
    if st.button("📝 新增上报", use_container_width=True):
        st.switch_page("pages/1_异常上报.py")
with col_bottom3:
    if st.button("📊 数据统计", use_container_width=True):
        st.switch_page("pages/3_数据统计.py")