import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectDir = process.cwd();
const sourcePath = path.join(projectDir, "data", "referencias_parseadas_candidate.json");
const corpusPath = path.join(projectDir, "data", "corpus.csv");
const outputPath = path.join(projectDir, "data", "auditoria_referencias.xlsx");
const previewDir = path.join(os.tmpdir(), "codex-auditoria-referencias");
const sampleSeed = 20260915;

function mulberry32(seed) {
  return function random() {
    let value = (seed += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffled(items, random) {
  const copy = [...items];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const other = Math.floor(random() * (index + 1));
    [copy[index], copy[other]] = [copy[other], copy[index]];
  }
  return copy;
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const headers = rows.shift().map((value) => value.replace(/^\uFEFF/, ""));
  return rows
    .filter((values) => values.some((value) => value !== ""))
    .map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
}

function cleanXmlValue(value) {
  if (typeof value !== "string") return value;
  return value.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\uFFFE\uFFFF]/g, "");
}

function candidateRow(candidate, prefix = []) {
  return [
    ...prefix,
    candidate.documentId,
    candidate.sourcePdf,
    candidate.candidateIndex,
    candidate.surname ?? "",
    candidate.year ?? "",
    candidate.title ?? "",
    candidate.entry ?? "",
    candidate.flags.join("; "),
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ].map(cleanXmlValue);
}

function styleTitle(sheet, rangeAddress) {
  const range = sheet.getRange(rangeAddress);
  range.format.font = { name: "Arial", size: 15, bold: true, color: "#17365D" };
  range.format.rowHeight = 25;
}

function styleHeader(range) {
  range.format = {
    fill: "#1F4E78",
    font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "inside", style: "thin", color: "#FFFFFF" },
  };
  range.format.rowHeight = 32;
}

function setAuditValidations(sheet, startRow, endRow, verdictCol, surnameCol, yearCol, titleCol) {
  sheet.getRange(`${verdictCol}${startRow}:${verdictCol}${endRow}`).dataValidation = {
    rule: { type: "list", values: ["referencia_correcta", "fragmentada", "fusionada", "no_es_referencia"] },
  };
  for (const column of [surnameCol, yearCol, titleCol]) {
    sheet.getRange(`${column}${startRow}:${column}${endRow}`).dataValidation = {
      rule: { type: "list", values: ["sí", "no", "no_aplica"] },
    };
  }
}

function styleAuditInputs(sheet, rangeAddress, verdictAddress) {
  sheet.getRange(rangeAddress).format.fill = "#FFF2CC";
  sheet.getRange(rangeAddress).format.font = { name: "Arial", size: 10, color: "#222222" };
  const verdict = sheet.getRange(verdictAddress);
  verdict.conditionalFormats.add("containsText", {
    text: "referencia_correcta",
    format: { fill: "#E2F0D9", font: { color: "#375623", bold: true } },
  });
  for (const errorValue of ["fragmentada", "fusionada", "no_es_referencia"]) {
    verdict.conditionalFormats.add("containsText", {
      text: errorValue,
      format: { fill: "#FCE4D6", font: { color: "#9C0006", bold: true } },
    });
  }
}

const source = JSON.parse(await fs.readFile(sourcePath, "utf8"));
const corpusRows = parseCsv(await fs.readFile(corpusPath, "utf8"));
const corpusById = new Map(corpusRows.map((row) => [row.id, row]));

const candidates = [];
for (const [documentId, document] of Object.entries(source.documents)) {
  document.references.forEach((reference, index) => {
    candidates.push({
      key: `${documentId}:${index + 1}`,
      documentId,
      sourcePdf: document.source_pdf,
      candidateIndex: index + 1,
      surname: reference.surname,
      year: reference.year,
      title: reference.title,
      entry: reference.entry,
      flags: reference.quality_flags ?? [],
    });
  });
}

if (candidates.length !== 1242) {
  throw new Error(`Se esperaban 1242 candidatos y se encontraron ${candidates.length}.`);
}

const random = mulberry32(sampleSeed);
const randomSample = shuffled(candidates, random).slice(0, 150);

const diagnostic = [];
const diagnosticKeys = new Set();
function addDiagnostic(items, count, reason) {
  let added = 0;
  for (const candidate of shuffled(items, random)) {
    if (diagnosticKeys.has(candidate.key)) continue;
    diagnostic.push({ ...candidate, reason });
    diagnosticKeys.add(candidate.key);
    added += 1;
    if (added === count) break;
  }
}

