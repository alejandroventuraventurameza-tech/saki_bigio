# Plan metodológico — P3 y P4 sobre Saki Bigio
**Trabajo grupal 01 · Historia del Pensamiento Económico · UP 2026-02**
Responsable: Alejandro (AL) · Preguntas: **P3** (ideas fundamentales) y **P4** (documentos donde las presenta)
**Versión 0.2 — 13/09/2026** · *(v0.1: diseño inicial. v0.2: incorpora el CV de agosto 2026 y los hallazgos de la Fase 1.)*

> Para el contexto del encargo, quién es Bigio y el estado del proyecto, ver **`CONTEXT.md`**. Este documento es el protocolo: qué se mide, cómo, y cómo se valida.

---

## 1. El problema metodológico de fondo

Aplicar historia del pensamiento económico a un autor **vivo, activo y técnico** tiene una dificultad que no tiene aplicarla a Smith o a Ulloa: no hay una obra cerrada ni una recepción sedimentada. Hay 46 documentos, veinte años de carrera, y un autor que sigue escribiendo. La tentación es resolverlo por descripción —listar papers y temas— y eso no responde P3.

La salida es tratar el corpus como **evidencia** y no como catálogo, con tres instrumentos que se corrigen entre sí:

| Instrumento | Qué ve | Qué no ve |
|---|---|---|
| **Bibliometría** | Estructura: con quién escribe, a quién cita, quién lo cita, cómo se agrupan sus temas | El contenido de una idea |
| **Texto como dato** | Prevalencia y deriva de conceptos, a escala que el ojo humano no alcanza | El argumento, la ironía, la objeción |
| **Lectura profunda** | Tesis, mecanismo, discrepancia, matiz | Todo lo que no da tiempo de leer |

Ninguno basta. El diseño consiste en usar cada uno donde es fuerte y en **cruzarlos** (§6).

### Tres reglas que no se negocian

1. **Medir no es interpretar.** Un conteo de palabras no es una idea. Todo número que entre al entregable va amarrado a una lectura que lo sostenga. Ash & Hansen (2023) lo dicen del propio campo: *lectura humana experta y algoritmos son complementos, y el benchmark de toda medida textual es el juicio humano experto.*
2. **Hipótesis antes que datos.** Las de §5 quedaron escritas antes de correr nada, con predicciones falsables. Si no pueden contradecirnos, no son evidencia.
3. **Honestidad de profundidad.** Convención heredada de `notas_lectura.json`: `integral` / `nucleo` / `parcial` / `mapeado`. Nada se cita como leído si solo fue mapeado.

---

## 2. Operacionalización de P3 y P4

**P3 — ¿Cuáles son las ideas fundamentales de su pensamiento económico?**

| Capa | Pregunta | Dónde se responde |
|---|---|---|
| **P3.a** Núcleo positivo | ¿Qué mecanismo reaparece como causa primera? | Papers publicados + WP; tópicos y concept detection |
| **P3.b** Compromiso metodológico | ¿Cómo cree que se produce conocimiento económico? | Discussions (lo que exige a otros) + `research_vision` |
| **P3.c** Núcleo normativo | ¿Qué debe hacer el banco central, y por qué? | Carta COVID, consultoría BCE, minicursos BCRP, discussions de política |

**P4 — ¿En qué documentos presenta su pensamiento?**

No es una bibliografía: es un argumento sobre la **jerarquía de géneros**. Cada formato tiene audiencia, extensión y grado de compromiso distintos, y el mismo autor dice cosas distintas en cada uno.

| Género | N | Qué revela | Grado de compromiso |
|---|---|---|---|
| Paper publicado | 13 | La tesis blindada ante referees | Máximo |
| Working paper / R&R | 11 | La frontera: dónde piensa hoy | Alto |
| **Discussion (slides)** | **14** | **Qué marco acepta y cuál no** | Alto pero informal |
| Comentario publicado | 3 | Lo mismo, ya canonizado | Máximo |
| Pre-PhD (BCRP) | 2 | El origen empírico peruano | — |
| Carta de política | 1 | Qué hace cuando el costo del error es real | Público |
| Research vision | 1 | Autodescripción | Declarativo |
| Divulgación / X | 1 + pendiente | Traducción al público no técnico | Mínimo |

