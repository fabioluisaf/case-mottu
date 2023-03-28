import pandas as pd
import numpy as np
import math
import vizinhos as vz

# retorna uma tupla com a lista de vertices e a matriz de adjacencia
def cria_grafo(data_frame: pd.DataFrame):
  df_size = data_frame.shape[0]
  vertices = np.empty((df_size, 2), dtype=float)
  vizinhancas = {}

  for index, _ in data_frame.iterrows():
    lat_radianos = data_frame.iloc[index]["latitude_final_nr"] * math.pi/180
    lon_radianos = data_frame.iloc[index]["longitude_final_nr"] * math.pi/180

    vertices[index] = (lat_radianos, lon_radianos)
    
  return (vertices, vizinhancas)

# calcula a distancia entre dois pontos na superficie de uma esfera, dadas latitude e longitude em radianos
def haversine_formula(lat_1, lon_1, lat_2, lon_2):
  lat_1_rad = lat_1
  lat_2_rad = lat_2

  DELTA_LAT = (lat_2 - lat_1)
  DELTA_LON = (lon_2 - lon_1) 
  RAIO_TERRA = 6371000 # em metros

  A = (math.sin(DELTA_LAT/2) ** 2) + (math.cos(lat_1_rad) * math.cos(lat_2_rad) * (math.sin(DELTA_LON/2) ** 2))
  C = 2 * math.atan2(math.sqrt(A), math.sqrt(1-A))

  return RAIO_TERRA * C

# preenche grafo criando apenas uma aresta nova por vertice
def preenche_grafo_guloso(vertices, vizinhancas: dict[int, vz.Vizinhos]):
  counter = 0

  for i in range(vertices.shape[0]):
    vi = vertices[i]
    vizinhancas[i] = vz.Vizinhos()
    distancias = np.full(vertices.shape[0], -1)

    for j in range(i):
      vj = vertices[j]
      distancias[j] = haversine_formula(vi[0], vi[1], vj[0], vj[1])

    min = np.Inf
    min_index = -1

    for j in range(vertices.shape[0]):
      if distancias[j] < min and distancias[j] > 0:
        min_index = j
        min = distancias[j]

    if min_index != -1:
      vizinhancas[i].add_vizinho(min_index, min)
      vizinhancas[min_index].add_vizinho(i, min)

    counter += 1
    print("Preenchendo aresta #{}".format(counter), end="\r")
  
  print("")

# realiza uma busca em profundidade no grafo a partir do vertice 0
def dfs(vizinhancas: dict[int, vz.Vizinhos]):
  visitados = set()
  qtd_visitados = 0
  pilha = []

  v_atual = 0
  pilha.append(v_atual)

  while(len(pilha) > 0):
    v_atual = pilha.pop()
    print("# Vertices visitados: {}".format(qtd_visitados), end="\r")

    if v_atual not in visitados:
      qtd_visitados += 1
      visitados.add(v_atual)
      pilha.extend(vizinhancas[v_atual].vizinhos)
  
  print("")
  return visitados

def maior_aresta(vizinhancas: dict[int, vz.Vizinhos]):
  max_val = -1
  max_ind = -1
  max_ind2 = -1

  for i in vizinhancas:
    for vizinho in vizinhancas[i].vizinhos:
      custo = vizinhancas[i].get_custo(vizinho)

      if custo > max_val:
        max_val = custo
        max_ind = i
        max_ind2 = vizinho

  return (max_ind, max_ind2 , max_val)

def menor_aresta(vizinhancas: dict[int, vz.Vizinhos]):
  min_val = np.Inf
  min_ind = -1
  min_ind2 = -1

  for i in vizinhancas:
    for vizinho in vizinhancas[i].vizinhos:
      custo = vizinhancas[i].get_custo(vizinho)

      if custo < min_val:
        min_val = custo
        min_ind = i
        min_ind2 = vizinho

  return (min_ind, min_ind2 , min_val)

def vertices_indexados(vertices):
  v_indexados = np.empty((vertices.shape[0], 3), dtype=float)

  for i in range(vertices.shape[0]):
    v_indexados[i][0] = i
    v_indexados[i][1] = vertices[i][0]
    v_indexados[i][2] = vertices[i][1]

  return v_indexados

