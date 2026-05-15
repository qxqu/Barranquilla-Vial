"""
Red Vial de Barranquilla — Grafos
Matemáticas Discretas 202610
Mapa real (pydeck) + interfaz moderna
"""

import streamlit as st
import pydeck as pdk
import pandas as pd

st.set_page_config(
    page_title="Red Vial — Barranquilla",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Coordenadas GPS reales [lon, lat] ────────────────────────────────────────
COORDS = [
    [-74.8082, 10.9235],   # 0  Terminal de Transporte  (sur, junto a autopista Circunvalar)
    [-74.7936, 10.9639],   # 1  Centro (Bolívar)         (centro histórico Barranquilla)
    [-74.8000, 10.9820],   # 2  El Prado                 (norte, barrio El Prado)
    [-74.8050, 10.9720],   # 3  Metroplus Norte           (centro-norte, corredor metrópolis)
    [-74.7840, 10.9870],   # 4  Villa Country             (norte, entre El Prado y Buenavista)
    [-74.7720, 10.9900],   # 5  Buenavista CC             (noreste, centro comercial)
    [-74.8100, 10.9330],   # 6  Estadio Metropolitano     (sur-occidente, estadio)
    [-74.8010, 10.9800],   # 7  Uninorte                  (norte, campus universitario)
    [-74.8530, 10.9870],   # 8  Puerto Colombia           (noroeste, municipio costero)
    [-74.7660, 10.9180],   # 9  Soledad                   (sur-este, municipio Soledad)
    [-74.7340, 10.9310],   # 10 Malambo                   (este, municipio Malambo)
    [-74.8230, 10.9490],   # 11 Las Américas              (occidente, av. Las Américas)
    [-74.7900, 10.9740],   # 12 Boston                    (norte-centro, barrio Boston)
    [-74.7780, 10.9960],   # 13 Riomar                    (norte, barrio Riomar)
    [-74.7940, 10.9610],   # 14 Barranquillita            (centro, puerto Barranquillita)
]

NOMBRES = [
    "Terminal", "Centro (Bolívar)", "El Prado",
    "Metroplus Norte", "Villa Country", "Buenavista CC",
    "Estadio Metro.", "Uninorte", "Puerto Colombia",
    "Soledad", "Malambo", "Las Américas",
    "Boston", "Riomar", "Barranquillita"
]

ARISTAS = [
    (0,1,12),(0,9,8),(0,14,10),
    (1,2,10),(1,12,6),(1,14,5),
    (2,3,7),(2,4,9),(2,12,8),
    (3,4,6),(3,5,11),
    (4,5,8),(4,6,12),(4,13,10),
    (5,7,9),(5,13,7),
    (6,11,14),
    (7,8,20),(7,13,6),
    (8,13,22),
    (9,10,15),(9,11,18),
    (11,12,9),
    (12,14,4)
]

N = 15

# ── Session state ────────────────────────────────────────────────────────────
def init_state():
    defaults = dict(origen=-1, destino=-1, camino=[], tiempo=-1,
                    algo="Dijkstra", matriz=[], ver_matriz=False,
                    _last_click=None)
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Algoritmos ───────────────────────────────────────────────────────────────
def dijkstra(o, d):
    INF = float("inf")
    dist = [INF]*N; dist[o] = 0
    prev = [-1]*N; vis = [False]*N
    for _ in range(N):
        u = -1
        for i in range(N):
            if not vis[i] and (u==-1 or dist[i]<dist[u]): u=i
        if u==-1 or dist[u]==INF: break
        vis[u]=True
        for a,b,w in ARISTAS:
            v,cw=-1,-1
            if a==u: v,cw=b,w
            if b==u: v,cw=a,w
            if v!=-1 and dist[u]+cw<dist[v]: dist[v]=dist[u]+cw; prev[v]=u
    if dist[d]==INF: return [],-1
    path,cur=[],d
    while cur!=-1: path.insert(0,cur); cur=prev[cur]
    return path,dist[d]

def floyd():
    INF=999999
    d=[[0 if i==j else INF for j in range(N)] for i in range(N)]
    nxt=[[-1]*N for _ in range(N)]
    for a,b,w in ARISTAS:
        if w<d[a][b]: d[a][b]=d[b][a]=w; nxt[a][b]=b; nxt[b][a]=a
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if d[i][k]+d[k][j]<d[i][j]:
                    d[i][j]=d[i][k]+d[k][j]; nxt[i][j]=nxt[i][k]
    return d,nxt

def floyd_path(o,d,nxt):
    path,cur=[],o
    while cur!=d and cur!=-1 and len(path)<=N:
        path.append(cur); cur=nxt[cur][d]
    if cur==d: path.append(d)
    return path

def calcular():
    o,d=st.session_state.origen,st.session_state.destino
    if o<0 or d<0: return
    if st.session_state.algo=="Floyd-Warshall":
        dm,nxt=floyd(); st.session_state.matriz=dm
        st.session_state.camino=floyd_path(o,d,nxt)
        st.session_state.tiempo=dm[o][d] if dm[o][d]<999999 else -1
    else:
        path,t=dijkstra(o,d)
        st.session_state.camino=path; st.session_state.tiempo=t
    st.session_state.ver_matriz=False

def arista_en_ruta(u,v):
    c=st.session_state.camino
    for i in range(len(c)-1):
        if (c[i]==u and c[i+1]==v) or (c[i]==v and c[i+1]==u): return True
    return False

# ── CSS global ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --surface:#f5f3ef; --surface2:#ece9e3;
  --border:#dedad3; --border2:#c8c3ba;
  --text:#111111; --muted:#888888; --light:#aaaaaa;
  --accent:#111111;
  --green:#22c55e;
  --amber:#f59e0b;
  --red:#ef4444;
  --bone:#f5f3ef;
}

