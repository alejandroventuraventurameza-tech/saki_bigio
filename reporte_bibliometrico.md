# Reporte bibliométrico — Fase 2

> **DOCUMENTO HISTÓRICO, SUSTITUIDO.** Para cifras y conclusiones vigentes use `reporte_final_refinado.md`. Este archivo conserva resultados anteriores a la canonización de versiones de OpenAlex y a la auditoría del parser de referencias.

**Proyecto Saki Bigio · P3 y P4 · Historia del Pensamiento Económico, UP 2026-02**
13/09/2026 · Fuentes: OpenAlex (autor `A5024020324`, ORCID 0000-0001-5932-0736), CV agosto 2026, y el corpus local de 46 documentos

---

## Resumen: qué cambió con los datos

Cinco resultados, en orden de importancia para P3 y P4. Dos de ellos **contradicen hipótesis que habíamos escrito antes** —H4 y H6—, y eso es lo mejor que le pudo pasar al trabajo.

1. **H4 queda falsificada como genealogía, y lo que la reemplaza es mejor.** Gurley & Shaw aparece **cero veces** en 3.38 millones de caracteres. Wicksell, cero. Keynes, una vez, y de adorno. Bigio llega a la tesis del Banking School sin pasar por el Banking School: **redescubrimiento sin genealogía**. §4.
2. **A Bigio lo leen los bancos centrales más que las universidades de élite.** El Sistema de la Reserva Federal lo cita más que Chicago, Yale, Columbia, Harvard y NYU **sumadas**. §3.
3. **El 39% de sus citas vive en literatura gris.** Su paper de *Econometrica* registra 1 cita; el working paper del mismo paper, 119. §2.
4. **Su genealogía intelectual está documentada y es peruana en su origen: Julio Velarde → Thomas Sargent.** §5.
5. **H6 también cae, y su reemplazo es una tesis clásica de HPE.** La teoría de las crisis de cadena de pagos existía en 2015, cinco años antes de la carta del COVID. §6.

---

## 1. Desempeño: el impacto, bien medido

**Perfil OpenAlex:** 89 registros → 75 ítems de investigación (se descartan 12 datasets y 2 paquetes de software) → **~35 trabajos distintos** una vez agrupadas las versiones. 1,050 citas, h-index 14, i10-index 17.

> **Nota de depuración.** En la consulta 1 advertí contaminación por un homónimo del área médica, porque el perfil lista afiliaciones a UCLA Health y UCLA Medical Center. Revisados los 89 registros, **no hay ningún trabajo médico**: las afiliaciones espurias son ruido de metadatos, probablemente arrastrado desde lineages institucionales. La advertencia era correcta como precaución y equivocada como diagnóstico; lo dejo escrito para que quede el rastro.

El dato que importa no son las citas brutas sino el **impacto normalizado por campo y año (FWCI)**, donde 1.0 es el promedio mundial:

| Trabajo | Año | Revista | Citas | **FWCI** | Percentil |
|---|---|---|---|---|---|
| *Endogenous Liquidity and the Business Cycle* | 2015 | American Economic Review | 190 | **61.6** | 99.8 |
| *Distortions in Production Networks* | 2020 | Quarterly J. of Economics | 223 | **42.8** | 99.9 |
| *Optimal Self-Employment Income Tax Enforcement* | 2011 | J. of Public Economics | 87 | 5.2 | 95.2 |
| *Liquidity Shocks, Business Cycles and Asset Prices* | 2017 | European Economic Review | 20 | 2.8 | 90.7 |
| *Debt-Maturity Management with Liquidity Costs* | 2023 | JPE: Macro | 13 | 1.7 | 84.9 |
| *Financial Risk Capacity* | 2021 | AEJ: Macro | 22 | 1.2 | 79.2 |

Un FWCI de 61.6 significa que *Endogenous Liquidity* recibió **61 veces** las citas del trabajo promedio de su campo y su año. Sus dos papers principales están en el **0.2% superior** de la literatura económica mundial.

*Cautela a declarar:* valores de FWCI por encima de 40 son extremos y en parte reflejan bases de comparación pequeñas en el campo-año. Por eso se reporta el percentil al lado: dos medidas distintas, la misma conclusión.

