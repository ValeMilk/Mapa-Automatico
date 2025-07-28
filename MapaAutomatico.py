import pandas as pd
import pyodbc
import folium
import math
from datetime import datetime
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from datetime import datetime, timedelta

def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))

def build_distance_matrix(coords):
    return [[haversine_distance(c1, c2) for c2 in coords] for c1 in coords]

def solve_tsp(distance_matrix):
    size = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(size, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        return int(distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)] * 1000)

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 10

    solution = routing.SolveWithParameters(params)
    if solution:
        idx = routing.Start(0)
        route = []
        while not routing.IsEnd(idx):
            route.append(manager.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        route.append(manager.IndexToNode(idx))
        return route
    return list(range(size))

def gerar_mapa_com_query(tipo):
    print("Conectando ao banco...")
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=10.1.0.3\\SQLSTANDARD;"
        "DATABASE=dbactions;"
        "UID=analistarpt;"
        "PWD=mM=DU9lUd3C$qb@"
    )
    conn = pyodbc.connect(conn_str)

    if tipo == 1:
        nome_arquivo = "mapa_motorista.html"
        query = """SET DATEFIRST 7;
        WITH DataReferencia AS (
            SELECT CAST(
                DATEADD(DAY, 
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
                dt.M06_ID_CLIENTE AS CODIGO,
                dt.M06_ID_A76 AS OP,
                c.A00_FANTASIA AS NOME_FANTASIA,
                c.A00_LAT AS LATITUDE,
                c.A00_LONG AS LONGITUDE,
                m.M13_DESC AS MOTORISTA,
                SUM(dt.M06_TOTPRO) AS FATURAMENTO,
                ROW_NUMBER() OVER (
                    PARTITION BY dt.M06_ID_CLIENTE 
                    ORDER BY dt.M06_DTSAIDA
                ) AS rn
            FROM M06 AS dt
            JOIN A00 AS c ON dt.M06_ID_CLIENTE = c.A00_ID
            JOIN M13 AS m ON dt.M06_ID_M13 = m.M13_ID
            JOIN DataReferencia dr ON CAST(dt.M06_DTSAIDA AS DATE) = dr.DATA_ENTREGA
            WHERE 
                c.A00_STATUS = 1
                AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
                AND dt.M06_STATUS IN (1, 3)
            GROUP BY 
                dt.M06_STATUS, dt.M06_DTSAIDA, dt.M06_ID_CLIENTE, dt.M06_ID_A76,
                c.A00_FANTASIA, c.A00_LAT, c.A00_LONG, m.M13_DESC
        )
        SELECT M06_DTSAIDA, CODIGO, OP, NOME_FANTASIA, LATITUDE, LONGITUDE, MOTORISTA, FATURAMENTO
        FROM RankedData
        WHERE rn = 1
        ORDER BY M06_DTSAIDA ASC;"""
    elif tipo == 2:
        nome_arquivo = "mapa_interior_semana.html"
        query = """ SET DATEFIRST 7;  -- domingo = 1, segunda = 2, etc.

WITH SemanaAtual AS (
    -- Calcula a data de segunda e terça da SEMANA CORRENTE,
    -- independentemente do dia em que a query for executada
    SELECT
      CAST(
        DATEADD(
          DAY,
          2 - DATEPART(WEEKDAY, GETDATE()), 
          CAST(GETDATE() AS DATE)
        ) 
      AS DATE) AS DataSegunda,
      CAST(
        DATEADD(
          DAY,
          3 - DATEPART(WEEKDAY, GETDATE()), 
          CAST(GETDATE() AS DATE)
        ) 
      AS DATE) AS DataTerca
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
      -- filtra apenas as saídas de segunda e terça desta semana
      AND CAST(dt.M06_DTSAIDA AS DATE) 
          IN (sa.DataSegunda, sa.DataTerca)
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
    elif tipo == 3:
        nome_arquivo = "mapa_motorista_do_dia.html"
        query = """SET DATEFIRST 7;
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
                dt.M06_ID_CLIENTE AS CODIGO,
                dt.M06_ID_A76 AS OP,
                c.A00_FANTASIA AS NOME_FANTASIA,
                c.A00_LAT AS LATITUDE,
                c.A00_LONG AS LONGITUDE,
                m.M13_DESC AS MOTORISTA,
                SUM(dt.M06_TOTPRO) AS FATURAMENTO,
                ROW_NUMBER() OVER (
                    PARTITION BY dt.M06_ID_CLIENTE 
                    ORDER BY dt.M06_DTSAIDA
                ) AS rn
            FROM M06 AS dt
            JOIN A00 AS c ON dt.M06_ID_CLIENTE = c.A00_ID
            JOIN M13 AS m ON dt.M06_ID_M13 = m.M13_ID
            JOIN DataReferencia dr ON CAST(dt.M06_DTSAIDA AS DATE) = dr.DATA_ENTREGA
            WHERE 
                c.A00_STATUS = 1
                AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
                AND dt.M06_STATUS IN (1, 3)
            GROUP BY 
                dt.M06_STATUS, dt.M06_DTSAIDA, dt.M06_ID_CLIENTE, dt.M06_ID_A76,
                c.A00_FANTASIA, c.A00_LAT, c.A00_LONG, m.M13_DESC
        )
        SELECT M06_DTSAIDA, CODIGO, OP, NOME_FANTASIA, LATITUDE, LONGITUDE, MOTORISTA, FATURAMENTO
        FROM RankedData
        WHERE rn = 1
        ORDER BY M06_DTSAIDA ASC;"""
    else:
        nome_arquivo = "mapa_cliente.html"
        query = """WITH RankedData AS (
            SELECT 
                dt.M06_STATUS,
                dt.M06_DTSAIDA,
                dt.M06_ID_CLIENTE AS CODIGO,
                dt.M06_ID_A76 AS OP,
                c.A00_FANTASIA AS NOME_FANTASIA,
                c.A00_LAT AS LATITUDE,
                c.A00_LONG AS LONGITUDE,
                SUM(dt.M06_TOTPRO) AS FATURAMENTO,
                ROW_NUMBER() OVER (
                    PARTITION BY dt.M06_ID_CLIENTE 
                    ORDER BY dt.M06_DTSAIDA
                ) AS rn
            FROM M06 AS dt
            JOIN A00 AS c ON dt.M06_ID_CLIENTE = c.A00_ID
            WHERE 
                c.A00_STATUS = 1
                AND CAST(dt.M06_DTSAIDA AS DATE) BETWEEN CAST(GETDATE() AS DATE) AND CAST(DATEADD(DAY, 5, GETDATE()) AS DATE)
                AND dt.M06_ID_A76 IN (38, 39, 100, 1171, 101, 172, 112, 130, 113)
                AND dt.M06_STATUS IN (1, 3)
            GROUP BY 
                dt.M06_STATUS, dt.M06_DTSAIDA, dt.M06_ID_CLIENTE, dt.M06_ID_A76,
                c.A00_FANTASIA, c.A00_LAT, c.A00_LONG
        )
        SELECT M06_DTSAIDA, CODIGO, OP, NOME_FANTASIA, LATITUDE, LONGITUDE, FATURAMENTO
        FROM RankedData
        WHERE rn = 1
        ORDER BY M06_DTSAIDA ASC;"""

    print("Executando query...")
    df = pd.read_sql(query, conn)
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
    df['FATURAMENTO'] = pd.to_numeric(df['FATURAMENTO'], errors='coerce')
    df['M06_DTSAIDA'] = pd.to_datetime(df['M06_DTSAIDA']).dt.date
    print(f"🔍 Tipo: {tipo} | Registros: {len(df)}")

     # coordenadas padrão (CD ValeMilk)
    casa_motorista = (-3.7572635398641, -38.5854081195323)
# segunda casa para o mapa interior da semana
    casa_interior  = (-3.812116512138767,-39.258664813321374)  # coloque aí as coordenadas que quiser

    origem = casa_interior if tipo == 2 else casa_motorista

# --- Cria o mapa a partir da origem correta ---
    mapa = folium.Map(location=origem, zoom_start=10)

# --- Marca a origem no mapa ---
    folium.Marker(
        origem,
    icon=folium.Icon(color='gray', icon='home', prefix='fa'),
    tooltip='CD - VALEMILK' if tipo != 2 else 'Casa Interior'
).add_to(mapa)


    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'cadetblue', 'pink', 'black']

    if tipo in [1,2,3]:
        df['MOTORISTA'] = df.get('MOTORISTA', 'DESCONHECIDO')
        truck_colors = {t: colors[i % len(colors)] for i, t in enumerate(df['MOTORISTA'].dropna().unique())}

        for truck, grp in df.groupby('MOTORISTA'):
            clientes_validos = grp[grp['LATITUDE'].notnull() & grp['LONGITUDE'].notnull()].reset_index(drop=True)
            if clientes_validos.empty:
                continue

            coords = [origem] + list(zip(clientes_validos['LATITUDE'], clientes_validos['LONGITUDE']))
            dm = build_distance_matrix(coords)
            route = solve_tsp(dm)
            ordered_coords = [coords[i] for i in route if i < len(coords)]

            color = truck_colors[truck]
            fg = folium.FeatureGroup(name=f'{truck}')
            count = 1
            for i in route[1:]:
                if i == 0 or (i - 1) >= len(clientes_validos):
                    continue
                row = clientes_validos.iloc[i - 1]
                loc = (row['LATITUDE'], row['LONGITUDE'])
                nome = row['NOME_FANTASIA']
                codigo = row['CODIGO']
                icon_html = f"<div style='width:30px;height:30px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;'>{count}</div>"
                folium.Marker(loc, icon=folium.DivIcon(html=icon_html), tooltip=f"{count} - {nome}", popup=f"<b>{nome}</b><br>Cód: {codigo}").add_to(fg)
                folium.PolyLine([ordered_coords[count - 1], loc], color=color, weight=2).add_to(fg)
                count += 1
            fg.add_to(mapa)
    else:
        df['MOTORISTA'] = 'CLIENTES'
        datas_unicas = sorted(df['M06_DTSAIDA'].unique())
        data_colors = {data: colors[i % len(colors)] for i, data in enumerate(datas_unicas)}
        for data, grupo_data in df.groupby('M06_DTSAIDA'):
            fg = folium.FeatureGroup(name=f'Saída: {data.strftime("%d/%m/%Y")}')
            color = data_colors[data]
            for idx, row in grupo_data.iterrows():
                loc = (row['LATITUDE'], row['LONGITUDE'])
                nome = row['NOME_FANTASIA']
                codigo = row['CODIGO']
                icon_html = f"<div style='width:30px;height:30px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;'>{idx+1}</div>"
                folium.Marker(loc, icon=folium.DivIcon(html=icon_html), tooltip=f"{nome} - {data.strftime('%d/%m')}", popup=f"<b>{nome}</b><br>Cód: {codigo}<br>Data: {data.strftime('%d/%m/%Y')}").add_to(fg)
            fg.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    df_group = df.groupby('MOTORISTA').agg(
        FATURAMENTO_TOTAL=('FATURAMENTO', 'sum'),
        CLIENTES=('CODIGO', 'nunique')
    ).reset_index()

    faturamento_total = df['FATURAMENTO'].sum()
    total_clientes = df['CODIGO'].nunique()

    legenda_html = (
        f"<div style='position:fixed;bottom:50px;left:50px;width:300px;"
        f"background:white;border:2px solid grey;z-index:9999;padding:10px;"
        f"box-shadow:2px 2px 5px rgba(0,0,0,0.3);font-size:14px;'>"
        f"<b>Clientes totais:</b> {total_clientes}<br>"
        f"<b>Faturamento total:</b> R$ {faturamento_total:,.2f}<br>"
        f"<b>Atualizado:</b> {datetime.now().strftime('%d/%m/%Y')}<br>"
        f"<b>Data de Saída:</b> {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y') if tipo == 1 else datetime.now().strftime('%d/%m/%Y')}<br><br>"
    )

    if tipo == 1:
        legenda_html += ''.join([
            f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
            f"<div style='width:15px;height:15px;background:{truck_colors.get(row['MOTORISTA'], 'gray')};"
            f"border-radius:50%;margin-right:8px;'></div>"
            f"<b>{row['MOTORISTA'].upper()}</b>: R$ {row['FATURAMENTO_TOTAL']:,.2f}"
            f"</div>"
            for _, row in df_group.iterrows()
        ])
    elif tipo in [3,2]:
        legenda_html += ''.join([
            f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
            f"<div style='width:15px;height:15px;background:{truck_colors.get(row['MOTORISTA'], 'gray')};"
            f"border-radius:50%;margin-right:8px;'></div>"
            f"<b>{row['MOTORISTA'].upper()}</b>: R$ {row['FATURAMENTO_TOTAL']:,.2f}"
            f"</div>"
            for _, row in df_group.iterrows()
        ])
    else:
        legenda_html += "<br><b>Datas:</b><br>" + ''.join([
            f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
            f"<div style='width:15px;height:15px;background:{data_colors[d]};"
            f"border-radius:50%;margin-right:8px;'></div>{d.strftime('%d/%m/%Y')}</div>"
            for d in datas_unicas
        ])

    legenda_html += "</div>"
    mapa.get_root().html.add_child(folium.Element(legenda_html))
    mapa.save(nome_arquivo)
    print(f"✅ Mapa salvo em: {nome_arquivo}")