const mergedCandidates = candidates.filter((candidate) =>
  candidate.flags.some((flag) => flag.startsWith("possible_merged")),
);
addDiagnostic(mergedCandidates, mergedCandidates.length, "Todos los casos possible_merged");
addDiagnostic(
  candidates.filter((candidate) => candidate.flags.includes("missing_year")),
  20,
  "Muestra dirigida: missing_year",
);
addDiagnostic(
  candidates.filter((candidate) => candidate.flags.includes("title_not_isolated")),
  20,
  "Muestra dirigida: title_not_isolated",
);

const documentsWithReferences = Object.entries(source.documents).map(([documentId, document]) => ({
  documentId,
  sourcePdf: document.source_pdf,
  extractedCount: document.references.length,
  corpus: corpusById.get(documentId) ?? {},
}));
const datedDocuments = [...documentsWithReferences].sort((left, right) => {
  const leftYear = Number(left.corpus.anio || 9999);
  const rightYear = Number(right.corpus.anio || 9999);
  return leftYear - rightYear || left.documentId.localeCompare(right.documentId);
});
const coverageDocuments = [];
const coverageKeys = new Set();
for (let index = 0; index < 6; index += 1) {
  const position = Math.round((index * (datedDocuments.length - 1)) / 5);
  const document = datedDocuments[position];
  if (!coverageKeys.has(document.documentId)) {
    coverageDocuments.push(document);
    coverageKeys.add(document.documentId);
  }
}
for (const documentId of ["P04", "D15"]) {
  const corpus = corpusById.get(documentId) ?? {};
  const verifiedPdfPaths = {
    P04: "saki_research/published_papers/bigio_schneider_liquidity_shocks_business_cycles_asset_prices.pdf",
    D15: "saki_research/discussions/bigio_safety_traps_caballero_farhi.pdf",
  };
  if (!coverageKeys.has(documentId)) {
    coverageDocuments.push({
      documentId,
      sourcePdf: verifiedPdfPaths[documentId],
      extractedCount: 0,
      corpus,
    });
    coverageKeys.add(documentId);
  }
}

const workbook = Workbook.create();
const auditSheet = workbook.worksheets.add("Auditoría aleatoria");
const diagnosticSheet = workbook.worksheets.add("Casos dirigidos");
const coverageSheet = workbook.worksheets.add("Cobertura");
const instructionsSheet = workbook.worksheets.add("Instrucciones");

auditSheet.showGridLines = false;
auditSheet.getRange("A1").values = [["Auditoría manual de referencias"]];
styleTitle(auditSheet, "A1:Q1");
auditSheet.getRange("A2").values = [["Muestra aleatoria simple de 150 candidatos. Use esta hoja para estimar la precisión general."]];
auditSheet.getRange("A2:Q2").format.font = { name: "Arial", size: 10, italic: true, color: "#595959" };
auditSheet.getRange("A4:N4").values = [[
  "Revisadas", "", "Referencias correctas", "", "Precisión", "", "Apellidos correctos", "", "Años correctos", "", "Títulos correctos", "", "Pendientes", "",
]];
auditSheet.getRange("B4").formulas = [["=COUNTIFS(J9:J158,\"referencia_correcta\")+COUNTIFS(J9:J158,\"fragmentada\")+COUNTIFS(J9:J158,\"fusionada\")+COUNTIFS(J9:J158,\"no_es_referencia\")"]];
auditSheet.getRange("D4").formulas = [["=COUNTIFS(J9:J158,\"referencia_correcta\")"]];
auditSheet.getRange("F4").formulas = [["=IF(B4=0,\"\",D4/B4)"]];
auditSheet.getRange("H4").formulas = [["=IF(COUNTIFS(K9:K158,\"sí\")+COUNTIFS(K9:K158,\"no\")=0,\"\",COUNTIFS(K9:K158,\"sí\")/(COUNTIFS(K9:K158,\"sí\")+COUNTIFS(K9:K158,\"no\")))"]];
auditSheet.getRange("J4").formulas = [["=IF(COUNTIFS(L9:L158,\"sí\")+COUNTIFS(L9:L158,\"no\")=0,\"\",COUNTIFS(L9:L158,\"sí\")/(COUNTIFS(L9:L158,\"sí\")+COUNTIFS(L9:L158,\"no\")))"]];
auditSheet.getRange("L4").formulas = [["=IF(COUNTIFS(M9:M158,\"sí\")+COUNTIFS(M9:M158,\"no\")=0,\"\",COUNTIFS(M9:M158,\"sí\")/(COUNTIFS(M9:M158,\"sí\")+COUNTIFS(M9:M158,\"no\")))"]];
auditSheet.getRange("N4").formulas = [["=150-B4"]];
for (const cell of ["A4", "C4", "E4", "G4", "I4", "K4", "M4"]) {
  auditSheet.getRange(cell).format = { fill: "#D9EAF7", font: { name: "Arial", size: 10, bold: true, color: "#17365D" } };
}
for (const cell of ["B4", "D4", "F4", "H4", "J4", "L4", "N4"]) {
  auditSheet.getRange(cell).format = { font: { name: "Arial", size: 11, bold: true, color: "#222222" } };
}
auditSheet.getRange("F4:L4").format.numberFormat = "0.0%";
auditSheet.getRange("A6").values = [["Complete las columnas amarillas. No mezcle esta tasa con la hoja Casos dirigidos."]];
auditSheet.getRange("A6:Q6").format.font = { name: "Arial", size: 10, italic: true, color: "#7F6000" };

