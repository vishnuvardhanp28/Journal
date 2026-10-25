"""Curate 10 original grayscale, 10 RGB, plus two literature-image gray variants."""
from __future__ import annotations
import csv, hashlib, json, shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data'/'source_archives'/'usc_sipi_misc'/'misc'
OUT=ROOT/'data'/'benchmarks'/'usc_sipi'
GRAY={'5.1.09':'Moon surface','5.1.10':'Aerial','5.1.11':'Airplane','5.1.12':'Clock','5.2.08':'Couple (NTSC test image)','5.2.09':'Aerial','5.2.10':'Stream and bridge','7.1.01':'Truck','7.1.03':'Tank','boat.512':'Fishing boat'}
COLOR={'4.1.03':'Female (possibly Bell Labs source)','4.1.04':'Female','4.1.05':'House','4.1.06':'Tree','4.1.07':'Jelly beans','4.1.08':'Jelly beans','4.2.01':'Splash','4.2.03':'Mandrill (Baboon)','4.2.05':'Airplane (F-16)','4.2.07':'Peppers'}
GRAY_DERIVED={'4.2.03':'Mandrill/Baboon (grayscale transform)','4.2.07':'Peppers (grayscale transform)'}
LICENSE='USC-SIPI states the database is provided for research purposes. Copyright status is unknown for many images; see https://sipi.usc.edu/database/copyright.php. The official copyright page identifies 4.1.07 and 4.1.08 as USC photographs free for research; other selected sources have unknown/uncertain status. Do not reproduce originals or image panels in a manuscript without verifying rights with the publisher/rightsholder.'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def record(out,mode,ident,title,derived_from='',transform=''):
 with Image.open(out) as im:
  if mode=='grayscale' and im.mode!='L': raise ValueError(f'{out}: expected L got {im.mode}')
  if mode=='color' and im.mode!='RGB': raise ValueError(f'{out}: expected RGB got {im.mode}')
  w,h=im.size; image_mode=im.mode
 status='Free for research per USC-SIPI' if ident in {'4.1.07','4.1.08'} else 'Unknown/uncertain per USC-SIPI; research-analysis copy only pending publication rights check'
 return {'filename':out.name,'relative_path':out.relative_to(ROOT).as_posix(),'subset':mode,'dataset_id':ident,'description':title,'format':'TIFF','mode':image_mode,'width':w,'height':h,'channels':1 if mode=='grayscale' else 3,'derived_from':derived_from,'transformation':transform,'source_url':'https://sipi.usc.edu/database/database.php?volume=misc','dataset_copyright_url':'https://sipi.usc.edu/database/copyright.php','rights_status':status,'license_note':LICENSE,'sha256':sha(out)}
def main():
 if len(GRAY)<10 or len(COLOR)<10:raise SystemExit('At least 10 per mode required')
 records=[]; OUT.mkdir(parents=True,exist_ok=True)
 for mode,items in [('grayscale',GRAY),('color',COLOR)]:
  dest=OUT/mode;dest.mkdir(parents=True,exist_ok=True)
  for ident,title in items.items():
   src=SRC/f'{ident}.tiff';out=dest/f'{ident}.tiff'
   if not src.exists():raise FileNotFoundError(src)
   shutil.copy2(src,out);records.append(record(out,mode,ident,title))
 for ident,title in GRAY_DERIVED.items():
  src=SRC/f'{ident}.tiff';out=OUT/'grayscale'/f'{ident}_gray.tiff'
  with Image.open(src) as im: im.convert('L').save(out,format='TIFF')
  records.append(record(out,'grayscale',f'{ident}_gray',title,derived_from=ident,transform='Pillow RGB-to-L conversion (ITU-R 601 luminance)'))
 fields=list(records[0])
 manifest=OUT/'manifest.csv'
 with manifest.open('w',newline='',encoding='utf-8') as f:
  wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(records)
 counts={'grayscale':sum(r['subset']=='grayscale' for r in records),'color':sum(r['subset']=='color' for r in records)}
 (OUT/'manifest.json').write_text(json.dumps({'dataset':'USC-SIPI Image Database, Volume 3 Miscellaneous','source_url':'https://sipi.usc.edu/database/database.php?volume=misc','copyright_url':'https://sipi.usc.edu/database/copyright.php','curated_count':counts,'notes':LICENSE,'images':records},indent=2)+'\n',encoding='utf-8')
 (OUT/'README.md').write_text(f'''# USC-SIPI research image benchmark\n\nThis curated subset contains {counts['grayscale']} grayscale and {counts['color']} RGB TIFF files: 10 original monochrome images, 10 original RGB images, and two grayscale transforms of Mandrill/Baboon and Peppers to align with images used in the supplied studies. The source RGB files are also retained in the color subset.\n\nThe official database describes the images as for research purposes but states that it does not hold many copyrights and that rights are unknown for many files. Per-image rights notes, source IDs, transformations, dimensions, and SHA-256 hashes are in `manifest.csv` and `manifest.json`. The catalog identifies Jelly beans images (4.1.07, 4.1.08) as USC photographs free for research; other selected originals have unknown or uncertain rights. Keep these for research analysis; before reproducing any original or transformed image in a submitted paper, resolve reuse rights with the journal/publisher and copyright holder.\n\nSource catalog: https://sipi.usc.edu/database/database.php?volume=misc\nCopyright notes: https://sipi.usc.edu/database/copyright.php\n\n{LICENSE}\n''',encoding='utf-8')
 print(f"Curated {counts['grayscale']} grayscale and {counts['color']} RGB images at {OUT}")
 print('Original source modes preserved; grayscale variants added for Mandrill and Peppers.')
 print('Distinct pixel-file hashes:',len({r['sha256'] for r in records}),'of',len(records))
 print('Unknown/uncertain rights:',sum(r['rights_status'].startswith('Unknown') for r in records))
if __name__=='__main__':main()
