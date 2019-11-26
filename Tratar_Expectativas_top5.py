# Execucao em 127,0 segundos
import pandas as pd
from pandas import Series, read_csv
from datetime import timedelta
import numpy as np
###################################### COMENTARIOS ######################################
# O conteudo do arquivo criado deve ser tratado no excel em "texto para coluna" delimitado por virgulas e importado como texto ...
# ... e deve ser utilizado nas celulas verdes do arquivo Excel "Tratar a expectativa do IPCA.xlsx".
# ... e deve ser utilizado nas celulas verdes do arquivo Excel "Tratar a expectativa da SELIC.xlsx".
######################################- Diretorios -############################################
# Deve-se mudar para os diretorios 'direc' de saida do arquivo baixado no R.
direc = {'ipca':'D:/Eric Ott/Faculdade/TCC/Modelo_BCB_Expec/ipcatop5.csv',
		 'selic':'D:/Eric Ott/Faculdade/TCC/Modelo_BCB_Expec/selictop5.csv'}
##############################################################################################
for serie in direc: # para cada diretorio
	file1 = pd.read_csv(direc[serie]) # le o arquivo CSV 
	ref = pd.DatetimeIndex(file1['reference_month']) # Para o mes de referencia ...
	ref_month = ref.month # ... Guarda o mes e o ano em ref_month e ref_year.
	ref_year = ref.year   #
	data = pd.DatetimeIndex(file1['date']) # Para a data em que foi feita a projecao ...
	proj_day = data.day     # ... Guarda o dia, mes e ano em proj_day, proj_month e proj_year.
	proj_month = data.month #
	proj_year = data.year   #
	# A formula abaixo e' a do Apendice A.
	months_ahead = (ref_year - proj_year)*12 + ref_month - proj_month # calcula para quantos meses a frente foram feitas as projecoes
	months_ahead.index = data # indexa a serie criada acima pela data em que foi feita a projecao.
	proj_type = pd.Series(file1['type']) # Cria uma serie para o 'tipo' da projecao: L longo prazo; M medio prazo; C curto prazo.
	if serie == 'ipca':
		sdi = pd.Series(file1['mean']) # pega a media da variavel de interesse projetada e cria uma serie pra ela. Poderia ser a mediana 'median'.
		type_mm = 'mean' #utilizado na linha 38
	else:
		sdi = pd.Series(file1['median']) # pega a media da variavel de interesse projetada e cria uma serie pra ela. Poderia ser a mediana 'median'.
		type_mm = 'median' #utilizado na linha 38
	sdi.index = data # indexa a serie criada acima pela data em que foi feita a projecao.
	indexes = pd.DataFrame(data=[proj_year, proj_month, proj_day, months_ahead, proj_type]).T # cria um dataframe transposto, com as informãcoes de cada projecao.
	indexes.columns = ("year","month","day","months_ahead","proj_type") # nomeia as colunas
	indexes.index = data # indexa o dataframe criado acima pela data em que foi feita a projecao.
	indexes = pd.MultiIndex.from_frame(indexes) # cria um multiindex com o dataframe
	df = pd.DataFrame(data=sdi) # cria um dataframe contendo apenas a serie sdi e...
	df.index = indexes #... indexa esse dataframe com o multiindexador
	df = df.dropna() # remove as observacoes ausentes "NA"s.
	df = pd.pivot_table(df,values=type_mm,index=["year","month"],columns=["months_ahead","proj_type"],aggfunc=np.mean) #Agrega em um pivot_table pela media das media dos meses, para cada mes
	df = df.drop(["C","L"],level=1,axis=1) # remove as projecoes de curto e longo prazo, e fica apenas com as de medio.
	df = df.drop([-1,0,13,14,15,16,17,18,19],level=0,axis=1) # remove as colunas referentes aos meses que nao sao de interesse (acima de 12 e menor que 1)
	df = df.reset_index() # reseta o indexador, para virar um dataframe mais 'limpo'
	df = (df.fillna(method="ffill") + df.fillna(method="bfill"))/2 # se sobrou um valor ausente, este sera substituido pela media do valor anterior com o seguinte.
	#print(df)
	direc_out = direc[serie][:-4] + '_treated.csv' #renomeia o arquivo de saida pra nao substituir o anterior
	df.to_csv(direc_out) # salva o dataframe como csv
	print('Arquivo .csv criado em:', direc_out)

