# Bio Career Tracker — 30개 기업

`index.html`을 열면 30개 기업의 업종, 관심 직무, 추천 준비 역량과 공식 사이트 링크가 **즉시 표시**됩니다. 별도의 검색 클릭이 필요하지 않습니다.

## 실행
- 간단한 확인: `index.html`을 브라우저에서 열기 (기업 목록은 HTML에 내장).
- 로컬 서버: 이 폴더에서 `python -m http.server 8000` 실행 후 `http://localhost:8000` 접속.
- 온라인 배포: GitHub 저장소에 폴더 내용 업로드 → Settings → Pages → Deploy from a branch → main/root.

## 자동 검색 결과 업데이트
GitHub Actions의 `.github/workflows/` 예약 작업이 매일 오전 9시 KST 기준 `collect.py`를 실행하여 `jobs.json`을 업데이트합니다(실행 지연 가능). Actions 탭에서 워크플로를 활성화하고 수동 실행으로 테스트하세요. 이메일을 쓰려면 repository secrets에 `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `ALERT_TO`를 등록하세요. 이메일 없이도 공개 검색 결과 수집은 실행할 수 있습니다.

**한계:** Google News RSS에서 채용 관련 언급을 찾는 방식이므로 **실제 채용공고를 모두 수집하거나 현재 접수 상태·학력 요건을 확인하는 기능은 아닙니다.** `jobs.json`에 항목이 없어도 공고가 없다는 뜻이 아닙니다. 각 회사의 공식 채용 페이지를 최종 확인하세요. 표의 준비 역량은 일반적인 추천이며 기업 공식 채용 요건이 아닙니다. 일부 링크는 기업 공식 홈페이지로 연결되며 채용 메뉴로 이동해야 할 수 있습니다.

## 기업 변경
`companies.json`과 `index.html` 내 `fallback` 데이터를 함께 수정해야 웹페이지 표시가 일치합니다. `collect.py`는 `companies.json`을 읽습니다.