const auditHeaders = [
  "sample_id", "document_id", "source_pdf", "candidate_index", "surname_extracted", "year_extracted", "title_extracted", "entry_extracted", "quality_flags", "veredicto", "surname_correcto", "year_correcto", "title_correcto", "correccion", "observacion", "revisor", "fecha_revision",
];
auditSheet.getRange("A8:Q8").values = [auditHeaders];
styleHeader(auditSheet.getRange("A8:Q8"));
const auditRows = randomSample.map((candidate, index) => candidateRow(candidate, [`R${String(index + 1).padStart(3, "0")}`]));
auditSheet.getRange("A9:Q158").values = auditRows;
auditSheet.getRange("A9:Q158").format.font = { name: "Arial", size: 10, color: "#222222" };
auditSheet.getRange("A9:Q158").format.verticalAlignment = "top";
auditSheet.getRange("G9:I158").format.wrapText = true;
auditSheet.getRange("N9:O158").format.wrapText = true;
auditSheet.getRange("F9:F158").format.numberFormat = "0";
auditSheet.getRange("Q9:Q158").format.numberFormat = "yyyy-mm-dd";
styleAuditInputs(auditSheet, "J9:Q158", "J9:J158");
setAuditValidations(auditSheet, 9, 158, "J", "K", "L", "M");
const auditTable = auditSheet.tables.add("A8:Q158", true, "AuditRandomTable");
auditTable.style = "TableStyleMedium2";
auditSheet.freezePanes.freezeRows(8);
auditSheet.freezePanes.freezeColumns(3);

diagnosticSheet.showGridLines = false;
diagnosticSheet.getRange("A1").values = [["Casos dirigidos"]];
styleTitle(diagnosticSheet, "A1:R1");
diagnosticSheet.getRange("A2").values = [["Casos difíciles para diagnosticar el extractor. No se incluyen en la estimación general de precisión."]];
diagnosticSheet.getRange("A2:R2").format.font = { name: "Arial", size: 10, italic: true, color: "#595959" };
const diagnosticHeaders = ["motivo_muestra", ...auditHeaders.slice(1)];
diagnosticSheet.getRange("A5:Q5").values = [diagnosticHeaders];
styleHeader(diagnosticSheet.getRange("A5:Q5"));
const diagnosticRows = diagnostic.map((candidate) => candidateRow(candidate, [candidate.reason]));
const diagnosticEnd = 5 + diagnosticRows.length;
diagnosticSheet.getRange(`A6:Q${diagnosticEnd}`).values = diagnosticRows;
diagnosticSheet.getRange(`A6:Q${diagnosticEnd}`).format.font = { name: "Arial", size: 10, color: "#222222" };
diagnosticSheet.getRange(`A6:Q${diagnosticEnd}`).format.verticalAlignment = "top";
diagnosticSheet.getRange(`G6:I${diagnosticEnd}`).format.wrapText = true;
diagnosticSheet.getRange(`N6:O${diagnosticEnd}`).format.wrapText = true;
diagnosticSheet.getRange(`F6:F${diagnosticEnd}`).format.numberFormat = "0";
diagnosticSheet.getRange(`Q6:Q${diagnosticEnd}`).format.numberFormat = "yyyy-mm-dd";
styleAuditInputs(diagnosticSheet, `J6:Q${diagnosticEnd}`, `J6:J${diagnosticEnd}`);
setAuditValidations(diagnosticSheet, 6, diagnosticEnd, "J", "K", "L", "M");
const diagnosticTable = diagnosticSheet.tables.add(`A5:Q${diagnosticEnd}`, true, "AuditDiagnosticTable");
diagnosticTable.style = "TableStyleMedium4";
diagnosticSheet.freezePanes.freezeRows(5);
diagnosticSheet.freezePanes.freezeColumns(3);

