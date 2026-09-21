# CONTEXT.md — Proyecto "Saki Bigio" (Historia del Pensamiento Económico, UP 2026-02)

> **Qué es este archivo.** Es el archivo de contexto único del proyecto. Cualquier asistente (Claude, ChatGPT, Codex) que vaya a trabajar aquí debe leerlo primero y tratarlo como la fuente de verdad sobre el estado del trabajo.
> **Versión 4 · 15/09/2026 · control asistido del extractor de referencias incorporado.**

---

## 1. El encargo

Trabajo grupal 1 del curso **Historia del Pensamiento Económico** (Universidad del Pacífico, 2026-02): *"Aportes de economistas peruanos al pensamiento económico"*. El grupo escogió a **Saki Bigio**.

Exposición de 15–20 minutos, fechas 15 y 22 de setiembre según sorteo; la presentación se envía al docente el primer día de exposiciones antes de clase. La nota es individual pero se valora la parsimonia del grupo.

**Reparto de las 8 preguntas** (`asignacion_preguntas.xlsx`):

| Integrante | Preguntas |
|---|---|
| AN — Aníbal | 1 biografía · 2 contexto histórico · 5 beneficiarios |
| **AL — Alejandro** | **3 ideas fundamentales · 4 documentos donde las presenta** |
| L — Luis | 6 utilidad para su época · 7 contribuciones perdurables · 8 discípulos y legado |

**Este repositorio cubre solo P3 y P4.** Lo que resulte útil para AN y L se les entrega aparte.

---

## 2. Traducción de las preguntas

**P3 — Ideas fundamentales.** No es "¿de qué escribe?" sino *¿cuál es la fricción que él cree que organiza la macroeconomía, y qué se sigue de eso para la política?* Tres capas: **P3.a** núcleo positivo, **P3.b** compromiso metodológico, **P3.c** núcleo normativo.

**P4 — Dónde lo presenta.** No es una bibliografía: es un argumento sobre la **jerarquía de géneros**. Cada formato tiene audiencia y grado de compromiso distintos, y el mismo autor dice cosas distintas en cada uno.

---

## 3. Quién es Saki Bigio (verificado contra su CV, agosto de 2026)

| | |
|---|---|
| Posición | Associate Professor con tenure, Departamento de Economía, **UCLA** (2022–); Assistant Professor 2015–2022 |
| Nacionalidades | Perú, EE. UU., Polonia, España |
| Intereses declarados | *Macroeconomics, Finance and Banking* |
| Formación | **B.A. Universidad del Pacífico, 1999–2003** (asesor de tesis: **Julio Velarde**); **Ph.D. New York University, 2006–2012** (asesores: **Thomas Sargent** y **Ricardo Lagos**) |
| Primer empleo | **Research Economist, BCRP, 2004–2005**, bajo **Renzo Rossini** |
| Trayectoria | Columbia Business School 2012–2015 · Kenen Fellow, Princeton 2014–2015 · UCLA 2015– · Research Scholar, Fed de San Francisco 2019–2021 |
| NBER | Faculty Research Fellow 2015–2025; **Research Associate (EFG + IFM) 2026–** |
| Editorial | Editorial Board, *AEJ: Macroeconomics* (2024–) |
| Producción | 14 publicaciones · 3 comentarios publicados · 6 R&R · 6 working papers |
| Revistas top | **Cuatro de las cinco top**: AER, Econometrica, QJE y REStud (×2). Tiene *JPE: Macroeconomics*, que no es el JPE — decirlo con precisión |
| Consultorías | **Banco Central Europeo — evaluación de políticas de balance (2022)**; Rivian Technologies (2022) |
| Vínculo con Perú | Premio de Investigación BCRP 2005 · minicursos dictados en el BCRP (2015, 2024) · Best Publication, Peruvian Economic Association 2020, 2021, 2022, 2025 · Keynote PEA 2025 · Banco Mundial 2025 · organizó *Frictions and Exchange Rates* (Cusco 2019) y *Expectations and Inflation* (Lima 2024) |

---

## 4. El corpus

**48 documentos · 1 995 páginas · 3,42 millones de caracteres · 2006–2026.** Catálogo en `data/corpus.csv`; PDFs fuente en `saki_research/`. La extracción de referencias se hace directamente desde esos PDFs y produce una base candidata, no un resultado validado.

