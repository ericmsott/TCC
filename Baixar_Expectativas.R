########################## SETUP INICIAL ####################################
library(rbcb)
start_date = "2002-01-01"
end_date = "2019-26-11"

########################## BAIXAR EXPECTATIVAS ###########################

# Essa parte demora um pouco.Qualquer coisa, basta aumentar a "start_date" ou diminuir a "end_date".

PIB<-get_quarterly_market_expectations("PIB Total",
                                       start_date = start_date,end_date = end_date)
ipca_top5<-get_top5s_monthly_market_expectations("IPCA",
                                                 start_date = start_date,end_date = end_date)
selic_top5<-get_top5s_monthly_market_expectations("Meta para taxa over-selic",
                                                 start_date = start_date,end_date = end_date)

########################### SALVANDO EM CSV ##############################

# Aqui tem que estar atento ao diretorio onde o codigo esta salvando.

write.csv(PIB, file="PIB.csv")
write.csv(ipca_top5, file="ipcatop5.csv")
write.csv(selic_top5, file="selictop5.csv")