coverageSheet.showGridLines = false;
coverageSheet.getRange("A1").values = [["Auditoría de cobertura"]];
styleTitle(coverageSheet, "A1:L1");
coverageSheet.getRange("A2").values = [["Cuente las referencias reales del PDF y registre cuántas tienen correspondencia uno a uno con la extracción."]];
coverageSheet.getRange("A2:L2").format.font = { name: "Arial", size: 10, italic: true, color: "#595959" };
coverageSheet.getRange("A3").values = [["La selección contiene seis documentos con referencias detectadas y dos sin sección detectada para comprobar posibles omisiones completas."]];
coverageSheet.getRange("A3:L3").format.font = { name: "Arial", size: 10, italic: true, color: "#7F6000" };
const coverageHeaders = [
  "document_id", "titulo", "anio", "genero", "source_pdf", "candidatos_extraidos", "referencias_reales", "coincidencias_uno_a_uno", "omitidas", "fragmentadas_o_fusionadas", "cobertura", "observacion",
];
coverageSheet.getRange("A5:L5").values = [coverageHeaders];
styleHeader(coverageSheet.getRange("A5:L5"));
const coverageRows = coverageDocuments.map((document) => [
  document.documentId,
  document.corpus.titulo ?? "",
  document.corpus.anio ? Number(document.corpus.anio) : "",
  document.corpus.genero ?? "",
  document.sourcePdf,
  document.extractedCount,
  "",
  "",
  "",
  "",
  "",
  "",
].map(cleanXmlValue));
const coverageEnd = 5 + coverageRows.length;
coverageSheet.getRange(`A6:L${coverageEnd}`).values = coverageRows;
coverageSheet.getRange(`I6:I${coverageEnd}`).formulas = coverageRows.map((_, index) => {
  const row = index + 6;
  return [`=IF(OR(G${row}=\"\",H${row}=\"\"),\"\",G${row}-H${row})`];
});
coverageSheet.getRange(`K6:K${coverageEnd}`).formulas = coverageRows.map((_, index) => {
  const row = index + 6;
  return [`=IF(OR(G${row}=\"\",H${row}=\"\",G${row}=0),\"\",H${row}/G${row})`];
});
coverageSheet.getRange(`A6:L${coverageEnd}`).format.font = { name: "Arial", size: 10, color: "#222222" };
coverageSheet.getRange(`B6:B${coverageEnd}`).format.wrapText = true;
coverageSheet.getRange(`E6:E${coverageEnd}`).format.wrapText = true;
coverageSheet.getRange(`G6:H${coverageEnd}`).format.fill = "#FFF2CC";
coverageSheet.getRange(`J6:J${coverageEnd}`).format.fill = "#FFF2CC";
coverageSheet.getRange(`L6:L${coverageEnd}`).format.fill = "#FFF2CC";
coverageSheet.getRange(`K6:K${coverageEnd}`).format.numberFormat = "0.0%";
for (const column of ["G", "H", "J"]) {
  coverageSheet.getRange(`${column}6:${column}${coverageEnd}`).dataValidation = {
    rule: { type: "whole", operator: "between", formula1: 0, formula2: 10000 },
  };
}
const coverageTable = coverageSheet.tables.add(`A5:L${coverageEnd}`, true, "CoverageAuditTable");
coverageTable.style = "TableStyleMedium2";
coverageSheet.freezePanes.freezeRows(5);

