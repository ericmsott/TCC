mode quiet

smpl @all

'Seleciona a variável a ser prevista.
string variavel = "dm"


'A primeira janela de projeção começa em %first_proj e termina em %last_proj.
%begin = "2002m02"
%first_proj = "2011m07"

'A última janela de projeção começa em %last_proj .

%last_proj = "2018m7"

'A serie projetada termina na observação %end:
%end = "2019m07"

'Fixa o parâmetro que define o horizonte preditivo máximo:
scalar horizon = 12

'O número de execuções do programa é:
scalar init = @dtoo(%first_proj)
scalar fim = @dtoo(%last_proj)
scalar num = fim - init + 1

'Essa parte do programa realiza as projecoes do modelo.
'O procedimento executado é o seguinte:
'1) fixa a amostra para projecao da variavel.
'2) cria as variaveis que irao compor os overrides do scenario
'3) cria o scenario do modelo e faz o override com as variaveis exogenas
'2) gera previsões para o período selecionado. 
'4) volta para o passo 1 colocando mais uma observação na amostra.

smpl %begin %end

'Cria as series com os erros de projeccao para 1 a 12 passos a frente.
'Cria as series com as projeções para 1 a 12 passos a frente.
'Os horizontes de projeccao sao indexados pelo indice h.
for !h = 1 to horizon 
	delete(noerr) erroquad_eq{!h}
	delete(noerr) erro_eq{!h}
	delete(noerr) proj_eq{!h}
	delete(noerr) erroperc_eq{!h}
	series erro_eq{!h}
	series erroquad_eq{!h}
	series proj_eq{!h}
	series erroperc_eq{!h}
next

for !i = 1 to num
	
	'Ajusta a amostra de estimação para m+0.
	smpl %begin %first_proj + !i -1

	series pib_potencial_{!i} = pib_potencial
	series pib_hiato_m1_{!i} = pib_hiato_m1
	series selic_average_{!i} = selic_average
	series juro_real_neutro_{!i} = juro_real_neutro
	series dbancgg_{!i} = dbancgg
	series de_{!i} = de
	series oc_{!i} = oc

	'Ajusta a amostra de estimação para m+12.
	smpl %begin %first_proj + !i -1 +horizon

	'O loop abaixo insere as expectativas FOCUS para a taxa selic nos periodos seguintes, calcula o juro real utlizando essa selic <<esperada>>.
	for !p = 1 to horizon 
		scalar auxi = !p-1
		scalar auxi2 = !p + 1
		selic_average_{!i}(init+!i+auxi) = selic_m{!p}(init+!i+auxi) 'insere a mediana das expectativas focus para a selic.
		juro_real_neutro_{!i}(init+!i+auxi) =  juro_real_neutro_m{!p}(init+!i+auxi)
		pib_potencial_{!i}(init+!i+auxi) = pib_potencial_m{!p}(init+!i+auxi)
		pib_hiato_m1_{!i}(init+!i+auxi) = pib_hiato_m{auxi2}(init+!i+auxi)
		oc_{!i}(init+!i+auxi) = oc(init+!i-1)
		de_{!i}(init+!i+auxi) = de(init+!i-1)
		dbancgg_{!i}(init+!i+auxi) = dbancgg(init+!i-1)
	next 'fecha o loop de for indexado por p.
		
	smpl %first_proj + !i %first_proj + !i -1 + horizon

	%op = "_"+@str(!i)
	modelo.scenario(n, a = %op) !i 'cria um scenario novo com allias "_!i"
	modelo.override() selic_average_{!i} juro_real_neutro_{!i} pib_potencial_{!i} pib_hiato_m1_{!i} oc_{!i} de_{!i} dbancgg_{!i} 'faz o override do scenario para as variaveis exogenas
	'Soluciona o modelo
	modelo.solve
	series y_f{!i} = {variavel}_{!i}
	modelo.scenario(d) !i

	'Calculo das projeções e dos erros de previsao. Onde erroquad_eq sao os erros quadraticos, erroperc_eq os erros percentuais  e erro_eq os erros propriamente ditos.
	for !h = 1 to horizon
		scalar aux = !h-1
		proj_eq{!h}(init+!i+aux) = y_f{!i}(init+!i+aux)
		erroquad_eq{!h}(init+!i+aux) = ({variavel}(init+!i+aux) - proj_eq{!h}(init+!i+aux))^2
		erroperc_eq{!h}(init+!i+aux) = (({variavel}(init+!i+aux) - proj_eq{!h}(init+!i+aux))/{variavel}(init+!i+aux))^2
		erro_eq{!h}(init+!i+aux) = ({variavel}(init+!i+aux) - proj_eq{!h}(init+!i+aux))
	next 'fecha o loop de for indexado por h.
										
next 'fecha o loop indexado por i.

'CALCULO DOS ERROS MEDIOS QUADRATICOS
		
matrix(2,12) erro_mod
				
smpl %first_proj + 1 %end
for !f = 1 to horizon
	erro_mod(1,!f) = (@mean(erroquad_eq{!f}))^(1/2)
	erro_mod(2,!f) = 100*(@mean(erroperc_eq{!f}))^(1/2)
next '!f

table(3,13) result_mod
setcell(result_mod, 1, 2, "1", "c")
setcell(result_mod, 1, 3, "2", "c")
setcell(result_mod, 1, 4, "3", "c")
setcell(result_mod, 1, 5, "4", "c")
setcell(result_mod, 1, 6, "5", "c")
setcell(result_mod, 1, 7, "6", "c")
setcell(result_mod, 1, 8, "7", "c")
setcell(result_mod, 1, 9, "8", "c")
setcell(result_mod, 1, 10, "9", "c")
setcell(result_mod, 1, 11, "10", "c")
setcell(result_mod, 1, 12, "11", "c")
setcell(result_mod, 1, 13, "12", "c")
setcell(result_mod, 2, 1,"REQM", "c")
setcell(result_mod, 3, 1,"REQPM", "c")

result_mod.setlines(a1:a1) +o
result_mod.setlines(b1:l1) +o
result_mod.setlines(c1:l1) +o
result_mod.setlines(a2:a2) +o
result_mod.setlines(b2:l2) +o
result_mod.setlines(c2:l2) +o

for !coluna = 1 to 12	
	setcell(result_mod, 2, !coluna+1, erro_mod(1,!coluna), 3)
	setcell(result_mod, 3, !coluna+1, erro_mod(2,!coluna), 3)
next  'fechamento do loop de for indexado por coluna.

smpl @all

'Apaga objetos desnecessarios
delete init
delete fim
delete aux
delete auxi
delete horizon
delete vv_*
'As series y_* sao as series projetadas
'delete y_*
delete *_0*
delete erro_mod
'O loop abaixo apaga todas as equaccoes, modelos e series filtradas
for !eps = 1 to num
	delete *_!eps
	delete *_t!eps
	delete *_cyc!eps
next
delete num


