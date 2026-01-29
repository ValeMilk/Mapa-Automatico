"""
Módulo para geração do Mapa Geral de Clientes (Lojas 81 e 82)
"""
import hashlib
from colorsys import hsv_to_rgb
from html import escape as html_escape
from sqlalchemy import create_engine
import pandas as pd
import folium
import urllib

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
        <input type="text" class="filter-search" placeholder="🔎 Buscar {label.lower()}..." />
        <label><input type="checkbox" class="check-all" /> Selecionar todos</label>
        <div class="scrollbox">{checkbox_items}</div>
    </div>
    """

# ========= Geração do Mapa =========
def generate_map_html():
    """Gera o HTML do mapa geral de clientes"""
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
        return "<h3>Nenhum cliente com coordenadas válidas.</h3>"

    # Mapa base
    centro = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=centro, zoom_start=6, width="100%", height="100%", tiles="OpenStreetMap")

    # Cores por supervisor (fixas)
    df["SUPERVISOR"] = df["SUPERVISOR"].fillna("N/A").astype(str)
    fixed_colors = ["#f50c0c", "#0c5ffa", "#208317", "#000000"]
    unique_sup = sorted(df["SUPERVISOR"].unique(), key=lambda x: x.upper())
    sup_color = {sup: fixed_colors[i % len(fixed_colors)] for i, sup in enumerate(unique_sup)}

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

    overlay = f"""
<style>
  * {{ box-sizing: border-box; }}
  
  #filter-toggle {{
    position: fixed; top: 15px; left: 15px;
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; border: none; padding: 12px 20px;
    z-index: 1101; border-radius: 8px; cursor: pointer; 
    font-weight: 600; font-size: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  #filter-toggle:hover {{
    transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3);
  }}
  
  #filter-popup {{
    display: none; position: fixed; top: 50%; left: 50%; 
    transform: translate(-50%, -50%);
    background: white; padding: 0; border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3); z-index: 1100; 
    width: 420px; max-width: 95vw; max-height: 85vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    overflow: hidden;
  }}
  #filter-popup.active {{ display: flex; flex-direction: column; }}
  
  .filter-header {{
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; padding: 20px; display: flex; justify-content: space-between;
    align-items: center; border-radius: 16px 16px 0 0;
  }}
  .filter-header h3 {{
    margin: 0; font-size: 18px; font-weight: 600;
  }}
  .filter-popup-close {{
    background: rgba(255,255,255,0.2); color: white;
    border: none; width: 32px; height: 32px; border-radius: 50%; 
    cursor: pointer; font-size: 18px; display: flex; align-items: center;
    justify-content: center; transition: all 0.2s ease;
  }}
  .filter-popup-close:hover {{
    background: rgba(255,255,255,0.3); transform: rotate(90deg);
  }}
  
  .filter-content {{
    padding: 20px; overflow-y: auto; flex: 1;
  }}
  
  .filter-group {{ 
    margin-bottom: 20px; background: #f8f9fa; padding: 15px;
    border-radius: 10px; border: 1px solid #e9ecef;
  }}
  .filter-group > label:first-child {{ 
    font-weight: 600; font-size: 13px; display: block; 
    margin-bottom: 10px; color: #495057; text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .filter-search {{
    width: 100%; padding: 10px 12px; margin-bottom: 10px; 
    border-radius: 8px; border: 2px solid #dee2e6; font-size: 13px;
    transition: all 0.2s ease; background: white;
  }}
  .filter-search:focus {{
    outline: none; border-color: #0066cc; box-shadow: 0 0 0 3px rgba(0,102,204,0.1);
  }}
  
  .check-all {{
    margin-bottom: 8px !important; accent-color: #0066cc;
  }}
  .filter-group > label:has(.check-all) {{
    display: flex !important; align-items: center; gap: 6px;
    font-weight: 500 !important; font-size: 12px !important;
    color: #6c757d !important; text-transform: none !important;
    margin-bottom: 8px !important; cursor: pointer;
  }}
  
  .scrollbox {{
    background: white; padding: 8px; border-radius: 8px; 
    max-height: 150px; overflow-y: auto; border: 1px solid #dee2e6;
  }}
  .scrollbox::-webkit-scrollbar {{ width: 8px; }}
  .scrollbox::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 10px; }}
  .scrollbox::-webkit-scrollbar-thumb {{ background: #0066cc; border-radius: 10px; }}
  .scrollbox::-webkit-scrollbar-thumb:hover {{ background: #004c99; }}
  
  .scrollbox label {{ 
    display: flex; align-items: center; gap: 8px; padding: 6px 8px;
    font-size: 13px; line-height: 1.4; cursor: pointer; border-radius: 6px;
    transition: background 0.15s ease; color: #212529;
  }}
  .scrollbox label:hover {{ background: #f8f9fa; }}
  .scrollbox input[type="checkbox"] {{
    width: 16px; height: 16px; cursor: pointer; accent-color: #0066cc;
  }}
  
  .filter-actions {{
    padding: 15px 20px; background: #f8f9fa; border-top: 1px solid #dee2e6;
    display: flex; gap: 10px; flex-wrap: wrap;
  }}
  .filter-actions button {{
    flex: 1; min-width: 100px; padding: 10px 16px; border: none;
    border-radius: 8px; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.2s ease;
  }}
  #btn-search {{
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; flex: 1 1 100%;
  }}
  #btn-search:hover {{
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,102,204,0.4);
  }}
  #btn-clear {{
    background: #6c757d; color: white;
  }}
  #btn-clear:hover {{ background: #5a6268; }}
  #btn-deselect {{
    background: #dc3545; color: white;
  }}
  #btn-deselect:hover {{ background: #c82333; }}
  #btn-toggle {{
    background: #17a2b8; color: white;
  }}
  #btn-toggle:hover {{ background: #138496; }}
  
  #counter {{
    position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
    color: white; padding: 10px 20px; border-radius: 25px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px; font-weight: 600; z-index: 1100;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  }}
  #counter span {{ font-size: 16px; }}
