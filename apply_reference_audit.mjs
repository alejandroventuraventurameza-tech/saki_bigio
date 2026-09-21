import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const projectDir = process.cwd();
const workbookPath = path.join(projectDir, "data", "auditoria_referencias.xlsx");
const adjudicationPath = path.join(projectDir, "tmp", "pdfs", "reference_audit", "adjudications.json");
const previewDir = path.join(projectDir, "tmp", "xlsx", "auditoria_referencias");

const coverageResults = {
  E01: {
    real: 59,
    matched: 32,
    broken: 30,
    note: "Conteo manual de la bibliografía (pp. PDF 20–22). Hay cortes en saltos de línea, fusiones y una referencia omitida por completo.",
  },
  C03: {
    real: 4,
    matched: 0,
    broken: 3,
    note: "Las cuatro referencias reales quedaron repartidas entre tres filas; ninguna fila es una referencia completa uno-a-uno.",
  },
  P08: {
    real: 66,
    matched: 24,
    broken: 28,
    note: "Conteo manual de la sección References. Se observaron numerosas fusiones y fragmentos, además de referencias sin fila completa.",
  },
  W06: {
    real: 21,
    matched: 8,
    broken: 12,
    note: "Conteo manual de las pp. PDF 25–26. Una referencia (Jones et al.) fue omitida y varias quedaron partidas o fusionadas.",
  },
  P10: {
    real: 85,
    matched: 25,
    broken: 42,
    note: "Conteo manual de las pp. PDF 43–48. El extractor perdió grupos completos y fusionó varias entradas con autores repetidos.",
  },
  W11: {
    real: 37,
    matched: 20,
    broken: 15,
    note: "Conteo manual de las pp. PDF 54–56. Tres referencias finales no fueron extraídas y otras quedaron fragmentadas o fusionadas.",
  },
  P04: {
    real: 19,
    matched: 0,
    broken: 0,
    note: "La bibliografía ocupa las pp. PDF 37–38 y contiene 19 referencias, pero el extractor candidato devolvió cero.",
  },
  D15: {
    real: 0,
    matched: 0,
    broken: 0,
    note: "Revisión completa del PDF: no contiene una sección bibliográfica ni una lista de referencias; la extracción cero es correcta.",
  },
};

function rowKey(row) {
  return `${String(row[0]).trim()}:${Number(row[2])}`;
}

function auditMatrix(rows, adjudications) {
  return rows.map((row) => {
    const key = rowKey(row);
    const result = adjudications[key];
    if (!result) throw new Error(`Falta dictamen para ${key}`);
    return [
      result.veredicto,
      result.surname_correcto,
      result.year_correcto,
      result.title_correcto,
      result.correccion,
      result.observacion,
      result.revisor,
      new Date(2026, 8, 15, 12, 0, 0),
    ];
  });
}

const payload = JSON.parse(await fs.readFile(adjudicationPath, "utf8"));
const adjudications = payload.adjudications;
const inputBlob = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(inputBlob);

const auditSheet = workbook.worksheets.getItem("Auditoría aleatoria");
const diagnosticSheet = workbook.worksheets.getItem("Casos dirigidos");
const coverageSheet = workbook.worksheets.getItem("Cobertura");
const instructionsSheet = workbook.worksheets.getItem("Instrucciones");
if (!auditSheet || !diagnosticSheet || !coverageSheet || !instructionsSheet) {
  throw new Error("El libro no contiene las cuatro hojas esperadas.");
}

const auditKeys = auditSheet.getRange("B9:D158").values;
const diagnosticKeys = diagnosticSheet.getRange("B6:D48").values;
auditSheet.getRange("J9:Q158").values = auditMatrix(auditKeys, adjudications);
diagnosticSheet.getRange("J6:Q48").values = auditMatrix(diagnosticKeys, adjudications);

auditSheet.getRange("O9:O158").format.wrapText = true;
diagnosticSheet.getRange("O6:O48").format.wrapText = true;
auditSheet.getRange("Q9:Q158").format.numberFormat = "yyyy-mm-dd";
diagnosticSheet.getRange("Q6:Q48").format.numberFormat = "yyyy-mm-dd";

