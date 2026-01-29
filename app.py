from flask import Flask, send_file, render_template_string, url_for, Response
from flask_compress import Compress
import os
import threading
from datetime import datetime
from MapaAutomatico import gerar_mapa_com_query

app = Flask(__name__)
Compress(app)  # Habilita compressão GZIP automática

# Configurações de otimização
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/json'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Vale Milk • Geração de Mapas</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <style>
        * { box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background-color: #F2F2F2;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0066B3;
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
        }
        header img { height: 50px; margin-right: 20px; }
        h1 { font-size: 1.8em; margin: 0; }

        /* Layout */
        .container {
            padding: 60px 20px 0 20px;
            display: flex;
            justify-content: center;
        }
        .columns {
            width: 100%;
            max-width: 1200px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 40px;
        }
        .column {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .column h2 {
            color: #0066B3;
            margin: 0 0 16px 0;
            font-size: 1.3em;
        }

        /* Botões */
        .btn {
            background-color: #0066B3;
            color: white;
            border: none;
            padding: 14px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 10px;
            text-align: center;
            text-decoration: none;
            transition: background-color 0.3s ease;
            width: 280px;
            margin: 10px 0;
        }
        .btn:hover { background-color: #3399FF; }
        .btn i { margin-right: 8px; }

        /* Responsivo */
        @media (max-width: 900px) {
            .columns {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <header>
        <img src="{{ url_for('static', filename='logo_valemilk.png') }}" alt="Vale Milk Logo">
        <h1>Geração de Mapas</h1>
    </header>

    <div class="container">
        <div class="columns">
            <!-- Coluna Esquerda: Capital -->
<div class="column">
  <h2>Capital</h2>

  <form action="/mapa_2" method="get">
    <button class="btn" type="submit">
      <i class="fas fa-calendar-day"></i> 🕐 Mapa geral de pedidos (LJ 81)
    </button>
  </form>

  <form action="/mapa_3" method="get">
    <button class="btn" type="submit">
      <i class="fas fa-user"></i> 🕺 Mapa Entrega Atual (LJ 81)
    </button>
  </form>

  <form action="/mapa_1" method="get">
    <button class="btn" type="submit">
      <i class="fas fa-truck"></i> 🚚 Mapa programação de entrega (LJ 81)
    </button>
  </form>

  <a href="https://app.powerbi.com/view?r=eyJrIjoiZDU0NzI4NDYtZTEyNy00ZGM3LWFjYjEtZmVlNGVjM2JlMzIzIiwidCI6ImU0YTI3ZWNmLWY1MzUtNDg2Zi05Yjc2LWVlZjVmNmNjYzE2NCJ9" target="_blank" class="btn">
    <i class="fas fa-chart-bar"></i> 📊 Estoque minimo LJ 81
  </a>
</div>
            

            <!-- Coluna do Meio: Mapa Geral -->
            <div class="column">
                <h2>Mapa Geral</h2>
                <a href="/mapa_geral" target="_blank" class="btn">
                    <i class="fa-solid fa-map-location-dot"></i> 🌎 Mapa Geral de Clientes 
                </a>
            </div>

            <!-- Coluna Direita: Interior -->
            <div class="column">
                <h2>Interior</h2>
                <form action="/mapa_5" method="get">
                    <button class="btn" type="submit">
                        <i class="fas fa-calendar-alt"></i> 🗓️ Mapa geral de pedidos futuros (LJ 82)
                    </button>
                </form>
                
                <form action="/mapa_4" method="get">
                    <button class="btn" type="submit">
                        <i class="fas fa-user"></i> 🏡 Mapa Interior Carga anterior(LJ 82)
                    </button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/mapa_1")
def mapa_motorista():
    if not os.path.exists("mapa_motorista.html"):
        gerar_mapa_com_query(1)
    return send_file("mapa_motorista.html")

@app.route("/mapa_2")
def mapa_cliente():
    if not os.path.exists("mapa_cliente.html"):
        gerar_mapa_com_query(2)
    return send_file("mapa_cliente.html")

@app.route("/mapa_3")
def mapa_motorista_do_dia():
    if not os.path.exists("mapa_motorista_do_dia.html"):
        gerar_mapa_com_query(3)
    return send_file("mapa_motorista_do_dia.html")

@app.route('/mapa_4')
def rota_interior_semana():
    if not os.path.exists("mapa_interior_semana.html"):
        gerar_mapa_com_query(4)
    return send_file('mapa_interior_semana.html')

@app.route('/mapa_5')
def mapa_interior_geral():
    return send_file('mapa_interior_geral.html')

@app.route('/mapa_geral')
def mapa_geral():
    """Mapa geral de clientes"""
    return send_file('mapa_geral_clientes.html')

def atualizar_mapa(tipo, nome_arquivo):
    try:
        agora = datetime.now()
        atualizar = True

        if os.path.exists(nome_arquivo):
            ultima_modificacao = datetime.fromtimestamp(os.path.getmtime(nome_arquivo))
            diff_minutos = (agora - ultima_modificacao).total_seconds() / 60
            if diff_minutos < 5:  # Atualiza apenas se passou mais de 5 minutos
                print(f"✅ {nome_arquivo} atualizado há {diff_minutos:.1f} min. Pulando.")
                atualizar = False

        if atualizar:
            print(f"⏳ Atualizando {nome_arquivo}...")
            gerar_mapa_com_query(tipo=tipo)
            print(f"✅ {nome_arquivo} atualizado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao atualizar {nome_arquivo}: {e}")

    threading.Timer(300, atualizar_mapa, args=(tipo, nome_arquivo)).start()

def atualizar_mapa_geral(nome_arquivo):
    """Atualiza o mapa geral de clientes"""
    try:
        agora = datetime.now()
        atualizar = True

        if os.path.exists(nome_arquivo):
            ultima_modificacao = datetime.fromtimestamp(os.path.getmtime(nome_arquivo))
            diff_minutos = (agora - ultima_modificacao).total_seconds() / 60
            if diff_minutos < 5:
                print(f"✅ {nome_arquivo} atualizado há {diff_minutos:.1f} min. Pulando.")
                atualizar = False

        if atualizar:
            print(f"⏳ Atualizando {nome_arquivo}...")
            from mapa_geral_module import generate_map_html
            html = generate_map_html()
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {nome_arquivo} atualizado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao atualizar {nome_arquivo}: {e}")

    threading.Timer(300, atualizar_mapa_geral, args=(nome_arquivo,)).start()

def gerar_mapas_iniciais():
    """Gera todos os mapas na inicialização do servidor para evitar lentidão no primeiro acesso"""
    print("🚀 Gerando mapas iniciais...")
    mapas = [
        (1, "mapa_motorista.html"),
        (2, "mapa_cliente.html"),
        (3, "mapa_motorista_do_dia.html"),
        (4, "mapa_interior_semana.html"),
        (5, "mapa_interior_geral.html")
    ]
    
    for tipo, nome in mapas:
        if not os.path.exists(nome):
            print(f"⏳ Gerando {nome}...")
            try:
                gerar_mapa_com_query(tipo)
                print(f"✅ {nome} gerado.")
            except Exception as e:
                print(f"❌ Erro ao gerar {nome}: {e}")
    
    # Gera mapa geral de clientes
    if not os.path.exists("mapa_geral_clientes.html"):
        print(f"⏳ Gerando mapa_geral_clientes.html...")
        try:
            from mapa_geral_module import generate_map_html
            html = generate_map_html()
            with open("mapa_geral_clientes.html", 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ mapa_geral_clientes.html gerado.")
        except Exception as e:
            print(f"❌ Erro ao gerar mapa_geral_clientes.html: {e}")
    
    print("✅ Todos os mapas iniciais foram gerados!")

# Gerar mapas na inicialização
gerar_mapas_iniciais()

# Iniciar atualização automática dos mapas
atualizar_mapa(1, "mapa_motorista.html")
atualizar_mapa(2, "mapa_cliente.html")
atualizar_mapa(3, "mapa_motorista_do_dia.html")
atualizar_mapa(4, "mapa_interior_semana.html")
atualizar_mapa(5, "mapa_interior_geral.html")
atualizar_mapa_geral("mapa_geral_clientes.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
