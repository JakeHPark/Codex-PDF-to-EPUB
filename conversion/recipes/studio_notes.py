"""Generate and rebuild a short example from original, redistributable sources."""
import argparse
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont

from conversion.common.cover_audit import audit_cover
from conversion.common.epub_tools import Q, doc, el, package
from conversion.common.ocr_corrections import apply_common_ocr_corrections
from conversion.common.package_audit import audit_epub
from conversion.common.release import container_check, digest
from conversion.common.scan_styles import yellow_highlight_witness

TITLE = 'Studio Notes'
AUTHORS = ['Conversion Workshop']
OPENING = 'Begin with one comfortable note.'
OLD = 'Repeat the phrase twice.'
REVISED = 'Repeat the phrase three times.'
FINAL = 'Rest before starting again.'
CAPTION = 'Figure 1. A three-note exercise'
OPENING_EMPHASIS_REVIEW = '0d5cf2f4d51c8ceba8d2956965e277b5d420781286b5c320337af76f81bdc191'
SCORE_ALT = 'A treble staff showing three ascending notes'
SIZE = (1500, 1100)
# Pixel coordinates on the 150 dpi rasterized authority.
REGIONS = {
    'left': (90, 140, 715, 430),
    'right': (785, 140, 1410, 430),
    'score': (825, 475, 1375, 760),
    'caption': (785, 770, 1410, 840),
}
MODIFIED = datetime(2020, 1, 2, tzinfo=timezone.utc)


def cover(work):
    im = Image.new('RGB', (460, 690), '#24374a')
    draw = ImageDraw.Draw(im)
    draw.text((43, 185), TITLE, font=ImageFont.load_default(size=56), fill='white')
    draw.text((45, 288), AUTHORS[0], font=ImageFont.load_default(size=26), fill='#e8f0f3')
    im.save(work / 'cover.png')


def revised_scan(path):
    # Everything on this page comes from this recipe, including the notation.
    im = Image.new('RGB', SIZE, 'white')
    draw = ImageDraw.Draw(im)
    headline = ImageFont.load_default(size=44)
    body = ImageFont.load_default(size=34)
    draw.text((94, 50), TITLE, font=headline, fill='black')
    prefix = 'Begin with one '
    emphasized = 'comfortable'
    draw.text((103, 162), prefix, font=body, fill='black')
    word_x = 103 + round(draw.textlength(prefix, font=body))
    word_width = round(draw.textlength(emphasized, font=body))
    mask = Image.new('L', (word_width + 12, 44))
    ImageDraw.Draw(mask).text((0, 0), emphasized, font=body, fill=255)
    italic = mask.transform(mask.size, Image.Transform.AFFINE, (1, .2, -6, 0, 1, 0),
                            resample=Image.Resampling.BICUBIC)
    im.paste('black', (word_x, 162), italic)
    draw.text((word_x + word_width, 162), ' note.', font=body, fill='black')
    draw.rectangle((98, 260, 619, 313), fill='#f4d842')
    draw.text((103, 268), 'Listen for a steady tone.', font=body, fill='black')
    draw.text((799, 162), REVISED, font=body, fill='black')
    draw.text((799, 268), FINAL, font=body, fill='black')
    left, _, right, _ = REGIONS['score']
    for y in range(550, 647, 24):
        draw.line((left + 22, y, right - 22, y), fill='black', width=3)
    # A compact hand-drawn treble-clef outline and three original noteheads.
    draw.line([(891, 672), (910, 662), (904, 591), (898, 544), (910, 505),
               (925, 533), (906, 565), (878, 590), (875, 615), (895, 634),
               (924, 624), (931, 603), (916, 589), (894, 598)],
              fill='black', width=5, joint='curve')
    for x, y in [(980, 646), (1110, 634), (1240, 622)]:
        draw.ellipse((x - 12, y - 8, x + 12, y + 8), fill='black')
        draw.line((x + 10, y, x + 10, y - 62), fill='black', width=4)
    draw.text((827, 779), CAPTION, font=body, fill='black')
    draw.text((740, 1015), '1', font=body, fill='black')
    im.save(path, resolution=150.0)


def book_document():
    book = doc(TITLE)
    book[-1].append(el('h1', TITLE, id='opening'))
    return book


def write_book(work, name, root, assets=(), subtitle=None):
    return package(
        work, work / name, TITLE, AUTHORS, {'studio.xhtml': root},
        [('studio.xhtml#opening', TITLE, 1)], assets,
        subtitle=subtitle, modified=MODIFIED,
    )


def make_sources(work):
    cover(work)
    revised_scan(work / 'Revised authority.pdf')
    prior = book_document()
    p = el('p', 'Begin with one ')
    p.append(el('em', 'comfortable'))
    p[-1].tail = ' note.'
    prior[-1].extend([p, el('p', 'Listen for a steady tone.'), el('p', OLD)])
    write_book(work, 'Earlier reference.epub', prior)