Y un detalle nada menor: **sus dos papers de mayor impacto normalizado son los únicos dos que firmó solo.** De 24 papers publicados o en working paper, solo dos son de autoría individual — y son *Learning Under Fear of Floating* (2010) y *Endogenous Liquidity* (2015), el de FWCI 61.6.

---

## 2. Dónde viven realmente sus citas

| Tipo de documento | N | Citas |
|---|---|---|
| Artículos, libros y capítulos | 20 | 642 |
| **Reportes NBER y preprints (SSRN, RePEc)** | **54** | **408** |

**El 38.9% de sus citas está en literatura gris.** Y el caso individual es más elocuente que el agregado:

| Trabajo | Versión working paper | Versión publicada |
|---|---|---|
| *Banks, Liquidity Management and Monetary Policy* | NBER WP 2014: **119 citas** | Econometrica 2022: **1 cita** (FWCI 0.0, percentil 0.6) |
| *A Q-Theory of Banks* | NBER WP 2020: **10 citas** | REStud: **0 citas** |
| *Repurchase Options in the Market for Lemons* | NBER WP 2020: 2 citas | REStud: 0 citas |

Es el mismo paper. Pero *Banks, Liquidity Management and Monetary Policy* circuló ocho años como working paper antes de aparecer en *Econometrica*, y para entonces toda la profesión ya lo citaba por el NBER. La versión publicada —el artículo top-citado de *Econometrica* 2022-2023 según su propio CV— aparece en OpenAlex como si no existiera.

Además, **tres de sus trabajos más citados no están publicados en ninguna revista**: *Scrambling for Dollars* (66 citas), *Transfers vs. Credit Policy* (46) y *A Model of Credit, Money, Interest and Prices* (18).

**Por qué esto es un hallazgo y no un defecto de los datos.** Para P4 —¿en qué documentos presenta su pensamiento?— la respuesta empírica es incómoda para la pregunta tal como está formulada: en economía **el documento que porta el pensamiento no es el artículo publicado, sino el working paper**. El artículo llega años tarde, cuando la conversación ya ocurrió. Cualquier medición de "dónde está su pensamiento" que se limite a revistas indexadas se pierde casi el 40% del objeto. Eso es un dato sobre cómo funciona la disciplina, y merece un minuto de la exposición.

---

## 3. Quién lo cita: el mapa de su influencia

710 trabajos citan sus seis papers principales. Desagregados:

**Por campo** — 578 de Economics/Econometrics/Finance, 60 de Business/Management, 38 de Ciencias Sociales. Es decir: **su influencia es intradisciplinaria y concentrada.** No se desborda hacia otras áreas.

**Por país** — EE.UU. 375, China 96, Reino Unido 87, Francia 50, Alemania 41, Canadá 38, Italia 33, **España 29**, Brasil 12. La presencia española y latinoamericana es modesta pero real.

**Por institución** (las que más lo citan):

| Institución | Menciones |
|---|---|
| National Bureau of Economic Research | 101 |
| **Federal Reserve** (sistema) | **98** |
| Centre for Economic Policy Research | 38 |
| University of Chicago | 31 |
| **Federal Reserve Board of Governors** | **28** |
| Yale University | 23 |
| Columbia University | 23 |
| **Federal Reserve Bank of New York** | **21** |
| University of California, Los Angeles | 18 |
| Northwestern University | 17 |
| Harvard University | 16 |
| **Federal Reserve Bank of Minneapolis** | **15** |
| **Banco de España** | **15** |
| New York University | 15 |

Sumando las entidades del Sistema de la Reserva Federal: **162 menciones**. Chicago, Yale, Columbia, Harvard y NYU juntas: **108**.

Por tipo de institución: `education` 538, `government` 83, `facility` 77, `nonprofit` 154.

> **Cómo leer esto con honestidad.** NBER y CEPR no son empleadores: son redes de afiliación que cargan los propios académicos, así que sus 101 y 38 no compiten con las universidades. Las cifras de la Reserva Federal y del Banco de España, en cambio, corresponden a economistas de planta de bancos centrales. Y `government` + `facility` = 160 menciones institucionales que no vienen del sistema universitario.

