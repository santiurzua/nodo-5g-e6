```
Pontificia Universidad Cat ́olica de Chile
Escuela de Ingenier ́ıa
Departamento de Ingenier ́ıa El ́ectrica
IEE3112 – Proyecto Final de Ingenier ́ıa El ́ectrica
```
# Dise ̃no y Prototipado de un Nodo de Monitoreo Ambiental para

# Predios Agr ́ıcolas con Capacidad de Comunicaci ́on 5G

## Contexto y Alcances del Proyecto

Dentro de las problem ́aticas sanitarias que afectan a la vitivinicultura regional en Chile, el o ́ıdio de la vid (Ery-
siphe necator) se posiciona como una de las amenazas m ́as relevantes, debido a su impacto directo en el rendimiento,
la calidad de la fruta y la calidad del vino. Bajo condiciones microclim ́aticas favorables, esta enfermedad puede
provocar p ́erdidas severas, que en casos extremos pueden alcanzar hasta el 100 % de la producci ́on. Su desarrollo
est ́a estrechamente asociado a variables microclim ́aticas locales, tales como la humedad relativa, la temperatura y
la ventilaci ́on del dosel vegetal, las cuales presentan una alta variabilidad espacial entre cuarteles y subcuarteles.
Esta variabilidad se encuentra influenciada por factores como la topograf ́ıa, la exposici ́on solar, la cercan ́ıa a cursos
de agua, la densidad vegetativa y las pr ́acticas de manejo agron ́omico.

La gesti ́on sanitaria actual se basa mayoritariamente en estaciones meteorol ́ogicas puntuales y en estrategias
preventivas generalizadas orientadas a minimizar el riesgo. Sin embargo, este enfoque no logra capturar la hetero-
geneidad microclim ́atica real del vi ̃nedo, lo que conduce a aplicaciones no focalizadas, al sobreuso de fungicidas,
al aumento de los costos operacionales, a un mayor riesgo de generaci ́on de resistencia del pat ́ogeno y a efectos
ambientales adversos. Adem ́as, limita la capacidad de anticipar focos tempranos de la enfermedad y de priorizar
acciones preventivas de manera eficiente.

Para contribuir a abordar esta problem ́atica, este proyecto propone el dise ̃no y prototipado de un nodo aut ́onomo
de monitoreo microclim ́atico que act ́ue como habilitante tecnol ́ogico para una futura plataforma digital de apoyo a
la toma de decisiones, capaz de capturar la variabilidad microclim ́atica real del vi ̃nedo. Se espera que, al finalizar el
proyecto, se disponga de un prototipo funcional validado en condiciones controladas (TRL 4), que permita avanzar
hacia el despliegue futuro de una red de monitoreo microclim ́atico en campo.

## Objetivos

Dise ̃nar, prototipar y validar un nodo de monitoreo microclim ́atico capaz de medir de forma continua variables
ambientales cr ́ıticas para el desarrollo del o ́ıdio de la vid —particularmente temperatura del aire y humedad relati-
va— e integrar dichas mediciones en un sistema de transmisi ́on de datos mediante conectividad 5G.

```
Para la consecuci ́on del objetivo, se plantean los siguientes objetivos espec ́ıficos:
```
```
(i) Disenar la arquitectura de hardware del nodo de monitoreo microclim ̃ ́atico , incluyendo la espe-
cificaci ́on y selecci ́on de sensores de temperatura y humedad relativa adecuados para operaci ́on en ambiente
agr ́ıcola, considerando precisi ́on, estabilidad, rango de operaci ́on, consumo energ ́etico y protecci ́on frente a
condiciones ambientales adversas.
```
```
(ii) Disenar e implementar el sistema de adquisici ̃ ́on y procesamiento de datos del nodo , integrando
elementos capaces de realizar el muestreo, acondicionamiento y almacenamiento temporal de las mediciones
ambientales, garantizando la integridad y trazabilidad de los datos generados.
```
```
(iii) Implementar un sistema de transmisi ́on inal ́ambrica basado en tecnolog ́ıa 5G , que permita la
comunicaci ́on confiable y de baja latencia entre el nodo de monitoreo y un terminal remoto de almacenamiento
o an ́alisis de datos, considerando protocolos de comunicaci ́on adecuados para dispositivos IoT y mecanismos
de gesti ́on eficiente del consumo energ ́etico.
```
### 1


```
(iv) Disenar e implementar un mecanismo de operaci ̃ ́on energ ́etica aut ́onoma , considerando un sistema
de generaci ́on de energ ́ıa solar y almacenamiento en bater ́ıas.
```
```
(v) Validar experimentalmente el prototipo del nodo de monitoreo en condiciones controladas.
```
## Entregables

```
El proyecto contempla entregables asociados al logro de tres hitos t ́ecnicos, seg ́un se detalla a continuaci ́on.
```
```
Hito 1: Propuesta Conceptual
```
- Definici ́on de bloques funcionales del sistema.
- Definici ́on requerimientos del sistema: sensores, comunicaci ́on, c ́omputo y energ ́ıa.
- Propuesta de componentes: sensores, microcontroladores, transceptores, bater ́ıas, etc.
- Presupuesto estimado.

```
Hito 2: Ingenier ́ıa B ́asica
```
- Dise ̃no de diagramas bajo nivel (elementos electr ́onicos, mec ́anicos y de software)
- Diagrama de flujo y diagramas secuenciales de los protocolos de comunicaci ́on
- Especificaci ́on t ́ecnica de hardware.
- Especificaci ́on t ́ecnica de firmware/software.
- An ́alisis de proveedores.
- Presupuesto final para la elaboraci ́on del prototipo.

```
Hito 3: Prototipado y Validaci ́on
```
- Prototipo del nodo.
- Lista de materiales ( _bill of materials_ ).
- Esquem ́aticos de placas electr ́onicas y componentes circuitales.
- Software y firmware de elementos program ́ables.
- Dise ̃no de pruebas de desempe ̃no e informe de resultados experimentales.
- Propuesta de mejoras futuras.
- Detalle actualizado del costo total del proyecto.

## Host

El host de este proyecto es el centro de investigaci ́on VitiScience en colaboraci ́on con el centro de investigaci ́on
CPS-RTC. La contraparte t ́ecnica asignada es el ingeniero Juan Ignacio Lorca, del CPS-RTC.

## Recursos

El proyecto tiene asignado un monto para gastos de operaci ́on de $500.000 para financiar la fabricaci ́on del
prototipo y de $230.000 para financiar visitas a predios agr ́ıcolas. Licencias de software, componentes de prueba y
accesos a otros recursos t ́ecnicos ser ́an provistos.

### 2


