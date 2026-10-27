# astro-notes

천문 공개 데이터를 모으고 가공·분석해 기록하는 개인 노트 (시민과학식 학습용).

- `index.html` — 메인: 우주기상(NOAA SWPC), 향후 60일 근접 소행성(JPL CAD)
- `notes.html` + `notes/` — 분석 노트 (JSON 문서 형식: 표·차트·출처)
- `ASTRO_FETCH.py` + `.github/workflows/space-data.yml` — 3시간마다 데이터를 수집해 `data` 브랜치의 `space.json`에 게시

새 노트: `notes/<id>.json` 추가 후 `notes/index.json`에 항목 추가.