**La tesis analítica de P4:** el género con mayor densidad de pensamiento por página no es el paper publicado sino la **discussion**, porque es el único donde un economista declara qué *no* acepta. Y la evidencia está a la vista: en su discussion de Barro-Bianchi (Bank of Korea, 2025), Bigio abre con *"I lived through Peru's hyperinflation"*, encuadra con Sargent-Wallace, y escribe literalmente **"I disagree"** sobre la interpretación FTPL de los autores. Nada de eso aparecería en un paper suyo.

---

## 3. El corpus y sus unidades

**46 documentos · 1,962 páginas · 3.38 M caracteres · 2006–2026.** Catálogo en `data/corpus.csv`; texto plano en `data/fulltext/`. Inventario y brechas en `CONTEXT.md` §4.

### 3.1 La unidad de análisis no es el documento

Punto técnico decisivo. Para bibliometría la unidad es el documento. **Para modelado de tópicos, no:** con 46 documentos un LDA es inestable y los "tópicos" resultantes son ruido con nombre. Por eso el texto se segmenta en **secciones** (intro, modelo, calibración, resultados, política, conclusión) y **párrafos**, llevando N a ~10³–10⁴ unidades.

Esto además habilita una medida que el documento entero no permite: **dónde dentro de un paper aparece cada concepto**. No es lo mismo que "liquidez" aparezca en la introducción —donde se vende el paper— que en la sección del modelo, donde se paga el costo de formalizarla. Esa distinción es precisamente lo que separa un tema de una idea fundamental.

### 3.2 Limpieza (crítica en economía)

Los PDFs de macro son 30–50% matemáticas, tablas y apéndices. El pipeline descarta ecuaciones (*display* e *inline*), tablas, figuras, apéndices y la lista de referencias —esta última se extrae aparte, es insumo de la red de citas— y conserva prosa. Sin este paso la matriz documento-término queda contaminada con residuos de LaTeX y todo lo que venga después se cae.

### 3.3 Las discussions son slides, no prosa

Hallazgo de Fase 1: los 14 archivos de `discussions/` son **presentaciones**, no textos. No tienen abstract ni referencias, sí tienen portada fechada. Consecuencias:

- **No entran al modelado de tópicos** con los papers: la densidad léxica de una lámina no es comparable con la de un párrafo. Se analizan aparte.
- **Sí entran al análisis cualitativo**, y con ventaja: una lámina obliga a la frase mínima. Cuando Bigio escribe *"Inflationary Finance ≠ FTPL"* en un bullet, está destilando una objeción teórica a su forma más compacta posible.
- Su portada da fecha y sede, lo que las hace fechables una por una (2012–2025) y por tanto utilizables en la línea de tiempo.

---

## 4. Las tres capas

### Capa A — Bibliometría (marco Donthu et al. 2021)

**A1. Análisis de desempeño.** Producción por año y género; coautores por paper; venue y su rango; citas totales y **citas normalizadas por edad y campo** (FWCI). Sin normalizar, un ranking de citas solo mide antigüedad y el "hallazgo" sería espurio.

**A2. Mapeo científico.** Cuatro redes:

| Red | Nodos / aristas | Qué responde |
|---|---|---|
| Coautoría | autores / co-firma | Su comunidad: Bianchi (3), Nuño (3), Zilberman (3), Weill-Zuniga (2), Silva (2)… |
| **Citas salientes** | obras que él cita | **Su tradición** — el instrumento central para H3 y H4 |
| Citas entrantes | quién lo cita | Su influencia y dónde aterrizó |
| Co-palabras | keywords + JEL | Sus temas y cómo se agrupan |

**A3. Evolución temática.** Diagramas estratégicos por subperiodo (centralidad × densidad, à la Cobo/SciMAT). Es la versión rigurosa de la línea de tiempo: un tema puede ser *motor*, *básico-transversal*, *emergente* o *periférico*, y verlo moverse de emergente a motor a lo largo de veinte años **es** la evolución del pensamiento.

**Fuentes y reparto del trabajo.**

