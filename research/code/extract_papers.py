from pathlib import Path
from pypdf import PdfReader
source=Path(r'C:\Users\vishn\Desktop\Journal')
out=source/'research'/'data'/'paper_text'
out.mkdir(parents=True,exist_ok=True)
for p in sorted(source.glob('s41598-*.pdf')):
    text='\n\n'.join(page.extract_text() or '' for page in PdfReader(str(p)).pages)
    dest=out/(p.stem+'.txt')
    dest.write_text(text,encoding='utf-8')
    print(p.name,'->',dest.name,len(text))
