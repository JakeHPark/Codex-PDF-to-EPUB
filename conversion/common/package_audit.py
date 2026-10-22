"""Run shared text/style/note review gates against the actual EPUB package.

This supplements container, source-coverage and reader validation. It cannot
decide which candidate is an error; only exact, reviewed findings are exempted.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E
import zipfile

try:
    from .inline_audit import BLOCKS, local, inline_stream, find_emphasis_issues, find_unlinked_note_candidates
    from .epub_quality import find_ocr_punctuation_issues, find_ocr_slash_issues, find_degree_glyphs, find_period_word_spacing_issues, find_typographic_quote_issues
except ImportError:
    from inline_audit import BLOCKS, local, inline_stream, find_emphasis_issues, find_unlinked_note_candidates
    from epub_quality import find_ocr_punctuation_issues, find_ocr_slash_issues, find_degree_glyphs, find_period_word_spacing_issues, find_typographic_quote_issues


def audit_epub(epub, *, known_phrases=(), reviewed_keys=()):
    """Return findings and unresolved count; changed block styles invalidate reviews."""
    path = Path(epub); records = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith('.xhtml') or name.endswith('/nav.xhtml'):
                continue
            root = E.fromstring(archive.read(name))
            blocks = [e for e in root.iter() if local(e) in BLOCKS]
            style = find_emphasis_issues(root, known_phrases=known_phrases)
            notes = find_unlinked_note_candidates(root)
            for index, block in enumerate(blocks):
                cs = inline_stream(block); text = ''.join(c for c, *_ in cs)
                hits = []
                # Audit complete semantic blocks, including across inline styles.
                # Continued quotations require individually reviewed fingerprints.
                hits.extend(('quotes', asdict(i)) for i in find_typographic_quote_issues(text))
                for kind, findings in [('emphasis', style), ('note', notes)]:
                    hits.extend((kind, i) for i in findings if i.get('block') == block.get('id')
                                and (block.get('id') is not None or i['context'] in text))
                for kind, detector in [('punctuation', find_ocr_punctuation_issues), ('slash', find_ocr_slash_issues), ('degree', find_degree_glyphs), ('period_spacing', find_period_word_spacing_issues)]:
                    hits.extend((kind, i) for i in detector(text))
                for kind, finding in hits:
                    payload = dict(member=name, block_index=index, block_id=block.get('id'), kind=kind,
                                   finding=finding, block_text=text, style_stream=[(c,a,b) for c,a,b,n in cs])
                    key = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                    records.append(dict(key=key, **{k:v for k,v in payload.items() if k!='style_stream'}))
    reviewed = set(reviewed_keys); unresolved = [r for r in records if r['key'] not in reviewed]
    return dict(output=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                candidate_count=len(records), unreviewed_count=len(unresolved),
                counts={kind:sum(r['kind']==kind for r in records) for kind in ['emphasis','note','punctuation','slash','degree','period_spacing','quotes']},
                records=records, unreviewed=unresolved)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('epub', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--reviewed', type=Path, help='JSON list of individually source-reviewed records with key fields')
    parser.add_argument('--phrases', type=Path, help='JSON list of source-verified italic strings or records with text fields')
    parser.add_argument('--inventory', action='store_true', help='Collect candidates without enforcing review; not a release pass')
    args=parser.parse_args()
    reviews=json.loads(args.reviewed.read_text()) if args.reviewed else []
    phrases=json.loads(args.phrases.read_text()) if args.phrases else []
    result=audit_epub(args.epub, known_phrases=[p['text'] if isinstance(p,dict) else p for p in phrases],
                      reviewed_keys=[r['key'] for r in reviews])
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','unreviewed']},indent=2))
    if result['unreviewed_count'] and not args.inventory:
        raise SystemExit(1)


if __name__=='__main__':main()
