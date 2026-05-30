import streamlit as st
import folium
from folium.plugins import MiniMap, MousePosition
from streamlit_folium import st_folium
import requests
import json
import os

# ====== 页面全局配置 ======
st.set_page_config(
    page_title="盲道帮扶系统 · 志愿者端",
    page_icon="🦯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====== 全局样式 ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');

.stApp { background: #f0f4f8; font-family: 'Noto Sans SC', sans-serif; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 引入界面 */
.landing-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
.landing-icon { font-size: 5rem; margin-bottom: 1rem; }
.landing-title { font-size: 2.8rem; font-weight: 800; color: #1a2332; margin-bottom: 0.75rem; }
.landing-desc { font-size: 1.1rem; color: #5a6a7a; line-height: 1.9; max-width: 500px; text-align: center; margin-bottom: 2rem; }
.landing-stats { display: flex; gap: 2.5rem; margin-bottom: 2.5rem; }
.landing-stat-num { font-size: 1.8rem; font-weight: 800; color: #3b82f6; }
.landing-stat-label { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }
.enter-btn { background: #3b82f6; color: white; padding: 0.9rem 3rem; font-size: 1.1rem; font-weight: 700; border-radius: 50px; border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(59,130,246,0.35); transition: all 0.3s; letter-spacing: 0.05em; width: 100%; max-width: 320px; }
.enter-btn:hover { background: #2563eb; box-shadow: 0 6px 25px rgba(59,130,246,0.45); transform: translateY(-2px); }

/* 顶部导航栏 */
.top-bar { display: flex; align-items: center; justify-content: space-between; background: white; padding: 0.6rem 1.5rem; border-bottom: 1px solid #e5e9ef; }
.top-logo { font-size: 1.2rem; font-weight: 700; color: #1a2332; }
.top-logo span { color: #3b82f6; }
.top-nav-btn { padding: 0.45rem 1.1rem; border-radius: 20px; border: none; font-size: 0.88rem; font-weight: 600; cursor: pointer; background: transparent; color: #64748b; transition: all 0.25s; }
.top-nav-btn:hover { background: #f1f5f9; color: #3b82f6; }
.top-nav-btn.active { background: #3b82f6; color: white; }

/* 工具栏 */
.stats-bar { display: flex; background: white; border-bottom: 1px solid #e5e9ef; }
.stat-item { flex: 1; text-align: center; padding: 0.6rem; border-right: 1px solid #e5e9ef; }
.stat-item:last-child { border-right: none; }
.stat-item .num { font-size: 1.4rem; font-weight: 800; color: #1a2332; }
.stat-item .lbl { font-size: 0.7rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

/* 图例 */
.legend-panel { background: white; border-left: 1px solid #e5e9ef; padding: 1.25rem; height: 100%; }
.legend-title { font-size: 0.9rem; font-weight: 700; color: #1a2332; margin-bottom: 1rem; }
.legend-row { display: flex; align-items: center; margin-bottom: 0.7rem; font-size: 0.85rem; color: #3d4a5c; }
.legend-line { width: 28px; height: 3px; border-radius: 2px; margin-right: 10px; flex-shrink: 0; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 10px; flex-shrink: 0; }

/* 位置信息 */
.loc-panel { background: white; padding: 1rem 1.25rem; border-top: 1px solid #e5e9ef; margin-top: 0; }
.loc-label { font-size: 0.85rem; font-weight: 700; color: #1a2332; margin-bottom: 0.75rem; }
.loc-coord { font-size: 0.82rem; color: #3d4a5c; margin-bottom: 0.4rem; }
.loc-address { background: #f8fafc; border-radius: 8px; padding: 0.6rem; font-size: 0.8rem; color: #64748b; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ====== 会话状态 ======
if 'entered' not in st.session_state:
    st.session_state.entered = False

if 'markers' not in st.session_state:
    if os.path.exists('abnormal_markers.json'):
        with open('abnormal_markers.json', 'r', encoding='utf-8') as f:
            st.session_state.markers = json.load(f)
    else:
        st.session_state.markers = []

if 'tactile_data' not in st.session_state:
    st.session_state.tactile_data = None

# ====== 常量 ======
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

CITY_CONFIGS = {
    "东京 (新宿-涩谷)": {
        "center": [35.6850, 139.7300], "zoom": 14,
        "bbox": {"south": 35.6500, "west": 139.6800, "north": 35.7200, "east": 139.7800},
        "label": "东京"
    },
    "首尔 (江南-明洞)": {
        "center": [37.5650, 126.9750], "zoom": 14,
        "bbox": {"south": 37.5400, "west": 126.9400, "north": 37.5900, "east": 127.0100},
        "label": "首尔"
    },
}

PAVING_COLORS = {
    "yes": "#10b981", "contrasted": "#3b82f6", "partial": "#f59e0b",
    "primitive": "#8b5cf6", "incorrect": "#ef4444", "no": "#94a3b8",
}
PAVING_LABELS = {
    "yes": "标准盲道", "contrasted": "高对比度盲道", "partial": "部分盲道",
    "primitive": "简易盲道", "incorrect": "错误盲道", "no": "无盲道",
}
HIGHWAY_LABELS = {
    "footway": "人行道", "crossing": "人行横道", "steps": "楼梯",
    "bus_stop": "公交站", "elevator": "电梯", "platform": "站台", "path": "小径",
}

# ====== 辅助函数 ======
def fetch_tactile_paving(bbox: dict, area_name: str = "") -> dict:
    query = f"""
    [out:json][timeout:90];
    (
        node["tactile_paving"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        way["tactile_paving"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
    );
    out body; >; out skel qt;
    """
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        elements = data.get("elements", [])
        return {
            "elements": elements,
            "node_count": sum(1 for e in elements if e["type"] == "node"),
            "way_count": sum(1 for e in elements if e["type"] == "way")
        }
    except:
        return {"elements": [], "node_count": 0, "way_count": 0}

def get_highway_name(tags: dict) -> str:
    return HIGHWAY_LABELS.get(tags.get("highway", ""), tags.get("highway", ""))

def get_address_from_coords(lat, lon):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "accept-language": "zh"},
            headers={"User-Agent": "BlindPathFinder/1.0"}, timeout=5
        )
        if resp.status_code == 200:
            return resp.json().get("display_name", "未知地址")
    except:
        pass
    return "地址解析失败"

def add_tactile_layer(m: folium.Map, elements: list):
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in elements if e["type"] == "node"}
    group = folium.FeatureGroup(name="盲道路径")
    for e in elements:
        if e["type"] != "way":
            continue
        tags = e.get("tags", {})
        paving = tags.get("tactile_paving", "unknown")
        coords = [(nodes[n][0], nodes[n][1]) for n in e["nodes"] if n in nodes]
        if len(coords) < 2:
            continue
        hw = get_highway_name(tags)
        color = PAVING_COLORS.get(paving, "#06b6d4")
        label = PAVING_LABELS.get(paving, "未知")
        folium.PolyLine(
            coords, color=color, weight=3.5, opacity=0.85,
            popup=folium.Popup(f"<b>{hw}</b><br>盲道状态：{label}<br>OSM ID：{e['id']}", max_width=200),
            tooltip=f"{hw} - {label}"
        ).add_to(group)
    group.add_to(m)

# ====== 引入界面 ======
if not st.session_state.entered:
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        st.markdown('<div class="landing-icon">🦯</div>', unsafe_allow_html=True)
        st.markdown('<div class="landing-title">盲道帮扶系统</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="landing-desc">每一位视障人士都值得被温柔以待。<br>加入我们，用行动点亮城市的无障碍之路。</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            '<div class="landing-stats">'
            '<div style="text-align:center;"><div class="landing-stat-num">3000+</div><div class="landing-stat-label">盲道节点</div></div>'
            '<div style="text-align:center;"><div class="landing-stat-num">1200+</div><div class="landing-stat-label">盲道路径</div></div>'
            '<div style="text-align:center;"><div class="landing-stat-num">实时</div><div class="landing-stat-label">数据更新</div></div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # 这个按钮点击后会 rerun，然后 entered 变 True
        if st.button("🚀  进入志愿者系统", type="primary", use_container_width=False):
            st.session_state.entered = True
            st.rerun()
    
    st.stop()

# ====== 主系统界面 ======

# 顶部导航栏
c_logo, c_nav, c_act = st.columns([2, 3, 2])
with c_logo:
    st.markdown('<div class="top-logo">🦯 盲道帮扶 · <span>志愿者端</span></div>', unsafe_allow_html=True)

with c_nav:
    cols_nav = st.columns(3)
    with cols_nav[0]:
        st.button("🗺️ 实时监测", use_container_width=True, type="primary")
    with cols_nav[1]:
        if st.button("📋 异常列表", use_container_width=True):
            st.switch_page("pages/2_异常列表.py")
    with cols_nav[2]:
        if st.button("📊 数据统计", use_container_width=True):
            st.switch_page("pages/3_数据统计.py")

with c_act:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("📝 上报", use_container_width=True):
            st.switch_page("pages/1_异常上报.py")
    with col_a2:
        if st.button("🔄 刷新", use_container_width=True):
            st.session_state.tactile_data = None
            st.rerun()

# 城市选择工具栏
tool_col1, tool_col2, tool_col3, tool_col4 = st.columns([1.5, 1, 1, 3])
with tool_col1:
    selected_city = st.selectbox("📍 监测区域", options=list(CITY_CONFIGS.keys()), index=0, label_visibility="collapsed")
with tool_col2:
    if st.button("🔄 刷新数据", use_container_width=True):
        st.session_state.tactile_data = None
        st.rerun()
with tool_col3:
    if st.button("📝 上报异常", use_container_width=True):
        st.switch_page("pages/1_异常上报.py")
with tool_col4:
    st.caption("💡 点击地图查看经纬度，点击盲道路径查看详情")

# 获取盲道数据
city_cfg = CITY_CONFIGS[selected_city]
if st.session_state.tactile_data is None:
    with st.spinner(f"📥 正在加载 {city_cfg['label']} 盲道数据，请稍候..."):
        result = fetch_tactile_paving(city_cfg["bbox"], city_cfg["label"])
        st.session_state.tactile_data = result
        st.session_state.tactile_stats = {
            "nodes": result.get("node_count", 0),
            "ways": result.get("way_count", 0)
        }
else:
    result = st.session_state.tactile_data

elements = result.get("elements", [])
node_count = st.session_state.tactile_stats.get("nodes", 0)
way_count = st.session_state.tactile_stats.get("ways", 0)
pending = len([m for m in st.session_state.markers if m.get("status") == "待处理"])
resolved = len([m for m in st.session_state.markers if m.get("status") == "已处理"])

# 统计条
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item"><div class="num" style="color:#3b82f6;">{node_count}</div><div class="lbl">盲道节点</div></div>
    <div class="stat-item"><div class="num" style="color:#10b981;">{way_count}</div><div class="lbl">盲道路径</div></div>
    <div class="stat-item"><div class="num" style="color:#ef4444;">{pending}</div><div class="lbl">待处理异常</div></div>
    <div class="stat-item"><div class="num" style="color:#10b981;">{resolved}</div><div class="lbl">已处理</div></div>
    <div class="stat-item"><div class="num" style="color:#64748b;">{city_cfg['label']}</div><div class="lbl">当前区域</div></div>
</div>
""", unsafe_allow_html=True)

# 地图 + 右侧信息面板
map_col, info_col = st.columns([5, 1])

with map_col:
    m = folium.Map(location=city_cfg["center"], zoom_start=city_cfg["zoom"], tiles=None)
    
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; OpenStreetMap &copy; CARTO', name='CartoDB 清晰版'
    ).add_to(m)
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; OpenStreetMap', name='OpenStreetMap'
    ).add_to(m)
    
    MousePosition(position="bottomleft", separator=" | ", prefix="坐标: ", num_digits=6).add_to(m)
    MiniMap(toggle_display=True, position="bottomright").add_to(m)
    add_tactile_layer(m, elements)
    
    ab_group = folium.FeatureGroup(name="⚠️ 上报异常")
    for marker in st.session_state.markers:
        folium.Marker(
            location=[marker['lat'], marker['lon']],
            popup=folium.Popup(f"⚠️ {marker['type']}<br>{marker['description']}<br>状态：{marker['status']}", max_width=200),
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(ab_group)
    ab_group.add_to(m)
    
    folium.LayerControl(collapsed=True).add_to(m)
    map_data = st_folium(m, width="100%", height=620, returned_objects=["last_clicked"])

with info_col:
    # 图例
    st.markdown('<div class="legend-panel">', unsafe_allow_html=True)
    st.markdown('<div class="legend-title">🎨 盲道图例</div>', unsafe_allow_html=True)
    for key, color in PAVING_COLORS.items():
        label = PAVING_LABELS.get(key, key)
        st.markdown(f'<div class="legend-row"><div class="legend-line" style="background:{color};"></div>{label}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e5e9ef;margin:0.75rem 0;">', unsafe_allow_html=True)
    st.markdown('<div class="legend-row"><div class="legend-dot" style="background:#ef4444;"></div>⚠️ 上报异常</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 位置信息
    st.markdown('<div class="loc-panel">', unsafe_allow_html=True)
    st.markdown('<div class="loc-label">📍 位置信息</div>', unsafe_allow_html=True)
    
    if map_data and map_data.get("last_clicked"):
        clicked = map_data["last_clicked"]
        if clicked.get("lat") and clicked.get("lng"):
            lat, lon = clicked["lat"], clicked["lng"]
            st.markdown(f'<div class="loc-coord"><b>经度：</b>{lon:.6f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="loc-coord"><b>纬度：</b>{lat:.6f}</div>', unsafe_allow_html=True)
            with st.spinner("获取地址..."):
                address = get_address_from_coords(lat, lon)
            st.markdown(f'<div class="loc-address">{address[:60]}</div>', unsafe_allow_html=True)
            if st.button("📍 上报该位置", use_container_width=True):
                st.switch_page("pages/1_异常上报.py")
    else:
        st.markdown('<div class="loc-address">点击地图任意位置查看坐标和地址</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("🗺️ 盲道数据来源：OpenStreetMap (tactile_paving) | 地理编码：Nominatim | 志愿者端 v1.0")