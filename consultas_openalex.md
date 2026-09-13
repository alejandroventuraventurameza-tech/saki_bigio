# Consultas a OpenAlex — instrucciones de ejecución

**Por qué esto va por fuera.** Desde mi entorno OpenAlex responde `Rate limit exceeded / insufficient budget` (la IP del proxy está compartida y sin cuota). Semantic Scholar y Crossref sí responden, así que **el grueso de la bibliometría lo construyo yo aquí** con esas dos. OpenAlex aporta tres cosas que las otras dos no tienen, y solo esas tres se piden aquí:

1. **FWCI** (*Field-Weighted Citation Impact*) y `citation_normalized_percentile` — impacto normalizado por campo y por edad. Es lo que evita el error de reportar rankings de citas que en realidad solo miden antigüedad.
2. La **taxonomía de *topics*** de OpenAlex (jerarquía topic → subfield → field → domain), que sirve como tercera taxonomía externa de validación, independiente de los JEL y de la taxonomía que el propio Bigio declara.
3. Los ***facets* agregados** (`group_by`), que responden en un solo llamado preguntas que de otro modo exigirían cientos: quién lo cita, desde qué país, desde qué tipo de institución, en qué año.

---

## Cómo pedírselo a ChatGPT

Copia y pega este bloque como **primer mensaje** del proyecto de ChatGPT, junto con el archivo `CONTEXT.md`:

> Necesito que actúes como recolector de datos, no como analista. Vas a consultar la API pública de OpenAlex (no requiere clave) y devolverme las respuestas **en JSON literal, completo y sin modificar**.
>
> Reglas estrictas:
> - **No resumas, no interpretes, no reformatees y no recortes.** Si la respuesta es larga, entrégamela como archivo `.json` descargable. El resumen destruye el dato.
> - No inventes ningún campo. Si una consulta falla, dime el código de error y la URL exacta que usaste.
> - Ejecuta las consultas **en orden**; la consulta 1 produce el identificador que necesitan todas las demás.
> - Añade `&mailto=alejandroventuraventurameza@gmail.com` a cada URL (es el *polite pool* de OpenAlex, da mejor servicio).
> - Nombra cada archivo de salida exactamente como indico.
>
> Contexto: es para un trabajo universitario de historia del pensamiento económico sobre el economista peruano Saki Bigio (UCLA). Las consultas vienen a continuación.

Después pega las consultas de abajo, una por una o todas juntas.

---

## Consulta 1 — Desambiguar al autor

```
https://api.openalex.org/authors?search=Saki Bigio
```

**Qué verificar antes de seguir:** puede devolver varios perfiles con el mismo nombre (Semantic Scholar devuelve tres). Quédate con el que tenga `last_known_institution` / `affiliations` = **University of California, Los Angeles** y del orden de 25–70 trabajos. Anota su `id` (tiene la forma `https://openalex.org/A#########`).

> En todas las consultas siguientes, **`<AID>`** = ese identificador, solo la parte `A#########`.

**Archivo:** `openalex_01_author.json`

---

## Consulta 2 — Todos sus trabajos, con impacto normalizado

```
https://api.openalex.org/works?filter=authorships.author.id:<AID>&per-page=200&sort=publication_year:desc&select=id,doi,display_name,publication_year,publication_date,type,cited_by_count,fwci,citation_normalized_percentile,counts_by_year,primary_location,primary_topic,topics,keywords,referenced_works_count,authorships
```

Este es **el llamado más importante de todos**. Trae de golpe: título, año, tipo, revista, citas, FWCI, percentil normalizado, citas por año, tópicos, keywords y la lista completa de coautores.

**Archivo:** `openalex_02_works.json`

---

## Consulta 3 — Perfil temático agregado

Cuatro llamados cortos; cada uno devuelve una tabla pequeña de conteos.

```
https://api.openalex.org/works?filter=authorships.author.id:<AID>&group_by=publication_year
https://api.openalex.org/works?filter=authorships.author.id:<AID>&group_by=primary_topic.id
https://api.openalex.org/works?filter=authorships.author.id:<AID>&group_by=primary_topic.field.id
https://api.openalex.org/works?filter=authorships.author.id:<AID>&group_by=type
```

**Archivo:** `openalex_03_facets_autor.json` (los cuatro resultados juntos, cada uno bajo una clave que diga qué agrupación es).

