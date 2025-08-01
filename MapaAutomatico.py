import pandas as pd
import pyodbc
import folium
import math
from datetime import datetime, timedelta
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# --- Utilitários ---
def haversine_distance(coord1, coord2):
    R = 6371
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def build_distance_matrix(coords):
    return [[haversine_distance(c1, c2) for c2 in coords] for c1 in coords]

def solve_tsp(distance_matrix, time_limit=10):
    size = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(size, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def dist_cb(from_idx, to_idx):
        return int(distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)] * 1000)

    idx_cb = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(idx_cb)
    routing.AddDimension(idx_cb, 0, int(1e9), True, 'Distance')

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = time_limit

    sol = routing.SolveWithParameters(params)
    if sol:
        node = routing.Start(0)
        route = []
        while True:
            route.append(manager.IndexToNode(node))
            if routing.IsEnd(node):
                break
            node = sol.Value(routing.NextVar(node))
        return route
    return list(range(size))

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
 """  # mantém exatamente seu SQL original para tipo 1
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
 """  # SQL original para tipo 2
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
        -- agora pegamos direto de c:
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
 """  # SQL original para tipo 3
    elif tipo == 4:
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
            """  # SQL original para tipo 4
    else:
        raise ValueError(f"Tipo inesperado: {tipo}")

    df = pd.read_sql(query, conn)

    # normalizações
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
    if 'M06_DTSAIDA' in df.columns:
        df['M06_DTSAIDA'] = pd.to_datetime(df['M06_DTSAIDA'])
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

    if tipo in [1, 3, 4]:
        # ramo com motorista + TSP com prioridades
        if 'MOTORISTA' not in df.columns:
            df['MOTORISTA'] = 'DESCONHECIDO'
        truck_colors = {t: colors[i % len(colors)] for i, t in enumerate(df['MOTORISTA'].dropna().unique())}

        for truck, grp in df.groupby('MOTORISTA'):
            clientes = grp.dropna(subset=['LATITUDE', 'LONGITUDE']).reset_index(drop=True)
            if clientes.empty:
                continue

            p1 = clientes[clientes.get('A00_ID_A56_SEMANA', 3) == 1]
            p2 = clientes[clientes.get('A00_ID_A56_SEMANA', 3) == 2]
            p3 = clientes[clientes.get('A00_ID_A56_SEMANA', 3) == 3]

            ordered = []
            last_loc = origem
            for block in (p1, p2, p3):
                if block.empty:
                    continue
                coords = [last_loc] + list(zip(block['LATITUDE'], block['LONGITUDE']))
                dm = build_distance_matrix(coords)
                route = solve_tsp(dm)
                if route and route[-1] == 0:
                    route = route[:-1]
                ordered += [block.iloc[i-1] for i in route if i > 0]
                last_loc = coords[route[-1]] if route else last_loc

            fg = folium.FeatureGroup(name=f'Motorista: {truck}')
            prev = origem
            for idx, row in enumerate(ordered, start=1):
                loc = (row['LATITUDE'], row['LONGITUDE'])
                emo = ('☀️' if row.get('A00_ID_A56_SEMANA', 3) == 1 else '⚡' if row.get('A00_ID_A56_SEMANA', 3) == 2 else '🕒')
                icon_html = (
                    f"<div style='width:30px;height:30px;border-radius:50%;"
                    f"background:{truck_colors.get(truck,'gray')};display:flex;align-items:center;"
                    f"justify-content:center;font-weight:bold;color:white;'>"
                    f"{idx}<br>{emo}</div>"
                )
                folium.Marker(
                    loc,
                    icon=folium.DivIcon(html=icon_html),
                    tooltip=f"{idx} - {row.get('CODIGO','')} - {row.get('NOME_FANTASIA','')} ({emo})"
                ).add_to(fg)
                folium.PolyLine([prev, loc], color=truck_colors.get(truck,'gray'), weight=2, opacity=0.8).add_to(fg)
                prev = loc
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
            f"<b>Prioridades:</b> ☀️=MANHA, ⚡= ATÉ 16hrs, 🕒=DIURNO<br>"
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

    elif tipo == 2:
        # tipo 2: TSP por data com prioridades (1,2,3)
        if 'M06_DTSAIDA' in df.columns:
            datas_unicas = sorted(df['M06_DTSAIDA'].dropna().unique())
        else:
            datas_unicas = []

        data_colors = {d: colors[i % len(colors)] for i, d in enumerate(datas_unicas)}

        for d in datas_unicas:
            fg = folium.FeatureGroup(name=f"Saída: {d.strftime('%d/%m/%Y')}")
            clientes_data = df[df['M06_DTSAIDA'] == d].copy()

            p1 = clientes_data[clientes_data.get('A00_ID_A56_SEMANA', 3) == 1]
            p2 = clientes_data[clientes_data.get('A00_ID_A56_SEMANA', 3) == 2]
            p3 = clientes_data[clientes_data.get('A00_ID_A56_SEMANA', 3) == 3]

            ordered = []
            last_loc = origem
            for block in (p1, p2, p3):
                if block.empty:
                    continue
                coords = [last_loc] + list(zip(block['LATITUDE'], block['LONGITUDE']))
                dm = build_distance_matrix(coords)
                route = solve_tsp(dm)
                if route and route[-1] == 0:
                    route = route[:-1]
                ordered += [block.iloc[i-1] for i in route if i > 0]
                last_loc = coords[route[-1]] if route else last_loc

            prev = origem
            for idx, row in enumerate(ordered, start=1):
                loc = (row['LATITUDE'], row['LONGITUDE'])
                emo = ('☀️' if row.get('A00_ID_A56_SEMANA', 3) == 1 else '⚡' if row.get('A00_ID_A56_SEMANA', 3) == 2 else '🕒')
                icon_html = (
                    f"<div style='width:30px;height:30px;border-radius:50%;"
                    f"background:{data_colors.get(d,'gray')};display:flex;align-items:center;"
                    f"justify-content:center;font-weight:bold;color:white;'>"
                    f"{idx}<br>{emo}</div>"
                )
                folium.Marker(
                    loc,
                    icon=folium.DivIcon(html=icon_html),
                    tooltip=f"{idx} - {row.get('CODIGO','')} - {row.get('NOME_FANTASIA','')} ({emo})"
                ).add_to(fg)
                folium.PolyLine([prev, loc], color=data_colors.get(d,'gray'), weight=2, opacity=0.8).add_to(fg)
                prev = loc
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
            f"<b>Prioridades:</b> ☀️=MANHA, ⚡= ATÉ 16hrs, 🕒=DIURNO<br>"
            f"<b>Datas:</b><br>"
            + ''.join([
                f"<div style='display:flex;align-items:center;margin-bottom:5px;'>"
                f"<div style='width:15px;height:15px;background:{data_colors.get(d,'gray')};"
                f"border-radius:50%;margin-right:8px;'></div>{d.strftime('%d/%m/%Y')}</div>"
                for d in datas_unicas
            ])
            + "</div>"
        )
        mapa.get_root().html.add_child(folium.Element(legenda_html))

    # salvar e saída
    mapa.save(nome_arquivo)
    print(f"✅ Mapa salvo em: {nome_arquivo}")