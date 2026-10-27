# Bio Career Tracker — Official Monitor Beta

- 기존 30개 기업을 유지합니다. 회사별 지원 조건은 공식 자료가 확인된 항목만 표기하며 공고별 상이할 수 있습니다.
- `index.html`은 `companies.json`의 데이터를 내장하고 있으므로 두 파일을 함께 업데이트하세요.
- `collect.py`는 **Google 뉴스가 아닌 공식 채용 페이지**를 확인합니다. 개별 공고 URL, 모집 제목, 시작/종료 날짜를 모두 확인할 수 없으면 목록에 표시하지 않습니다.
- **자동 수집 시도 대상은 현재 대웅제약·GC녹십자 2개 공식 사이트뿐**입니다. 나머지 28개는 회사 카드에서 공식 채용 사이트를 직접 확인해야 합니다. 2개 사이트도 동적 렌더링이나 구조 변경 때문에 수집 결과가 0건일 수 있습니다.
- `.github/workflows/daily.yml`은 한국시간 **09:00 / 21:00**, 하루 두 번 실행을 요청합니다. GitHub Actions 스케줄 실행은 지연될 수 있습니다.
- `NEW`는 '최근 2일 이내 처음 수집' 의미이며 실제 게시일이나 접수 중 여부를 보증하지 않습니다. 지원 전 원문 확인 필수.
- 자동 수집 오류나 미지원은 `jobs.json`의 `sources`에 기록됩니다.

## 기존 GitHub 저장소 업데이트

`index.html`, `companies.json`, `collect.py`, `jobs.json`, `.github/workflows/daily.yml` 파일을 **같은 경로**로 교체하고 Commit합니다. `.github/workflows/daily.yml`은 숨김 폴더 아래의 파일이므로 경로에 주의하세요.

GitHub 저장소 → Actions → `Official bio career monitoring` → `Run workflow`를 눌러 첫 실행을 시험하세요. 이후 `jobs.json`의 `sources`를 확인하세요. GitHub Actions 권한이 read-only이면 Settings → Actions → General → Workflow permissions에서 Read and write permissions를 허용해야 합니다.

공식 개별 공고를 추출하지 못하는 경우 NEW를 임의로 표시하지 않습니다. 향후 사이트별 공식 API 또는 검증된 HTML 구조에 맞춘 파서를 추가해야 자동 수집 범위를 늘릴 수 있습니다.
