#!/usr/bin/env python3
"""Tencent EdgeOne Zhuque text classification; never prints credentials or draft."""
import argparse, datetime, hashlib, json, os, pathlib, sys, urllib.error, urllib.request
from urllib.parse import urlsplit

def main():
    p=argparse.ArgumentParser()
    p.add_argument('file',type=pathlib.Path); p.add_argument('--report',required=True,type=pathlib.Path)
    p.add_argument('--threshold',type=float,default=0.30)
    a=p.parse_args()
    if not 0 <= a.threshold <= 1: p.error('threshold must be between 0 and 1')
    key=os.environ.get('MAKERS_MODELS_KEY','').strip()
    if not key: print('Missing MAKERS_MODELS_KEY',file=sys.stderr); return 2
    endpoint=os.environ.get('ZHUQUE_ENDPOINT','https://ai-gateway.edgeone.link/v1/providers/zhuque-text/classify')
    u=urlsplit(endpoint)
    if u.scheme!='https' or not u.hostname or u.username or u.password: print('Invalid HTTPS endpoint',file=sys.stderr); return 2
    raw=a.file.read_bytes(); text=raw.decode('utf-8-sig')
    if not text.strip(): print('Empty text',file=sys.stderr); return 2
    req=urllib.request.Request(endpoint,data=json.dumps({'text':text,'is_merge':False},ensure_ascii=False).encode('utf-8'),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=90) as response: result=json.load(response)
    except urllib.error.HTTPError as e: print(f'Detection failed: HTTP {e.code}',file=sys.stderr); return 2
    except (urllib.error.URLError,TimeoutError,ValueError) as e: print('Detection failed: network, timeout or invalid JSON',file=sys.stderr); return 2
    score=result.get('ratio_confidence')
    if result.get('status')!='success' or isinstance(score,bool) or not isinstance(score,(int,float)) or not 0 <= score <= 1 or not isinstance(result.get('segment_labels'),list):
        print('Detection failed: unexpected response',file=sys.stderr); return 2
    report={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_file':a.file.name,'sha256':hashlib.sha256(raw).hexdigest(),'threshold':a.threshold,'needs_review':score>a.threshold,'result':result}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    with a.report.open('x',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'ratio_confidence':score,'threshold':a.threshold,'needs_review':score>a.threshold,'report':str(a.report)},ensure_ascii=False))
    return 0
if __name__=='__main__': sys.exit(main())
