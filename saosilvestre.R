
library(ggplot2)
library(dplyr)
# library(reshape)
library(tidyr)

ss <- read.csv('saosilvestre.csv', header=TRUE, stringsAsFactor=FALSE)
ss <- ss %>%
  mutate(data=ISOdate(ano, 12, 1), 
         horario=paste(format(data, '%Y-%m-%d'), horario),
         tempo=as.difftime(tempo),
         pace=1000*tempo/percurso) %>%
  arrange(ano, tempo) %>%
  group_by(ano) %>%
  mutate(sexo=if (n() == 1) 'masculino' else c('masculino', 'feminino')) %>%
  ungroup

idx <- grep('^-', ss$pais)
ss[idx[1], 'pais'] <- 'Brasil'
ss[idx[2], 'pais'] <- 'Quênia'

idx <- grep('^$', ss$pais)
ss[idx, 'pais'] <- 'Brasil'

ss[which(ss$pace > 4),]$percurso <- 15000

ss <- ss %>% mutate(pace=1000*tempo/percurso)

ss_ano <- ss %>%
  group_by(ano) %>% 
  summarise(corrida=n(), masculino=min(tempo), feminino=max(tempo), percurso=max(percurso)) %>%
  mutate(pace_masculino=1000*masculino/percurso, pace_feminino=1000*feminino/percurso) %>%
  mutate(percurso_grupo=cut(percurso, breaks=c(0,10000, 15000), labels=c('< 10K', '> 10K'))) %>%
  mutate(pace_dif=pace_feminino-pace_masculino) %>%
  select(ano, corrida, percurso_grupo, pace_masculino, pace_feminino, pace_dif)

ss_ano_m <- gather(as.data.frame(ss_ano), variable, value, -ano, -corrida, -percurso_grupo, -pace_dif)

ggplot(data=filter(ss_ano_m, corrida == 2), aes(x=ano, y=as.numeric(value), colour=variable, shape=percurso_grupo)) +
  geom_point(size=3)

ggplot(data=filter(ss_ano, corrida == 2), aes(x=ano, y=as.numeric(pace_dif, units='secs'))) +
  geom_line() + stat_smooth(method=lm)

ggplot(data=ss, aes(pais, fill=sexo)) +
  geom_bar() +
  theme(axis.text.x=element_text(angle=45, hjust=1))