instructionsSheet.showGridLines = false;
instructionsSheet.getRange("A1").values = [["Cómo completar la auditoría"]];
styleTitle(instructionsSheet, "A1:H1");
const instructions = [
  ["Fuente", "data/referencias_parseadas_candidate.json"],
  ["Semilla de la muestra", String(sampleSeed)],
  ["Muestra principal", "150 candidatos seleccionados aleatoriamente entre los 1,242"],
  ["1", "Abra el PDF indicado en source_pdf y busque el autor, el año o una frase del título."],
  ["2", "Marque referencia_correcta cuando la fila represente una sola referencia bibliográfica completa."],
  ["3", "Use fragmentada si una referencia quedó partida; fusionada si hay dos o más referencias en una fila; no_es_referencia si la fila no corresponde a una referencia."],
  ["4", "Revise surname, year y title por separado. Use no_aplica solo cuando el campo no pueda evaluarse."],
  ["5", "Escriba la referencia corregida cuando encuentre un error y explique brevemente el problema."],
  ["6", "La precisión de la muestra principal se calcula automáticamente en Auditoría aleatoria."],
  ["7", "No incorpore los Casos dirigidos al porcentaje general. Esa hoja sirve para diagnosticar fallas."],
  ["8", "En Cobertura, cuente las referencias reales de cada PDF y las coincidencias uno a uno."],
  ["Criterio recomendado", "95% o más: apto para agregados; 90% a 94%: usar con correcciones y advertencia; menos de 90%: corregir y repetir."],
];
instructionsSheet.getRange(`A3:B${instructions.length + 2}`).values = instructions;
instructionsSheet.getRange(`A3:A${instructions.length + 2}`).format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#17365D" },
  verticalAlignment: "top",
};
instructionsSheet.getRange(`B3:B${instructions.length + 2}`).format = {
  font: { name: "Arial", size: 10, color: "#222222" },
  verticalAlignment: "top",
  wrapText: true,
};
instructionsSheet.getRange(`A3:B${instructions.length + 2}`).format.borders = {
  preset: "all",
  style: "thin",
  color: "#D9E2F3",
};

for (const sheet of [auditSheet, diagnosticSheet]) {
  const widths = {
    A: 24, B: 12, C: 44, D: 13, E: 18, F: 11, G: 38, H: 86, I: 27,
    J: 23, K: 18, L: 16, M: 17, N: 70, O: 48, P: 18, Q: 15,
  };
  for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
}
const coverageWidths = { A: 12, B: 48, C: 10, D: 16, E: 48, F: 19, G: 18, H: 23, I: 12, J: 27, K: 13, L: 50 };
for (const [column, width] of Object.entries(coverageWidths)) coverageSheet.getRange(`${column}:${column}`).format.columnWidth = width;
instructionsSheet.getRange("A:A").format.columnWidth = 24;
instructionsSheet.getRange("B:B").format.columnWidth = 105;

workbook.recalculate();

auditSheet.getRange("J9:M9").values = [["referencia_correcta", "sí", "sí", "sí"]];
workbook.recalculate();
const dynamicTestValues = auditSheet.getRange("A4:N4").values[0];
if (dynamicTestValues[1] !== 1 || dynamicTestValues[3] !== 1 || dynamicTestValues[5] !== 1 || dynamicTestValues[13] !== 149) {
  throw new Error(`La prueba dinámica de los indicadores falló: ${JSON.stringify(dynamicTestValues)}`);
}
auditSheet.getRange("J9:M9").values = [["", "", "", ""]];
workbook.recalculate();

const auditInspect = await workbook.inspect({
  kind: "table",
  range: "Auditoría aleatoria!A1:Q14",
  include: "values,formulas",
  tableMaxRows: 14,
  tableMaxCols: 17,
  maxChars: 10000,
});
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
  maxChars: 4000,
});

await fs.mkdir(previewDir, { recursive: true });
const previews = [
  ["Auditoría aleatoria", "A1:Q20", "01_auditoria.png"],
  ["Casos dirigidos", "A1:Q18", "02_casos_dirigidos.png"],
  ["Cobertura", `A1:L${coverageEnd}`, "03_cobertura.png"],
  ["Instrucciones", `A1:B${instructions.length + 2}`, "04_instrucciones.png"],
];
for (const [sheetName, range, fileName] of previews) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await preview.arrayBuffer()));
}

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const saved = await FileBlob.load(outputPath);
const reloaded = await SpreadsheetFile.importXlsx(saved);
const savedInspect = await reloaded.inspect({ kind: "sheet,table", include: "id,name", maxChars: 5000 });

console.log(JSON.stringify({
  outputPath,
  previewDir,
  sourceCandidates: candidates.length,
  randomSample: randomSample.length,
  diagnosticSample: diagnostic.length,
  mergedInDiagnostic: diagnostic.filter((item) => item.reason.includes("possible_merged")).length,
  coverageDocuments: coverageDocuments.map((item) => item.documentId),
  dynamicTest: "OK: una fila completa actualiza revisadas, correctas, precisión y pendientes; luego se restaura",
  auditInspect: auditInspect.ndjson,
  formulaErrors: formulaErrors.ndjson,
  savedInspect: savedInspect.ndjson,
}, null, 2));