#MainMenu, header, footer { visibility: hidden; }

/* ── Force bone background on ALL Streamlit root elements ── */
body,
html,
[data-testid="stApp"],
section[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
.appview-container,
.main,
.block-container {
  background: #f5f3ef !important;
  background-color: #f5f3ef !important;
}

.block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
section[data-testid="stAppViewContainer"] { padding:0 !important; height:100vh !important; overflow:hidden !important; }
.main { padding:0 !important; height:100vh !important; overflow:hidden !important; }
div[data-testid="stHorizontalBlock"] { gap:0 !important; height:100vh !important; align-items:stretch !important; }
div[data-testid="column"] { padding:0 !important; }
div[data-testid="column"]:first-child {
  height:100vh !important; overflow-y:auto; overflow-x:hidden;
  background:var(--surface); border-right:1px solid var(--border);
}
div[data-testid="column"]:last-child {
  height:100vh !important; overflow:hidden; flex:1 !important;
  background:#f5f3ef !important; background-color:#f5f3ef !important;
}
div[data-testid="column"]:last-child > div,
div[data-testid="column"]:last-child > div > div,
div[data-testid="column"]:last-child [data-testid="stVerticalBlock"],
div[data-testid="column"]:last-child [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="column"]:last-child .element-container,
div[data-testid="column"]:last-child [class*="block-"] {
  background:#f5f3ef !important; background-color:#f5f3ef !important;
}
div[data-testid="stPydeckChart"] { height:100vh !important; background:#f5f3ef !important; }
div[data-testid="stPydeckChart"] > div { height:100vh !important; background:#f5f3ef !important; }

/* ── Sidebar components ── */
.sb-header {
  padding:18px 18px 14px; border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:10px;
  position:sticky; top:0; background:var(--surface); z-index:10;
}
.sb-logo-icon {
  width:34px; height:34px; background:var(--accent);
  border-radius:9px; display:flex; align-items:center;
  justify-content:center; color:#fff; font-size:16px; flex-shrink:0;
}
.sb-title { font-size:13px; font-weight:600; color:var(--text); line-height:1.2; font-family:'DM Sans',sans-serif; }
.sb-sub   { font-size:10px; color:var(--muted); font-family:'DM Mono',monospace; margin-top:2px; }
.sb-label {
  font-size:10px; font-weight:600; letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted);
  margin-bottom:6px; font-family:'DM Sans',sans-serif;
}
.sb-divider { height:1px; background:var(--border); margin:6px 0; }

.node-card {
  border:1px solid var(--border); border-radius:10px;
  padding:9px 12px; background:var(--surface2);
  display:flex; align-items:center; gap:8px; min-height:42px; margin-bottom:8px;
  font-family:'DM Mono',monospace; font-size:12px; font-weight:500;
}
.nc-dot  { width:8px; height:8px; border-radius:50%; background:var(--light); flex-shrink:0; }
.nc-text { color:var(--muted); }
.node-card.active-origin { border-color:var(--green); background:rgba(34,197,94,.06); }
.node-card.active-origin .nc-dot  { background:var(--green); }
.node-card.active-origin .nc-text { color:var(--green); }
.node-card.active-dest   { border-color:var(--amber); background:rgba(245,158,11,.06); }
.node-card.active-dest   .nc-dot  { background:var(--amber); }
.node-card.active-dest   .nc-text { color:var(--amber); }

.result-panel { border:1px solid var(--border); border-radius:10px; overflow:hidden; font-family:'DM Sans',sans-serif; }
.result-empty { padding:14px; font-size:11.5px; color:var(--light); line-height:1.6; }
.result-time-row { background:var(--accent); color:#fff; padding:12px 14px; display:flex; align-items:baseline; gap:6px; }
.result-minutes { font-size:26px; font-weight:600; line-height:1; }
.result-unit    { font-size:11px; opacity:.7; }
.result-meta    { font-size:10px; opacity:.55; margin-left:auto; font-family:'DM Mono',monospace; }
.result-stops   { padding:6px 0; }
.stop-item { display:flex; align-items:center; gap:8px; padding:5px 14px; font-size:11.5px; position:relative; }
.stop-item + .stop-item::before { content:''; position:absolute; left:19px; top:-4px; width:1px; height:8px; background:var(--border); }
.stop-dot { width:10px; height:10px; border-radius:50%; border:2px solid var(--border); flex-shrink:0; }
.stop-dot.so { border-color:var(--green); background:var(--green); }
.stop-dot.sd { border-color:var(--amber); background:var(--amber); }
.stop-dot.sm { border-color:var(--red);   background:var(--red);   }
.stop-name   { font-weight:500; color:var(--text); }
.stop-name.so { color:var(--green); }
.stop-name.sd { color:var(--amber); }
.stop-name.sm { color:var(--red);   }

.instr-list { display:flex; flex-direction:column; gap:5px; }
.instr-item { display:flex; align-items:center; gap:8px; font-size:11.5px; color:var(--muted); font-family:'DM Sans',sans-serif; }
.instr-num  {
  width:18px; height:18px; background:var(--surface2);
  border:1px solid var(--border); border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:9px; font-weight:600; color:var(--text); flex-shrink:0;
}

.legend-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.legend-item { display:flex; align-items:center; gap:6px; font-size:11px; color:var(--muted); font-family:'DM Sans',sans-serif; }
.leg-dot  { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
.leg-line { width:16px; height:2.5px; border-radius:1px; flex-shrink:0; }

.matrix-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:2px; font-family:'DM Sans',sans-serif; }
.matrix-sub   { font-size:10px; color:var(--muted); margin-bottom:8px; font-family:'DM Mono',monospace; }
.matrix-wrap  { overflow-x:hidden; width:100%; }
.matrix-wrap table {
  border-collapse:collapse; font-size:7.5px; font-family:'DM Mono',monospace;
  background:#f5f3ef !important; width:100%; table-layout:fixed;
}
.matrix-wrap td, .matrix-wrap th {
  border:1px solid var(--border); height:20px; text-align:center;
  color:#111111 !important; background:#f5f3ef !important;
  overflow:hidden; white-space:nowrap; padding:0 1px;
}
.matrix-wrap th {
  color:#888888 !important; background:#ece9e3 !important;
  font-weight:600; font-size:7px;
}
.matrix-wrap tr th:first-child {
  text-align:right; padding-right:4px; font-size:6.5px;
  width:52px; min-width:52px; max-width:52px;
}
.cell-diag { background:#ece9e3 !important; color:#aaaaaa !important; }
.cell-ruta { background:rgba(239,68,68,.12) !important; color:#ef4444 !important; font-weight:700; }
.cell-inf  { color:#cccccc !important; background:#f5f3ef !important; }

/* ── Streamlit native button styling ── */
div[data-testid="column"]:first-child .stButton > button {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
  color: var(--muted) !important;
  width: 100% !important;
  padding: 8px 10px !important;
  box-shadow: none !important;
  transition: all .15s !important;
}
div[data-testid="column"]:first-child .stButton > button:hover {
  border-color: var(--border2) !important;
  color: var(--text) !important;
  background: var(--surface2) !important;
}

/* Force white background globally to override dark theme */
html, body,
section[data-testid="stAppViewContainer"],
section[data-testid="stAppViewContainer"] > div,
div[data-testid="stAppViewBlockContainer"],
.main, .main > div {
  background: #f5f3ef !important;
  background-color: #f5f3ef !important;
  color: #111111 !important;
}

/* Force bone background on ALL elements inside sidebar */
div[data-testid="column"]:first-child,
div[data-testid="column"]:first-child > div,
div[data-testid="column"]:first-child > div > div,
div[data-testid="column"]:first-child > div > div > div,
div[data-testid="column"]:first-child [data-testid="stVerticalBlock"],
div[data-testid="column"]:first-child [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="column"]:first-child .stMarkdown,
div[data-testid="column"]:first-child .element-container,
div[data-testid="column"]:first-child .stButton,
div[data-testid="column"]:first-child [class*="block-"] {
  background: #f5f3ef !important;
  background-color: #f5f3ef !important;
  color: #111111 !important;
}

/* Columns inside sidebar (algo buttons row) */
div[data-testid="column"]:first-child div[data-testid="stHorizontalBlock"] {
  height: auto !important;
  gap: 6px !important;
  padding: 0 18px !important;
}
div[data-testid="column"]:first-child div[data-testid="stHorizontalBlock"] div[data-testid="column"] {
  background: #ffffff !important;
  height: auto !important;
  overflow: visible !important;
  padding: 0 !important;
}

/* Calcular/Reiniciar/Matrix buttons - full width with padding */
div[data-testid="column"]:first-child > div > div > div > div[data-testid="element-container"] .stButton,
div[data-testid="column"]:first-child > div > div > div > div .stButton {
  padding: 0 18px;
}
div[data-testid="column"]:first-child > div > div > div > div[data-testid="element-container"] .stButton > button {
  width: 100% !important;
}

/* Status bar */
.statusbar {
  position:fixed; bottom:0; left:280px; right:0; height:28px;
  background:#f5f3ef; border-top:1px solid #dedad3;
  display:flex; align-items:center; padding:0 14px; gap:8px;
  font-size:11px; font-family:'DM Mono',monospace; color:#888;
  z-index:9999;
}
.st-dot { width:6px; height:6px; border-radius:50%; background:#bbb; flex-shrink:0; }
.st-dot.a { background:#22c55e; }
</style>
""", unsafe_allow_html=True)

# ── Pydeck layers ────────────────────────────────────────────────────────────
def build_layers():
    camino  = st.session_state.camino
    origen  = st.session_state.origen
    destino = st.session_state.destino

    edges_normal, edges_route = [], []
    _empty = {"path":[[0,0],[0,0]],"weight":0,"from":0,"to":0}
    for a,b,w in ARISTAS:
        row={"path":[COORDS[a],COORDS[b]],"weight":w,"from":a,"to":b}
        (edges_route if arista_en_ruta(a,b) else edges_normal).append(row)

    layer_edges = pdk.Layer(
        "PathLayer",
        data=pd.DataFrame(edges_normal if edges_normal else [_empty]),
        get_path="path", get_width=3, get_color=[140,140,140,110],
        width_units="pixels", pickable=False,
    )
    layer_route = pdk.Layer(
        "PathLayer",
        data=pd.DataFrame(edges_route if edges_route else [_empty]),
        get_path="path", get_width=7, get_color=[239,68,68,220],
        width_units="pixels", pickable=False,
    )

    mids=[]
    for a,b,w in ARISTAS:
        enR=arista_en_ruta(a,b)
        mids.append({
            "position":[(COORDS[a][0]+COORDS[b][0])/2,(COORDS[a][1]+COORDS[b][1])/2,0],
            "text":f"{w}m",
            "color":[220,50,50,230] if enR else [80,80,80,200],
        })
    layer_weights = pdk.Layer(
        "TextLayer", data=pd.DataFrame(mids),
        get_position="position", get_text="text",
        get_size=11, get_color="color",
        get_background_color=[250,250,250,215],
        background=True, billboard=True, pickable=False,
    )

    nodes=[]
    for i in range(N):
        esO=i==origen; esD=i==destino
        enR=i in camino and not esO and not esD
        if esO:   color=[34,197,94,255];  line=[22,163,74,255];  r=50
        elif esD: color=[245,158,11,255]; line=[217,119,6,255];  r=50
        elif enR: color=[239,68,68,255];  line=[220,38,38,255];  r=42
        else:     color=[255,255,255,245];line=[140,140,140,200];r=35
        nodes.append({"position":COORDS[i]+[0],"idx":i,"nombre":NOMBRES[i],
                      "color":color,"line_color":line,"radius":r})

    df_n=pd.DataFrame(nodes)
    layer_nodes = pdk.Layer(
        "ScatterplotLayer", data=df_n,
        get_position="position", get_fill_color="color",
        get_line_color="line_color", get_radius="radius",
        radius_units="meters", stroked=True, line_width_min_pixels=2,
        radius_min_pixels=6, radius_max_pixels=18,
        pickable=True, auto_highlight=True,
        highlight_color=[17,17,17,60], id="nodes",
    )
    layer_idx = pdk.Layer(
        "TextLayer", data=df_n,
        get_position="position", get_text="idx",
        get_size=13, get_color=[30,30,30,240],
        font_weight=700, billboard=True, pickable=False,
        get_pixel_offset=[0,1],
    )
    layer_labels = pdk.Layer(
        "TextLayer", data=df_n,
        get_position="position", get_text="nombre",
        get_size=11, get_color=[30,30,30,220],
        get_background_color=[255,255,255,210],
        background=True, billboard=True, pickable=False,
        get_pixel_offset=[0,26],
    )

    return [layer_edges, layer_route, layer_weights, layer_nodes, layer_idx, layer_labels]

# ── Layout ───────────────────────────────────────────────────────────────────
col_sb, col_map = st.columns([280, 999], gap="small")

# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with col_sb:
    o = st.session_state.origen
    d = st.session_state.destino
    camino = st.session_state.camino

    # Header
    st.markdown("""
    <div class="sb-header">
      <div class="sb-logo-icon">🗺</div>
      <div>
        <div class="sb-title">Red Vial Barranquilla</div>
        <div class="sb-sub">Matemáticas Discretas · 202610</div>
      </div>
    </div>
    <div style="padding:12px 18px 0">
    """, unsafe_allow_html=True)

    # Instrucciones
    st.markdown("""
    <div class="sb-label">Cómo usar</div>
    <div class="instr-list">
      <div class="instr-item"><div class="instr-num">1</div>Clic en un nodo → <b>Origen</b></div>
      <div class="instr-item"><div class="instr-num">2</div>Clic en otro nodo → <b>Destino</b></div>
      <div class="instr-item"><div class="instr-num">3</div>Clic de nuevo → <b>Reinicia</b></div>
    </div>
    <div class="sb-divider" style="margin-top:12px"></div>
    """, unsafe_allow_html=True)

    # Origen / Destino
    o_cls  = "active-origin" if o>=0 else ""
    o_text = f"[{o}] {NOMBRES[o]}" if o>=0 else "— sin selección —"
    d_cls  = "active-dest" if d>=0 else ""
    d_text = f"[{d}] {NOMBRES[d]}" if d>=0 else "— sin selección —"

    st.markdown(f"""
    <div class="sb-label">Origen</div>
    <div class="node-card {o_cls}">
      <div class="nc-dot"></div><div class="nc-text">{o_text}</div>
    </div>
    <div class="sb-label">Destino</div>
    <div class="node-card {d_cls}">
      <div class="nc-dot"></div><div class="nc-text">{d_text}</div>
    </div>
    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    # Resultado
    st.markdown('<div class="sb-label" style="margin-top:10px">Resultado</div>', unsafe_allow_html=True)
    if camino:
        stops_html = ""
        for i,n in enumerate(camino):
            cls = "so" if i==0 else ("sd" if i==len(camino)-1 else "sm")
            stops_html += f'<div class="stop-item"><div class="stop-dot {cls}"></div><div class="stop-name {cls}">{NOMBRES[n]}</div></div>'
        st.markdown(f"""
        <div class="result-panel">
          <div class="result-time-row">
            <div class="result-minutes">{st.session_state.tiempo}</div>
            <div class="result-unit">min</div>
            <div class="result-meta">{st.session_state.algo} · {len(camino)} paradas</div>
          </div>
          <div class="result-stops">{stops_html}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-panel"><div class="result-empty">Selecciona origen y destino en el mapa para calcular la ruta óptima.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-divider" style="margin-top:10px"></div>', unsafe_allow_html=True)

    # Algoritmo — botones nativos Streamlit
    st.markdown('<div class="sb-label" style="margin-top:10px">Algoritmo</div>', unsafe_allow_html=True)

    algo = st.session_state.algo
    lbl_d = ("✓ Dijkstra" if algo=="Dijkstra" else "Dijkstra")
    lbl_f = ("✓ Floyd-W"  if algo=="Floyd-Warshall" else "Floyd-W")

    bc1, bc2 = st.columns(2, gap="small")
    with bc1:
        if st.button(lbl_d, key="btn_dijk", use_container_width=True):
            if st.session_state.algo != "Dijkstra":
                st.session_state.algo = "Dijkstra"
                if st.session_state.origen>=0 and st.session_state.destino>=0:
                    calcular()
                st.rerun()
    with bc2:
        if st.button(lbl_f, key="btn_floyd", use_container_width=True):
            if st.session_state.algo != "Floyd-Warshall":
                st.session_state.algo = "Floyd-Warshall"
                if st.session_state.origen>=0 and st.session_state.destino>=0:
                    calcular()
                st.rerun()

    # Calcular
    can_calc = o>=0 and d>=0
    if st.button("▶  Calcular ruta", key="btn_calc", use_container_width=True, disabled=not can_calc):
        calcular()
        st.rerun()

    # Reiniciar
    if st.button("↺  Reiniciar", key="btn_reset", use_container_width=True):
        for k,v in dict(origen=-1,destino=-1,camino=[],tiempo=-1,matriz=[],ver_matriz=False).items():
            st.session_state[k]=v
        st.session_state["_last_click"] = None
        st.rerun()

    st.markdown('<div class="sb-divider" style="margin-top:6px"></div>', unsafe_allow_html=True)

    # Leyenda
    st.markdown("""
    <div class="sb-label" style="margin-top:10px">Leyenda</div>
    <div class="legend-grid">
      <div class="legend-item"><div class="leg-dot" style="background:#22c55e"></div>Origen</div>
      <div class="legend-item"><div class="leg-dot" style="background:#f59e0b"></div>Destino</div>
      <div class="legend-item"><div class="leg-dot" style="background:#ef4444"></div>En ruta</div>
      <div class="legend-item"><div class="leg-dot" style="background:#fff;border:1.5px solid #ccc"></div>Normal</div>
      <div class="legend-item"><div class="leg-line" style="background:#ef4444"></div>Ruta óptima</div>
      <div class="legend-item"><div class="leg-line" style="background:#bbb"></div>Vía normal</div>
    </div>
    <div class="sb-divider" style="margin-top:10px"></div>
    <div style="margin-top:10px"></div>
    """, unsafe_allow_html=True)

    # Matriz toggle
    tog_lbl = "▲  Ocultar matriz F-W" if st.session_state.ver_matriz else "▼  Ver matriz F-W"
    if st.button(tog_lbl, key="btn_matrix", use_container_width=True):
        st.session_state.ver_matriz = not st.session_state.ver_matriz
        if st.session_state.ver_matriz and not st.session_state.matriz:
            dm,_=floyd(); st.session_state.matriz=dm
        st.rerun()

    if st.session_state.ver_matriz and st.session_state.matriz:
        dm = st.session_state.matriz
        short = lambda s: s[:11]+"…" if len(s)>12 else s
        headers = "".join(f"<th>{j}</th>" for j in range(N))
        rows = ""
        for i in range(N):
            cells = ""
            for j in range(N):
                v=dm[i][j]
                if i==j: cells+='<td class="cell-diag">—</td>'
                elif arista_en_ruta(i,j): cells+=f'<td class="cell-ruta">{v}</td>'
                elif v>9999: cells+='<td class="cell-inf">∞</td>'
                else: cells+=f'<td>{v}</td>'
            rows+=f'<tr><th style="text-align:right;padding-right:5px;font-size:8px">{short(NOMBRES[i])}</th>{cells}</tr>'
        st.markdown(f"""
        <div style="margin-top:10px">
          <div class="matrix-title">Matriz Floyd-Warshall</div>
          <div class="matrix-sub">Tiempos mínimos en minutos entre nodos</div>
          <div class="matrix-wrap"><table><tr><th></th>{headers}</tr>{rows}</table></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close padding div

# ═══════════════════════════════════════
# MAPA
# ═══════════════════════════════════════
with col_map:
    view = pdk.ViewState(
        longitude=-74.7960,
        latitude=10.9570,
        zoom=11.5,
        pitch=0,
        bearing=0,
    )
    deck = pdk.Deck(
        layers=build_layers(),
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={
            "html": "<b style='font-size:13px'>{nombre}</b><br>"
                    "<span style='color:#aaa;font-size:11px;font-family:monospace'>Nodo {idx}</span>",
            "style": {
                "background":"#111111","color":"#ffffff",
                "fontFamily":"DM Sans,sans-serif","fontSize":"12px",
                "borderRadius":"8px","padding":"8px 12px","border":"none",
            }
        },
    )

    event = st.pydeck_chart(
        deck,
        on_select="rerun",
        selection_mode="single-object",
        use_container_width=True,
        height=900,
        key="mapa",
    )

    # Procesar click en nodo
    if event and event.selection:
        sel = event.selection.get("objects", {})
        clicked_idx = None
        for layer_name, objs in sel.items():
            if objs and isinstance(objs, list) and objs:
                obj = objs[0]
                if "idx" in obj:
                    clicked_idx = int(obj["idx"]); break

        last = st.session_state.get("_last_click", None)
        if clicked_idx is not None and clicked_idx != last:
            st.session_state["_last_click"] = clicked_idx
            if st.session_state.origen < 0:
                st.session_state.origen = clicked_idx
                st.rerun()
            elif st.session_state.destino < 0 and clicked_idx != st.session_state.origen:
                st.session_state.destino = clicked_idx
                calcular(); st.rerun()
            else:
                st.session_state.origen   = clicked_idx
                st.session_state.destino  = -1
                st.session_state.camino   = []
                st.session_state.tiempo   = -1
                st.session_state.ver_matriz = False
                st.session_state["_last_click"] = clicked_idx
                st.rerun()
        elif clicked_idx is None:
            st.session_state["_last_click"] = None

# ── Status bar ───────────────────────────────────────────────────────────────
camino = st.session_state.camino
dot_cls = "a" if camino else ""
if camino:
    ruta_txt = " → ".join(NOMBRES[n][:9] for n in camino)
    status_txt = f"{st.session_state.algo} &nbsp;·&nbsp; {ruta_txt} &nbsp;·&nbsp; {st.session_state.tiempo} min"
else:
    status_txt = "Haz clic en dos nodos del mapa para calcular la ruta más rápida"

st.markdown(f"""
<div class="statusbar">
  <div class="st-dot {dot_cls}"></div>
  <span>{status_txt}</span>
</div>
""", unsafe_allow_html=True)