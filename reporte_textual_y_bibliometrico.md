# Análisis textual del front matter y análisis bibliométrico

> **DOCUMENTO HISTÓRICO, SUSTITUIDO.** Para el análisis vigente use `reporte_final_refinado.md` y el cuaderno ejecutado `analisis_bibliometrico.ipynb`. Este archivo contiene conteos de registros y referencias que no superaron la auditoría posterior.

**Proyecto Saki Bigio · P3 y P4 · Historia del Pensamiento Económico, UP 2026-02**
Fase 3 · 14/09/2026 · Corpus de 47 documentos (2006–2026)

---

## 0. Antes que nada: una variable que estaba mal

Hasta esta fase, el año de cada documento era el **año de publicación**. Para un paper de economía eso es un error, y resulta que es un error grande.

Crucé los 89 registros de OpenAlex —que incluyen las versiones NBER, SSRN y RePEc de cada trabajo— contra el corpus, y quedó el **año de primera versión pública** de cada obra. El resultado:

| Trabajo | 1.ª versión | Publicación | Rezago |
|---|---|---|---|
| Portfolio Choice and Settlement Frictions | 2015 | 2026 | **11 años** |
| Banks, Liquidity Management and Monetary Policy | 2013 | 2022 | 9 |
| A Q-Theory of Banks | 2018 | 2026 | 8 |
| Distortions in Production Networks | 2013 | 2020 | 7 |
| Heterogeneous Beliefs, Asset Prices and Business Cycles | 2019 | 2026 | 7 |
| Debt-Maturity Management with Liquidity Costs | 2017 | 2023 | 6 |
| Repurchase Options in the Market for Lemons | 2020 | 2026 | 6 |
| Endogenous Liquidity and the Business Cycle | 2010 | 2015 | 5 |

Sobre los trece papers publicados: **media de 4,9 años, mediana de 6, máximo de 11.** Y hay working papers que ya llevan más: *A Theory of Payment-Chain Crises* circula desde 2015 y sigue sin publicarse; *A Model of Credit, Money, Interest and Prices* desde 2016.

**Por qué esto es un hallazgo de P4 y no un detalle técnico.** Si uno fecha el pensamiento de Bigio por la fecha de publicación, se equivoca en promedio por casi cinco años y en un caso por once. Y explica de paso el fenómeno de la literatura gris que ya habíamos medido: el working paper de Bianchi y Bigio acumula 119 citas y el artículo de *Econometrica* del mismo paper, una. No es un defecto de los índices: es que **durante nueve años el objeto que la profesión citaba era el working paper**, porque era el único que existía.

Todo lo que sigue usa el año de primera versión. La periodización queda en 9 / 16 / 22 documentos, mucho más equilibrada que la anterior.

---

## Parte I — Análisis textual del front matter

### 1. Qué se analizó y qué no

Unidad: **título + abstract + keywords declarados**, de los 47 documentos. Es deliberadamente el material que el propio autor escribe para presentar su trabajo — lo que Gentzkow, Kelly y Taddy llamarían la primera representación, y lo que un bibliómetra analizaría primero.

**Cobertura real, declarada sin maquillaje:**

| | Documentos |
|---|---|
| Con abstract recuperable | 21 de 47 |
| Con keywords declarados | 15 |
| Con códigos JEL | 13 |
| Solo con título | 26 |

Los 26 sin abstract no son un fallo de extracción: son los **14 juegos de diapositivas de discussions**, los 3 comentarios publicados, la carta del COVID, el ensayo de agenda, la charla de divulgación y el capítulo en castellano — géneros que por naturaleza no llevan abstract.

**Consecuencia metodológica que hay que decir en la exposición:** con esta cobertura, el análisis del front matter sirve para leer **la evolución de los temas declarados**, no para medir prevalencia de conceptos. Las frecuencias por periodo que aparecen abajo son indicativas, no estimaciones. Lo que medirá prevalencia es el análisis de texto completo, que es la fase siguiente y trabajará sobre 3,38 millones de caracteres en lugar de 21 abstracts.

### 2. Los términos que lo distinguen en cada periodo

TF-IDF sobre los tres periodos concatenados, 1–2 gramas, sin palabras vacías:

| Periodo | n | Términos distintivos |
|---|---|---|
| **I · 2006–2013** | 9 | distortions · sectoral distortions · inputted income · desarrollo · crecimiento · liquidity management · labor · collection |
| **II · 2014–2019** | 16 | payments · asset prices · business cycles · equity · beliefs · crises · asset pricing · heterogeneous beliefs · insurance |
| **III · 2020–2026** | 22 | demand · inflation · dollar · dollar liquidity · reserve · transfers · credit policy · fluctuations · covid · margin |

Se lee solo: del Perú y la distorsión sectorial (con dos documentos en castellano, de ahí *desarrollo* y *crecimiento*), a los precios de activos y las creencias, a la demanda de reservas, el dólar y la inflación.

