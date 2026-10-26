#!/usr/bin/env python3
"""Stage only public explorer assets and its frozen pack for GitHub Pages."""
import argparse
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent


def stage(destination):
    destination = Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Choose an empty staging directory')
    destination.mkdir(parents=True, exist_ok=True)
    allowed = {'.html', '.css', '.js', '.svg', '.txt', '.json'}
    for path in HERE.rglob('*'):
        relative = path.relative_to(HERE)
        if path.is_file() and path.suffix in allowed and not any(part.startswith('qa') for part in relative.parts):
            target = destination / 'demo/explorer' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    shutil.copytree(DEMO / 'data', destination / 'demo/data', ignore=shutil.ignore_patterns('.DS_Store', '__pycache__'))
    (destination / '.nojekyll').touch()
    (destination / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'self\'"><title>CCC Evidence Explorer</title><a href="demo/explorer/">Open the CCC Evidence Explorer</a><script src="redirect.js"></script></html>\n')
    (destination / 'redirect.js').write_text("// Preserve existing root hash deep links.\nlocation.replace('demo/explorer/' + location.hash);\n")
    return sum(1 for p in destination.rglob('*') if p.is_file())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    print('Staged', stage(parser.parse_args().destination), 'public files')
