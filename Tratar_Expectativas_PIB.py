# Execucao em 4,5 segundos
import pandas as pd
from pandas import Series, read_csv
from datetime import timedelta
import numpy as np
################################ COMENTARIOS ######################################
# Deve-se mudar para o diretorio 'direc' de saida do arquivo baixado no R.
# O output do codigo deve ser tratado no excel em "texto para coluna" delimitado por virgulas e importado como texto ...
# ... depois deve-se substituir ponto "." por virgula "," ...
# ... e utilizado no arquivo Excel "Tratar a expectativa do PIB para mensal.xlsx".
################################- Diretorio -######################################
# Deve-se mudar para o diretorio 'direc' de saida do arquivo baixado no R.
direc = {'pib':'D:/Eric Ott/Faculdade/TCC/Modelo_BCB_Expec/PIB.csv'}
##################################################################################
for serie in direc: # para cada diretorio
	file1 = pd.read_csv(direc[serie]) # le o arquivo CSV
	ref = pd.DatetimeIndex(file1['reference_quarter']) # Para o trimetre de referencia ...
	ref_quarter = ref.month # ... Guarda o trimestre e o ano em ref_quarter e ref_year.
	ref_year = ref.year     #
	data = pd.DatetimeIndex(file1['date']) # Para a data em que foi feita a projecao ...
	proj_day = data.day     # ... Guarda o dia, mes e ano em proj_day, proj_month e proj_year.
	proj_month = data.month #
	proj_year = data.year   #
	# A formula abaixo e' a do Apendice A.
	quarters_ahead = (ref_year - proj_year)*4 + ref_quarter - (proj_month/3).astype(int) # calcula para quantos trimestres a frente foram feitas as projecoes
	quarters_ahead.index = data # indexa a serie criada acima pela data em que foi feita a projecao.
	sdi = pd.Series(file1['mean']) # pega a media da variavel de interesse projetada e cria uma serie pra ela. Poderia ser a mediana 'median'.
	sdi.index = data # indexa a serie criada acima pela data em que foi feita a projecao.
	indexes = pd.DataFrame(data=[proj_year, proj_month, proj_day, quarters_ahead]).T # cria um dataframe transposto, com as informãcoes de cada projecao.
	indexes.columns = ("year","month","day","quarters_ahead") # nomeia as colunas
	indexes.index = data # indexa o dataframe criado acima pela data em que foi feita a projecao.
	indexes = pd.MultiIndex.from_frame(indexes) # cria um multiindex com o dataframe
	df = pd.DataFrame(data=sdi)  # cria um dataframe contendo apenas a serie sdi e...
	df.index = indexes #... indexa esse dataframe com o multiindexador
	df = df.dropna()   # remove as observacoes ausentes "NA"s.
	df = pd.pivot_table(df,values="mean",index=["year","month"],columns=["quarters_ahead"],aggfunc=np.mean) #Agrega em um pivot_table pela media das media dos dias de cada mes
	df = df.drop([-1,6],axis=1) # remove as colunas reference_quarters aos trimestres que nao sao de interesse (acima de 5 e abaixo de 0)
	df = df.reset_index()       # reseta o indexador, para virar um dataframe mais 'limpo'
	df = (df.fillna(method="ffill") + df.fillna(method="bfill"))/2 # se sobrou um valor ausente, este sera substituido pela media do valor anterior com o seguinte.
	df.index = (df['year']/10).astype('str').str.replace('.','')+pd.Series(np.array(["m"]*len(df.index)))+(df['month']/10).astype('str').str.replace('.','') # remove os '.0' criados
	df = df.drop(['year','month'], axis=1)
	df.columns = pd.Index(["pib_q0","pib_q1","pib_q2","pib_q3","pib_q4","pib_q5"],name='data')
	print(df)
	direc_out = direc[serie][:-4] + '_treated.csv' #renomeia o arquivo
	df.to_csv(direc_out)
	print('Arquivo .csv criado em:', direc_out)