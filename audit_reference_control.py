"""Control congelado del extractor: muestra y evidencia PDF reproducibles."""
import argparse
import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'tmp/referencias_parseadas_candidate_v4.json'
PACKET = ROOT / 'tmp/control_referencias_final.json'

def folded(text):
    text = unicodedata.normalize('NFKD', text).lower()
    return ''.join(c for c in text if c.isalnum())

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--show', type=int)
    p.add_argument('--contexts', action='store_true')
    a = p.parse_args()
    if a.show is not None:
        rows = json.loads(PACKET.read_text(encoding='utf-8'))['sample']
        for row in rows[a.show:a.show + 20]:
            print(f"\n{row['sample_id']} {row['document_id']}:{row['reference_index']} p{row['page_start']}-{row['page_end']} | {row['surname']} | {row['year']} | {row['title']}")
            print('ENTRY:', row['entry'])
            if a.contexts:
                print('PDF:', row.get('pdf_context', 'SIN EVIDENCIA'))
        return
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    population = [dict(r, document_id=k, source_pdf=d['source_pdf'], reference_index=i)
                  for k,d in sorted(data['documents'].items()) for i,r in enumerate(d['references'], 1)]
    sample = random.Random(20260917).sample(population, 100)
    sample.sort(key=lambda r: (r['document_id'], r['reference_index']))
    by_pdf = {}
    for i,row in enumerate(sample, 1):
        row['sample_id'] = f'C-{i:03}'
        row['verdict'] = 'pendiente'
        by_pdf.setdefault(row['source_pdf'], []).append(row)
    for file, rows in by_pdf.items():
        with pdfplumber.open(ROOT/file) as pdf:
            for row in rows:
                contexts = []
                probe = folded(row['entry'])[:45]
                for page_number in range(row['page_start'], row['page_end'] + 1):
                    lines = (pdf.pages[page_number-1].extract_text() or '').splitlines()
                    scores = []
                    for i in range(len(lines)):
                        text = folded(' '.join(lines[i:i+3]))
                        scores.append(sum(probe[j:j+8] in text for j in range(0,max(1,len(probe)-7),4)))
                    best = max(range(len(scores)), key=lambda i: scores[i]) if scores else 0
                    contexts.append(f'Página PDF {page_number}:\n'+'\n'.join(lines[max(0,best-1):best+8]))
                row['pdf_context'] = '\n'.join(contexts)
        print(file, flush=True)
    PACKET.write_text(json.dumps({'source_sha256': hashlib.sha256(raw).hexdigest(), 'parser_sha256': hashlib.sha256((ROOT/'parse_refs.py').read_bytes()).hexdigest(), 'seed': 20260917,
        'design': 'Muestra aleatoria simple sin reemplazo de 100 filas; revisión por Codex con extracción independiente pdfplumber. Misma colección documental utilizada en desarrollo; no validación externa.',
        'population': len(population), 'sample': sample}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(data['meta'])
    print({k: len(v['references']) for k,v in sorted(data['documents'].items())})

if __name__ == '__main__':
    main()
