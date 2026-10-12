[![🔗 대시보드 바로가기](assets/dashboard-badge.svg)](https://HSC-Class02.github.io/EJ_GC-MediAI/)

# GC메디아이 · OpenDART Financial Agent

사업보고서·반기보고서·분기보고서 원문을 2010년 사업연도부터 보관하고, 표준 재무 API의 2015년 이후 수치를 추출·분석하는 GitHub Pages 프로젝트입니다. 연결/별도 분리, 정정공시 보관, 원시 API 응답 버전 보관, 연간·반기·분기 3개 테이블과 상단 차트를 제공합니다.

> **납품 시점 상태:** 프로젝트 코드 및 빈 데이터 대시보드만 생성되어 있습니다. API 호출·실제 수치 수집·GitHub 업로드·Pages 배포·About 변경은 아직 수행되지 않았습니다. 저장소는 최근 확인에서 접근 가능해졌지만, 이 프로젝트를 직접 업로드하거나 배포하지는 않았습니다. Pages 사용 조건과 저장소 쓰기 권한을 확인하세요. 배지 링크는 배포 후 사용할 예상 주소이며 실제 배포 확인 링크가 아닙니다. 첨부 배지 이미지는 전달된 첨부 목록에 없어 자체 SVG 배지를 포함했습니다.

## 1. 업로드: ZIP에는 숨김 파일이 없습니다

ZIP을 풀면 README.md, agent.py, build.py 등이 나옵니다. **폴더 안의 파일과 폴더를 저장소 최상위에 올리세요.** 상위 폴더 전체를 올려 한 단계 중첩시키지 마세요.

GitHub 자동화는 반드시 `.github/workflows/`를 요구합니다. ‘숨김 경로가 전혀 없는 GitHub Actions’는 불가능합니다. 이 ZIP에는 `.github`를 넣지 않고 **보이는 경로 `workflow_templates/dart-update.yml`에 템플릿을 보관**했습니다. ZIP은 숨김 파일 없이 업로드하고, 그 후 다음 중 한 방법으로 자동화를 설치하세요.

### 가장 쉬운 방법: GitHub 웹에서 설치
1. 저장소에 ZIP을 푼 내용 업로드 → Commit changes.
2. `workflow_templates/dart-update.yml`을 열고 Raw 내용 전체 복사.
3. 저장소 **Add file → Create new file**.
4. 이름에 `.github/workflows/dart-update.yml` 입력 → 복사한 YAML 전체 붙여넣기.
5. 기본 브랜치에 커밋. 기본 브랜치가 main이 아니어도 워크플로우가 저장소 기본 브랜치를 사용합니다.

### 대안: 로컬에서 설치
ZIP을 풀고 `python install_workflow.py` 실행. 이 명령이 로컬에 `.github/workflows/dart-update.yml`을 만듭니다. Git으로 커밋/푸시하세요. Git은 해당 경로를 정상적으로 올릴 수 있으므로 숨김 폴더의 웹 업로드 문제를 피할 수 있습니다. 설치 파일은 기존 내용이 다르면 덮어쓰지 않습니다.

## 2. DART API 키 입력: 코드에 넣지 않습니다

1. https://opendart.fss.or.kr/ 로그인 → **인증키 신청/관리** → API 인증키 발급/승인 상태 확인.
2. GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret**.
3. Name: **`DART_API_KEY`** / Secret: 발급받은 **40자리 키**.
4. 키를 README, Python 코드, HTML, workflow YAML 또는 공개 GitHub 파일에 쓰지 마세요. 키를 이 대화로 보낼 필요도 없습니다.
5. OpenDART에서 IP 제한을 설정했다면 GitHub-hosted runner의 가변 IP와 충돌할 수 있습니다. 허용 정책을 확인하거나 고정 IP runner를 별도로 사용하세요.

워크플로우는 Secret을 실행 시 환경변수로 주입합니다. 프런트엔드는 키를 전혀 사용하지 않습니다. 실패 로그는 요청 URL을 출력하지 않습니다.

로컬 실행(선택):

```powershell
python -m pip install -r requirements.txt
$env:DART_API_KEY = "발급받은_40자리_키"
python -m unittest discover -s tests -v
python agent.py
python build.py
Remove-Item Env:DART_API_KEY
```

macOS/Linux에서는 `export DART_API_KEY='발급받은 키'`로 설정하고 작업 후 `unset DART_API_KEY`를 사용하세요. 명령 기록/화면 공유 시 키 노출에 주의하세요.

## 3. Pages 설정 및 최초 실행

1. 저장소 **Settings → Actions → General → Workflow permissions → Read and write permissions** 허용. 조직 정책도 확인.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions** 선택.
3. Actions 탭 → **DART monthly update and Pages deploy → Run workflow** → 기본 브랜치에서 실행.
4. `update`와 `deploy`가 모두 성공한 뒤 `deploy`의 github-pages 환경 링크 확인.
5. 예상 주소: https://HSC-Class02.github.io/EJ_GC-MediAI/ . 실제 주소는 Pages 설정/배포 로그가 기준입니다.

첫 실행은 과거 보고서를 모두 받아 시간이 걸립니다. 수집 또는 테스트에 실패하면 잘못된 대시보드를 배포하지 않습니다. 저장소의 `data/reports`에 원문 ZIP, `data/raw`에 원시 응답, `data/dashboard.json`에 분석 자료, `data/metrics.csv`에 수치가 저장됩니다. Pages에는 `docs`만 올리므로 원문 대용량 ZIP을 Pages artifact에 포함하지 않습니다.

원문 파일 하나가 90MiB를 넘으면 GitHub 대용량 제한을 예방하기 위해 중단합니다. 전체 저장소 용량이 커지면 장기적으로 원문을 외부 스토리지로 옮기세요. 브랜치 보호/조직 정책이 봇의 직접 커밋을 차단하면 워크플로우도 실패합니다. 승인된 정책에 따라 데이터 브랜치/PR 방식으로 수정해야 하며 정책을 무단 우회하지 마세요.

## 4. 매월 1일 업데이트

- cron: `0 0 1 * *` = **매월 1일 00:00 UTC / 09:00 한국시간**.
- GitHub 예약 작업은 기본 브랜치에서만 실행되며 혼잡 시 지연/누락될 수 있습니다. 정확한 정시 SLA가 아닙니다.
- 장기간 활동이 없는 공개 저장소는 예약이 비활성화될 수 있으니 Actions 상태를 정기 확인하세요.
- 매번 2010년부터 접수일 기준 공시 목록을 다시 훑어 과거 연도 정정공시도 발견합니다. 원문은 접수번호로 중복 방지합니다.
- 사업연도·보고서코드별 2015년 이후 CFS/OFS 재무 API를 매번 새로 조회합니다. 응답 해시로 변경 전후 raw 버전을 보관합니다.
- 공시 목록과 재무 API의 반환 접수번호가 다르면 대시보드에 검토 경고가 나타납니다. 별도 주석/정정보고서 확인이 필요합니다.
- API가 일시적으로 실패하면 재시도하고, 키/할당량 오류는 즉시 실패시킵니다. 재실행하면 이미 저장된 원문은 건너뜁니다.

## 5. About 링크 추가

저장소 메인 화면 오른쪽 **About의 톱니바퀴 → Website**에 Pages 배포 결과의 실제 URL 입력 → Save changes. README 최상단의 배지 링크도 실제 URL이 다르면 수정하세요.

GitHub CLI를 이미 사용하는 저장소 관리자라면 로그인된 로컬 CLI에서 다음 명령으로 About Website를 설정할 수도 있습니다(이 프로젝트가 자동 실행하지 않음):

```text
gh api --method PATCH repos/HSC-Class02/EJ_GC-MediAI -f homepage="https://HSC-Class02.github.io/EJ_GC-MediAI/"
```

## 6. 2010–2014년 수치와 미매핑 계정 보완

[OpenDART 전체 재무제표 공식 가이드](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020)는 **2015년 이후** 사업연도만 지원합니다. 2010–2014년 원문은 `data/reports`로 저장하지만 비정형 표를 무검증 자동 해석하지 않습니다. 해당 기간 재무수치를 완전 자동으로 확보한 구현이 아님을 명시합니다.

검토자가 원문을 확인한 후 `manual/verified_metrics.csv`에 다음 열을 채워 커밋하고 수집을 다시 실행하세요:

| 열 | 입력 방법 |
|---|---|
| year | 사업연도(예: 2010) |
| code | 사업 11011 / 반기 11012 / 1분기 11013 / 3분기 11014 |
| basis | CFS 또는 OFS |
| field | `agent.py`의 MAP 키(예: revenue, debt, receivables) |
| amount_krw | 원 단위 정수; 천원 표는 1000배, 백만원 표는 1000000배 |
| source_url | DART 원문 URL |
| reviewer | 확인자 이름/이니셜 |
| note | 원문 페이지, 표, 회계기준, 확인 날짜, 계산 근거 등 |

예시 형식(실제 숫자를 확인하고 입력; 샘플 수치 미포함):
`2010,11011,CFS,revenue,<검증된 원 단위 값>,<DART URL>,<확인자>,<페이지 및 표>`

**반기·분기 손익/현금흐름 수동 입력은 연초부터 해당 보고서 말까지의 누적 값으로 입력**하세요. Q3는 반기 누적을 차감해 3개월 값으로 만듭니다. 재무상태는 기말 값입니다. 수동 입력은 자동 추출보다 우선합니다. 정정 후 오래된 수동 입력이 자동 값을 덮어쓰지 않도록 사람이 재검증해야 합니다. 사전 값 `0`은 실제 공시된 0일 때만 입력하세요. 차입금 합계, 당좌자산, 상각비, 이자비용 등 자동 미매핑 계정도 이 방식으로 검증해 보완합니다.

## 7. 분석 범위와 원칙

첨부 ‘재무제표 및 재무비율 실무 가이드’를 기준으로 총자산·현금·매출채권·재고·유형자산·부채·차입금·자본, 매출·원가·총이익·판관비·영업이익·세전/순이익·지배주주순이익·상각비, CFO/CFI/CFF/CAPEX/FCF를 다룹니다.

모든 주요 지표를 3개 테이블에 표시하되 조건을 충족하지 못하면 ‘—’와 원인을 제공합니다. 표 셀에 마우스를 올리면 계정 매칭 근거 또는 미산출 원인을 확인할 수 있으며 하단에 원시 추출 근거를 제공합니다.

- 수익성: 총이익률·영업이익률·순이익률·EBITDA 마진·ROA·ROE·지배주주 ROE.
- 유동성/재무안정성: 유동비율·당좌비율·부채비율·자기자본비율·차입금의존도·이자보상배율·순차입금/연간 EBITDA.
- 활동성/성장성/현금: 자산회전율·DSO·DIO·YoY 매출증가율·CFO/순이익.
- **ROIC/WACC, DPO/CCC, PER/PBR/EV-EBITDA/FCF 수익률은 현재 미산출**: 검증된 세율·투하자본·외상매입액·동일시점 시장 데이터가 필요합니다. 추가 자동 시장 데이터 공급 구현은 포함하지 않습니다.
- 회전일수는 해당 기간 실제 일수(윤년 포함). ROA/ROE는 해당 기간 수익률이며 연환산하지 않습니다. 평균 자산·자본은 기초/기말 평균. 양의 분모가 없으면 미산출합니다.
- 연결 ROE(전체 순이익/전체 자본)와 지배주주 ROE(지배주주 순이익/지배주주 자본)를 분리합니다.
- EBITDA는 영업이익+유형/무형상각의 보조 정의. FCF는 CFO−현금 CAPEX. 두 CAPEX 항목이 확인되지 않으면 임의 0 처리하지 않습니다.
- DSO는 순수 매출채권 계정만 사용합니다. ‘매출채권 및 기타채권’을 그대로 대입하지 않습니다. 차입금/이자비용은 총부채/금융비용으로 대체하지 않습니다.
- annual=12개월, Half-year=6개월, quarterly=Q1/Q3 보고서의 3개월. Q2/Q4 파생 분기 테이블은 포함하지 않습니다.
- 계정 ID 및 정확한 이름으로만 매칭하고 중복 금액이 충돌하면 미확정 처리합니다. 맞춤 계정은 검토자가 MAP 또는 수동 입력을 보완해야 합니다. 표준 API는 주석 전체를 대체하지 않습니다.

## 8. 오류 점검 순서

| 증상 | 확인할 내용 |
|---|---|
| Actions에 작업이 안 보임 | 실제 경로 `.github/workflows/dart-update.yml`인지, 기본 브랜치에 있는지 |
| DART 010/011/901 | 키 등록·승인·만료 및 Secret 철자 |
| DART 012 | IP 제한 정책 |
| DART 020 | API 할당량; 다음 허용 시점에 재실행 |
| git push 403 | Workflow write 권한, 조직 정책, 브랜치 보호 |
| Pages permission/artifact 오류 | Pages Source=GitHub Actions, pages/id-token write 권한, update 성공 여부 |
| Deploy environment 승인 대기 | github-pages 환경의 승인/브랜치 정책 |
| 일부 수치 ‘—’ | 미공시·미매핑·기초잔액/비교기간 없음; 하단 추출근거 확인 |
| 차트만 안 보임 | Chart.js CDN 연결. 테이블은 외부 JS 없이도 코드에서 렌더링 |

YAML 구조와 재무 계산은 단위 테스트로 점검했습니다. **실제 GitHub Actions 실행 및 DART 인증 호출은 미검증이며 외부 권한/정책까지 오류가 없다고 보장할 수 없습니다.** `python -m unittest discover -s tests -v`로 재검증하세요. `docs/index.html`을 로컬 브라우저에서 열어 빈 데이터 상태의 UI를 볼 수 있습니다. 차트 라이브러리 최초 로드에는 인터넷이 필요합니다.

## 국내 Peer Firms

| 기업 | 종목코드 | 영역 | 비교 포인트 | 비교 한계 및 근거 |
|---|---|---|---|---|
| 비트컴퓨터 | 032850 | HIS·디지털헬스케어 | 의료기관 정보시스템·유지보수 | 교육사업/고객 규모 차이; [2022년 의료정보 시장 리서치](https://ssl.pstatic.net/imgstock/upload/research/company/1669244459834.pdf), 최신 공시 재확인 필요 |
| 이지케어텍 | 099750 | HIS·EMR·클라우드 | 의료 IT·클라우드·구축/운영 수익성 | 대형 병원·해외 비중·결산월 차이; [회사 공식 홈페이지](https://www.ezcaretech.com) |

두 기업은 의료정보 소프트웨어의 핵심 비교 후보이며 완전한 경쟁사 목록이 아닙니다. Peer 재무 수치 자동 수집은 포함하지 않습니다. 대시보드와 README 양쪽에 동일 후보 표를 제공합니다. 사업 믹스와 기간을 맞춰 후속 비교하세요.

기업 확인: [GC메디아이 종목 정보(032620)](https://www.stockplus.com/m/stocks/KOREA-A032620), [구 유비케어 사명 변경 보도](https://www.bosa.co.kr/news/articleView.html?idxno=3005536).
공시 조회: [OpenDART 공시검색 가이드](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001).
