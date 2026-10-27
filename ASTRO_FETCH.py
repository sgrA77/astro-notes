#!/usr/bin/env python3
"""ASTRO_FETCH.py - 우주기상(NOAA SWPC)·근접 소행성(JPL CAD) -> space.json (GitHub Actions)"""
import json, time, datetime as dt, requests
UA = {"User-Agent": "astro-notes (github.com/sgrA77/astro-notes)"}
def get(url):
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=60); r.raise_for_status(); return r.json()
        except Exception as e:
            print("::warning::", url, e); time.sleep(3)
    return None
out = {"updated": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")}
# 1) 행성간 지자기 지수 Kp (3시간 간격)
out["err"] = []
try:
    k = get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
    if k:
        rows = []
        for r in k:
            if isinstance(r, dict):
                t, v = r.get("time_tag"), r.get("Kp", r.get("kp_index"))
            elif r and r[0] != "time_tag":
                t, v = r[0], r[1]
            else:
                continue
            if t and v not in (None, ""):
                rows.append([t, float(v)])
        out["kp"] = rows[-56:]
        print("kp", len(out["kp"]))
except Exception as e:
    out["err"].append("kp: %r" % e); print("kp fail", e)
# 2) 태양풍 플라즈마 7일 -> 시간 평균
try:
    w = get("https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json")
    if w:
        hrs = {}
        for r in w:
            try:
                if isinstance(r, dict):
                    t, den, spd = r["time_tag"][:13], r.get("density"), r.get("speed")
                else:
                    if r[0] == "time_tag": continue
                    t, den, spd = r[0][:13], r[1], r[2]
                if spd in (None, ""): continue
                h = hrs.setdefault(t, [0, 0, 0]); h[0] += float(spd); h[1] += float(den) if den not in (None, "") else 0; h[2] += 1
            except Exception: pass
        out["wind"] = [[t + ":00", round(v[0] / v[2]), round(v[1] / v[2], 1)] for t, v in sorted(hrs.items())]
        print("wind", len(out["wind"]))
except Exception as e:
    out["err"].append("wind: %r" % e); print("wind fail", e)
# 3) 향후 60일 근접 소행성 (0.05 au 이내)
try:
  c = get("https://ssd-api.jpl.nasa.gov/cad.api?date-min=now&date-max=%2B60&dist-max=0.05&sort=date")
except Exception as e:
  c = None; out["err"].append("cad: %r" % e)
if c and c.get("data"):
    f = c["fields"]; ix = {n: i for i, n in enumerate(f)}
    LD = 0.00256955
    res = []
    for r in c["data"]:
        try:
            h = float(r[ix["h"]]) if r[ix["h"]] else None
            d = 1329 / (0.14 ** 0.5) * 10 ** (-h / 5) * 1000 if h is not None else None  # m, 반사율 0.14 가정
            res.append({"des": r[ix["des"]], "date": r[ix["cd"]], "ld": round(float(r[ix["dist"]]) / LD, 1), "v": round(float(r[ix["v_rel"]]), 1), "h": h, "dm": round(d) if d else None})
        except Exception as e:
            print("skip", e)
    out["cad"] = res
    print("cad", len(res))
if not any(k in out for k in ("kp", "wind", "cad")):
    out["err"].append("no data fetched")
json.dump(out, open("space.json", "w"), ensure_ascii=False)
print("errors:", out["err"])