| Género | N | Nota |
|---|---|---|
| Publicados | 13 | |
| Working papers / R&R | 11 | |
| **Discussions (diapositivas)** | **15** | Todas fechadas, 2012–2025; se reincorporó *Safety Traps* (2016) |
| Comentarios publicados | 3 | Uno sobre la historia monetaria y fiscal del Perú |
| Pre-PhD (BCRP) | 2 | 2006 |
| Capítulo en castellano | 1 | **S01**, documento ancla |
| Carta de política | 1 | COVID, marzo de 2020 |
| Research vision | 1 | Agosto de 2026 |
| Divulgación | 1 | Charla Techsuyo, 2020 |

**Variable crítica: `anio_primera_version`.** El año de publicación es una fecha engañosa en economía. El rezago documentado entre primera versión y publicación en los trece artículos es **4,8 años de media; mediana 6; máximo 9**. La trazabilidad está en `data/first_version_sources.csv`: siete fechas tienen confianza alta y seis media. Toda periodización usa `anio_primera_version`, pero debe declarar esa incertidumbre.

**Faltan:** *A Monetary Theory of Bank Balance Sheets*; *A Comparative Statics Approach to Open-Market Operations*; los dos posts de Medium; la tesis doctoral de NYU; el archivo de X/@bigioeconomics.

### 4.1 Su propia taxonomía

En `research_vision.pdf` Bigio clasifica su obra posterior al doctorado en cinco familias: *Liquidity and Asymmetric Information* (5), *Money and Banking* (8), *Money, Credit and the New Keynesian Model* (4), *International Liquidity* (2) y **"Departures"** (3). Nos dice él mismo qué considera núcleo y qué periferia. Y su tabla empieza en 2012: deja fuera el BCRP, *Learning Under Fear of Floating* y el paper de evasión tributaria. **La distancia entre su autonarrativa y el registro completo es material de P3.**

---

## 5. Los hallazgos, en orden de importancia

### 5.1 Hay dos historias de origen, y dependen del público — **el hallazgo central de P4**

| | `research_vision.pdf` (2026) | **S01, capítulo UP (2022)** |
|---|---|---|
| Idioma / público | Inglés, profesión internacional | **Castellano, Perú** |
| Origen de su agenda | **Bear Stearns, marzo de 2008** | **BCRP, 2004** |
| Cita | *"I was embarrassed that, as a PhD student, I couldn't even define market liquidity!"* | *"Estas dos áreas estaban prácticamente divorciadas… ¿Por qué en nuestros modelos no tenemos bancos?"* |
| Referencias | ~90 | **3** |

Cuatro años de diferencia, ninguna de las dos falsa. El género y el público seleccionan qué parte del pensamiento aflora.

### 5.2 El núcleo positivo tiene nombre: la neutralidad de Wallace

> **La idea fundamental de Bigio es que la neutralidad de Wallace no se cumple, y la razón es la liquidez.**

Wallace (1981) es un Modigliani-Miller para operaciones de mercado abierto: bajo ciertas condiciones la composición del balance del banco central es irrelevante. El **núcleo monetario** de Bigio estudia fricciones que rompen esa irrelevancia. "Wallace" aparece en **9 de 48 documentos**.

### 5.3 Qué NO significa su crítica al modelo neokeynesiano — **advertencia importante**

Bigio critica el modelo NK por reducir la política a una sola tasa y tratar la banca como un velo. **Eso no es abogar por metas de agregados monetarios.** Su frase completa pide *"una reconciliación entre el modelo neokeynesiano y las estadísticas monetarias"* — integrar, no reemplazar. Su literatura es la de **implementación** (Poole 1968 y 1970, Bindseil, Afonso-Lagos, Ennis-Keister): corredor contra piso, reservas escasas contra abundantes. Y su paper W07 es de **estimación de la demanda de reservas**, cuya bibliografía incluye Baumol (1952), Tobin (1956), Laidler (1966, 1969) y **Lucas y Nicolini (2016), *On the Stability of Money Demand***, más Haavelmo y Philip Wright por el problema de identificación. **La inestabilidad de la demanda de dinero no es una objeción a Bigio: es su objeto de estudio.**

### 5.4 La experiencia del BCRP precedió una formalización específica de Bigio

Cronología documentada: encaje diferenciado por moneda en **1992** (Rossini 2016, p. 27) → metas de inflación bajo dolarización en 2002 → encaje marginal contracíclico 2007–08 y reducción de encajes **antes** que la tasa en octubre de 2008, con el primer recorte recién el 2 de febrero de 2009 (Quispe y Rossini 2010) → los practicantes escriben su caso en 2010 → el BIS lo analiza en 2011 citándolos a ellos → primera versión verificable de Bianchi y Bigio en **2013** (OpenAlex W2188338937), versión NBER en 2014 y *Econometrica* en 2022 → asesoría al BCE en 2022.

