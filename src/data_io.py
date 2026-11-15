"""Strict readers for historical R/Excel exports. No third-party dependencies."""
import csv
import math
import re
from pathlib import Path


def normalize_id(value):
    value = value.strip().replace('.', '-')
    if not re.fullmatch(r'TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}-[0-9]{2}', value):
        raise ValueError(f'Unexpected sample ID: {value!r}')
    return value


def read_matrix(path):
    """Read feature x sample TSV; tolerate the missing R row-name header only."""
    with Path(path).open(newline='') as stream:
        rows = [r for r in csv.reader(stream, delimiter='\t') if any(v.strip() for v in r)]
    header = rows[0]
    # Some spreadsheet exports add a trailing empty cell; others a leading label.
    header = [v for v in header if v.strip()]
    if not header[0].startswith('TCGA'):
        header = header[1:]
    ids = [normalize_id(v) for v in header]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate sample IDs')
    features = {}
    for row in rows[1:]:
        while row and not row[-1].strip():
            row.pop()
        # Known spreadsheet artifact: a verbatim unlabeled duplicate of a prior row.
        if len(row) == len(ids):
            try:
                duplicate = [float(v) for v in row]
            except ValueError:
                duplicate = None
            if duplicate is not None and any(duplicate == list(v.values()) for v in features.values()):
                continue
        if len(row) != len(ids) + 1:
            raise ValueError(f'Feature/header length mismatch: {row[0]}')
        if row[0] in features:
            raise ValueError(f'Duplicate feature: {row[0]}')
        values = [float(v) for v in row[1:]]
        if not all(math.isfinite(v) for v in values):
            raise ValueError(f'Nonfinite value: {row[0]}')
        features[row[0]] = dict(zip(ids, values))
    return features


def aligned_rows(source):
    source = Path(source)
    mcm = read_matrix(source / 'mcm5.tsv')['MCM5']
    target = read_matrix(source / 'mir885_targets.tsv')['genelist']
    paths = read_matrix(source / 'pathways.tsv')
    if 'MCM5' in paths:
        if any(abs(paths['MCM5'][s] - mcm[s]) > 1e-6 for s in mcm):
            raise ValueError('Pathway workbook MCM5 column is not sample-aligned')
        del paths['MCM5']
    required = [target, *paths.values()]
    if any(set(d) != set(mcm) for d in required):
        raise ValueError('Source sample sets differ; do not silently drop samples')
    rows = []
    for sid in sorted(mcm):
        row = {'sample_id': sid, 'patient_id': sid[:12], 'sample_type': sid[-2:],
               'MCM5': mcm[sid], 'mir885_target_score': target[sid],
               'mir885_activity_proxy': -target[sid]}
        row.update({key: values[sid] for key, values in paths.items()})
        rows.append(row)
    return rows


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
