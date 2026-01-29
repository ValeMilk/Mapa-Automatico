# Otimizações de Performance

## Problema Original
- Outros PCs demoravam muito para acessar http://10.1.1.115:3000/
- Primeira requisição aos mapas era muito lenta (geração sob demanda)

## Soluções Implementadas

### 1. Pré-geração de Mapas na Inicialização
**O que foi feito:**
- Adicionada função `gerar_mapas_iniciais()` que cria todos os 5 mapas quando o servidor inicia
- Mapas são gerados uma única vez no boot do container
- Eliminada geração síncrona durante requisições HTTP

**Resultado:**
- Primeira requisição agora retorna arquivo já pronto
- Tempo de resposta reduzido de ~10-15s para ~0.3s

### 2. Cache Inteligente
**O que foi feito:**
- Removidas verificações `if not os.path.exists()` das rotas
- Cache de 5 minutos na função `atualizar_mapa()`
- Evita regenerações desnecessárias

**Resultado:**
- Menos processamento redundante
- Servidor mais responsivo

### 3. Auto-atualização em Background
**O que já existia (mantido):**
- Thread timer que atualiza mapas a cada 5 minutos
- Atualização não bloqueia requisições HTTP
- Sistema sempre servindo dados atualizados

## Métricas de Performance

### Antes:
- Página principal: ~1-2s (primeira vez)
- Mapas: ~10-15s (primeira vez, geração sob demanda)

### Depois:
- Página principal: ~0.15s
- Mapas: ~0.32s (arquivo pré-gerado)

## Próximas Otimizações Possíveis

1. **Compressão GZIP**: Habilitar no Gunicorn para reduzir tamanho de HTML
2. **CDN para assets estáticos**: Logo e CSS externos
3. **Índices no SQL Server**: Adicionar índices em M06_DTSAIDA, M06_ID_CLIENTE
4. **Pooling de conexões**: Reutilizar conexões PyODBC
5. **Minificação HTML**: Remover espaços dos mapas Folium gerados