Prueba clave: Quispe y Rossini (2010) tiene **once referencias, ninguna a un modelo teórico**, y en 35 936 caracteres extraídos no aparecen "model" ni "theory". Allí escriben *"the disconnection of other interest rates with the policy rate"*. La primera versión verificable del modelo bancario de Bianchi y Bigio circula **tres años después**, en 2013.

**Alcance obligatorio:** esto no demuestra que la práctica precediera a “la teoría” en general. P07 cita antecedentes como Poole (1968), no modela dolarización y no menciona al Perú. El encaje cambiario de 1992 y el modelo bancario de 2013 son objetos relacionados, no idénticos. El BCRP actuó con sustento analítico y cuantitativo, y el Perú fue temprano pero no único: Montoro y Moreno estudian también Brasil y Colombia. La distancia descriptiva 1992→2013 es 21 años; no es una estimación causal.

### 5.5 A Bigio lo leen los bancos centrales, sin sumar jerarquías institucionales

Las seis obras canónicas más citadas corresponden a 14 registros/versiones y reúnen **774 trabajos citantes únicos** en OpenAlex. En la faceta de linaje institucional, el nodo padre **Federal Reserve System** aparece en 98 trabajos. Los 28 del Board, 21 de la Fed de Nueva York y 15 de Minneapolis no se suman al padre: la taxonomía es jerárquica y de pertenencia múltiple.

### 5.6 La huella JEL es descriptiva y sensible al corte temporal

Con el corte 2006–2013 / 2014–2019 / 2020–2026, el primer periodo contiene C, D, E, G, H y O; el segundo, E y G; el tercero, D, E, F y G. Si el primer corte termina en 2012, C pasa al segundo periodo. Es robusto el predominio agregado de **E y G**; no lo es la ubicación exacta de las familias menores. La aparición de F documenta economía internacional, pero no identifica por sí sola una “marca peruana”.

### 5.7 La unidad bibliométrica correcta es la obra, no el registro

OpenAlex entrega **89 registros brutos**. Tras excluir 12 datasets y 2 softwares quedan 75 registros de investigación, que `canonicalize_openalex.py` agrupa en **34 obras canónicas**. No se suman `cited_by_count` entre versiones porque los conjuntos de citantes pueden solaparse. Por ello se retira el “39 % en literatura gris”: era una atribución de registros, no una participación identificada a nivel de obra.

---

## 6. Estado de las hipótesis

| | Hipótesis | Estado |
|---|---|---|
| H1 | La liquidez no es un supuesto sino un resultado de equilibrio | Respaldada |
| H2 | No cambia de tema: cambia de escenario donde aplica la misma fricción | Respaldada |
| H3 | Mainstream post-Lucas | **Confirmada, con escuela precisa: nuevo monetarismo (Lagos en 7 de 9 bibliografías, Rocheteau, Williamson) + macro-finanzas + implementación monetaria** |
| H4 | Heredero explícito de Tobin–Gurley y Shaw | **No respaldada por el corpus.** Gurley-Shaw y Banking School no aparecen como genealogía explícita; esto no prueba ausencia de influencia indirecta |
| **H4′** | **No hay genealogía histórica explícita hacia Gurley–Shaw o la Banking School en el corpus** | **Sostenida en esta formulación acotada.** La búsqueda nula es evidencia textual, no evidencia de independencia cognitiva |
| H5 | El origen peruano es la pregunta fundacional, no un residuo | **Versión fuerte, respaldada** |
| H6 | En Bigio, la política precede a la teoría | Falsificada: *A Theory of Payments Crises* es de 2015, anterior a la carta del COVID |
| **H6‴** | **La implementación peruana precedió una formalización específica de Bigio** | **Sostenida con cautela.** No equivale a precedencia sobre la teoría monetaria en general; véase §5.4 |

---

## 7. Método