**Lo que esto significa.** El público real de Bigio son los departamentos de investigación de los bancos centrales. Eso no es un accidente: es coherente con todo lo demás de su expediente —consultoría al Banco Central Europeo sobre políticas de balance (2022), Research Scholar en la Fed de San Francisco (2019-2021), minicursos dictados en el BCRP (2015 y 2024), y una lista de seminarios donde los bancos centrales superan a las universidades—. Y responde con dato duro, no con opinión, la pregunta 5 del cuestionario —*¿qué grupos son los principales beneficiarios de su pensamiento?*—, que es la de Aníbal: **los bancos centrales**, y de manera abrumadora.

---

## 4. La tradición: lo que H4 predijo y lo que los datos dicen

Aquí el trabajo se pone interesante, porque la hipótesis falla.

### 4.1 La prueba

Busqué 34 nombres-ancla en los **3.38 millones de caracteres** de los 46 documentos del corpus. La prueba es de presencia/ausencia por documento (mide amplitud de uso, no intensidad), y una ausencia total es evidencia fuerte.

**Presentes, ordenados por número de documentos en que aparecen:**

| Ancla | Docs | Tradición |
|---|---|---|
| Sargent | 15 | (ver §5 — es su asesor) |
| Woodford | 13 | Nueva economía keynesiana |
| **Kiyotaki-Moore** | **11** | Fricciones financieras / colateral |
| Bernanke-Gertler | 9 | Acelerador financiero |
| Holmström-Tirole | 9 | Intermediación y liquidez |
| Lagos-Wright | 7 | **Nuevo monetarismo** (búsqueda y dinero) |
| Brunnermeier-Sannikov | 7 | Macro-finanzas continua |
| Lucas | 7 | Núcleo post-Lucas |
| Gertler-Kiyotaki | 6 | Política crediticia |
| Akerlof | 4 | **Economía de la información** |
| Gorton, Poole, Friedman, Tobin | 4 c/u | |
| Diamond-Dybvig, Kiyotaki-Wright, Minsky, Fisher | 3 c/u | |

**Ausentes por completo (cero ocurrencias en los 46 documentos):**

> **Gurley & Shaw · Wicksell · Hayek · Schumpeter · Patinkin · Thornton · Goodfriend**

Y **Keynes aparece exactamente una vez**, en un solo documento (*Heterogeneous Beliefs*), dentro de una lista decorativa de antecedentes narrativos: *"From Sprague (1910) and Fisher (1933) to Keynes (1936), Minsky (1986), Kindleberger (1996), and Shiller (2000)…"*. No es un insumo del modelo: es una frase de introducción.

**Y "Tobin" no es el Tobin que suponíamos.** De las cuatro apariciones, tres son **la q de Tobin** —la razón valor de mercado sobre valor libro— usada como variable, no como doctrina. La única mención sustantiva a Tobin como teórico monetario está en *Monetary Policy Implementation Regimes and Reserve Demand*:

> *"The theoretical foundations trace to Baumol (1952) and Tobin (1956), whose inventory-theoretic models characterize money holdings as balancing transaction needs against the opportunity cost…"*

Es decir: **Baumol-Tobin**, la demanda transaccional de dinero. Real, explícita, y distinta de lo que H4 predecía (Tobin 1963, *Commercial Banks as Creators of Money*).

### 4.2 La profundidad histórica de su bibliografía

De 1,855 años citados en las secciones de referencias del corpus:

| Década | Menciones |
|---|---|
| 1970s | 48 |
| 1980s | 108 |
| 1990s | 168 |
| 2000s | 379 |
| **2010s** | **668** |
| 2020s | 401 |

**El 95.5% de lo que cita es de 1970 en adelante. El 57% es de 2010 en adelante.** (Lo anterior a 1950 suma 3.4%, y esa cifra es un techo: incluye falsos positivos de números de página y de volumen.) Sus anclas más antiguas son Akerlof 1970, Merton 1974, Hulten 1978, Wilson 1979, y —como excepción— Baumol 1952 y Tobin 1956.

### 4.3 H4 reformulada: redescubrimiento sin genealogía

H4 decía que Bigio es heredero de la tradición Tobin–Gurley & Shaw y que su trabajo es la reencarnación microfundada de la disputa Currency School contra Banking School. **Como afirmación genealógica, es falsa y los datos son inequívocos.**

Pero el contenido no lo es. Bigio cierra su ensayo de agenda con esta frase:

> *"Regulation that treats banks as mere intermediaries misses their monetary role."*

