import hashlib
from colorsys import hsv_to_rgb
from html import escape as html_escape

from flask import Flask, Response
from flask_compress import Compress
from sqlalchemy import create_engine
import pandas as pd
import folium
import urllib
import os
from datetime import datetime

app = Flask(__name__)
Compress(app)

# Configurações de compressão
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Cache do mapa
_map_cache = None
_map_cache_time = None
CACHE_DURATION = 300  # 5 minutos

# ========= Conexão =========
odbc_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.1.0.3\\SQLSTANDARD;"
    "DATABASE=dbactions;"
    "UID=analistarpt;"
    "PWD=mM=DU9lUd3C$qb@;"
    "TrustServerCertificate=yes;"
    "MARS_Connection=Yes;"
)
conn_str = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)
engine = create_engine(conn_str, pool_pre_ping=True)

# ========= SQL =========
SQL = """
SELECT 
    c.A00_ID,
    c.A00_FANTASIA,
    c.A00_LAT        AS latitude,
    c.A00_LONG       AS longitude,
    ar.A14_DESC      AS AREA_DESC,
    c.A00_ID_VEND    AS Vendedor,
    v.A00_NOME       AS NOME_VENDEDOR,
    s.A00_NOME       AS SUPERVISOR
FROM A00 c
INNER JOIN A14 ar ON c.A00_ID_A14 = ar.A14_ID
LEFT  JOIN A00 v  ON c.A00_ID_VEND = v.A00_ID
LEFT  JOIN A00 s  ON c.A00_ID_VEND_2 = s.A00_ID
WHERE c.A00_STATUS = 1
  AND c.A00_EN_CL  = 1
  AND ar.A14_DESC IS NOT NULL
  AND ar.A14_DESC NOT IN (
      '999 - L80-INDUSTRIA',
      '700 - L81 - REMESSA VENDA',
      '142 - L82-PARACURU-LICITAÇÃO',
      '147 - L82-PARAIPABA-LICITAÇÃO',
      '149 - L82-SGA-LICITAÇÃO',
      '000 - L82-EXTRA ROTA'
);
"""

# ========= Utilitários =========
def _to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def color_for_supervisor(name: str) -> str:
    """Gera cor única (#hex) a partir do nome do supervisor."""
    key = (name or "N/A").strip().lower()
    hue = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:6], 16) / 0xFFFFFF
    s, v = 0.65, 0.95
    r, g, b = hsv_to_rgb(hue, s, v)
    return _to_hex(r, g, b)

def esc_txt(s):
    return html_escape("" if s is None else str(s), quote=False)

def esc_attr(s):
    return html_escape("" if s is None else str(s), quote=True)

def make_filter_group(group_id, label, values):
    try:
        values_sorted = sorted(values, key=lambda x: int(str(x)))
    except Exception:
        values_sorted = sorted(values, key=lambda x: str(x).upper())
    checkbox_items = "".join(
        f"<label><input type='checkbox' value=\"{esc_attr(v)}\"/> {esc_txt(v)}</label>"
        for v in values_sorted
    )
    return f"""
    <div class="filter-group" id="{group_id}">
        <label>{label}</label>
        <input type="text" class="filter-search" placeholder="Buscar {label.lower()}..." />
        <label><input type="checkbox" class="check-all" /> Selecionar todos</label>
        <div class="scrollbox">{checkbox_items}</div>
    </div>
    """

