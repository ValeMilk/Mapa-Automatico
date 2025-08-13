import pandas as pd
import pyodbc
import folium
import math
from datetime import datetime, timedelta

# --- Utilitários ---
def haversine_distance(coord1, coord2):
    R = 6371
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def greedy_order(block_df, start_coord):
    """
    Ordena as visitas do bloco pelo vizinho mais próximo (greedy), começando em start_coord.
    Retorna uma lista de índices do block_df na ordem visitada.
    """
    if block_df.empty:
        return []

    remaining = block_df.index.tolist()
    order = []
    curr = start_coord

    while remaining:
        # escolhe o ponto restante mais próximo do atual
        nearest_idx = min(
            remaining,
            key=lambda i: haversine_distance(
                curr, (block_df.at[i, 'LATITUDE'], block_df.at[i, 'LONGITUDE'])
            )
        )
        order.append(nearest_idx)
        curr = (block_df.at[nearest_idx, 'LATITUDE'], block_df.at[nearest_idx, 'LONGITUDE'])
        remaining.remove(nearest_idx)

    return order, curr  # retorna também a última coordenada

def gerar_mapa_com_query(tipo):
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=10.1.0.3\\SQLSTANDARD;"
        "DATABASE=dbactions;"
        "UID=analistarpt;"
        "PWD=mM=DU9lUd3C$qb@"
    )
    conn = pyodbc.connect(conn_str)

    # montar query e nome de arquivo
    if tipo == 1:
        nome_arquivo = "mapa_motorista.html"
        query = """ SET DATEFIRST 7;

WITH DataReferencia AS (
    SELECT CAST(
        DATEADD(
            DAY, 
            CASE 
                WHEN DATEPART(WEEKDAY, GETDATE()) = 7 THEN 2
                ELSE 1
            END, 
            GETDATE()
        ) AS DATE
    ) AS DATA_ENTREGA
),

RankedData AS (
    SELECT 
        dt.M06_STATUS,
        dt.M06_DTSAIDA,
        dt.M06_ID_CLIENTE    AS CODIGO,
        dt.M06_ID_A76        AS OP,
        c.A00_FANTASIA       AS NOME_FANTASIA,
        c.A00_LAT            AS LATITUDE,
        c.A00_LONG           AS LONGITUDE,
        m.M13_DESC           AS MOTORISTA,
        c.A00_ID_A56_SEMANA  AS A00_ID_A56_SEMANA,
        c.A00_ID_A56_SABADO  AS A00_ID_A56_SABADO,
        SUM(dt.M06_TOTPRO)   AS FATURAMENTO,
        ROW_NUMBER() OVER (
            PARTITION BY dt.M06_ID_CLIENTE 
            ORDER BY dt.M06_DTSAIDA
        ) AS rn
    FROM M06 AS dt
    JOIN A00 AS c 
      ON dt.M06_ID_CLIENTE = c.A00_ID
    JOIN M13 AS m 
      ON dt.M06_ID_M13    = m.M13_ID
    JOIN DataReferencia AS dr 
      ON CAST(dt.M06_DTSAIDA AS DATE) = dr.DATA_ENTREGA
    WHERE 
        c.A00_STATUS    = 1
        AND dt.M06_ID_A76  IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
        AND dt.M06_STATUS  IN (1, 3)
    GROUP BY 
        dt.M06_STATUS, dt.M06_DTSAIDA, dt.M06_ID_CLIENTE, dt.M06_ID_A76,
        c.A00_FANTASIA, c.A00_LAT, c.A00_LONG, m.M13_DESC,
        c.A00_ID_A56_SEMANA, c.A00_ID_A56_SABADO
)

SELECT 
    M06_DTSAIDA,
    CODIGO,
    OP,
    NOME_FANTASIA,
    LATITUDE,
    LONGITUDE,
    MOTORISTA,
    A00_ID_A56_SEMANA,
    A00_ID_A56_SABADO,
    FATURAMENTO
FROM RankedData
WHERE rn = 1
ORDER BY M06_DTSAIDA ASC;
"""
    elif tipo == 2:
        nome_arquivo = "mapa_cliente.html"
        query = """ WITH RankedData AS (
    SELECT 
        dt.M06_STATUS,
        dt.M06_DTSAIDA,
        dt.M06_ID_CLIENTE      AS CODIGO,
        dt.M06_ID_A76          AS OP,
        c.A00_FANTASIA         AS NOME_FANTASIA,
        c.A00_LAT              AS LATITUDE,
        c.A00_LONG             AS LONGITUDE,
        c.A00_ID_A56_SEMANA    AS A00_ID_A56_SEMANA,
        c.A00_ID_A56_SABADO    AS A00_ID_A56_SABADO,
        SUM(dt.M06_TOTPRO)     AS FATURAMENTO,
        ROW_NUMBER() OVER (
            PARTITION BY dt.M06_ID_CLIENTE 
            ORDER BY dt.M06_DTSAIDA
        )                     AS rn
    FROM M06 AS dt
    JOIN A00 AS c 
      ON dt.M06_ID_CLIENTE = c.A00_ID
    WHERE 
        c.A00_STATUS = 1
        AND CAST(dt.M06_DTSAIDA AS DATE) 
            BETWEEN CAST(GETDATE() AS DATE) 
                AND CAST(DATEADD(DAY, 5, GETDATE()) AS DATE)
        AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
        AND dt.M06_STATUS IN (1, 3)
    GROUP BY 
        dt.M06_STATUS, 
        dt.M06_DTSAIDA, 
        dt.M06_ID_CLIENTE, 
        dt.M06_ID_A76,
        c.A00_FANTASIA, 
        c.A00_LAT, 
        c.A00_LONG,
        c.A00_ID_A56_SEMANA, 
        c.A00_ID_A56_SABADO
)
SELECT 
    M06_DTSAIDA,
    CODIGO,
    OP,
    NOME_FANTASIA,
    LATITUDE,
    LONGITUDE,
    A00_ID_A56_SEMANA,
    A00_ID_A56_SABADO,
    FATURAMENTO
FROM RankedData
WHERE rn = 1
ORDER BY M06_DTSAIDA ASC;
"""
    elif tipo == 3:
        nome_arquivo = "mapa_motorista_do_dia.html"
        query = """ SET DATEFIRST 7;

WITH DataReferencia AS (
    SELECT CAST(
        DATEADD(DAY, 
            CASE 
                WHEN DATEPART(WEEKDAY, GETDATE()) = 7 THEN 2
                ELSE 0
            END, 
            GETDATE()
        ) AS DATE
    ) AS DATA_ENTREGA
),

RankedData AS (
    SELECT 
        dt.M06_STATUS,
        dt.M06_DTSAIDA,
        dt.M06_ID_CLIENTE    AS CODIGO,
        dt.M06_ID_A76        AS OP,
        c.A00_FANTASIA       AS NOME_FANTASIA,
        c.A00_LAT            AS LATITUDE,
        c.A00_LONG           AS LONGITUDE,
        m.M13_DESC           AS MOTORISTA,
        c.A00_ID_A56_SEMANA  AS A00_ID_A56_SEMANA,
        c.A00_ID_A56_SABADO  AS A00_ID_A56_SABADO,
        SUM(dt.M06_TOTPRO)   AS FATURAMENTO,
        ROW_NUMBER() OVER (
            PARTITION BY dt.M06_ID_CLIENTE 
            ORDER BY dt.M06_DTSAIDA
        ) AS rn
    FROM M06 AS dt
    JOIN A00 AS c 
      ON dt.M06_ID_CLIENTE = c.A00_ID
    JOIN M13 AS m 
      ON dt.M06_ID_M13    = m.M13_ID
    JOIN DataReferencia AS dr 
      ON CAST(dt.M06_DTSAIDA AS DATE) = dr.DATA_ENTREGA
    WHERE 
        c.A00_STATUS    = 1
        AND dt.M06_ID_A76  IN (38,39,100,1171,101,172,112,130,113)
        AND dt.M06_STATUS  IN (1,3)
    GROUP BY 
        dt.M06_STATUS, dt.M06_DTSAIDA, dt.M06_ID_CLIENTE, dt.M06_ID_A76,
        c.A00_FANTASIA, c.A00_LAT, c.A00_LONG, m.M13_DESC,
        c.A00_ID_A56_SEMANA, c.A00_ID_A56_SABADO
)

SELECT 
    M06_DTSAIDA,
    CODIGO,
    OP,
    NOME_FANTASIA,
    LATITUDE,
    LONGITUDE,
    MOTORISTA,
    A00_ID_A56_SEMANA,
    A00_ID_A56_SABADO,
    FATURAMENTO
FROM RankedData
WHERE rn = 1
ORDER BY M06_DTSAIDA ASC;
"""
    elif tipo == 4:
        nome_arquivo = "mapa_interior_semana.html"
        query = """ SET DATEFIRST 7;

WITH SemanaAtual AS (
    SELECT
        CAST(DATEADD(DAY, 2 - DATEPART(WEEKDAY, GETDATE()), CAST(GETDATE() AS DATE)) AS DATE) AS DataSegunda,
        CAST(DATEADD(DAY, 3 - DATEPART(WEEKDAY, GETDATE()), CAST(GETDATE() AS DATE)) AS DATE) AS DataTerca
),
RankedData AS (
    SELECT
        dt.M06_DTSAIDA,
        dt.M06_ID_CLIENTE    AS CODIGO,
        dt.M06_ID_A76        AS OP,
        c.A00_FANTASIA       AS NOME_FANTASIA,
        c.A00_LAT            AS LATITUDE,
        c.A00_LONG           AS LONGITUDE,
        m.M13_DESC           AS MOTORISTA,
        SUM(dt.M06_TOTPRO)   AS FATURAMENTO,
        ROW_NUMBER() OVER (
            PARTITION BY dt.M06_ID_CLIENTE
            ORDER BY dt.M06_DTSAIDA
        ) AS rn
    FROM M06 AS dt
    JOIN A00 AS c ON c.A00_ID   = dt.M06_ID_CLIENTE
    JOIN M13 AS m ON m.M13_ID   = dt.M06_ID_M13
    CROSS JOIN SemanaAtual sa
    WHERE
        c.A00_STATUS       = 1
        AND dt.M06_ID_A76  IN (45, 46, 104, 105, 110, 111, 114, 115)
        AND dt.M06_STATUS  IN (1, 3)
        AND CAST(dt.M06_DTSAIDA AS DATE) IN (sa.DataSegunda, sa.DataTerca)
    GROUP BY
        dt.M06_DTSAIDA,
        dt.M06_ID_CLIENTE,
        dt.M06_ID_A76,
        c.A00_FANTASIA,
        c.A00_LAT,
        c.A00_LONG,
        m.M13_DESC
)
SELECT
    M06_DTSAIDA,
    CODIGO,
    OP,
    NOME_FANTASIA,
    LATITUDE,
    LONGITUDE,
    MOTORISTA,
    FATURAMENTO
FROM RankedData
WHERE rn = 1
ORDER BY M06_DTSAIDA;
"""
    else:
        raise ValueError(f"Tipo inesperado: {tipo}")

    df = pd.read_sql(query, conn)

    # --- normalizações ---
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
    if 'M06_DTSAIDA' in df.columns:
        df['M06_DTSAIDA'] = pd.to_datetime(df['M06_DTSAIDA'], errors='coerce')
    if 'A00_ID_A56_SEMANA' in df.columns:
        df['A00_ID_A56_SEMANA'] = pd.to_numeric(df['A00_ID_A56_SEMANA'], errors='coerce').fillna(3).astype(int)
    else:
        df['A00_ID_A56_SEMANA'] = 3

    casa_motorista = (-3.7572635, -38.5854081)
    casa_interior  = (-3.8121165, -39.2586648)
    origem = casa_interior if tipo == 4 else casa_motorista

    mapa = folium.Map(location=origem, zoom_start=10)
    folium.Marker(
        origem,
        icon=folium.Icon(color='gray', icon='home', prefix='fa'),
        tooltip='Casa Interior' if tipo == 4 else 'CD - VALEMILK'
    ).add_to(mapa)

    colors = ['red','blue','green','purple','orange','darkred','darkblue','cadetblue','pink','black']
    total_clientes = df['CODIGO'].nunique() if 'CODIGO' in df.columns else 0
    faturamento_total = df['FATURAMENTO'].sum() if 'FATURAMENTO' in df.columns else 0

    # --- funções auxiliares para desenhar ---
    def add_marker_polyline(feature_group, prev_loc, row, color, idx):
        loc = (row['LATITUDE'], row['LONGITUDE'])
        prio = row.get('A00_ID_A56_SEMANA', 3)
        emo = '☀️' if prio == 1 else ('⚡' if prio == 2 else '🕒')
        icon_html = (
            f"<div style='width:30px;height:30px;border-radius:50%;"
            f"background:{color};display:flex;align-items:center;"
            f"justify-content:center;font-weight:bold;color:white;'>"
            f"{idx}<br>{emo}</div>"
        )
        folium.Marker(
            loc,
            icon=folium.DivIcon(html=icon_html),
            tooltip=f"{idx} - {row.get('CODIGO','')} - {row.get('NOME_FANTASIA','')} ({emo})"
        ).add_to(feature_group)
        folium.PolyLine([prev_loc, loc], color=color, weight=2, opacity=0.8).add_to(feature_group)
        return loc

    # --- tipos 1,3,4: por MOTORISTA ---
    if tipo in [1, 3, 4]:
        if 'MOTORISTA' not in df.columns:
            df['MOTORISTA'] = 'DESCONHECIDO'
        truck_colors = {t: colors[i % len(colors)] for i, t in enumerate(df['MOTORISTA'].dropna().unique())}

        for truck, grp in df.groupby('MOTORISTA'):
            clientes = grp.dropna(subset=['LATITUDE', 'LONGITUDE']).reset_index(drop=False)  # guarda índice original
            if clientes.empty:
                continue

            # divide por prioridade
            p1 = clientes[clientes['A00_ID_A56_SEMANA'] == 1]
            p2 = clientes[clientes['A00_ID_A56_SEMANA'] == 2]
            p3 = clientes[clientes['A00_ID_A56_SEMANA'] == 3]

            ordered_rows = []
            last_loc = origem

            for block in (p1, p2, p3):
                if block.empty:
                    continue
                order, last_loc = greedy_order(block, last_loc)
                ordered_rows += [clientes.loc[i] for i in order]

            fg = folium.FeatureGroup(name=f'Motorista: {truck}')
            prev = origem
            for idx_vis, row in enumerate(ordered_rows, start=1):
                prev = add_marker_polyline(fg, prev, row, truck_colors.get(truck, 'gray'), idx_vis)
            fg.add_to(mapa)

        folium.LayerControl(collapsed=False).add_to(mapa)

        # legenda por motorista
        df_group = df.groupby('MOTORISTA', as_index=False).agg({'FATURAMENTO': 'sum'}).rename(columns={'FATURAMENTO': 'FATURAMENTO_TOTAL'})
        legenda_html = (
            f"<div style='position:fixed;bottom:50px;left:50px;width:300px;"
            f"background:white;border:2px solid grey;z-index:9999;padding:10px;"
            f"box-shadow:2px 2px 5px rgba(0,0,0,0.3);font-size:14px;'>"
            f"<b>Clientes totais:</b> {total_clientes}<br>"
            f"<b>Faturamento total:</b> R$ {faturamento_total:,.2f}<br>"
            f"<b>Atualizado:</b> {datetime.now().strftime('%d/%m/%Y')}<br>"
            f"<b>Data de Saída:</b> {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y') if tipo == 1 else datetime.now().strftime('%d/%m/%Y')}<br><br>"
            f"<b>Prioridades:</b> ☀️=MANHÃ, ⚡= ATÉ 16h, 🕒=DIURNO<br>"
            + ''.join([
                f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
                f"<div style='width:15px;height:15px;background:{truck_colors.get(row['MOTORISTA'], 'gray')};"
                f"border-radius:50%;margin-right:8px;'></div>"
                f"<b>{row['MOTORISTA'].upper()}</b>: R$ {row['FATURAMENTO_TOTAL']:,.2f}"
                f"</div>"
                for _, row in df_group.iterrows()
            ])
            + "</div>"
        )
        mapa.get_root().html.add_child(folium.Element(legenda_html))

    # --- tipo 2: por DATA ---
    elif tipo == 2:
        if 'M06_DTSAIDA' in df.columns:
            datas_unicas = sorted(df['M06_DTSAIDA'].dropna().unique())
        else:
            datas_unicas = []

        data_colors = {d: colors[i % len(colors)] for i, d in enumerate(datas_unicas)}

        for d in datas_unicas:
            fg = folium.FeatureGroup(name=f"Saída: {pd.to_datetime(d).strftime('%d/%m/%Y')}")
            clientes_data = (
                df[(df['M06_DTSAIDA'] == d) & df['LATITUDE'].notna() & df['LONGITUDE'].notna()]
                .reset_index(drop=False)
            )
            if clientes_data.empty:
                continue

            p1 = clientes_data[clientes_data['A00_ID_A56_SEMANA'] == 1]
            p2 = clientes_data[clientes_data['A00_ID_A56_SEMANA'] == 2]
            p3 = clientes_data[clientes_data['A00_ID_A56_SEMANA'] == 3]

            ordered_rows = []
            last_loc = origem
            for block in (p1, p2, p3):
                if block.empty:
                    continue
                order, last_loc = greedy_order(block, last_loc)
                ordered_rows += [clientes_data.loc[i] for i in order]

            prev = origem
            for idx_vis, row in enumerate(ordered_rows, start=1):
                prev = add_marker_polyline(fg, prev, row, data_colors.get(d, 'gray'), idx_vis)

            fg.add_to(mapa)

        folium.LayerControl(collapsed=False).add_to(mapa)

        legenda_html = (
            f"<div style='position:fixed;bottom:50px;left:50px;width:340px;"
            f"background:white;border:2px solid grey;z-index:9999;padding:10px;"
            f"box-shadow:2px 2px 5px rgba(0,0,0,0.3);font-size:14px;'>"
            f"<b>Clientes totais:</b> {total_clientes}<br>"
            f"<b>Faturamento total:</b> R$ {faturamento_total:,.2f}<br>"
            f"<b>Atualizado:</b> {datetime.now().strftime('%d/%m/%Y')}<br>"
            f"<b>Data de Saída:</b> {datetime.now().strftime('%d/%m/%Y')}<br><br>"
            f"<b>Prioridades:</b> ☀️=MANHÃ, ⚡= ATÉ 16h, 🕒=DIURNO<br>"
            f"<b>Datas:</b><br>"
            + ''.join([
                f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
                f"<div style='width:15px;height:15px;background:{data_colors.get(d,'gray')};"
                f"border-radius:50%;margin-right:8px;'></div>{pd.to_datetime(d).strftime('%d/%m/%Y')}</div>"
                for d in datas_unicas
            ])
            + "</div>"
        )
        mapa.get_root().html.add_child(folium.Element(legenda_html))

    # salvar e saída
    mapa.save(nome_arquivo)
    print(f"✅ Mapa salvo em: {nome_arquivo}")