| Fuente | Estado | Qué aporta | Quién |
|---|---|---|---|
| Semantic Scholar Graph API | ✔ verificada | Referencias y citas con metadata completa, en lote | Claude |
| Crossref | ✔ verificada | Metadata canónica, DOIs, referencias | Claude |
| OpenAlex | ✖ bloqueada aquí (cuota) | **FWCI**, percentil normalizado, taxonomía de *topics*, *facets* agregados | Alejandro vía ChatGPT — ver `consultas_openalex.md` |
| RePEc/IDEAS + CitEc, NBER | pendiente | Working papers de economía, que S2 y OpenAlex indexan mal | Claude |

**Advertencia de desambiguación:** Semantic Scholar devuelve **tres** IDs distintos para "Saki Bigio" (uno con 64 trabajos y 950 citas, h=14, que es el bueno). Se desambigua a mano contra `data/corpus.csv` antes de contar nada.

### Capa B — Texto como dato (marco Gentzkow, Kelly & Taddy 2019)

**B1. Representar.** Extracción con `pymupdf` → limpieza (§3.2) → lematización en inglés → matriz documento-término con n-gramas 1–3 (en macro los bigramas *son* los conceptos: *liquidity shock*, *interbank market*, *reserve demand*, *convenience yield*) → filtro de Arellano et al.: fuera los términos presentes en <10% o >90% de las unidades.

**B2. Mapear a medidas.** Dos vías, deliberadamente:

- **Inductiva.** Modelo de tópicos sobre unidades-sección. `k` **no** se elige por perplejidad sola: se estiman ~15 modelos, se eligen por coherencia sustantiva de los top-10 términos + lectura manual de una muestra + consistencia con la trayectoria conocida (protocolo Arellano, Izumi & Martínez 2026). Con corpus chico NMF es más estable que LDA; se reportan ambos y se discrepa en voz alta si difieren.
- **Deductiva.** *Concept detection* (Problema II de Ash & Hansen): diccionarios semilla expandidos con embeddings entrenados sobre el propio corpus, para conceptos que **vienen del curso de HPE, no del algoritmo**: `fricción`, `equilibrio general`, `bienestar/optimalidad`, `dinero y liquidez`, `intermediación bancaria`, `heterogeneidad y distribución`, `redes de producción`, `expectativas y creencias`, `Estado/institución`, `economía abierta y dolarización`.

Esta segunda vía es la que amarra el ejercicio al curso: los conceptos los pone la historia del pensamiento; la máquina solo mide dónde están.

**B3. Usar.** Participación de cada tópico/concepto regresada sobre **año** (deriva temática), sobre **género** (¿dice cosas distintas en una discussion que en un paper?) y sobre **sección** (¿la fricción está en el modelo o solo en la intro?).

### Capa C — Lectura profunda conjunta

La capa donde trabajamos los dos.

**Documentos ancla — lectura `integral`, sin excepción:**

| ID | Documento | Por qué |
|---|---|---|
| **V01** | *Liquidity and Macroeconomics: a vision and my research agenda* (2026) | Él respondiendo P3 en primera persona. El documento de mayor valor del repositorio, sin competencia |
| E02 | Bigio & Salas, efectos no lineales de política monetaria en economía dolarizada, Perú (BCRP, 2006) | El punto de partida |
| P03 | *Endogenous Liquidity and the Business Cycle* (AER 2015) | La semilla teórica |
| P07 | Bianchi & Bigio, *Banks, Liquidity Management and Monetary Policy* (Econometrica 2022) | Su paper más característico; artículo top-citado de Econometrica 2022-23 |
| W02 | Bigio & Sannikov, *A Model of Credit, Money, Interest, and Prices* (R&R J. of Finance) | La frontera actual |
| N01 | *A Concrete Policy Response to the Covid-19 Crisis* (15 marzo 2020) | El núcleo normativo bajo presión |
| C03 | Comentario a Martinelli & Vega, *The Monetary and Fiscal History of Peru, 1960–2017* | Bigio haciendo historia económica del Perú |
| D03 | Discussion de Piazzesi & Schneider, *Payments, Credit and Asset Prices* | Contiene una *"Two-Minute History of Money"* escrita por él: **Bigio haciendo historia del pensamiento monetario** |