---

## Consulta 4 — Quién lo cita (el mapa de su influencia)

Primero, de `openalex_02_works.json`, toma los **seis trabajos con mayor `cited_by_count`** y anota sus `id`. Luego, sustituyendo `<W1>…<W6>` por esos identificadores (solo la parte `W#########`, separados por `|`, que en OpenAlex significa "o"):

```
https://api.openalex.org/works?filter=cites:<W1>|<W2>|<W3>|<W4>|<W5>|<W6>&group_by=publication_year
https://api.openalex.org/works?filter=cites:<W1>|<W2>|<W3>|<W4>|<W5>|<W6>&group_by=primary_topic.field.id
https://api.openalex.org/works?filter=cites:<W1>|<W2>|<W3>|<W4>|<W5>|<W6>&group_by=institutions.country_code
https://api.openalex.org/works?filter=cites:<W1>|<W2>|<W3>|<W4>|<W5>|<W6>&group_by=institutions.type
https://api.openalex.org/works?filter=cites:<W1>|<W2>|<W3>|<W4>|<W5>|<W6>&group_by=authorships.institutions.lineage
```

**Para qué sirve cada una.** La primera da la curva temporal de su influencia. La segunda dice en qué campos aterrizó (¿solo macro, o también finanzas, redes, comercio?). La tercera y la cuarta son la prueba directa de una hipótesis interesante: **si `institutions.type` muestra una proporción inusual de `government` y `facility`, quiere decir que quienes más lo leen son bancos centrales, no universidades** — y eso convierte "¿a qué grupos beneficia su pensamiento?" en un dato en lugar de una opinión. La quinta nombra las instituciones concretas.

**Archivo:** `openalex_04_facets_citantes.json`

---

## Consulta 5 — Sus dos trabajos más citados, en detalle

Para los dos `id` con mayor `cited_by_count`, uno por uno:

```
https://api.openalex.org/works/<W1>
https://api.openalex.org/works/<W2>
```

Trae el registro completo, incluida la lista `referenced_works` (todo lo que ese paper cita). Es el insumo del análisis de tradición intelectual.

**Archivo:** `openalex_05_top_works_detalle.json`

---

## Consulta 6 *(opcional, solo si las anteriores salieron limpias)* — La tradición, resuelta

De `openalex_05`, toma los `referenced_works` de ambos papers (serán ~50–120 identificadores `W#########`). Pídele a ChatGPT que los resuelva en lotes de 50:

```
https://api.openalex.org/works?filter=openalex_id:<W_a>|<W_b>|...|<W_50>&per-page=50&select=id,display_name,publication_year,authorships,cited_by_count,primary_topic
```

Esto convierte una lista de códigos en la bibliografía real que Bigio está construyendo por debajo — es la evidencia directa para la hipótesis **H4** (la tradición Tobin–Gurley & Shaw, Currency School vs. Banking School).

**Archivo:** `openalex_06_referencias_resueltas.json`

---

## Qué hacer con los archivos

Guárdalos todos en `saki_bigio/data/openalex/` y avísame. Yo los cruzo con `data/corpus.csv` y con lo que traiga de Semantic Scholar y Crossref.

**Advertencia de lectura.** OpenAlex indexa mal los *working papers* de economía, que es justo donde vive buena parte de la obra de Bigio (6 R&R + 6 WP según su CV). Es decir: **el conteo de OpenAlex va a subestimar su producción reciente**. Eso no es un error a corregir, es un límite a declarar en el entregable — y de paso es un dato sobre cómo funciona la disciplina, porque en economía el *working paper* circula y se cita durante años antes de existir formalmente para los índices.

---

## Nota sobre el proyecto de ChatGPT

Si vas a crear el proyecto local en ChatGPT, súbele estos tres archivos y ninguno más:

1. `CONTEXT.md` — lo orienta por completo.
2. `consultas_openalex.md` — este archivo.
3. `data/corpus.csv` — para que pueda cotejar lo que OpenAlex devuelve contra lo que ya tenemos.

No le subas los PDFs: 46 documentos y 1,962 páginas le van a saturar el contexto y va a empezar a resumir en lugar de traer datos, que es exactamente lo que no queremos de él en esta división del trabajo.