def get_posicao(vertices_indexados, v_index):
  for i in range(vertices_indexados.shape[0]):
    if vertices_indexados[i][0] == v_index:
      return (vertices_indexados[i][1], vertices_indexados[i][2])

def coord_media(vertices_indexados, v1, v2):
  pos1 = get_posicao(vertices_indexados, v1)
  pos2 = get_posicao(vertices_indexados, v2)

  lat_m = (pos1[0] + pos2[0])/2
  lon_m = (pos1[1] + pos2[1])/2

  return (lat_m, lon_m)

def ajusta_pos_vertice(v_index, nova_lat, nova_lon, vertices_indexados):
  for i in range(vertices_indexados.shape[0]):
    if vertices_indexados[i][0] == v_index:
      vertices_indexados[i][1] = nova_lat
      vertices_indexados[i][2] = nova_lon
      return
    
def agrupa_vertices(v1, v2, vertices_indexados, vizinhancas: dict[int, vz.Vizinhos]):
  index_final = v1 if v1 <= v2 else v2
  index_descartar = v2 if v1 <= v2 else v1

  nova_pos = coord_media(vertices_indexados, index_final, index_descartar)
  ajusta_pos_vertice(index_final, nova_pos[0], nova_pos[1], vertices_indexados)

  for vizinho in [v for v in vizinhancas[index_descartar].vizinhos if v != index_final]:
    pos_v_final = get_posicao(vertices_indexados, index_final)
    pos_vizinho = get_posicao(vertices_indexados, vizinho)

    custo = haversine_formula(pos_v_final[0], pos_v_final[1], pos_vizinho[0], pos_vizinho[1])

    vizinhancas[vizinho].remove_vizinho(index_descartar)

    vizinhancas[index_final].add_vizinho(vizinho, custo)
    vizinhancas[vizinho].add_vizinho(index_final, custo)

  vizinhancas[index_final].remove_vizinho(index_descartar)
  vizinhancas[index_descartar].limpa_vizinhos()

  return (index_final, index_descartar)

def remove_vertice_indexado(vertices_indexados, to_remove):
  ind_remover = -1

  for i in range(vertices_indexados.shape[0]):
    if vertices_indexados[i][0] == to_remove:
      ind_remover = i
  
  if ind_remover >= 0:
    return np.delete(vertices_indexados, ind_remover, 0)

def agrupa_grafo(vertices_indexados, vizinhancas: dict[int, vz.Vizinhos], qtd_grupos: int):
  while vertices_indexados.shape[0] > qtd_grupos:
    u, v, _ = menor_aresta(vizinhancas)

    _, descartado = agrupa_vertices(u, v, vertices_indexados, vizinhancas)   
    vertices_indexados = remove_vertice_indexado(vertices_indexados, descartado)

    print("# de vertices: {}               ".format(vertices_indexados.shape[0]), end="\r")

  print("")

  return vertices_indexados

def vertices_indexados_graus(vertices_indexados):
  for i in range(vertices_indexados.shape[0]):
    vertices_indexados[i][1] = vertices_indexados[i][1] * 180/math.pi
    vertices_indexados[i][2] = vertices_indexados[i][2] * 180/math.pi

def tupla_graus(t):
  return (t[0] * 180/math.pi, t[1] * 180/math.pi)
##############################################################################################
##############################################################################################

df = pd.read_csv("C:\\Users\\PC\\Desktop\\case mottu\\dados-filtrados.csv")
# N = df.shape[0]
N = 1000

(vertices, vizinhancas) = cria_grafo(df[0:N])
vertices_indexados = vertices_indexados(vertices)

preenche_grafo_guloso(vertices, vizinhancas)
# visitados = dfs(vizinhancas)
# qtd_visitados = len(visitados)

# print("Vertices conexos: {}".format(qtd_visitados))
# print("Grafo conexo: {}".format(qtd_visitados == N))
# print("Aresta com maior custo, maior custo: {}".format(maior_aresta(vizinhancas)))

vertices_indexados = agrupa_grafo(vertices_indexados, vizinhancas, 10)
vertices_indexados_graus(vertices_indexados)
print(vertices_indexados)