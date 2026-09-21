"""Registra dictámenes explícitos del control, sin corregir la muestra evaluada."""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'tmp/referencias_parseadas_candidate_v4.json'
PACKET = ROOT/'tmp/control_referencias_final.json'

# Dictámenes establecidos tras revisar las 100 entradas y su contexto PDF.
# No se aplica una segunda corrección al extractor después de congelar esta muestra.
SEGMENT_ERRORS = {
    65: ('contaminada', 'La fila incorpora el encabezado de la página 23 de Research vision; la referencia termina en 2010,3,547.'),
    86: ('fusionada', 'La fila reúne tres referencias de Woodford: 1998, 1999 y 2010. Separarlas según la página PDF 47.'),
}
SURNAME_ERRORS = {
    27: ('di Giovanni', 'La raya remite a Julian di Giovanni y coautores; se heredó Costello incorrectamente.'),
    95: ('Jordà', 'La notación repetida remite a Òscar Jordà; se heredó Hardy incorrectamente.'),
}
YEAR_ERRORS = {18: (2000, '1990 pertenece al título; el año bibliográfico impreso es Winter 2000.')}
TITLE_ERRORS = {
    8: ('Price Rigidities, Asymmetries, and Output Fluctuations', 'El título extraído incluye la institución y el número de working paper.'),
    10: ('Financial Frictions and Real Devaluations', 'El título extraído incluye la institución y el número de working paper.'),
    16: ('Theories of “bad policy”', 'Solo se aisló la frase entrecomillada dentro del título.'),
    39: ('Money, Payments, and Liquidity', 'El título extraído incluye editorial y edición.'),
}
EXPECTED = {'E01':59, 'C01':11, 'C03':4, 'P04':19, 'P08':66, 'P10':85, 'W06':21, 'W11':37, 'D15':0}

def wilson(k,n):
    z=1.959963984540054; p=k/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half, center+half]

def main():
    packet=json.loads(PACKET.read_text(encoding='utf-8'))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==packet['source_sha256']
    assert hashlib.sha256((ROOT/'parse_refs.py').read_bytes()).hexdigest()==packet['parser_sha256']
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    for row in packet['sample']:
        n=int(row['sample_id'].split('-')[1]); notes=[]; corrections={}
        row['verdict']=SEGMENT_ERRORS.get(n, ('correcta', ''))[0]
        row['surname_correct']=n not in SURNAME_ERRORS
        row['year_correct']=n not in YEAR_ERRORS and row['year'] is not None
        row['title_correct']=row['title'] is not None and n not in TITLE_ERRORS
        if n in SEGMENT_ERRORS:
            notes.append(SEGMENT_ERRORS[n][1])
            if row['verdict']=='fusionada':
                row['surname_correct']=row['year_correct']=row['title_correct']=False
        for errors, key in [(SURNAME_ERRORS,'surname'),(YEAR_ERRORS,'year'),(TITLE_ERRORS,'title')]:
            if n in errors:
                corrections[key]=errors[n][0];notes.append(errors[n][1])
        if row['title'] is None:
            notes.append('La referencia está conservada en entry, pero el campo title está vacío.')
        row['record_ready']=row['verdict']=='correcta' and all(row[k] for k in ['surname_correct','year_correct','title_correct'])
        row['basic_fields_ready']=row['verdict']=='correcta' and row['surname_correct'] and row['year_correct']
        row['corrections']=corrections
        row['review_note']=' '.join(notes) or 'Una referencia completa; apellido inicial, año y título concuerdan con el PDF, admitiendo diferencias de espacios y tipografía.'
        row['reviewer']='Codex (control asistido, no auditor externo humano)'
        row['review_date']='2026-09-15'
    rows=packet['sample'];n=len(rows)
    packet['metrics']={
        'sample_size':n,'segmentation_correct':sum(r['verdict']=='correcta' for r in rows),
        'basic_fields_ready':sum(r['basic_fields_ready'] for r in rows),
        'record_ready':sum(r['record_ready'] for r in rows),
        'verdict_counts':dict(Counter(r['verdict'] for r in rows)),
        'missing_titles':sum(r['title'] is None for r in rows),
        'incorrect_titles':len(TITLE_ERRORS),'incorrect_surnames':len(SURNAME_ERRORS),'incorrect_years':len(YEAR_ERRORS),
        'release_threshold':0.95,
    }
    for key in ['segmentation_correct','basic_fields_ready','record_ready']:
        packet['metrics'][key+'_rate']=packet['metrics'][key]/n
        packet['metrics'][key+'_wilson95']=wilson(packet['metrics'][key],n)
    packet['network_release']=False
    packet['network_release_reason']='77/100 filas contienen simultáneamente una referencia limpia, apellido inicial, año y título utilizable. Además falta resolver identidades y versiones de obras citadas; la coincidencia de conteos no mide exhaustividad.'
    packet['definitions']={
        'segmentation_correct':'Una fila corresponde a una referencia completa, sin fragmentos, fusiones ni encabezados ajenos. Se admiten notas de retorno impresas y notación de autor repetido.',
        'basic_fields_ready':'Segmentación correcta más apellido del primer autor y año bibliográfico correctos según el PDF.',
        'record_ready':'Criterio básico más título completo aislado. Se toleran espacios y tipografía, no la inclusión de editorial/revista ni títulos parciales.',
        'scope':'La extracción independiente facilita el contraste; la revisión fue realizada por el mismo asistente que desarrolló el extractor, sobre el mismo corpus. No constituye validación humana externa ni una prueba de identidad de obras.'
    }
    packet['count_checks']=[{'document_id':k,'expected':v,'extracted':len(data['documents'].get(k,{}).get('references',[])),
                           'source_pdf':data['documents'].get(k,{}).get('source_pdf','saki_research/discussions/bigio_safety_traps_caballero_farhi.pdf'),
                           'interpretation':'Concordancia de conteo, no estimación de recall.'} for k,v in EXPECTED.items()]
    assert packet['metrics']['record_ready']==77,packet['metrics']
    assert all(c['expected']==c['extracted'] for c in packet['count_checks'])
    out=ROOT/'data/auditoria_referencias_control.json'
    out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    candidate=ROOT/'data/referencias_parseadas_candidate.json'
    archive=ROOT/'data/archive/referencias_parseadas_candidate_v1.json'
    archive.parent.mkdir(exist_ok=True)
    if not archive.exists(): archive.write_bytes(candidate.read_bytes())
    data['meta']['status']='candidate_control_reviewed_not_validated'
    data['meta']['control_audit']='data/auditoria_referencias_control.json'
    data['meta']['control_metrics']=packet['metrics']
    data['meta']['warning']='Control asistido: 98/100 filas correctamente segmentadas; 77/100 con apellido, año y título utilizables. No habilitada para redes de referencias ni porcentajes históricos.'
    candidate.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(packet['metrics'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
