import pandas as pd

# Scripts usados para resolver o case

'''
  TODO:
    - usar algum algoritmo de clusterização para separar o grafo em 10 clusters
    - centro desse cluster == a posição ideal pro posto de abastecimento
'''

# usada pra plotar as coordenadas no site www.mapcustomizer.com
def coleta_coordenadas():
  df = pd.read_csv("C:\\Users\\PC\\Desktop\\case mottu\\Dados Mottu-e - L7d.csv")

  for i in range(19):
    start_index = i*1000
    end_index = (i+1)*1000

    df_lat_lon = df[["latitude_final_nr", "longitude_final_nr"]]
    file_name = "C:\\Users\\PC\\Desktop\\case mottu\\soh-coordenadas\\soh-coordenadas-{}.csv".format(i)

    df_lat_lon[start_index:end_index].to_csv(file_name, sep=",", index=False,header=False)

# remove os elementos com latitude e longitude com erros (filtrados manualmente)
def filtra_erros() -> pd.DataFrame:
  df = pd.read_csv("C:\\Users\\PC\\Desktop\\case mottu\\Dados Mottu-e - L7d.csv")

  # apesar de serem 4, tem 5 rows com essas coords
  COORDS_ERRADAS = [(-24.21475,-46.05467),
                    (-23.502775,2.152943),
                    (-24.205957,-46.05467),
                    (-13.005145,2.152943)]
  
  for i in range(len(COORDS_ERRADAS)):
    matches = df.loc[(df["latitude_final_nr"] == COORDS_ERRADAS[i][0]) & (df["longitude_final_nr"] == COORDS_ERRADAS[i][1])].index
    
    for indice in matches:
      df = df.drop(indice)
  
  return df

def salva_dados_filtrados():
  df = filtra_erros()
  file_name = "C:\\Users\\PC\\Desktop\\case mottu\\dados_filtrados.csv"
  df.to_csv(file_name, sep=",", index=False)