- **Capa A, bibliometría** (Donthu et al. 2021): desempeño sobre **obras canónicas** y mapeo exploratorio. Las facetas institucionales se tratan como pertenencias múltiples, no como categorías aditivas.
- **Capa B, texto como dato** (Gentzkow, Kelly y Taddy 2019): títulos limpios como unidad comparable para 48 documentos. La cobertura desigual de abstracts impide mezclar título y abstract para medir prevalencias. Con este tamaño, co-palabras y JEL son exploratorios y se reporta sensibilidad a umbrales/cortes.
- **Capa de referencias:** `parse_refs.py` produjo 1.413 entradas candidatas en 30 documentos. Tres controles asistidos y sus remediaciones corrigieron los defectos observados; después se ejecutó una auditoría técnica integral sobre todas las filas. Esta última combinó tamizaje determinista, incorporación de las 300 observaciones ya contrastadas y revisión visual asistida de fallos literales, patrones multiobra, entradas largas, años atípicos y marcadores de contaminación. Se documentaron 18 operaciones estructurales, con 19 filas netas añadidas, y 17 correcciones de frontera de título. La candidata vigente contiene 1.435 referencias: 1.343 aceptadas, 90 corregidas y 2 excepciones atribuibles a la propia fuente. Persisten un título omitido en el PDF y seis años faltantes, uno de ellos mal impreso como «219» por la fuente. Esta cobertura técnica integral fue realizada por Codex y no equivale a una auditoría humana externa. OpenAlex respondió para las 1.435 filas mediante 1.267 consultas únicas: 370 filas —303 identidades distintas— alcanzaron alta confianza automática y 24 quedaron en revisión. La adjudicación documental aceptó 19 y rechazó 5; una fila adicional se resolvió directamente por DOI. La capa separada contiene así 390 filas resueltas y 320 identidades distintas; 1.045 filas permanecen sin identidad aceptada. La copia conservadora está en `data/referencias_parseadas_candidate_openalex.json`, la adjudicada en `data/referencias_parseadas_candidate_openalex_adjudicada.json`, la auditoría integral en `data/auditoria_integral_ia_referencias.json` y el dictamen en `data/auditoria_openalex_coincidencias_provisionales.json`; ninguna habilita todavía redes exhaustivas ni porcentajes históricos. Estado externo en `data/openalex/openalex_reference_resolution_status.json`.
- **Capa C, lectura profunda conjunta**: fichas con anclas citables y dos preguntas abiertas; Alejandro lee y reacciona antes de cerrar cada ficha. Salida en `notas_lectura_bigio.json`.
- **Validación**: V1 codificación humana vs. algoritmo (κ de Cohen) · V2 códigos JEL · V3 taxonomía autodeclarada · V4 convergencia entre red de citas y texto · V5 topics de OpenAlex.

---

## 8. Convenciones del repositorio

```
saki_bigio/
├── CONTEXT.md                      ← este archivo
├── plan_metodologico.md            protocolo completo
├── consultas_openalex.md           queries para ejecutar fuera del entorno
├── reporte_bibliometrico.md        Fase 2
├── reporte_fase2b_y_H6.md          Fase 2b y veredicto sobre H6
├── reporte_textual_y_bibliometrico.md   Fase 3 (histórico; cifras sustituidas)
├── reporte_final_refinado.md            síntesis vigente para P3 y P4
├── fuentes_H6.md                   diseño de falsación y fuentes
├── fichas/                         fichas de lectura por documento
├── data/                           corpus.csv, first_version_sources.csv, frontmatter.json,
│                                   referencias_parseadas_candidate.json, openalex/
├── saki_research/                  PDFs fuente por género
├── theoretical_background/         metodología + notas_lectura.json
└── miscellaneous/
```

- **IDs del corpus:** `P##` publicado · `W##` working paper/R&R · `D##` discussion · `C##` comentario · `E##` pre-PhD · `S01` capítulo en castellano · `V01`/`N##` otros.
- **Commits:** *conventional commits* en español, uno por entrega, ejecutados por Alejandro desde GitHub Desktop.
- **Honestidad de profundidad:** `integral` / `nucleo` / `parcial` / `mapeado`. Nada se cita como leído si solo fue mapeado.

---

## 9. Reglas para asistentes que trabajen en este proyecto

1. **Cada afirmación lleva su fuente pegada.** Autor, año y página, o el archivo de datos del que sale el número. Una afirmación sin verificación posible no entra al entregable.
2. **Medir no es interpretar.** Un conteo de palabras no es una idea. Todo número va amarrado a una lectura que lo sostenga.
3. **Nada de datos inventados.** Si una cifra no está verificada contra el CV, el PDF o una API, se marca como pendiente.
4. **No resumir datos crudos.** Si se trae una respuesta de una API, se trae el JSON literal.
5. **Trabajo conjunto.** Alejandro co-lee y valida; no se cierran fichas ni conclusiones sin su reacción.
6. **Eficiencia.** Ningún PDF completo entra al contexto: se extrae a disco y se procesa con scripts.

---

## 10. Estado y siguiente paso