Eso **es** la tesis del Banking School, palabra por palabra: los bancos no intermedian fondos preexistentes, crean dinero. Es lo que Tobin argumentó en 1963 y lo que Gurley y Shaw formalizaron en 1960.

La conclusión correcta, entonces, no es que Bigio herede esa tradición sino que **llega a ella sin haberla transitado**. Arriba por modelación —equilibrio general cuantitativo, fricciones microfundadas, calibración— a una posición doctrinal de doscientos años de antigüedad, sin citar a ninguno de sus formuladores. Llamémoslo **H4' — redescubrimiento sin genealogía**.

**Por qué esta es la mejor tesis disponible para un curso de historia del pensamiento económico.** No es una crítica a Bigio; es una descripción de cómo se relaciona la macroeconomía contemporánea con su propio pasado. La disciplina **re-deriva** en lugar de **heredar**: la historia del pensamiento económico no circula como bibliografía sino que reaparece, sin nombre, como resultado de un modelo. Y la evidencia es un resultado nulo —cero menciones en 3.38 millones de caracteres—, que es la clase de evidencia más difícil de discutir.

Esa afirmación, además, se puede poner a prueba: si es correcta, debería valer también para otros macroeconomistas contemporáneos, no solo para Bigio. Es una hipótesis con vida más allá de este trabajo.

### 4.4 H3, en cambio, queda confirmada

Su tradición efectiva es la que predijimos, con una precisión que conviene registrar. La bibliografía de sus dos papers más citados está encabezada por **Akerlof 1970, "The Market for Lemons"** —la referencia más citada de toda su bibliografía, 23,000 citas—, seguida de Myers-Majluf, Stiglitz-Weiss, Merton, Diamond-Dybvig, Kiyotaki-Moore, Bernanke-Gertler-Gilchrist, Holmström-Tirole, Lagos-Wright, Acemoglu-Carvalho-Ozdaglar y Gabaix.

Cuatro linajes, todos post-1970:

- **Economía de la información** (Akerlof, Stiglitz-Weiss, Myers-Majluf, Wilson, Prescott-Townsend, Kurlat)
- **Macro-finanzas y fricciones financieras** (Kiyotaki-Moore, Bernanke-Gertler, Holmström-Tirole, Gertler-Karadi, Brunnermeier-Sannikov, Diamond-Dybvig)
- **Nuevo monetarismo** (Lagos-Wright, Kiyotaki-Wright, Lester-Postlewaite-Wright, Eisfeldt)
- **Redes de producción y mala asignación** (Long-Plosser, Hulten, Acemoglu et al., Gabaix, Baqaee-Farhi, Hsieh-Klenow)

---

## 5. La genealogía que sí existe, y es peruana

Lo que no aparece como bibliografía aparece como **maestros**, y está documentado por él mismo. En su comentario a la historia monetaria y fiscal del Perú escribe:

> *"I had the good fortune to later on have Velarde and Sargent as undergraduate and graduate thesis advisers."*

**Julio Velarde** —hoy presidente del Banco Central de Reserva del Perú— fue su asesor de tesis de pregrado en la Universidad del Pacífico. **Thomas Sargent** —Nobel 2011— fue su asesor de doctorado en NYU. En el mismo texto agradece comentarios a *"Tom Sargent and Rody Manuelli"*, y recuerda sus lecturas favoritas del primer curso de macroeconomía: Sargent (1986) sobre las hiperinflaciones de Europa del Este, y Velarde y Rodríguez (1992) sobre el Perú.

A eso se suma **Ricardo Lagos**, también de NYU, a quien agradece junto a Sargent *"for their constant guidance"* en *Endogenous Liquidity* — y Lagos es, con Randall Wright, el fundador del marco de búsqueda y dinero que aparece en 7 de sus documentos.

El otro extremo de la genealogía es igual de nítido. En su ensayo de agenda cuenta que **Sargent le sugirió quedarse un año más en el doctorado** para empezar el mercado laboral con un proyecto adicional — y de esa sugerencia salió su segunda línea de investigación.