**Protocolo de co-lectura** (el que funcionó en el Prompt 01 de HPE): por documento, una ficha con (i) tesis en una frase, (ii) la fricción y el mecanismo, (iii) 3–5 anclas textuales citables con página, (iv) el puente a HPE, (v) **dos preguntas abiertas para ti**. Tú lees el documento, reaccionas a la ficha, y recién ahí se cierra. Salida acumulativa en `notas_lectura_bigio.json`, con tu mismo esquema (`id`, `titulo`, `autores`, `profundidad`, `tesis`, `conceptos_clave`, `uso_en_trabajo`).

**Las 14 discussions** van con plantilla corta de seis campos: paper discutido, sede y fecha, qué elogia, **qué objeta**, qué marco alternativo propone, frase citable. El agregado de las catorce objeciones es el mejor retrato disponible de lo que Bigio considera *buena macroeconomía* — y responde P3.b mejor que cualquier paper suyo.

---

## 5. Hipótesis preregistradas y su estado

| | Hipótesis | Predicción falsable | Estado tras Fase 1 |
|---|---|---|---|
| **H1** | **Hilo conductor:** la liquidez no es un supuesto sino un resultado; los activos son líquidos o ilíquidos *en equilibrio*, y esa iliquidez endógena propaga los ciclos y limita a la política monetaria | El concepto `dinero y liquidez` domina en las cuatro etapas y aparece en secciones de modelo, no solo en introducciones | **Fuertemente respaldada.** Su propio ensayo de agenda se titula *"Liquidity and Macroeconomics"*, y dedica una nota al margen a que *"no tenemos una definición matemática apropiada de liquidez"* antes de ofrecer la suya |
| **H2** | **Continuidad, no ruptura:** no cambia de tema, cambia de escenario donde aplica la misma fricción | Alta persistencia del tópico liquidez, alta rotación de los tópicos de contexto institucional | Respaldada por la estructura de `research_vision`: nueve preguntas encadenadas, todas sobre liquidez en escenarios distintos |
| **H3** | **Ubicación doctrinal:** mainstream cuantitativo post-Lucas, en la intersección de nuevo keynesianismo, nuevo monetarismo (Kiyotaki-Wright, Lagos-Wright) y macro-finanzas (Bernanke-Gertler, Kiyotaki-Moore, Brunnermeier-Sannikov), con herencia de economía de la información (Akerlof) | Densidad de citas salientes hacia esos nodos | Pendiente (Fase 2). Indicio: coautoría con Sannikov; discussions a Lagos-Zhang y a Di Tella-Kurlat |
| **H4** | **El puente con el curso (apuesta fuerte):** heredero moderno de **Tobin–Gurley & Shaw**. El sistema bancario *crea* dinero sujeto a la gestión de su balance, y el dinero se analiza como elección de portafolio, no como agregado exógeno. *"A Q-Theory of Banks"* es la q de Tobin aplicada a bancos; su trabajo sobre implementación monetaria es la reencarnación microfundada de **Currency School vs. Banking School**, con Bigio del lado de la endogeneidad bancaria del dinero | Citas salientes densas hacia Tobin, Gurley-Shaw, Kiyotaki-Moore, Lagos-Wright, Diamond-Dybvig; y **ausencia** de densidad hacia el cuantitativismo de Chicago o la Nueva Economía Clásica pura | Pendiente. Indicio fuerte: cierra su ensayo con *"Regulation that treats banks as mere intermediaries misses their monetary role"* — que es, palabra por palabra, la tesis del Banking School |
| **H5** | **La marca peruana:** el origen (dolarización parcial, miedo a flotar) no desaparece; reaparece transformado en liquidez internacional en dólares | Co-ocurrencia entre `economía abierta/dolarización` y `dinero y liquidez` en 2022–2026, no solo en el pre-PhD | Respaldada por estructura: *Scrambling for Dollars* (con Bianchi y Engel) y *Dollar Liquidity Flows in a Small-Open Economy* (con Paul Castillo, del BCRP) |

> Si los datos matan H1 o H4, **eso es el hallazgo** y se reporta así. Ese es el punto de haberlas escrito antes.

### 5.1 Una hipótesis nueva, que solo apareció al leer el corpus

**H6 — La política precede a la teoría.** El 15 de marzo de 2020 Bigio escribe una carta abierta diciendo que el riesgo central del COVID no es la tasa de interés sino **el colapso de la cadena de pagos**, y propone operaciones de mercado abierto sobre crédito a pymes. Cinco años después, *A Theory of Payment-Chain Crises* (con Méndez y van Patten) formaliza exactamente ese objeto.

