"""
MÃ³dulo para geraÃ§Ã£o do Mapa Geral de Clientes (Lojas 81 e 82)
"""
import hashlib
import os
from colorsys import hsv_to_rgb
from html import escape as html_escape
from sqlalchemy import create_engine
import pandas as pd
import folium
import urllib

# ========= ConexÃ£o =========
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
      '142 - L82-PARACURU-LICITAÃ‡ÃƒO',
      '147 - L82-PARAIPABA-LICITAÃ‡ÃƒO',
      '149 - L82-SGA-LICITAÃ‡ÃƒO',
      '000 - L82-EXTRA ROTA'
);
"""

# ========= UtilitÃ¡rios =========
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
        f"<label><input type='checkbox' value=\"{esc_attr(v)}\"/> <span>{esc_txt(v)}</span></label>"
        for v in values_sorted
    )
    return f"""
    <div class="filter-group" id="{group_id}">
        <label>{label}</label>
        <input type="text" class="filter-search" placeholder="ðŸ”Ž Buscar {label.lower()}..." />
        <label><input type="checkbox" class="check-all" /> Selecionar todos</label>
        <div class="scrollbox">{checkbox_items}</div>
    </div>
    """

# ========= GeraÃ§Ã£o do Mapa =========
def generate_map_html():
    """Gera o HTML do mapa geral de clientes"""
    try:
        df = pd.read_sql(SQL, engine)
    except Exception as e:
        return f"<pre style='color:red'>ERRO AO LER DO BANCO:\n{e}</pre>"

    # Carregar dados de Rede e Subrede do CSV
    try:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rede e subrede.csv')
        df_rede = pd.read_csv(csv_path, dtype=str, usecols=['A00_ID', 'REDE', 'SUBREDE'])
        df_rede['A00_ID'] = df_rede['A00_ID'].astype(str).str.strip()
        df['A00_ID'] = df['A00_ID'].astype(str).str.strip()
        df = df.merge(df_rede, on='A00_ID', how='left')
        df['REDE'] = df['REDE'].fillna('').astype(str).str.strip()
        df['SUBREDE'] = df['SUBREDE'].fillna('').astype(str).str.strip()
    except Exception:
        df['REDE'] = ''
        df['SUBREDE'] = ''

    # Coordenadas vÃ¡lidas
    df = df.copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]
    
    # Criar campo Regional baseado na rota
    def get_regional(rota):
        rota_str = str(rota).upper()
        if 'L81' in rota_str:
            return 'L81-CAPITAL'
        elif 'L82' in rota_str:
            return 'L82-INTERIOR'
        else:
            return 'OUTROS'
    
    df['REGIONAL'] = df['AREA_DESC'].apply(get_regional)
    
    if df.empty:
        return "<h3>Nenhum cliente com coordenadas vÃ¡lidas.</h3>"

    # Mapa base
    centro = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=centro, zoom_start=6, width="100%", height="100%", tiles="OpenStreetMap")

    # Cores por supervisor â€” hue uniformemente distribuÃ­do no HSV, garante cores distintas
    df["SUPERVISOR"] = df["SUPERVISOR"].fillna("N/A").astype(str)
    unique_sup = sorted(df["SUPERVISOR"].unique(), key=lambda x: x.upper())
    n_sup = max(len(unique_sup), 1)

    def _hsv_color(idx, total):
        h = idx / total
        r, g, b = hsv_to_rgb(h, 0.75, 0.90)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    sup_color = {sup: _hsv_color(i, n_sup) for i, sup in enumerate(unique_sup)}

    fg = folium.FeatureGroup(name="Clientes", show=True)

    # Marcadores
    total_markers = 0
    for _, r in df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 200px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #0066cc;">
                {esc_txt(r.A00_FANTASIA)}
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 3px; font-weight: bold;">ID:</td><td style="padding: 3px;">{esc_txt(r.A00_ID)}</td></tr>
                <tr><td style="padding: 3px; font-weight: bold;">Rota:</td><td style="padding: 3px;">{esc_txt(r.AREA_DESC)}</td></tr>
                <tr><td style="padding: 3px; font-weight: bold;">Vendedor:</td><td style="padding: 3px;">{esc_txt(r.NOME_VENDEDOR)}</td></tr>
                <tr><td style="padding: 3px; font-weight: bold;">Supervisor:</td><td style="padding: 3px;">{esc_txt(r.SUPERVISOR)}</td></tr>
                <tr><td style="padding: 3px; font-weight: bold;">Rede:</td><td style="padding: 3px;">{esc_txt(r.REDE) or '-'}</td></tr>
                <tr><td style="padding: 3px; font-weight: bold;">Subrede:</td><td style="padding: 3px;">{esc_txt(r.SUBREDE) or '-'}</td></tr>
            </table>
        </div>
        """

        icon_html = f"""
        <div class="custom-marker" 
             data-id="{esc_attr(r.A00_ID)}"
             data-cliente="{esc_attr(r.A00_FANTASIA)}"
             data-rota="{esc_attr(r.AREA_DESC)}"
             data-vendedor="{esc_attr(r.NOME_VENDEDOR)}"
             data-supervisor="{esc_attr(r.SUPERVISOR)}"
             data-regional="{esc_attr(r.REGIONAL)}"
             data-rede="{esc_attr(r.REDE)}"
             data-subrede="{esc_attr(r.SUBREDE)}"
             style="background-color:{sup_color[r.SUPERVISOR]}; 
                    border-radius:50%; width:24px; height:24px; 
                    display:flex; align-items:center; justify-content:center;">
            <i class="fa fa-shopping-cart" style="color:white; font-size:14px;"></i>
        </div>
        """
        marker = folium.Marker(
            location=[r.latitude, r.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.DivIcon(html=icon_html)
        )
        marker.add_to(fg)
        total_markers += 1
    
    fg.add_to(m)
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
    regional_group   = make_filter_group("regional-group", "Regional", df["REGIONAL"].dropna().unique())
    area_group       = make_filter_group("area-group", "Rota", df["AREA_DESC"].dropna().unique())
    id_group         = make_filter_group("id-group", "ID", df["A00_ID"].astype(str).unique())
    name_group       = make_filter_group("name-group", "Cliente", df["A00_FANTASIA"].dropna().unique())
    vendedor_group   = make_filter_group("vendedor-group", "Vendedor", df["NOME_VENDEDOR"].dropna().unique())
    supervisor_group = make_filter_group("supervisor-group", "Supervisor", df["SUPERVISOR"].dropna().unique())
    rede_values      = [v for v in df["REDE"].unique() if v and v != 'nan']
    subrede_values   = [v for v in df["SUBREDE"].unique() if v and v != 'nan']
    rede_group       = make_filter_group("rede-group", "Rede", rede_values) if rede_values else ""
    subrede_group    = make_filter_group("subrede-group", "Subrede", subrede_values) if subrede_values else ""

    # Serializar sup_color para JS
    sup_color_js = "{" + ", ".join(f'"{k}": "{v}"' for k, v in sup_color.items()) + "}"
    json_sups_js = "[" + ", ".join(f'{{"name": "{k}", "color": "{v}"}}' for k, v in sup_color.items()) + "]"

    overlay = f"""
<style>
  * {{ box-sizing: border-box; }}

  /* ===== SIDEBAR ===== */
  #sidebar {{
    position: fixed; top: 0; left: 0; height: 100vh; width: 300px;
    background: #fff; z-index: 1200;
    display: flex; flex-direction: column;
    box-shadow: 4px 0 20px rgba(0,0,0,.15);
    transition: transform 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  #sidebar.collapsed {{ transform: translateX(-300px); }}

  #sidebar-header {{
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; padding: 16px 20px;
    display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }}
  #sidebar-header h3 {{ margin: 0; font-size: 16px; font-weight: 600; }}

  #sidebar-body {{
    flex: 1; overflow-y: auto; padding: 12px;
    scrollbar-width: thin; scrollbar-color: #0066cc #f1f1f1;
  }}
  #sidebar-body::-webkit-scrollbar {{ width: 6px; }}
  #sidebar-body::-webkit-scrollbar-thumb {{ background: #0066cc; border-radius: 10px; }}

  #sidebar-footer {{
    padding: 12px; border-top: 1px solid #dee2e6;
    display: flex; gap: 8px; flex-shrink: 0;
  }}
  #sidebar-footer button {{
    flex: 1; padding: 9px; border: none; border-radius: 8px;
    font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
  }}
  #btn-clear {{ background: #6c757d; color: white; }}
  #btn-clear:hover {{ background: #5a6268; }}
  #btn-deselect {{ background: #dc3545; color: white; }}
  #btn-deselect:hover {{ background: #c82333; }}

  /* Toggle button (tab outside sidebar) */
  #sidebar-toggle {{
    position: fixed; top: 50%; left: 300px;
    transform: translateY(-50%);
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; border: none; width: 28px; height: 56px;
    border-radius: 0 8px 8px 0;
    cursor: pointer; z-index: 1201; font-size: 14px;
    transition: left 0.3s ease; display: flex; align-items: center; justify-content: center;
    box-shadow: 3px 0 10px rgba(0,0,0,.2);
  }}
  body.sidebar-collapsed #sidebar-toggle {{ left: 0; }}

  /* ===== FILTER GROUPS ===== */
  .filter-group {{
    margin-bottom: 14px; background: #f8f9fa; padding: 12px;
    border-radius: 10px; border: 1px solid #e9ecef;
  }}
  .filter-group > label:first-child {{
    font-weight: 600; font-size: 12px; display: block;
    margin-bottom: 8px; color: #495057; text-transform: uppercase; letter-spacing: 0.5px;
  }}
  .filter-search {{
    width: 100%; padding: 7px 10px; margin-bottom: 8px;
    border-radius: 7px; border: 2px solid #dee2e6; font-size: 12px; transition: all 0.2s;
  }}
  .filter-search:focus {{ outline: none; border-color: #0066cc; box-shadow: 0 0 0 3px rgba(0,102,204,.1); }}
  .filter-group > label:has(.check-all) {{
    display: flex !important; align-items: center; gap: 6px;
    font-weight: 500 !important; font-size: 12px !important;
    color: #6c757d !important; text-transform: none !important;
    margin-bottom: 6px !important; cursor: pointer;
  }}
  .scrollbox {{
    background: white; padding: 6px; border-radius: 7px;
    max-height: 130px; overflow-y: auto; border: 1px solid #dee2e6;
    scrollbar-width: thin; scrollbar-color: #0066cc #f1f1f1;
  }}
  .scrollbox::-webkit-scrollbar {{ width: 6px; }}
  .scrollbox::-webkit-scrollbar-thumb {{ background: #0066cc; border-radius: 10px; }}
  .scrollbox label {{
    display: flex; align-items: center; gap: 7px; padding: 5px 6px;
    font-size: 12px; cursor: pointer; border-radius: 5px; transition: background .15s; color: #212529;
  }}
  .scrollbox label:hover {{ background: #e9f0fb; }}
  .scrollbox input[type="checkbox"] {{ width: 15px; height: 15px; accent-color: #0066cc; }}

  /* ===== COUNTER ===== */
  #counter {{
    position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; padding: 8px 18px; border-radius: 25px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px; font-weight: 600; z-index: 1100;
    box-shadow: 0 4px 15px rgba(0,0,0,.2); pointer-events: none;
  }}

  /* deslocar mapa quando sidebar aberta */
  .leaflet-container {{ margin-left: 300px; width: calc(100% - 300px) !important; transition: all 0.3s; }}
  body.sidebar-collapsed .leaflet-container {{ margin-left: 0; width: 100% !important; }}
  #counter {{ transition: left 0.3s; }}
</style>

<!-- Sidebar -->
<div id="sidebar">
  <div id="sidebar-header">
    <h3>ðŸ”Ž Filtros de Clientes</h3>
  </div>
  <div id="sidebar-body">
    {regional_group}
    {area_group}
    {id_group}
    {name_group}
    {vendedor_group}
    {supervisor_group}
    {rede_group}
    {subrede_group}
  </div>
  <div id="sidebar-footer">
    <button id="btn-clear">ðŸ”„ Limpar</button>
    <button id="btn-deselect">âŒ Desmarcar</button>
  </div>
</div>
<button id="sidebar-toggle" title="Mostrar/ocultar filtros">â—€</button>

<div id="counter">Registros: <span id="marker-count">{total_markers}</span></div>

<script>
  // ===== Sidebar toggle =====
  var sidebar = document.getElementById('sidebar');
  var toggleBtn = document.getElementById('sidebar-toggle');
  var sidebarOpen = true;
  toggleBtn.addEventListener('click', function() {{
    sidebarOpen = !sidebarOpen;
    if (sidebarOpen) {{
      sidebar.classList.remove('collapsed');
      document.body.classList.remove('sidebar-collapsed');
      toggleBtn.style.left = '300px';
      toggleBtn.textContent = 'â—€';
    }} else {{
      sidebar.classList.add('collapsed');
      document.body.classList.add('sidebar-collapsed');
      toggleBtn.style.left = '0';
      toggleBtn.textContent = 'â–¶';
    }}
    // ForÃ§ar redimensionamento do mapa
    setTimeout(function() {{
      if (typeof L !== 'undefined') {{
        document.querySelectorAll('.leaflet-map-pane').forEach(function() {{}});
        for (var k in window) {{
          try {{
            if (window[k] && window[k]._leaflet_id && window[k].invalidateSize) {{
              window[k].invalidateSize();
            }}
          }} catch(e) {{}}
        }}
      }}
    }}, 310);
  }});

  // ===== Cores por supervisor (para restaurar) =====
  var SUP_COLOR = {sup_color_js};

  // ===== InicializaÃ§Ã£o filtros =====
  function initFilters() {{
    var map = null;
    var group = null;
    if (typeof L !== 'undefined') {{
      for (var key in window) {{
        try {{
          if (window[key] && window[key]._leaflet_id && window[key].getCenter) {{
            map = window[key]; break;
          }}
        }} catch(e) {{}}
      }}
    }}
    if (!map) {{ setTimeout(initFilters, 500); return; }}
    map.eachLayer(function(layer) {{
      if (layer instanceof L.FeatureGroup) group = layer;
    }});
    if (!group) {{ setTimeout(initFilters, 500); return; }}

    // Contagem visÃ­veis
    function countVisible() {{
      var n = 0;
      group.eachLayer(function(l) {{ if (map.hasLayer(l)) n++; }});
      var el = document.getElementById('marker-count');
      if (el) el.textContent = n;
    }}
    map.on('layeradd layerremove', countVisible);
    countVisible();

    // Indexar marcadores
    var markerData = [];
    group.eachLayer(function(marker) {{
      var icon = marker.getElement();
      if (icon) {{
        var d = icon.querySelector('.custom-marker');
        if (d) {{
          markerData.push({{
            marker: marker,
            el: d,
            id: d.getAttribute('data-id') || '',
            cliente: d.getAttribute('data-cliente') || '',
            rota: d.getAttribute('data-rota') || '',
            vendedor: d.getAttribute('data-vendedor') || '',
            supervisor: d.getAttribute('data-supervisor') || '',
            regional: d.getAttribute('data-regional') || '',
            rede: d.getAttribute('data-rede') || '',
            subrede: d.getAttribute('data-subrede') || ''
          }});
        }}
      }}
    }});

    // Busca nos scrollboxes
    document.querySelectorAll('.filter-search').forEach(function(input) {{
      input.addEventListener('input', function() {{
        var term = this.value.toLowerCase();
        var scrollbox = this.parentElement.querySelector('.scrollbox');
        scrollbox.querySelectorAll('label').forEach(function(label) {{
          label.style.display = label.textContent.toLowerCase().includes(term) ? 'flex' : 'none';
        }});
      }});
    }});

    // Selecionar todos
    document.querySelectorAll('.check-all').forEach(function(cb) {{
      cb.addEventListener('change', function() {{
        var scrollbox = this.parentElement.parentElement.querySelector('.scrollbox');
        scrollbox.querySelectorAll('input[type="checkbox"]').forEach(function(c) {{ c.checked = cb.checked; }});
        applyFilters();
      }});
    }});

    // Aplicar filtros em tempo real
    document.querySelectorAll('.filter-group .scrollbox input[type="checkbox"]').forEach(function(cb) {{
      cb.addEventListener('change', applyFilters);
    }});

    function hsvToHex(h, s, v) {{
      var r, g, b;
      var i = Math.floor(h * 6);
      var f = h * 6 - i;
      var p = v * (1 - s); var q = v * (1 - f * s); var t = v * (1 - (1 - f) * s);
      switch(i % 6) {{
        case 0: r=v; g=t; b=p; break; case 1: r=q; g=v; b=p; break;
        case 2: r=p; g=v; b=t; break; case 3: r=p; g=q; b=v; break;
        case 4: r=t; g=p; b=v; break; case 5: r=v; g=p; b=q; break;
      }}
      return '#' + [r,g,b].map(function(x) {{ return Math.round(x*255).toString(16).padStart(2,'0'); }}).join('');
    }}

    function applyFilters() {{
      var selRegionais  = getChecked('#regional-group');
      var selRotas      = getChecked('#area-group');
      var selIds        = getChecked('#id-group');
      var selClientes   = getChecked('#name-group');
      var selVendedores = getChecked('#vendedor-group');
      var selSups       = getChecked('#supervisor-group');
      var selRedes      = getChecked('#rede-group');
      var selSubredes   = getChecked('#subrede-group');

      var visibleVendedores = {{}};
      var visibleCount = 0;

      markerData.forEach(function(item) {{
        var show = true;
        if (selRegionais.length  && selRegionais.indexOf(item.regional)   === -1) show = false;
        if (selRotas.length      && selRotas.indexOf(item.rota)           === -1) show = false;
        if (selIds.length        && selIds.indexOf(item.id)               === -1) show = false;
        if (selClientes.length   && selClientes.indexOf(item.cliente)     === -1) show = false;
        if (selVendedores.length && selVendedores.indexOf(item.vendedor)  === -1) show = false;
        if (selSups.length       && selSups.indexOf(item.supervisor)      === -1) show = false;
        if (selRedes.length      && selRedes.indexOf(item.rede)           === -1) show = false;
        if (selSubredes.length   && selSubredes.indexOf(item.subrede)     === -1) show = false;

        if (show) {{
          if (!map.hasLayer(item.marker)) group.addLayer(item.marker);
          visibleCount++;
          if (item.vendedor) visibleVendedores[item.vendedor] = true;
        }} else {{
          if (map.hasLayer(item.marker)) group.removeLayer(item.marker);
        }}
      }});

      // Cores dinÃ¢micas por vendedor se exatamente 1 supervisor filtrado
      var uniqueVisVendedores = Object.keys(visibleVendedores).sort();
      if (selSups.length === 1) {{
        var nVend = Math.max(uniqueVisVendedores.length, 1);
        var vendColor = {{}};
        uniqueVisVendedores.forEach(function(v, i) {{
          vendColor[v] = hsvToHex(i / nVend, 0.75, 0.90);
        }});
        markerData.forEach(function(item) {{
          if (map.hasLayer(item.marker) && item.el) {{
            item.el.style.backgroundColor = vendColor[item.vendedor] || '#999';
          }}
        }});
        // Atualizar legenda
        var legendContent = '<b>Vendedor</b><div style="margin-top:6px">';
        uniqueVisVendedores.forEach(function(v) {{
          legendContent += "<div style='display:flex;align-items:center;gap:8px;margin:2px 0'>" +
            "<span style='display:inline-block;width:12px;height:12px;border-radius:50%;background:" + vendColor[v] + ";border:1px solid #0002'></span>" +
            v + "</div>";
        }});
        legendContent += '</div>';
        document.getElementById('legend').innerHTML = legendContent;
      }} else {{
        // Restaurar cores por supervisor
        markerData.forEach(function(item) {{
          if (item.el) {{
            item.el.style.backgroundColor = SUP_COLOR[item.supervisor] || '#999';
          }}
        }});
        // Restaurar legenda
        var legendContent = '<b>Supervisor</b><div style="margin-top:6px">';
        var sups = {json_sups_js};
        sups.forEach(function(entry) {{
          legendContent += "<div style='display:flex;align-items:center;gap:8px;margin:2px 0'>" +
            "<span style='display:inline-block;width:12px;height:12px;border-radius:50%;background:" + entry.color + ";border:1px solid #0002'></span>" +
            entry.name + "</div>";
        }});
        legendContent += '</div>';
        document.getElementById('legend').innerHTML = legendContent;
      }}

      document.getElementById('marker-count').textContent = visibleCount;
    }}

    function getChecked(selector) {{
      var el = document.querySelector(selector);
      if (!el) return [];
      return Array.from(el.querySelectorAll('.scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
    }}

    // BotÃ£o Limpar
    document.getElementById('btn-clear').addEventListener('click', function() {{
      document.querySelectorAll('.filter-group input[type="checkbox"]').forEach(function(cb) {{ cb.checked = false; }});
      markerData.forEach(function(item) {{
        if (!map.hasLayer(item.marker)) group.addLayer(item.marker);
        if (item.el) item.el.style.backgroundColor = SUP_COLOR[item.supervisor] || '#999';
      }});
      countVisible();
    }});

    // BotÃ£o Desmarcar
    document.getElementById('btn-deselect').addEventListener('click', function() {{
      document.querySelectorAll('.filter-group input[type="checkbox"]').forEach(function(cb) {{ cb.checked = false; }});
    }});
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initFilters);
  }} else {{
    setTimeout(initFilters, 1000);
  }}
</script>
"""

    html = html.replace(
        "</body>",
        legend_html + overlay + "</body>"
    )

    return html