</style>

<button id="filter-toggle">🔍 Filtros</button>
<div id="counter">Registros: <span id="marker-count">{total_markers}</span></div>

<div id="filter-popup">
  <div class="filter-header">
    <h3>🔎 Filtros de Clientes</h3>
    <button class="filter-popup-close" onclick="document.getElementById('filter-popup').classList.remove('active')">✕</button>
  </div>
  <div class="filter-content">
    {regional_group}
    {area_group}
    {id_group}
    {name_group}
    {vendedor_group}
    {supervisor_group}
  </div>
  <div class="filter-actions">
    <button id="btn-search">🔍 Buscar</button>
    <button id="btn-clear">🔄 Limpar</button>
    <button id="btn-deselect">❌ Desmarcar</button>
    <button id="btn-toggle">👁️ Toggle</button>
  </div>
</div>

<script>
  document.getElementById("filter-toggle").onclick = function() {{
    document.getElementById("filter-popup").classList.add("active");
  }};
  
  // Esperar o DOM e Leaflet carregarem completamente
  function initFilters() {{
    // Buscar o mapa e feature group dinamicamente
    var map = null;
    var group = null;
    
    // Tentar encontrar o objeto do mapa Leaflet
    if (typeof L !== 'undefined') {{
      for (var key in window) {{
        try {{
          if (window[key] && window[key]._leaflet_id && window[key].getCenter) {{
            map = window[key];
            console.log('Mapa encontrado:', key);
            break;
          }}
        }} catch(e) {{}}
      }}
    }}
    
    if (!map) {{
      console.error('Mapa não encontrado! Tentando novamente em 500ms...');
      setTimeout(initFilters, 500);
      return;
    }}
    
    // Encontrar o FeatureGroup
    map.eachLayer(function(layer) {{
      if (layer instanceof L.FeatureGroup) {{
        group = layer;
        console.log('FeatureGroup encontrado');
      }}
    }});
    
    if (!group) {{
      console.error('FeatureGroup não encontrado! Tentando novamente em 500ms...');
      setTimeout(initFilters, 500);
      return;
    }}
    
    console.log('✓ Mapa e FeatureGroup inicializados com sucesso');
    
    // Contagem de marcadores
    function countVisible() {{
      var n = 0;
      group.eachLayer(function(l) {{
        if (map.hasLayer(l)) n += 1;
      }});
      var el = document.getElementById('marker-count');
      if (el) el.textContent = n;
    }}
    map.on('layeradd layerremove', countVisible);
    countVisible();
    
    // Construir índice de marcadores
    var markerData = [];
    group.eachLayer(function(marker) {{
      // Buscar o elemento HTML do marcador
      var icon = marker.getElement();
      if (icon) {{
        var markerDiv = icon.querySelector('.custom-marker');
        if (markerDiv) {{
          var data = {{
            marker: marker,
            id: markerDiv.getAttribute('data-id') || '',
            cliente: markerDiv.getAttribute('data-cliente') || '',
            rota: markerDiv.getAttribute('data-rota') || '',
            vendedor: markerDiv.getAttribute('data-vendedor') || '',
            supervisor: markerDiv.getAttribute('data-supervisor') || '',
            regional: markerDiv.getAttribute('data-regional') || ''
          }};
          markerData.push(data);
        }}
      }}
    }});
    
    console.log('Total marcadores indexados:', markerData.length);
    if (markerData.length > 0) {{
      console.log('Exemplo de dados extraídos:', markerData[0]);
    }}
    
    // Busca interna nos grupos de filtros
    document.querySelectorAll('.filter-search').forEach(function(input) {{
      input.addEventListener('input', function() {{
        var term = this.value.toLowerCase();
        var scrollbox = this.parentElement.querySelector('.scrollbox');
        scrollbox.querySelectorAll('label').forEach(function(label) {{
          var text = label.textContent.toLowerCase();
          label.style.display = text.includes(term) ? 'flex' : 'none';
        }});
      }});
    }});
    
    // Selecionar todos
    document.querySelectorAll('.check-all').forEach(function(checkbox) {{
      checkbox.addEventListener('change', function() {{
        var scrollbox = this.parentElement.parentElement.querySelector('.scrollbox');
        var checkboxes = scrollbox.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(cb) {{
          cb.checked = checkbox.checked;
        }});
      }});
    }});
    
    // Botão Buscar
    document.getElementById('btn-search').addEventListener('click', function() {{
      var selectedRegionais = Array.from(document.querySelectorAll('#regional-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      var selectedRotas = Array.from(document.querySelectorAll('#area-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      var selectedIds = Array.from(document.querySelectorAll('#id-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      var selectedClientes = Array.from(document.querySelectorAll('#name-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      var selectedVendedores = Array.from(document.querySelectorAll('#vendedor-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      var selectedSupervisores = Array.from(document.querySelectorAll('#supervisor-group .scrollbox input:checked')).map(function(cb) {{ return cb.value; }});
      
      console.log('=== FILTROS SELECIONADOS ===');
      console.log('Regionais:', selectedRegionais);
      console.log('Rotas:', selectedRotas);
      console.log('IDs:', selectedIds);
      console.log('Clientes:', selectedClientes);
      console.log('Vendedores:', selectedVendedores);
      console.log('Supervisores:', selectedSupervisores);
      
      var visibleCount = 0;
      var hiddenCount = 0;
      var debugCount = 0;
      
      markerData.forEach(function(item) {{
        var show = true;
        var reasons = [];
        
        if (selectedRegionais.length > 0 && selectedRegionais.indexOf(item.regional) === -1) {{
          show = false;
          reasons.push('regional não match');
        }}
        if (selectedRotas.length > 0) {{
          if (selectedRotas.indexOf(item.rota) === -1) {{
            show = false;
            reasons.push('rota não match: "' + item.rota + '" não está em ' + JSON.stringify(selectedRotas));
          }}
        }}
        if (selectedIds.length > 0 && selectedIds.indexOf(item.id) === -1) {{
          show = false;
          reasons.push('id não match');
        }}
        if (selectedClientes.length > 0 && selectedClientes.indexOf(item.cliente) === -1) {{
          show = false;
          reasons.push('cliente não match');
        }}
        if (selectedVendedores.length > 0 && selectedVendedores.indexOf(item.vendedor) === -1) {{
          show = false;
          reasons.push('vendedor não match');
        }}
        if (selectedSupervisores.length > 0 && selectedSupervisores.indexOf(item.supervisor) === -1) {{
          show = false;
          reasons.push('supervisor não match');
        }}
        
        if (debugCount < 3) {{
          console.log('Item', debugCount + 1, ':', {{
            id: item.id,
            cliente: item.cliente,
            rota: item.rota,
            regional: item.regional,
            vendedor: item.vendedor,
            supervisor: item.supervisor,
            show: show,
            reasons: reasons
          }});
          debugCount++;
        }}
        
        if (show) {{
          if (!map.hasLayer(item.marker)) {{
            group.addLayer(item.marker);
          }}
          visibleCount++;
        }} else {{
          if (map.hasLayer(item.marker)) {{
            group.removeLayer(item.marker);
          }}
          hiddenCount++;
        }}
      }});
      
      console.log('=== RESULTADO ===');
      console.log('Visíveis:', visibleCount, 'Ocultos:', hiddenCount);
      countVisible();
      document.getElementById('filter-popup').classList.remove('active');
    }});
    
    // Botão Limpar
    document.getElementById('btn-clear').addEventListener('click', function() {{
      document.querySelectorAll('.filter-group input[type="checkbox"]').forEach(function(cb) {{
        cb.checked = false;
      }});
      markerData.forEach(function(item) {{
        if (!map.hasLayer(item.marker)) {{
          group.addLayer(item.marker);
        }}
      }});
      countVisible();
    }});
    
    // Botão Desmarcar
    document.getElementById('btn-deselect').addEventListener('click', function() {{
      document.querySelectorAll('.filter-group input[type="checkbox"]').forEach(function(cb) {{
        cb.checked = false;
      }});
    }});
    
    // Botão Toggle
    document.getElementById('btn-toggle').addEventListener('click', function() {{
      markerData.forEach(function(item) {{
        if (map.hasLayer(item.marker)) {{
          group.removeLayer(item.marker);
        }} else {{
          group.addLayer(item.marker);
        }}
      }});
      countVisible();
    }});
  }}
  
  // Iniciar quando DOM estiver pronto
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initFilters);
  }} else {{
    // DOM já carregado, mas dar tempo para Leaflet inicializar
    setTimeout(initFilters, 1000);
  }}
</script>
"""

    html = html.replace(
        "</body>",
        legend_html + overlay + "</body>"
    )

    return html