Si el patrón se repite —y hay al menos un segundo caso, la consultoría al BCE sobre políticas de balance en 2022 seguida del trabajo sobre regímenes de implementación monetaria y demanda de reservas—, entonces la dirección causal de su pensamiento va **del problema de política al modelo**, no al revés. Eso es una afirmación sustantiva de historia del pensamiento sobre cómo se produce teoría económica, y es verificable con fechas.

*Predicción falsable:* para los papers del núcleo, la fecha del primer documento de política o de la primera discussion sobre el tema precede sistemáticamente a la fecha del primer borrador del paper.

---

## 6. Validación

Lo que separa esto de un trabajo promedio no es el método sino que el método se someta a prueba.

| # | Prueba | Cómo | Costo |
|---|---|---|---|
| **V1** | Codificación humana vs. algoritmo | Muestra estratificada de 12 documentos, codificada por los dos de forma independiente contra el esquema de conceptos de §4-B2; se reporta κ de Cohen y **se discuten los desacuerdos**, que suelen ser más informativos que los acuerdos | Alto |
| **V2** | Contra taxonomía externa I | **Códigos JEL** declarados por el propio Bigio. Ya extraídos: 10 documentos los traen (E44, E51, E52, E58, G12, G21, G32, D82, F31, F41, C67, E31…). Si nuestros tópicos no se alinean con los JEL, el modelo está mal | Bajo |
| **V3** | Contra taxonomía externa II | **La taxonomía que él mismo declara** en `research_vision`: cinco familias, incluida una que llama *"Departures"*. ¿El algoritmo recupera esas cinco familias sin saberlas? | Bajo |
| **V4** | Convergencia entre capas | ¿La red de citas lo ubica en la misma tradición que el texto? Dos instrumentos independientes apuntando al mismo lugar | Medio |
| **V5** | Contra taxonomía externa III | Los *topics* de OpenAlex, taxonomía independiente tanto de los JEL como de la suya | Bajo (vía ChatGPT) |

Tener **tres taxonomías externas** —JEL, la suya, la de OpenAlex— para validar una clasificación inductiva es un lujo que la mayoría de aplicaciones de *text-as-data* no tiene. Hay que usarlo y hay que decirlo.

---

## 7. Periodización (corregida contra el CV)

La versión de v0.1 se basaba en nombres de archivo y estaba mal en las fechas de formación. Corregida:

| Etapa | Años | Posición institucional | Fricción trabajada | Documentos |
|---|---|---|---|---|
| **0. Origen peruano** | 1999–2005 | B.A. Universidad del Pacífico (1999–2003); **Research Economist, BCRP (2004–2005)** | Dolarización, tipo de cambio, corrupción — empírico, no teórico | E01, E02 |
| **1. Formación y giro teórico** | 2006–2012 | **Ph.D. NYU**; crisis 2008–09 | Liquidez endógena, información asimétrica | P01, P02 → P03 |
| **2. Consolidación** | 2012–2019 | Columbia GSB (2012–15) · Kenen Fellow Princeton (2014–15) · **UCLA (2015–)** | Bancos y gestión de liquidez, redes de producción, capacidad de riesgo | P03–P06, D01–D08 |
| **3. Emergencia pública** | 2019–2022 | **Research Scholar, FRB San Francisco (2019–21)**; COVID; tenure UCLA 2022 | Cadena de pagos, crédito vs. transferencias; salida al debate público | N01, N02, P07, W06, D09–D12 |
| **4. Frontera** | 2022–2026 | Associate Professor UCLA · NBER Research Associate 2026 · consultoría BCE | Creación de dinero, implementación monetaria, reservas, liquidez internacional en dólares, inflación pegajosa | W01–W05, W07–W11, P09–P13, D13, D14, V01 |

**El punto de quiebre está fechado y documentado por él mismo:** tercer año de doctorado en NYU, fin de semana de la caída de Bear Stearns, marzo de 2008. Su relato es que estaba discutiendo con gente de Wall Street qué debía hacer el gobierno para restaurar la liquidez y —en sus palabras— *"I was embarrassed that, as a PhD student, I couldn't even define market liquidity!"*. Toda la agenda posterior sale de esa vergüenza. Para una exposición de historia del pensamiento, es difícil pedir un origen mejor documentado.

