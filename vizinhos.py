class Vizinhos:
  def __init__(self):
    self.__vizinhos = {}

  @property
  def vizinhos(self):
    return self.__vizinhos.keys()

  def add_vizinho(self, vizinho_index, distancia):
    self.__vizinhos[vizinho_index] = distancia
  
  def remove_vizinho(self, vizinho_index):
    self.__vizinhos.pop(vizinho_index)

  def get_custo(self, vizinho_index):
    if vizinho_index in self.__vizinhos.keys():
      return self.__vizinhos[vizinho_index]
    else:
      return -1
    
  def ajusta_custo(self, vizinho_index, novo_custo):
    if vizinho_index in self.__vizinhos.keys():
      self.__vizinhos[vizinho_index] = novo_custo
    
  def limpa_vizinhos(self):
    self.__vizinhos = {}