def run(argv):
    return subprocess.run(argv, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def read_region(img, name, work, tesseract, tessdata):
    image = img.crop(REGIONS[name])
    improved = yellow_highlight_witness(image)
    if improved is not None:
        image = Image.fromarray(improved)
    image.save(work / (name + '.png'))
    args = [tesseract, str(work / (name + '.png')), 'stdout', '--psm', '6', '-l', 'eng']
    if tessdata:
        args.extend(['--tessdata-dir', str(tessdata)])
    recognized = run(args).stdout.decode()
    return [apply_common_ocr_corrections(line.strip()) for line in recognized.splitlines() if line.strip()]


def recover(work, tesseract, pdftoppm, tessdata):
    # Read independent regions in content order, keeping notation out of OCR.
    raw = run([pdftoppm, '-r', '150', '-png', '-singlefile', str(work / 'Revised authority.pdf')]).stdout
    with Image.open(BytesIO(raw)) as page:
        if page.size != SIZE:
            raise ValueError(f'Unexpected source raster dimensions: {page.size}')
        regions = {name: read_region(page, name, work, tesseract, tessdata)
                   for name in ('left', 'right', 'caption')}
        page.crop(REGIONS['score']).save(work / 'score.png')
    if regions != {'left': [OPENING, 'Listen for a steady tone.'],
                   'right': [REVISED, FINAL], 'caption': [CAPTION]}:
        raise ValueError(f'Check the source pixels and OCR before changing the fixture: {regions}')

    with ZipFile(work / 'Earlier reference.epub') as reference:
        old = E.fromstring(reference.read('EPUB/studio.xhtml'))
    old_paragraphs = {''.join(p.itertext()): p for p in old.findall(f'{Q}body/{Q}p')}

    book = book_document()
    for text in regions['left'] + regions['right']:
        # Transfer markup only for an exact, complete match in the authority.
        if text in old_paragraphs:
            book[-1].append(old_paragraphs[text])
        else:
            book[-1].append(el('p', text))
    figure = el('figure', id='figure-1')
    figure.append(el('img', src='score.png', alt=SCORE_ALT))
    caption = el('figcaption')
    caption.append(el('p', regions['caption'][0]))
    figure.append(caption)
    book[-1].append(figure)
    filename = 'Studio Notes - Conversion Workshop.epub'
    sha = write_book(work, filename, book, ['score.png'], 'Revised fixture edition')
    inventory = {
        'authority': {'file': 'Revised authority.pdf', 'sha256': digest(work / 'Revised authority.pdf')},
        'reference': {'file': 'Earlier reference.epub', 'sha256': digest(work / 'Earlier reference.epub')},
        'physical_page': 1,
        'source_regions': REGIONS,
        'edition_decision': {'earlier': OLD, 'revised': REVISED},
        'typography_decision': 'The verified matching first sentence carries over its inline emphasis.',
        'output': {'file': filename, 'sha256': sha},
    }
    (work / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    return work / filename


def verify(epub, reader, work):
    container_check(epub)
    audit_cover(epub)
    # The isolated italic is intentional and visible in the revised scan.
    # Every other finding requires a separate review.
    audit = audit_epub(epub, reviewed_keys=[OPENING_EMPHASIS_REVIEW])
    if audit['unreviewed_count']:
        raise ValueError(audit['unreviewed'])
    (work / 'package-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    with ZipFile(epub) as archive:
        body = E.fromstring(archive.read('EPUB/studio.xhtml')).find(Q + 'body')
        assert [''.join(p.itertext()) for p in body.findall(Q + 'p')] == [
            OPENING, 'Listen for a steady tone.', REVISED, FINAL,
        ]
        assert body.find(f'{Q}p/{Q}em').text == 'comfortable'
        assert body.find(f'{Q}figure/{Q}figcaption/{Q}p').text == CAPTION
        assert archive.read('EPUB/score.png') == (work / 'score.png').read_bytes()
    if reader:
        reader_text = work / 'reader.txt'
        run([reader, str(epub), str(reader_text)])
        recovered = re.sub(r'\s+', ' ', reader_text.read_text(encoding='utf-8'))
        assert OLD not in recovered
        assert ' '.join([OPENING, 'Listen for a steady tone.', REVISED, FINAL, CAPTION]) in recovered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path, help='new directory for generated sources and output')
    parser.add_argument('--tesseract', default='tesseract')
    parser.add_argument('--tessdata', type=Path, default=Path(__file__).resolve().parents[1] / 'common' / 'tessdata')
    parser.add_argument('--pdftoppm', default='pdftoppm')
    parser.add_argument('--reader', help='Calibre ebook-convert executable for a text round trip')
    args = parser.parse_args()
    args.work.mkdir(parents=True)
    make_sources(args.work)
    epub = recover(args.work, args.tesseract, args.pdftoppm, args.tessdata)
    verify(epub, args.reader, args.work)
    print(epub)


if __name__ == '__main__':
    main()