**Un detalle vale la pena:** *liquidity management* aparece como término distintivo ya en el **primer** periodo — porque *Banks, Liquidity Management and Monetary Policy* circula desde 2013, no desde 2022. Con la periodización vieja ese término habría aparecido recién en el tercer periodo, y la historia habría sido otra.

### 3. La huella JEL: dispersión, concentración, reapertura

Los códigos JEL son la taxonomía que el propio autor declara, y por eso son la mejor validación externa disponible. Familias por periodo:

| Periodo | Familias JEL presentes |
|---|---|
| **I · 2006–2013** | C, D, **E**, **G**, H, O — *seis familias* |
| **II · 2014–2019** | **E** (7), **G** (6) — *solo dos* |
| **III · 2020–2026** | D (1), **E** (7), **F** (3), **G** (4) |

Los códigos concretos más declarados: **E52** y **E58** (política monetaria y su conducción), **E44** (mercados financieros y macroeconomía), **E31** (nivel de precios e inflación), **E51** (dinero y crédito), **G21** (bancos).

Esto es una trayectoria limpia en tres tiempos:

1. **Dispersión.** El Bigio joven publica sobre corrupción y desarrollo (D73, O11, O50), evasión tributaria (D21, H26), dolarización y redes de insumo-producto (C67). Explora.
2. **Concentración.** Entre 2014 y 2019 **desaparece todo lo que no sea E o G**. Es el periodo en que se convierte en un macroeconomista monetario y nada más.
3. **Reapertura internacional.** Desde 2020 aparece la familia **F** —F31 tipos de cambio, F41 macroeconomía de economía abierta—, que no estaba en el periodo II.

Y la familia F es la marca peruana volviendo: *Scrambling for Dollars* y *Dollar Liquidity Flows in a Small-Open Economy*, este último con **Paul Castillo, del BCRP**. **H5 respaldada por la taxonomía que él mismo declara**, que es una evidencia mejor que nuestra lectura.

### 4. Trayectoria de conceptos — con su advertencia

Porcentaje de documentos de cada periodo cuyo front matter menciona el concepto:

| Concepto | I | II | III |
|---|---|---|---|
| liquidez | 22 % | **38 %** | 27 % |
| bancos | 11 % | **31 %** | 23 % |
| política monetaria | 22 % | 19 % | **27 %** |
| reservas / encaje | 11 % | 12 % | **18 %** |
| deuda | 0 % | 19 % | 18 % |
| crédito | 11 % | **25 %** | 9 % |
| inflación | 0 % | 0 % | **14 %** |
| dólares / tipo de cambio | 11 % | 0 % | 9 % |
| pagos | 0 % | 12 % | 0 % |

**Esta tabla no prueba nada por sí sola** y hay que tratarla con desconfianza: 26 de 47 documentos entran con el título solamente, de modo que un paper con abstract tiene mucha más superficie léxica que una discussion. El patrón que sí sobrevive a esa objeción es el de la familia JEL de §3, porque ahí cada documento aporta exactamente un conjunto de códigos, sin importar su longitud.

Lo que la tabla sugiere —y que el texto completo tendrá que confirmar o desmentir— es que **liquidez** no crece con el tiempo: ya está alta desde el principio y se mantiene. Que es exactamente lo que predice H2: no cambia de tema, cambia de escenario.

---

## Parte II — Análisis bibliométrico

### 5. Análisis de desempeño

**Producción.** 47 documentos en el corpus; ~35 obras distintas según OpenAlex una vez agrupadas las versiones; 13 papers publicados, 11 working papers o R&R, 14 discussions, 3 comentarios publicados.

**Revistas.** Está en **cuatro de las cinco revistas top de la profesión**: *American Economic Review* (2015), *Econometrica* (2022), *Quarterly Journal of Economics* (2020) y *Review of Economic Studies* (dos veces, ambas en 2026). Falta el *Journal of Political Economy* propiamente dicho — tiene *JPE: Macroeconomics*, que es una revista distinta y más joven. Conviene decirlo así de preciso, porque decir «las cinco top» sería falso y alguien puede corregirlo.

**Impacto normalizado.** Los dos papers centrales están en el 0,2 % superior de su campo-año: *Endogenous Liquidity* con FWCI 61,6 (percentil 99,8) y *Distortions in Production Networks* con 42,8 (percentil 99,9). Cautela obligatoria: valores de FWCI sobre 40 dependen de bases de comparación pequeñas; por eso se reporta el percentil al lado.

**Curva de citas recibidas por año** (OpenAlex, todas las versiones):