---

## 8. Fases y entregables

| Fase | Qué se hace | Entregable | Estado |
|---|---|---|---|
| 0 | Plan metodológico | `plan_metodologico.md` | ✅ |
| 1 | Extracción y catalogación del corpus; CV incorporado; taxonomía autodeclarada recuperada | `CONTEXT.md`, `data/corpus.csv`, `data/fulltext/` | ✅ |
| 2 | Bibliometría A1–A2: coautoría, citas salientes y entrantes, co-palabras, FWCI | `data/redes/`, `reporte_bibliometrico.md`, figuras | ⏭ en curso |
| 3 | Lectura profunda de los 8 anclas + plantilla de las 14 discussions | `notas_lectura_bigio.json` | ⏭ |
| 4 | Capa textual completa: tópicos, concept detection, análisis por género y sección | `reporte_textual.md` | ⏭ |
| 5 | Síntesis: respuesta a P3 y P4 + **línea de tiempo interactiva** | `respuesta_p3_p4.md` + artifact | ⏭ |
| 6 | Material expositivo (5–7 min de los 15–20 del grupo) + ficha para AN y L | slides + `ficha_grupo.md` | ⏭ |
| 7 | X/@bigioeconomics vía Chrome + Selenium; análisis comparado académico vs. público | `social_analysis.md` | ⏭ última prioridad |

**Disciplina de tokens** (restricción de diseño, no un detalle): ningún PDF entra completo a la conversación —se extrae a disco y se procesa con scripts, y a contexto solo llegan fragmentos dirigidos—; todo conteo lo hace código, no lectura; cada fase cierra con un archivo en el repositorio, de modo que la siguiente sesión arranca leyendo un `.md` corto en vez de reconstruir; y nada se genera "por si acaso".

---

## 9. Riesgos y límites a declarar en el entregable

1. **Cobertura de working papers.** Semantic Scholar, Crossref y OpenAlex indexan mal los WP de economía, que es donde vive buena parte de la obra actual de Bigio (6 R&R + 6 WP). Los conteos van a subestimar su producción reciente. No es un error a corregir sino un límite a declarar — y de paso es un dato sobre la disciplina: en economía el *working paper* circula y se cita años antes de existir para los índices.
2. **Desambiguación de autor.** Tres IDs en Semantic Scholar. Se resuelve a mano.
3. **Corpus chico para modelado de tópicos.** Tratado en §3.1 con segmentación por secciones. Aun así los tópicos se reportan como **exploratorios**.
4. **Sesgo de supervivencia.** Tenemos lo que se pudo descargar. La brecha conocida está listada en `CONTEXT.md` §4.
5. **Slides ≠ prosa.** Tratado en §3.3: las discussions se analizan aparte, nunca mezcladas con papers en la misma matriz.
6. **Riesgo de sobreinterpretación.** Bigio es un autor vivo con veinte años de carrera, no un clásico cerrado. Todo enunciado sobre "su pensamiento" se formula como lectura sostenida en evidencia, no como veredicto. En particular, H4 es una **lectura nuestra**: Bigio no se reclama heredero de Tobin ni de la Banking School, y hay que decirlo.
7. **`device_bash` caído.** Una actualización de Windows del 8 de setiembre impide montar la carpeta desde mi shell. Puedo leer y escribir archivos, pero no correr `git` en tu máquina: los commits los haces tú desde GitHub Desktop con el mensaje que acompaña cada entrega.

---

## 10. Decisiones abiertas

1. **¿Pedimos los documentos faltantes?** Los de mayor valor: la tesis doctoral de NYU (el eslabón entre el Perú del BCRP y la agenda de liquidez) y cualquier **entrevista o charla en español**, que es el género donde un académico explica su pensamiento sin el corsé técnico.
2. **¿Hasta dónde llevamos H6?** Si el patrón "la política precede a la teoría" se sostiene con fechas, deja de ser un detalle y pasa a ser la tesis de la exposición. Es más original que H1, y más riesgoso.
3. **De las seis hipótesis, ¿cuál atacamos primero?** Mi voto: **H4**, porque es la única que puede fallar de forma interesante y porque es la que convierte un trabajo de bibliometría en un trabajo de historia del pensamiento económico.