const coverageIds = coverageSheet.getRange("A6:A13").values.map((row) => String(row[0]).trim());
coverageSheet.getRange("G6:H13").values = coverageIds.map((id) => {
  const result = coverageResults[id];
  if (!result) throw new Error(`Falta auditoría de cobertura para ${id}`);
  return [result.real, result.matched];
});
coverageSheet.getRange("J6:J13").values = coverageIds.map((id) => [coverageResults[id].broken]);
coverageSheet.getRange("L6:L13").values = coverageIds.map((id) => [coverageResults[id].note]);
coverageSheet.getRange("I6:I13").formulas = coverageIds.map((_, index) => {
  const row = index + 6;
  return [`=IF(COUNT(G${row}:H${row})<2,"",G${row}-H${row})`];
});
coverageSheet.getRange("K6:K13").formulas = coverageIds.map((_, index) => {
  const row = index + 6;
  return [`=IF(OR(COUNT(G${row}:H${row})<2,G${row}=0),"",H${row}/G${row})`];
});
coverageSheet.getRange("L6:L13").format.wrapText = true;
coverageSheet.getRange("L6:L13").format.rowHeight = 46;

instructionsSheet.getRange("A16:B18").values = [
  ["Auditoría ejecutada", "2026-09-15 — Codex"],
  ["Método", "Contraste manual independiente de cada fila muestreada contra la sección de referencias de su PDF; conteo total en ocho documentos de cobertura."],
  ["Alcance", "150 casos aleatorios para la tasa general y 43 casos dirigidos solo para diagnóstico."],
];
instructionsSheet.getRange("A16:A18").format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#17365D" },
  verticalAlignment: "top",
};
instructionsSheet.getRange("B16:B18").format = {
  font: { name: "Arial", size: 10, color: "#222222" },
  verticalAlignment: "top",
  wrapText: true,
};
instructionsSheet.getRange("A16:B18").format.borders = {
  preset: "all",
  style: "thin",
  color: "#D9E2F3",
};

workbook.recalculate();

const summaryInspect = await workbook.inspect({
  kind: "table",
  range: "Auditoría aleatoria!A4:N4",
  include: "values,formulas",
  tableMaxRows: 4,
  tableMaxCols: 14,
  maxChars: 5000,
});
const coverageInspect = await workbook.inspect({
  kind: "table",
  range: "Cobertura!A5:L13",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 12,
  maxChars: 12000,
});
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "auditoría final: errores de fórmula",
  maxChars: 5000,
});

await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, fileName] of [
  ["Auditoría aleatoria", "A1:Q18", "01_auditoria.png"],
  ["Casos dirigidos", "A1:Q18", "02_casos_dirigidos.png"],
  ["Cobertura", "A1:L13", "03_cobertura.png"],
  ["Instrucciones", "A1:B18", "04_instrucciones.png"],
]) {
  const image = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await image.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(workbookPath);

const savedBlob = await FileBlob.load(workbookPath);
const reloaded = await SpreadsheetFile.importXlsx(savedBlob);
const savedSummary = await reloaded.inspect({
  kind: "table",
  range: "Auditoría aleatoria!A4:N4",
  include: "values,formulas",
  tableMaxRows: 4,
  tableMaxCols: 14,
  maxChars: 5000,
});
const savedCoverage = await reloaded.inspect({
  kind: "table",
  range: "Cobertura!A5:L13",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 12,
  maxChars: 12000,
});

console.log(JSON.stringify({
  workbookPath,
  previewDir,
  auditRows: auditKeys.length,
  diagnosticRows: diagnosticKeys.length,
  summaryInspect: summaryInspect.ndjson,
  coverageInspect: coverageInspect.ndjson,
  formulaErrors: formulaErrors.ndjson,
  savedSummary: savedSummary.ndjson,
  savedCoverage: savedCoverage.ndjson,
}, null, 2));
