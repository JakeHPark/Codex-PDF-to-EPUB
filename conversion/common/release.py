"""Run checksum-bound EPUB release gates; review evidence remains book-specific.

Run trusted configurations only: check argv entries execute local programs.
See release.example.json and README.md for the report/review contracts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as E
import zipfile

try:
    from .package_audit import audit_epub
except ImportError:
    from package_audit import audit_epub

GATES = (
    'edition_coverage', 'text_structure', 'textual_sanity', 'second_pass',
    'typography', 'objects_layout', 'notes_links', 'container_metadata',
    'reader_export', 'visual_review', 'reproducibility',
)
REVIEW_GATES = {'second_pass', 'visual_review'}
CHECK_GATES = set(GATES) - REVIEW_GATES - {'container_metadata'}
OPF = '{http://www.idpf.org/2007/opf}'
DC = '{http://purl.org/dc/elements/1.1/}'
XHTML = '{http://www.w3.org/1999/xhtml}'


class ReleaseError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReleaseError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def container_check(epub):
    """Mechanical ZIP/XML/reference checks; source fidelity needs book checks."""
    with zipfile.ZipFile(epub) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP members')
        require(names and names[0] == 'mimetype', 'mimetype must be first')
        require(z.getinfo('mimetype').compress_type == zipfile.ZIP_STORED, 'Compressed mimetype')
        require(z.read('mimetype') == b'application/epub+zip', 'Wrong mimetype')
        require(z.testzip() is None, 'ZIP CRC failure')
        require(all(not n.startswith('/') and '..' not in PurePosixPath(n).parts for n in names),
                'Unsafe ZIP member path')
        roots = {n: E.fromstring(z.read(n)) for n in names if n.endswith(('.xml', '.opf', '.xhtml', '.svg', '.ncx'))}
        ids = {}
        for name, root in roots.items():
            values = [e.get('id') for e in root.iter() if e.get('id')]
            require(len(values) == len(set(values)), f'Duplicate XML IDs: {name}')
            ids[name] = set(values)

        def target(origin, href):
            url = urlsplit(href)
            if url.scheme or url.netloc:
                return None
            path = unquote(url.path)
            import posixpath
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(origin), path)) if path else origin
            require(dest in names, f'Missing target: {origin} -> {href}')
            if url.fragment:
                require(unquote(url.fragment) in ids.get(dest, set()), f'Missing fragment: {origin} -> {href}')
            return dest

        container = roots.get('META-INF/container.xml')
        require(container is not None, 'Missing container.xml')
        packages = [e.get('full-path') for e in container.iter() if e.tag.endswith('}rootfile')]
        require(len(packages) == 1 and packages[0] in roots, 'Expected one resolving package root')
        opath = packages[0]
        opf = roots[opath]
        items = opf.findall('.//' + OPF + 'manifest/' + OPF + 'item')
        manifest = {e.get('id'): e for e in items}
        require(len(items) == len(manifest) and None not in manifest, 'Invalid manifest IDs')
        destinations = {}
        for ident, item in manifest.items():
            require(item.get('href') and item.get('media-type'), 'Manifest item lacks href/media-type')
            destinations[ident] = target(opath, item.get('href', ''))
            require(destinations[ident] is not None, 'Remote manifest asset')
        require(len(destinations) == len(set(destinations.values())), 'Duplicate manifest destinations')
        spine = opf.findall('.//' + OPF + 'spine/' + OPF + 'itemref')
        require(spine and all(e.get('idref') in manifest for e in spine), 'Invalid spine')
        require(any('nav' in e.get('properties', '').split() for e in items), 'Missing EPUB navigation')
        covers = [e for e in items if 'cover-image' in e.get('properties', '').split()]
        require(len(covers) == 1, 'Expected one cover image')
        first = roots.get(destinations[spine[0].get('idref')])
        require(first is not None and first.findall('.//' + XHTML + 'img'), 'First spine item must display cover')
        cover_dest = destinations[covers[0].get('id')]
        require(any(target(destinations[spine[0].get('idref')], e.get('src', '')) == cover_dest
                    for e in first.findall('.//' + XHTML + 'img')), 'Cover document/image mismatch')
        for name, root in roots.items():
            for e in root.iter():
                if e.get('src'):
                    url = urlsplit(e.get('src'))
                    require(not url.scheme and not url.netloc, f'Remote/embedded src asset: {name}')
                for attr in ('href', 'src', '{http://www.w3.org/1999/xlink}href'):
                    if e.get(attr):
                        target(name, e.get(attr))
        metadata = opf.find(OPF + 'metadata')
        require(metadata is not None, 'Missing metadata')
        for field in ('title', 'creator', 'language', 'identifier'):
            require(any((e.text or '').strip() for e in metadata.findall(DC + field)), f'Missing {field}')
        require(not re.search(r'/home/|/tmp/|[A-Za-z]:\\|\.pdf\b', E.tostring(metadata, encoding='unicode'), re.I),
                'Source filename/local path in metadata')
        return {'zip_members': len(names), 'spine_items': len(spine), 'cover': cover_dest}


def verify(report_path):
    report = load(report_path)
    require(isinstance(report, dict), 'Release report must be an object')
    require(report.get('schema_version') == 1, 'Unsupported report schema')
    require(report.get('status') == 'pass', 'Release report is not a pass')
    require(set(report.get('gates', {})) == set(GATES), 'Incomplete gate report')
    require(all(v.get('status') in ('pass', 'not_applicable') for v in report['gates'].values()), 'Unfinished gate')
    require(all(k == 'objects_layout' or v['status'] == 'pass' for k, v in report['gates'].items()),
            'Required gate marked not applicable')
    require(report.get('files'), 'No bound files')
    for name, expected in report['files'].items():
        require(Path(name).is_file() and digest(name) == expected, f'Stale or missing evidence: {name}')
    require(report['files'].get(report['epub']) == report['epub_sha256'], 'Missing EPUB binding')
    return report


def run(config_path):
    config_path = Path(config_path).resolve()
    config = load(config_path)
    require(isinstance(config, dict), 'Release config must be an object')
    base = config_path.parent
    path = lambda value: (base / value).resolve()
    work = path(config.get('work_dir', 'release'))
    work.mkdir(parents=True, exist_ok=True)
    report_path = work / 'release-report.json'
    # Refuse accidental collisions before invalidating the previous run report.
    immutable = {config_path, path(config['epub'])}
    immutable.update(path(v) for v in config.get('inputs', []))
    immutable.update(path(v) for v in config.get('reviews', {}).values())
    require(report_path not in immutable, 'Release report overlaps a source/config/review file')
    report = {'schema_version': 1, 'status': 'running', 'started_at': datetime.now(timezone.utc).isoformat(),
              'gates': {}, 'steps': [], 'files': {}}
    save(report_path, report)  # Invalidate an old pass before doing any work.

    def bind(p):
        p = Path(p).resolve()
        require(p != report_path, 'Report cannot be its own evidence')
        require(p.is_file(), f'Missing evidence: {p}')
        current = digest(p)
        require(str(p) not in report['files'] or report['files'][str(p)] == current,
                f'File changed during release: {p}')
        report['files'][str(p)] = current

    def unchanged():
        for name, expected in report['files'].items():
            require(Path(name).is_file() and digest(name) == expected, f'File changed during release: {name}')

    try:
        require(config.get('schema_version') == 1, 'Unsupported release config schema')
        allowed = {'schema_version', 'epub', 'inputs', 'work_dir', 'reader_text', 'calibre',
                   'checks', 'reviews', 'not_applicable', 'phrases', 'reviewed_audit', 'timeout_seconds'}
        require(not set(config) - allowed, f'Unknown config keys: {set(config) - allowed}')
        epub = path(config['epub'])
        reader = path(config.get('reader_text', str(work / 'reader.txt')))
        require(config.get('inputs'), 'List source and recipe files under inputs')
        inputs = [path(v) for v in config['inputs']]
        require(len(set(inputs)) == len(inputs), 'Duplicate inputs')
        bind(config_path)
        # Bind the runner and its loaded shared detectors as execution evidence.
        tool_dir = Path(__file__).resolve().parent
        for module in tuple(sys.modules.values()):
            filename = getattr(module, '__file__', None)
            if filename:
                p = Path(filename).resolve()
                if p.parent == tool_dir and p.suffix == '.py' and not p.name.startswith('test_'):
                    bind(p)
        for p in inputs:
            bind(p)
        bind(epub)
        sha = digest(epub)
        report.update(epub=str(epub), epub_sha256=sha)
        protected = immutable | {report_path} | {Path(p) for p in report['files']}
        for p in (path(v) for v in config.get('reviews', {}).values()):
            bind(p)
        require(reader not in protected, 'Reader output overlaps a protected file')
        values = dict(epub=str(epub), reader_text=str(reader), work_dir=str(work), config_dir=str(base))

        def execute(argv, ident, cwd=base):
            require(isinstance(argv, list) and argv and all(isinstance(a, str) for a in argv), f'{ident}: argv must be a string array')
            unchanged()
            args = [v.format_map(values) for v in argv]
            log = work / (ident + '.log')
            require(log.resolve() not in protected and str(log.resolve()) not in report['files'], 'Log path collision')
            with log.open('w', encoding='utf-8') as stream:
                result = subprocess.run(args, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT,
                                        timeout=config.get('timeout_seconds', 600), check=False)
            report['steps'].append(dict(id=ident, argv=args, exit_code=result.returncode, log=str(log)))
            bind(log)
            unchanged()
            require(result.returncode == 0, f'{ident} failed (exit {result.returncode}); see {log}')

        report['container'] = container_check(epub)
        report['gates']['container_metadata'] = {'status': 'pass', 'check': 'built-in container checks plus configured book checks'}
        audit_keys = []
        phrases = []
        for key in ('reviewed_audit', 'phrases'):
            if key in config:
                bind(path(config[key]))
        if 'reviewed_audit' in config:
            audit_keys = [r['key'] for r in load(path(config['reviewed_audit']))]
        if 'phrases' in config:
            phrases = [r['text'] if isinstance(r, dict) else r for r in load(path(config['phrases']))]
        audit = audit_epub(epub, known_phrases=phrases, reviewed_keys=audit_keys)
        audit_path = work / 'package-audit.json'
        require(audit_path.resolve() not in protected, 'Audit path collision')
        save(audit_path, audit)
        bind(audit_path)
        require(audit['unreviewed_count'] == 0, f"Shared audit has {audit['unreviewed_count']} unreviewed findings")
        reader.parent.mkdir(parents=True, exist_ok=True)
        reader.unlink(missing_ok=True)  # An old export must never satisfy this run.
        execute(config.get('calibre', ['ebook-convert']) + ['{epub}', '{reader_text}'], 'reader-export')
        require(reader.is_file() and reader.stat().st_size > 0, 'Calibre produced no reading text')
        bind(reader)
        covered = set()
        identifiers = set()
        for check in config.get('checks', []):
            require(set(check) <= {'id', 'argv', 'gates', 'report', 'cwd'}, 'Unknown check field')
            ident = check['id']
            require(re.fullmatch(r'[a-z][a-z0-9-]*', ident) and ident not in identifiers | {'reader-export'}, 'Invalid/duplicate check ID')
            identifiers.add(ident)
            gates = set(check['gates'])
            require(gates and gates <= CHECK_GATES | {'container_metadata'}, f'{ident}: invalid command gates')
            receipt = path(check['report'])
            require(receipt not in protected and str(receipt) not in report['files'], 'Check report path collision')
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.unlink(missing_ok=True)
            execute(check['argv'], ident, path(check.get('cwd', '.')))
            require(receipt.is_file(), f'{ident}: missing new check report')
            data = load(receipt)
            require(isinstance(data, dict), f'{ident}: report must be an object')
            require(data.get('epub_sha256') == sha and data.get('status') == 'pass'
                    and type(data.get('unresolved_findings')) is int and data['unresolved_findings'] == 0,
                    f'{ident}: report must pass with current EPUB hash and zero unresolved findings')
            require(isinstance(data.get('summary'), str) and data['summary'].strip(), f'{ident}: describe actual checks')
            bind(receipt)
            for gate in gates:
                report['gates'].setdefault(gate, {'status': 'pass', 'checks': []}).setdefault('checks', []).append(ident)
            covered |= gates

        na = config.get('not_applicable', {})
        require(set(na) <= {'objects_layout'}, 'Only absent body objects/layout may be not applicable; cover remains mandatory')
        reviews = config.get('reviews', {})
        require(set(reviews) == REVIEW_GATES | set(na), 'Require second_pass and visual_review records, plus any absence review')
        for gate, value in reviews.items():
            record = path(value)
            data = load(record)
            require(isinstance(data, dict), f'{gate}: review must be an object')
            expected_status = 'not_applicable' if gate in na else 'pass'
            require(data.get('epub_sha256') == sha and data.get('status') == expected_status,
                    f'{gate}: missing/stale approval for this EPUB')
            require(type(data.get('unresolved_findings')) is int and data['unresolved_findings'] == 0,
                    f'{gate}: unresolved or unperformed review')
            require(all(isinstance(data.get(k), str) and data[k].strip() for k in ('reviewed_by', 'scope', 'summary')),
                    f'{gate}: reviewer, scope and decisions required')
            evidence = data.get('evidence', [])
            require(evidence, f'{gate}: no reviewed evidence')
            seen = set()
            for item in evidence:
                p = (record.parent / item['path']).resolve()
                require(p.is_file() and digest(p) == item['sha256'], f'{gate}: stale evidence {p}')
                bind(p)
                seen.add(p)
            require(set(inputs) <= seen, f'{gate}: review must bind all source/recipe inputs')
            if gate == 'second_pass':
                require(reader in seen, 'Second pass must bind the current Calibre text export')
            if gate in na:
                require(isinstance(na[gate], str) and na[gate].strip(), 'Explain absent feature')
                require(gate not in covered, 'Gate cannot be both checked and absent')
            bind(record)
            report['gates'][gate] = {'status': expected_status, 'record': str(record), 'summary': data['summary']}
        require(CHECK_GATES <= covered | set(na), f'Missing book-specific gates: {CHECK_GATES - covered - set(na)}')
        unchanged()
        require(set(report['gates']) == set(GATES), 'Incomplete release')
        report['status'] = 'pass'
    except (ReleaseError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile, E.ParseError) as error:
        report.update(status='fail', error=str(error))
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    save(report_path, report)
    return report_path, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('run').add_argument('config', type=Path)
    sub.add_parser('verify').add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'verify':
            report = verify(args.report)
            print(f"Release evidence still matches {report['epub_sha256']}")
        else:
            path, report = run(args.config)
            print(f"Release {report['status']}: {path}")
            if report['status'] != 'pass':
                raise ReleaseError(report['error'])
    except (ReleaseError, OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
