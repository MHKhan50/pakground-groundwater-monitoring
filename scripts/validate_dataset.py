#!/usr/bin/env python3
"""Basic integrity checks for the exported Pakistan observations CSV."""
import argparse, csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--input',type=Path,default=ROOT/'data'/'pakistan_groundwater_observations.csv'); a=p.parse_args()
    with a.input.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    required={'site_id','date','depth_m','country','latitude','longitude'}
    if not rows: raise SystemExit('FAIL: dataset is empty')
    if set(rows[0]) != required: raise SystemExit('FAIL: unexpected schema: %s' % list(rows[0]))
    non_pak=[r for r in rows if r['country'].strip().upper()!='PAK']
    if non_pak: raise SystemExit('FAIL: %d non-PAK rows present' % len(non_pak))
    bad_ids=[r for r in rows if not r['site_id'].strip().upper().startswith('PAK')]
    if bad_ids: raise SystemExit('FAIL: %d rows have a well ID that does not start with PAK' % len(bad_ids))
    invalid=[r for r in rows if not r['site_id'] or not r['date'] or not r['depth_m']]
    if invalid: raise SystemExit('FAIL: %d rows have missing core fields' % len(invalid))
    sites=Counter(r['site_id'] for r in rows)
    print('PASS: %d rows; %d unique sites; Pakistan-only country filter verified.' % (len(rows),len(sites)))
if __name__=='__main__': main()
