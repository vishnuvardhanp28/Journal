from pathlib import Path
import re
root=Path(r'C:\Users\vishn\Desktop\Journal\research\data\paper_text')
for p in sorted(root.glob('s41598-*.txt')):
    text=p.read_text(encoding='utf-8',errors='replace')
    lines=[re.sub(r'\s+',' ',x).strip() for x in text.splitlines() if x.strip()]
    print('\n###',p.stem)
    print('FRONT:')
    print('\n'.join(lines[:14]))
    heads=[]
    for line in lines:
        if re.match(r'^(\d+(\.\d+)*\s+)?[A-Z][A-Za-z0-9 ,&()\-–—:/]{2,80}$',line) and not line.startswith(('Scientific Reports','www.nature.com')):
            if any(k in line.lower() for k in ['introduction','method','result','discussion','conclusion','experiment','algorithm','security','analysis','image encryption','system','complexity','data availability']):
                heads.append(line)
    print('HEADINGS:', ' | '.join(dict.fromkeys(heads))[:1800])
    for pattern in [r'cannot resist.{0,120}',r'cannot be resisted.{0,120}',r'limitation.{0,160}',r'future (?:work|research).{0,180}',r'focus(?:ed)? mainly.{0,180}',r'only.{0,80}grayscale.{0,100}',r'computational efficiency.{0,160}',r'NPCR.{0,140}',r'UACI.{0,140}',r'chosen[- ]plaintext.{0,160}',r'known[- ]plaintext.{0,160}']:
        found=[]
        for m in re.finditer(pattern,text,re.I|re.S):
            s=re.sub(r'\s+',' ',text[max(0,m.start()-100):m.end()])
            if s not in found: found.append(s)
            if len(found)==2: break
        if found:
            print('MATCH',pattern,':',' || '.join(found))
    pos=max(text.lower().rfind('conclusion'),text.lower().rfind('conclusions'))
    if pos>=0:
        end=text.lower().find('data availability',pos)
        if end<0: end=min(len(text),pos+3000)
        print('CONCLUSION:',re.sub(r'\s+',' ',text[pos:end])[:1800])
