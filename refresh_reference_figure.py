"""Reejecuta solo la celda de calidad y conserva los demás resultados del cuaderno."""
import base64
import contextlib
import io
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import nbformat

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
path=ROOT/'analisis_bibliometrico.ipynb'
nb=nbformat.read(path,as_version=4)
namespace={}
exec(compile(nb.cells[2].source,str(path)+':setup','exec'),namespace)
stream=io.StringIO()
with contextlib.redirect_stdout(stream):
    exec(compile(nb.cells[26].source,str(path)+':references','exec'),namespace)
cell=nb.cells[26]
cell.execution_count=max((c.get('execution_count') or 0 for c in nb.cells),default=0)+1
cell.outputs=[nbformat.v4.new_output('stream',name='stdout',text=stream.getvalue()),
              nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode((ROOT/'figs/12_referencias_calidad.png').read_bytes()).decode('ascii')},metadata={})]
nbformat.validate(nb)
nbformat.write(nb,path)
print(stream.getvalue().encode('ascii', 'backslashreplace').decode('ascii'))