```
2012   12  ███
2013   21  █████
2014   34  ████████
2015   34  ████████
2016   51  ████████████
2017   53  █████████████
2018   59  ██████████████
2019   93  ███████████████████████
2020  128  ████████████████████████████████
2021   91  ██████████████████████
2022   99  ████████████████████████
2023  120  ██████████████████████████████
2024   89  ██████████████████████
2025   97  ████████████████████████
2026   47  ███████████   (año en curso)
```

El salto está entre 2018 y 2020: de 59 a 128 citas anuales. Coincide con la publicación de *Distortions in Production Networks* en el QJE y con el COVID, cuando su trabajo sobre liquidez y crédito se volvió urgente. Desde entonces se estabiliza en torno a 100 citas anuales.

### 6. Análisis de colaboración

| Periodo | Trabajos | Coautores por trabajo | Firmados solo |
|---|---|---|---|
| I · 2006–2013 | 5 | 0,60 | **2** |
| II · 2014–2019 | 8 | 1,62 | 0 |
| III · 2020–2026 | 12 | 1,83 | 1 |

Treinta y un coautores distintos en veinticinco trabajos. Repiten **Javier Bianchi (3), Galo Nuño (3), Eduardo Zilberman (3)**, Dejanir Silva (2) y la dupla Weill–Zuniga (2). Red amplia y poco densa, característica de la macroeconomía contemporánea.

Dos cosas que vale la pena mirar juntas:

**Colabora cada vez más.** De 0,6 coautores por trabajo a 1,83. Es la trayectoria normal de una carrera académica moderna, pero tiene una consecuencia: **sus dos papers de mayor impacto normalizado son los dos que firmó solo.** *Learning Under Fear of Floating* (2009) y *Endogenous Liquidity* (2010) son sus dos únicos trabajos individuales, y el segundo tiene el FWCI más alto de toda su obra.

**Sus coautores son de bancos centrales.** Nuño en el Banco de España, Bianchi en la Fed de Minneapolis, D'Erasmo en la Fed de Filadelfia, Paul Castillo en el BCRP, Abad y García-Villegas en el Banco de España. La red de coautoría y el mapa de quién lo cita apuntan al mismo sitio, que es la convergencia que pedía la prueba V4.

### 7. Mapeo científico: quién lo cita y a quién cita

Ya reportado en el informe de la Fase 2 y cerrado en la 2b, se resume aquí para tener todo junto.

**A quién cita** (nueve bibliografías del núcleo de dinero y banca, 178 412 caracteres): **Lagos en 7 de 9**, seguido de Brunnermeier (6), Kiyotaki (5), Piazzesi (5), Rocheteau (5), Afonso (5), Gertler (4), Krishnamurthy (4), Bernanke (4), Diamond (4), Poole (3), Bindseil (3), Williamson (3). Nuevo monetarismo, macro-finanzas de fricciones y literatura de implementación monetaria.

**Quién lo cita** (710 trabajos citantes de sus seis papers principales): el Sistema de la Reserva Federal suma **162 menciones institucionales** contra las **108** de Chicago, Yale, Columbia, Harvard y NYU sumadas. Por tipo de institución, `government` y `facility` aportan 160 menciones fuera del sistema universitario. Por país: Estados Unidos 375, China 96, Reino Unido 87, España 29, Brasil 12.

**Profundidad histórica**: el 95,5 % de los años citados en sus bibliografías es de 1970 en adelante; el 57 %, de 2010 en adelante. Sus anclas más antiguas son Baumol (1952), Tobin (1956), Akerlof (1970), Merton (1974), Hulten (1978) y Wilson (1979).

---

## 8. Qué falta

| Pendiente | Qué aportaría |
|---|---|
| **Análisis de texto completo** | 3,38 millones de caracteres segmentados por sección. Es lo único que puede medir prevalencia de conceptos con seriedad, y lo que permitirá ver si la liquidez aparece en las secciones de modelo o solo en las introducciones |
| Detección de conceptos deductiva | Diccionarios semilla derivados del curso de HPE, con embeddings entrenados sobre el propio corpus (protocolo Ash y Hansen) |
| Red de co-citación | Qué autores son citados *juntos* por él, que es distinto de cuáles cita |
| Validación V1 | Codificación manual de doce documentos por los dos, y κ de Cohen contra la clasificación automática |
| Las 14 discussions | Plantilla de seis campos por cada una: qué elogia, **qué objeta**, qué marco alternativo propone |

---

## 9. Archivos generados

```
data/corpus.csv                        47 filas, ahora con anio_primera_version
data/frontmatter.json                  título, abstract, keywords y JEL por documento
data/analisis_textual.json             términos distintivos, trayectorias, JEL por periodo, red de coautoría
data/bibliometria.json                 citas por año, rezagos, colaboración por periodo
data/anclas_doctrinales.json           32 anclas doctrinales por documento
data/openalex/*.json                   las seis consultas
```

---

*Commit sugerido:*
`feat(saki_bigio): análisis textual del front matter y bibliometría; corrige la periodización por año de primera versión`
