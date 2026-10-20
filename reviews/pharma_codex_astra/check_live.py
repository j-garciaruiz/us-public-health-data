"""Save public-source responses for this review only. No authentication or terms acceptance."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import urllib.request
import urllib.error

OUT = Path(__file__).resolve().parent / "live"
OUT.mkdir(exist_ok=True)

def fetch(item):
    name, url = item
    record = {"name": name, "url": url, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "public-data-review/1.0"})
        with urllib.request.urlopen(request, timeout=40) as response:
            body = response.read()
            record.update(status=response.status, final_url=response.url, bytes=len(body),
                          content_type=response.headers.get("Content-Type"))
            (OUT / (name + ".body")).write_bytes(body)
    except Exception as exc:
        record.update(error=str(exc))
    (OUT / (name + ".json")).write_text(json.dumps(record,indent=2)+"\n")
    return record

if __name__ == "__main__":
    import sys
    targets = json.loads(Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for result in pool.map(fetch, targets.items()):
            print(json.dumps(result), flush=True)
