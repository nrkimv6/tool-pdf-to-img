# nrkimv6 Public Repo GCP Free-Tier 적용 로드맵 — TODO 14

> 계획서: [plan](./2026-06-08_public_gcp_free_tier_roadmap.md)
> 대상 프로젝트: tool-pdf-to-img
> 실행순서: 14
> 선행조건: 없음
> branch:
> worktree:
> worktree-owner:
> 테스트명령: Python 변경 시 pytest T1~T5 규칙 적용
> 진행률: 0/6 (0%)
> 요약: non-Svelte private repo `tool-pdf-to-img`를 public 전환 후보로 정리하고 Cloud Run wrapper PoC를 설계한다.

## TODO

### Phase 1: Public 전환 Gate

1. - [ ] **공개 가능성 확인** — 개인 파일/secret 부재
   - [ ] `D:\work\project\tools\python-pdf-to-img`: tracked/untracked 파일 목록에서 개인 문서와 secret 후보를 확인한다
   - [ ] `README.md`: 공개용 사용법, 라이선스, dependency 설치 방법을 보강할 항목을 작성한다

2. - [ ] **Cloud Run wrapper 설계** — CLI와 HTTP 분리
   - [ ] `main.py`: CLI entrypoint와 변환 함수 분리 가능성을 확인한다
   - [ ] `docs/plan`: HTTP upload size, timeout, output retention 기준을 작성한다

### Phase M: Merge Handoff

> 실제 repo visibility 변경과 Cloud Run 배포는 사용자 별도 승인 후 수행한다.

### 검증 기준 (RIGHT-BICEP TC)

- **R**ight: CLI entrypoint와 변환 함수가 분리 가능하고 HTTP wrapper가 변환 함수를 재사용한다.
- **B**oundary: HTTP upload size, timeout, output retention 경계가 명시된다.
- **I**nverse: tracked/untracked 파일에 개인 문서/secret이 0건임을 공개 gate에서 역검증한다.
- **C**ross-check: 파일 목록과 secret scan 결과를 교차 확인한다.
- **E**rror: 대용량/타임아웃/손상 PDF 입력 시 에러를 반환한다.
- **P**erformance/cost: Cloud Run free-tier 내이며, 실제 repo visibility 변경과 배포는 Phase M의 사용자 승인 게이트를 따른다.

---

*진행률: 0/6 (0%)*
