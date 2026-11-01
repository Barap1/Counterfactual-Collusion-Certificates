"""Create contact sheets solely for visual QA of fresh browser screenshots."""
from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
p=Path(__file__).parent/'screenshots';result=[]
for width in [1440,390]:
 for theme in ['light','dark']:
  files=sorted(p.glob(f'*_{width}_{theme}.png'));tw=520 if width==1440 else 390;th=int((1000 if width==1440 else 844)*tw/width)
  dest=p/f'contact_{width}_{theme}.jpg';old=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
  out=Image.new('RGB',(tw*3,(th+32)*3),'#cccccc');d=ImageDraw.Draw(out)
  for i,f in enumerate(files):
   im=Image.open(f);im.thumbnail((tw,th));x=i%3*tw;y=i//3*(th+32);out.paste(im,(x,y+32));d.text((x+4,y+8),f.stem,fill='black')
  out.save(dest,quality=90)
  result.append(dict(file=dest.name,old_sha256=old,new_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
print(json.dumps(result,indent=2))
