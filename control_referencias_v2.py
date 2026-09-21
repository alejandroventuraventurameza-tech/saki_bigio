"""Muestra reproducible de control; los dictámenes se añaden tras cotejar el PDF."""
import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'tmp/referencias_parseadas_candidate_v2.json'
PACKET = ROOT / 'tmp/control_referencias_v2.json'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', type=int)
    args = parser.parse_args()
    if args.show is not None:
        packet = json.loads(PACKET.read_text(encoding='utf-8'))
        for row in packet['sample'][args.show:args.show + 25]:
            print(f"{row['sample_id']} {row['document_id']}:{row['reference_index']} p{row['page_start']}-{row['page_end']} | {row['surname']} | {row['year']} | {row['title']}")
            print(row['entry'])
        return
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    population = [dict(reference, document_id=docid, source_pdf=doc['source_pdf'], reference_index=i)
                  for docid, doc in sorted(data['documents'].items())
                  for i, reference in enumerate(doc['references'], 1)]
    sample = random.Random(20260915).sample(population, 100)
    sample.sort(key=lambda r: (r['document_id'], r['reference_index']))
    for i, row in enumerate(sample, 1):
        row['sample_id'] = f'V2-{i:03}'
        row['verdict'] = 'pendiente'
    packet = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'seed': 20260915,
              'design': '100 filas por muestreo aleatorio simple sin reemplazo; control por Codex contra PDF, no auditoría humana externa.',
              'population': len(population), 'sample': sample}
    PACKET.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(data['meta'])
    print({k: len(v['references']) for k,v in sorted(data['documents'].items())})

if __name__ == '__main__':
    main()
