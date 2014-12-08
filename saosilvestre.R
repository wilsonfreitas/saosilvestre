
library(ggplot2)
library(dplyr)
library(tidyr)
library(lubridate)

ss <- read.csv('saosilvestre.csv', header=TRUE, stringsAsFactor=FALSE)
ss <- ss %>%
  mutate(data=ISOdate(ano, 12, 1), 
         horario=paste(format(data, '%Y-%m-%d'), horario),
         tempo=as.difftime(tempo),
         pace=1000*tempo/percurso) %>% # criar data e pace e formatar tempo e horario
  arrange(ano, tempo) %>%              # ordenar por tempo
  group_by(ano) %>%                    # agrupar por ano e marcar masculino e feminino
  mutate(sexo=if (n() == 1) 'masculino' else c('masculino', 'feminino')) %>%
  ungroup

## limpeza de dados
# dados faltantes
idx <- grep('^-', ss$pais)
ss[idx[1], 'pais'] <- 'Brasil'
ss[idx[2], 'pais'] <- 'Quênia'

idx <- grep('^$', ss$pais)
ss[idx, 'pais'] <- 'Brasil'

# percurso errado - atualiza o percurso e recalcula o pace.
# o pace ajuda a identificar o percurso errado
ss[which(ss$pace > 4),]$percurso <- 15000
ss <- ss %>% mutate(pace=1000*tempo/percurso)

# agrupamento por ano para comparar masculino e feminino
ss_ano <- ss %>%
  group_by(ano) %>% 
  summarise(corrida=n(), masculino=min(tempo), feminino=max(tempo), percurso=max(percurso)) %>%
  mutate(pace_masculino=1000*masculino/percurso, pace_feminino=1000*feminino/percurso) %>%
  mutate(percurso_grupo=cut(percurso, breaks=c(0,10000, 15000), labels=c('< 10K', '> 10K'))) %>%
  mutate(pace_dif=pace_feminino-pace_masculino) %>%
  select(ano, corrida, percurso_grupo, pace_masculino, pace_feminino, pace_dif)

ss_ano_m <- gather(ss_ano, variable, value, -ano, -corrida, -percurso_grupo, -pace_dif)
ss_ano_m <- ss_ano_m %>% mutate(value=as.numeric(value))


# análise pace_dif ----
# 
ggplot(data=filter(ss_ano_m, corrida == 2), aes(x=ano, y=value, colour=variable, shape=percurso_grupo)) +
  geom_point(size=3)

ggplot(data=filter(ss_ano, corrida == 2), aes(x=ano, y=as.numeric(pace_dif, units='secs'))) +
  geom_line() + stat_smooth(method='lm')

# análise da regressão pace_dif ~ ano
fit <- lm(as.numeric(pace_dif) ~ ano, data=filter(ss_ano, corrida == 2))
summary(fit)

# 
ggplot(data=ss, aes(pais, fill=sexo)) +
  geom_bar() +
  theme(axis.text.x=element_text(angle=45, hjust=1))

# análise de umidade relativa ----
#
temp <- read.csv('temperatura.csv', header=TRUE, stringsAsFactor=FALSE)
temp <- temp %>%
  mutate(Data=dmy(Data))

ggplot(data=temp, aes(x=Data, y=UmidadeRelativaMedia)) + geom_point() + stat_smooth(method='lm')

fit <- lm(as.numeric(UmidadeRelativaMedia) ~ year(Data), data=temp)
summary(fit)

ggplot(data=gather(temp, variable, value, -Data, -UmidadeRelativaMedia), aes(x=Data, y=value, colour=variable)) +
  geom_point() + stat_smooth(method='lm')

fit <- lm(as.numeric(TempCompensadaMedia) ~ year(Data), data=temp)
summary(fit)

# relacionando pace masculino e UmidadeRelativaMedia e TempCompensadaMedia
temp <- temp %>% mutate(ano=year(Data))
ss_temp <- merge(ss_ano, temp, by='ano')

ggplot(data=filter(ss_temp, percurso_grupo == '> 10K'), aes(x=TempCompensadaMedia, y=as.numeric(pace_masculino), colour=ano)) +
  geom_point() + stat_smooth(method='lm')

ggplot(data=filter(ss_temp, percurso_grupo == '> 10K'), aes(x=UmidadeRelativaMedia, y=as.numeric(pace_masculino), colour=ano)) +
  geom_point() + stat_smooth(method='lm')

fit <- lm(as.numeric(UmidadeRelativaMedia) ~ as.numeric(pace_masculino), data=ss_temp)
summary(fit)

fit <- lm(as.numeric(TempCompensadaMedia) ~ as.numeric(pace_masculino), data=ss_temp)
summary(fit)