# ========= Rota com Cache =========
def generate_map_html():
    """Gera o HTML do mapa (função separada para cache)"""
    try:
        df = pd.read_sql(SQL, engine)
    except Exception as e:
        return f"<pre style='color:red'>ERRO AO LER DO BANCO:\n{e}</pre>"

    # Coordenadas válidas
    df = df.copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]
    if df.empty:
        return "<h3>Nenhum cliente com coordenadas válidas.</h3>"

    # Mapa base
    centro = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=centro, zoom_start=6, width="100%", height="100%", tiles="OpenStreetMap")

    # Cores por supervisor
    df["SUPERVISOR"] = df["SUPERVISOR"].fillna("N/A").astype(str)
    # Lista fixa de cores
    fixed_colors = ["#f50c0c", "#0c5ffa", "#208317", "#000000"]

    # Supervisores ordenados
    unique_sup = sorted(df["SUPERVISOR"].unique(), key=lambda x: x.upper())

    # Mapeia supervisores para cores, repetindo se tiver mais de 4 supervisores
    sup_color = {sup: fixed_colors[i % len(fixed_colors)] for i, sup in enumerate(unique_sup)}

    fg = folium.FeatureGroup(name="Clientes", show=True)
    fg.add_to(m)

    # Marcadores
    for _, r in df.iterrows():
        popup = (
            f"<b>ID:</b> {esc_txt(r.A00_ID)}<br>"
            f"<b>Cliente:</b> {esc_txt(r.A00_FANTASIA)}<br>"
            f"<b>Rota:</b> {esc_txt(r.AREA_DESC)}<br>"
            f"<b>Vendedor:</b> {esc_txt(r.NOME_VENDEDOR)}<br>"
            f"<b>Supervisor:</b> {esc_txt(r.SUPERVISOR)}"
        )

        # Ícone customizado com cor #hex
        icon_html = f"""
        <div style="background-color:{sup_color[r.SUPERVISOR]}; 
                    border-radius:50%; width:24px; height:24px; 
                    display:flex; align-items:center; justify-content:center;">
            <i class="fa fa-shopping-cart" style="color:white; font-size:14px;"></i>
        </div>
        """
        folium.Marker(
            location=[r.latitude, r.longitude],
            popup=popup,
            icon=folium.DivIcon(html=icon_html)
        ).add_to(fg)

    folium.LayerControl(collapsed=False).add_to(m)

    # HTML do mapa
    html = m.get_root().render()

    # Legenda
    legend_items = "".join(
        f"<div style='display:flex;align-items:center;gap:8px;margin:2px 0;'>"
        f"<span style='display:inline-block;width:12px;height:12px;border-radius:50%;"
        f"background:{sup_color[name]};border:1px solid #0002;'></span>"
        f"{esc_txt(name)}</div>"
        for name in unique_sup
    )
    legend_html = (
        "<div id='legend' style='position:fixed;bottom:20px;right:20px;"
        "background:#fff;padding:10px 12px;border-radius:8px;border:1px solid #ccc;"
        "z-index:1100;max-height:300px;overflow:auto;font-size:12px;box-shadow:0 2px 10px rgba(0,0,0,.15)'>"
        "<b>Supervisor</b><div style='margin-top:6px'>"
        f"{legend_items}"
        "</div></div>"
    )

    # Filtros
    map_name = m.get_name()
    fg_name = fg.get_name()

    area_group       = make_filter_group("area-group", "Rota", df["AREA_DESC"].dropna().unique())
    id_group         = make_filter_group("id-group", "ID", df["A00_ID"].astype(str).unique())
    name_group       = make_filter_group("name-group", "Cliente", df["A00_FANTASIA"].dropna().unique())
    vendedor_group   = make_filter_group("vendedor-group", "Vendedor", df["NOME_VENDEDOR"].dropna().unique())
    supervisor_group = make_filter_group("supervisor-group", "Supervisor", df["SUPERVISOR"].dropna().unique())

    overlay = f"""
<style>
  #filter-toggle {{
    position: fixed; top: 10px; left: 10px;
    background: white; border: none; padding: 6px 12px;
    z-index: 1101; border-radius: 4px; cursor: pointer; font-weight: bold;
  }}
  #filter-popup {{
    display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    background: #0066cc; color: white; padding: 20px; border-radius: 10px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4); z-index: 1100; width: 320px;
    max-height: 90vh; overflow-y: auto; font-family: sans-serif;
  }}
  #filter-popup.active {{ display: block; }}
  .filter-popup-close {{
    float: right; background: white; color: #0066cc;
    border: none; padding: 2px 8px; border-radius: 10px; cursor: pointer; font-weight: bold;
  }}
  .filter-group {{ margin-bottom: 10px; }}
  .filter-group label {{ font-weight: bold; font-size: 12px; display: block; margin-top: 8px; }}
  .filter-search {{
    width: 100%; padding: 4px; margin-bottom: 4px; border-radius: 4px; border: none; font-size: 12px;
  }}
  .scrollbox {{
    background: white; padding: 4px; border-radius: 4px; max-height: 120px;
    overflow-y: auto; color: black; font-size: 12px;
  }}
  .scrollbox label {{ display: flex; align-items: center; gap: 4px; padding: 1px 0; font-size: 12px; line-height: 1.1; }}
  #counter {{
    position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
    background: rgba(0,0,0,0.7); color: white; padding: 6px 12px; border-radius: 6px;
    font-family: sans-serif; font-size: 14px; z-index: 1100;
  }}
</style>

<button id="filter-toggle">🔍 Filtros</button>
<div id="counter">Registros visíveis: <span id="marker-count">0</span></div>

<div id="filter-popup">
  <button class="filter-popup-close" onclick="document.getElementById('filter-popup').classList.remove('active')">❌</button>
  {area_group}
  {id_group}
  {name_group}
  {vendedor_group}
  {supervisor_group}
  <button id="btn-search" class="btn-buscar">Buscar</button>
  <div class="btn-group" style="display:flex;gap:6px;margin-top:10px;">
    <button id="btn-clear" class="btn-clear">Limpar</button>
    <button id="btn-deselect" class="btn-desmarcar">Desmarcar</button>
    <button id="btn-toggle" class="btn-toggle">Toggle Filtro</button>
  </div>
</div>

<script>
  document.getElementById("filter-toggle").onclick = function() {{
    document.getElementById("filter-popup").classList.add("active");
  }};
  (function() {{
    var map = {map_name};
    var group = {fg_name};
    function countVisible() {{
      var n = 0;
      group.eachLayer(function(l) {{
        if (map.hasLayer(l)) n += 1;
      }});
      var el = document.getElementById('marker-count');
      if (el) el.textContent = n;
    }}
    map.on('layeradd layerremove zoomend moveend', countVisible);
    setInterval(countVisible, 1000);
    countVisible();
    window._recountMarkers = countVisible;
  }})();
</script>
"""

    html = html.replace(
        "</body>",
        legend_html + overlay + '<script src="/static/filters.js"></script></body>'
    )

    return html

@app.route("/")
def index():
    global _map_cache, _map_cache_time
    
    # Verifica se precisa regenerar o cache
    now = datetime.now()
    if _map_cache is None or _map_cache_time is None or \
       (now - _map_cache_time).total_seconds() > CACHE_DURATION:
        print(f"⏳ Gerando mapa... (cache expirado ou vazio)")
        _map_cache = generate_map_html()
        _map_cache_time = now
        print(f"✅ Mapa gerado e cacheado por {CACHE_DURATION}s")
    else:
        elapsed = (now - _map_cache_time).total_seconds()
        print(f"✅ Servindo mapa do cache (idade: {elapsed:.1f}s)")
    
    return Response(_map_cache, mimetype="text/html")

if __name__ == "__main__":
    # Pré-gera o mapa na inicialização
    print("🚀 Pré-gerando mapa na inicialização...")
    _map_cache = generate_map_html()
    _map_cache_time = datetime.now()
    print(f"✅ Mapa pré-gerado! Servidor pronto.")
    
    # Em produção, use Gunicorn ao invés de debug
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