Precisamente, la corrección del extractor, sus tres controles asistidos, la auditoría integral y las remediaciones quedaron documentados entre el 15 y el 21/09/2026. El libro `data/auditoria_referencias.xlsx` conserva las hojas históricas y agrega «Auditoría integral» y «Detalle integral» para las 1.435 filas. La base inicial de 1.242 filas se preserva en `data/archive/referencias_parseadas_candidate_v1.json`; los estados intermedios hasta 1.416 filas permanecen en las versiones v2–v6; y los candidatos inmediatamente anteriores y posteriores al control exhaustivo están en `data/archive/referencias_parseadas_candidate_v7_exhaustive_ai_audit.json` y `data/archive/referencias_parseadas_candidate_v8_structural_ai_audit.json`. El archivo candidato vigente mantiene 1.435 entradas, seis años ausentes —cinco por condición *forthcoming* y uno mal impreso en la fuente— y un título ausente en el propio registro fuente. El control integral registró 18 operaciones estructurales, 19 filas netas añadidas y 17 correcciones de frontera de título; su cobertura es completa en sentido técnico, pero no es una certificación humana externa. Las consultas OpenAlex y la adjudicación de sus 24 coincidencias provisionales están completas: 370 asignaciones automáticas, 19 aceptadas tras revisión y una resolución directa por DOI cubren 390 filas —320 identidades distintas—, mientras 5 falsos positivos fueron rechazados y 1.045 filas siguen sin identidad aceptada. La construcción de redes exhaustivas continúa condicionada por esa cobertura incompleta y por la ausencia de una auditoría humana independiente. Véase `reporte_final_refinado.md`, subsección 4.4.

- ✅ **Fase 0** Plan metodológico · ✅ **Fase 1** Corpus (48 docs) · ✅ **Fase 2** Bibliometría canonizada y redes auditadas · ✅ **Fase 2b** Tradición del núcleo monetario con hipótesis acotadas · ✅ **Fase 3** Front matter, JEL, colaboración y periodización con sensibilidad
- ✅ **Refinado**: cronología *De la práctica a una formalización específica* actualizada el 21/09/2026 en `linea_tiempo.html` y `data/linea_tiempo.json`, con auditoría final de 1.435 referencias, cobertura OpenAlex y las figuras 01, 02, 03 y 05 del notebook; cuaderno ejecutable y síntesis vigente en `reporte_final_refinado.md`.
- ✅ **Matriz P3–P4**: `matriz_evidencia_p3_p4.md` relaciona cinco familias autodeclaradas, ideas fundamentales, mecanismos, documentos, citas con página y función expositiva; propone como valores añadidos la doble historia de origen, la publicación de límites del modelo y el arco BCRP–teoría–BCRP
- ✅ **Respuesta integrada P3–P4**: `respuesta_integrada_p3_p4.md` articula el núcleo de liquidez y balances, la jerarquía de géneros documentales, el método revelado por las *discussions* y el recorrido BCRP–teoría–BCRP; es la fuente vigente para construir la exposición
- ⏭ **Fase 4** Texto completo: 3,38 M de caracteres segmentados por sección; tópicos y detección de conceptos
- ✅ **Fase 5** Las 15 *discussions* vigentes —D01–D15; el conteo anterior de 14 estaba desactualizado— quedaron codificadas en `data/codificacion_discussions_bigio.json` y sintetizadas en `matriz_discussions_estilo_bigio.md`: Bigio identifica la fricción, exige implementación institucional, contrasta magnitudes y pide evidencia capaz de discriminar mecanismos
- ⏭ **Fase 6** Validación V1 con codificación manual de doce documentos
- ✅ **Fase 7** `entregables/Saki_Bigio_P3_P4_evidencia_notebook.pptx` contiene cinco diapositivas principales para 6:40 minutos y tres diapositivas de respaldo. Reescribe la respuesta P3–P4 distinguiendo síntesis propia, evidencia textual e interpretación histórica; incorpora sin recorte las figuras finales 01, 02, 03 y 05 del notebook, cautelas metodológicas, fuentes visibles y guion cronometrado en las notas del presentador. La versión anterior `Saki_Bigio_P3_P4_bibliometria.pptx` se conserva como antecedente.
- ⏭ **Siguiente paso** Ensayar el bloque P3–P4, ajustar el guion a la velocidad real de Alejandro e integrar estas cinco diapositivas principales en la presentación común de quince minutos sin duplicar la biografía, los beneficiarios ni el legado asignados a AN y L.
- ⏭ **Fase 8** X/@bigioeconomics (última prioridad)