**Esto es lo que reemplaza a la genealogía bibliográfica ausente.** Bigio no hereda una tradición leyendo: la hereda por contacto. Velarde le da el Perú y la política monetaria de una economía dolarizada; Sargent le da la teoría monetaria-fiscal y la macroeconomía recursiva; Lagos le da la microfundamentación del dinero. Y hoy **Yuliy Sannikov es su coautor**, no su bibliografía. Es una tradición transmitida por aprendizaje directo y coautoría, no por citas — que es exactamente el modo en que se transmite el pensamiento económico contemporáneo, y algo que una historia del pensamiento basada solo en textos no vería.

**Su red de coautoría** confirma la forma: 31 coautores distintos en 24 papers, con solo dos trabajos de autoría individual. Repiten **Javier Bianchi (3), Galo Nuño (3), Eduardo Zilberman (3)** y Dejanir Silva (2). Una red amplia y poco densa, característica de la macroeconomía actual — y con un eje marcado hacia investigadores de bancos centrales (Nuño en el Banco de España, Bianchi en la Fed de Minneapolis, Paul Castillo en el BCRP, D'Erasmo en la Fed de Filadelfia).

---

## 6. H6 también cae, y su reemplazo es mejor

H6 afirmaba que en Bigio **la política precede a la teoría**: la carta del 15 de marzo de 2020 sobre el colapso de la cadena de pagos habría antecedido a la teoría formal de las crisis de cadena de pagos.

El catálogo de OpenAlex lo desmiente. Existe un preprint de RePEc titulado **"A Theory of Payments Crises" fechado en 2015**, cinco años antes de la carta. Y hay más de esa camada temprana y desconocida: *"Liquid bank liabilities"* (2015), *"Data Lessons on Bank Behavior"* (2018), *"Banks Adjust Slowly: Evidence and Lessons for Modeling"* (2019, 17 citas).

**H6' — las crisis no producen teoría, seleccionan teoría.** La idea de que el riesgo macroeconómico central es la interrupción de la cadena de pagos ya estaba formulada en 2015 y no había encontrado su caso. En marzo de 2020 el mundo le entregó el caso, y Bigio pudo escribir en cuarenta y ocho horas una propuesta de política operativa —comprar papel respaldado por crédito a pymes, coordinar con los cuatro bancos más grandes, suspender Basilea III— porque **el modelo ya estaba escrito**.

Eso es una tesis reconocible de historia del pensamiento económico: las crisis no crean ideas nuevas, activan ideas disponibles. Friedman decía algo muy parecido sobre la función de mantener vivas alternativas hasta que lo políticamente imposible se vuelve inevitable. Lo notable aquí es que podemos **fecharlo con documentos**, que es más de lo que suele poder hacerse.

---

## 7. Documentos que no teníamos y que hay que conseguir

OpenAlex reveló nueve trabajos ausentes del repositorio. En orden de valor para P3 y P4:

| Trabajo | Año | Dónde | Por qué importa |
|---|---|---|---|
| **"Política monetaria: una nueva perspectiva"** | 2022 | **Universidad del Pacífico eBooks** | **Capítulo de libro en español, publicado por su propia alma máter.** Es Bigio presentando su pensamiento monetario en castellano y para un público peruano. Para P4 no hay nada mejor en toda la lista |
| *A Theory of Payments Crises* | 2015 | RePEc | La prueba documental de H6' |
| *Un modelo semiestructural de proyección para la economía peruana* | 2009 | BCRP / RePEc | El Bigio del banco central; 8 citas |
| *Monetary Policy under Balance Sheet Uncertainty* | 2006 | BCRP / RePEc | El título ya anuncia toda la agenda posterior, catorce años antes |
| *A Monetary and Fiscal History of Latin America, 1960–2017* | 2020 | U. of Minnesota Press | El libro que contiene su capítulo sobre el Perú; 59 citas |
| *Banks Adjust Slowly: Evidence and Lessons for Modeling* | 2019 | SSRN | 17 citas; versión temprana de *Q-Theory of Banks* |
| *Speculation-Driven Business Cycles* | 2019 | SSRN | Versión temprana de *Heterogeneous Beliefs* |
| *Liquid bank liabilities* · *Data Lessons on Bank Behavior* | 2015 · 2018 | RePEc | Eslabones de la línea de tiempo |

**Los dos primeros son prioridad.** El capítulo de la UP, porque un documento suyo en español dirigido al Perú vale por diez papers en inglés para responder P4 ante un jurado de historia del pensamiento económico. El de 2015, porque sostiene H6'.

---

## 8. Estado de las hipótesis

| | Hipótesis | Estado | Evidencia |
|---|---|---|---|
| **H1** | La liquidez como resultado endógeno, no supuesto | **Respaldada** | Su ensayo de agenda se titula así; define liquidez él mismo |
| **H2** | Continuidad: cambia de escenario, no de fricción | **Respaldada** | Nueve preguntas encadenadas en `research_vision`; §7 suma eslabones de 2006, 2015, 2018 |
| **H3** | Mainstream post-Lucas: información + macro-finanzas + nuevo monetarismo | **Confirmada** | Akerlof es su referencia más citada; Kiyotaki-Moore en 11 documentos; Lagos-Wright en 7 |
| **H4** | Heredero de Tobin–Gurley & Shaw / Banking School | **Falsificada** | Gurley-Shaw: 0. Wicksell: 0. Keynes: 1, decorativo. Tobin = la q, salvo Baumol-Tobin 1956 |
| **H4'** | **Redescubrimiento sin genealogía** | **Nueva, sostenida** | Llega a la tesis del Banking School sin citarla; 95.5% de su bibliografía es post-1970 |
| **H5** | La marca peruana persiste transformada | **Respaldada** | Velarde como asesor; Castillo (BCRP) como coautor; *Dollar Liquidity Flows in a SOE* |
| **H6** | La política precede a la teoría | **Falsificada** | *A Theory of Payments Crises*, 2015, precede a la carta de 2020 |
| **H6'** | **Las crisis seleccionan teoría, no la producen** | **Nueva, sostenida** | Teoría en 2015 → caso en 2020 → propuesta de política en 48 horas |

Dos hipótesis caídas de seis, y las dos reemplazadas por versiones más interesantes. Eso es lo que se supone que hacen las hipótesis preregistradas.

---

## 9. Límites de este reporte

1. **La prueba de anclas doctrinales es de presencia/ausencia por documento.** Mide amplitud, no intensidad: "Sargent en 15 documentos" no significa que sea su influencia principal, sino que su nombre aparece en 15 de 46 textos, y en varios casos como agradecimiento o referencia de manual (*Ljungqvist & Sargent*), no como deuda teórica. La ausencia total, en cambio, sí es concluyente.
2. **El conteo de décadas incluye falsos positivos** (números de página y de volumen dentro de las cadenas bibliográficas). Por eso el 3.4% pre-1950 se reporta como techo, no como estimación.
3. **Las menciones institucionales no son citas.** Un paper con seis autores de seis instituciones cuenta seis veces. Sirven para comparar proporciones entre sí, no como conteo absoluto.
4. **FWCI sobre 40 exige cautela** (bases de comparación pequeñas en el campo-año). Se reporta junto al percentil.
5. **OpenAlex no devolvió 29 de las 148 referencias solicitadas**, así que el análisis de tradición de §4 descansa en 119 de 155 referencias de dos papers.
6. **Sesgo de selección en la muestra de referencias.** Los dos papers analizados en profundidad se eligieron por ser los más citados — y resultaron ser el de redes de producción y el de liquidez en mercados de activos, **ninguno de los dos de dinero y banca**. Es decir: el criterio de selección eligió justamente los papers menos aptos para poner a prueba H4. La conclusión de §4.3 se sostiene porque la búsqueda de anclas se hizo sobre los 46 documentos completos, no sobre esa muestra; pero el análisis fino de la tradición **monetaria** todavía está pendiente, y se hará extrayendo las bibliografías locales de Bianchi-Bigio, *Q-Theory of Banks* y Bigio-Sannikov.

---

## 10. Lo que sigue

- **Fase 2b:** extraer las bibliografías de los tres papers de dinero y banca desde los PDFs locales, para cerrar el límite 6. Ahí es donde Tobin 1963 y Gurley-Shaw tendrían que aparecer si H4 fuera a sobrevivir en alguna forma.
- **Fase 3:** lectura profunda de los ocho documentos ancla y plantilla de las 14 discussions.
- **Para ti:** conseguir *"Política monetaria: una nueva perspectiva"* (UP, 2022) y *A Theory of Payments Crises* (2015). El primero puede estar en la biblioteca de la UP o en el fondo editorial.

---

*Commit sugerido:*
`feat(saki_bigio): reporte bibliométrico Fase 2 — falsifica H4 y H6, confirma H3`
