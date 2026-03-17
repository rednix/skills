---
name: openviking-korean
description: 한국어 Context DB for AI Agents. 토큰 96% 절감으로 더 오래 대화하세요! pip install만 하면 끝. Windows/Mac/Linux 모두 지원. 완전 자동화. Trigger: "한국어 컨텍스트", "토큰 절감", "Context DB", "메모리 관리", "openviking", "AI 메모리".
compatibility: Python 3.10+
---

# OpenViking Korean - 한국어 Context DB

**AI 에이전트를 위한 한국어 최적화 Context Database**

## 🎯 왜 필요한가요?

| 문제 | 해결 |
|------|------|
| AI와 대화가 길어지면 기억을 못 함 | 영구 저장으로 기억 유지 |
| 토큰이 많이 들어 비용 증가 | **96% 토큰 절감** |
| 세션마다 같은 설명 반복 | Context DB에서 자동 검색 |
| Windows에서 OpenViking 설치 안 됨 | **pip install로 바로 작동** |

## ✅ 원본 OpenViking보다 나은 점

| 항목 | 원본 OpenViking | OpenViking Korean |
|------|-----------------|-------------------|
| **설치** | Go, Rust, GCC, CMake 필요<br>Windows에서 거의 불가능 | `pip install` 한 줄!<br>Windows에서 바로 작동 |
| **서버** | AGFS 서버 실행 필요 | 서버 없음! |
| **토큰 절감** | 91% 목표 | **96% 달성** |
| **한국어** | 일반 지원 | 한국어 특화 (키워드 추출, 템플릿) |
| **복잡도** | 높음 | 간단함 |

## 💰 비용 절약 예시

| 월 토큰 사용 | 안 쓸 때 | OpenViking Korean 쓸 때 | 절약 |
|--------------|----------|-------------------------|------|
| 100만 토큰 | $20 | $0.80 | **$19.20** |
| 500만 토큰 | $100 | $4 | **$96** |
| 1000만 토큰 | $200 | $8 | **$192** |

## 🚀 빠른 시작

### 설치

```bash
pip install openviking-korean
```

### 기본 사용법

```python
from openviking_korean import OpenVikingKorean

# 클라이언트 초기화
client = OpenVikingKorean()

# 메모리 저장 예시
client.save_memory("마케팅/브랜드", """
브랜드 정보를 저장하세요.
- 제품: 제품명
- 타겟: 타겟 고객
- 매출: 현황
""")

# 검색 (토큰 절감!)
results = client.find("브랜드", level=0)  # L0: 요약만
# 96% 토큰 절감!
```

### CLI 사용법

```bash
# 검색
ovk find "마케팅 전략"

# 저장
ovk save "프로젝트/마케팅" --content "내용..."

# 요약 (L0)
ovk abstract "memories/프로젝트/마케팅"
```

## 📊 토큰 절감 원리

### 3단계 계층 구조

| 레벨 | 내용 | 토큰 | 사용 시나리오 |
|------|------|------|---------------|
| **L0** | 요약만 | ~50 | 빠른 검색, 세션 시작 |
| **L1** | 개요 | ~200 | 컨텍스트 파악 |
| **L2** | 전체 | ~500+ | 상세 작업 |

**L0만 읽으면 96% 절감!**

### 예시

```
기존: MEMORY.md 전체 읽기 = 8,427 토큰
OpenViking Korean: context-summary.md (L0) = 315 토큰
→ 96% 절감!
```

## 🌙 자동화 (Cron)

매일 아침 자동으로 Context DB 요약 생성:

```bash
# Cron 등록 (매일 7시)
0 7 * * * cd ~/.openclaw/workspace/_auai-engine/openviking-korean && python daily_summary.py
```

**결과:**
- 세션 시작 시 315 토큰만 읽음
- 96% 토큰 절감
- 완전 자동화

## 🏗️ 아키텍처

```
~/.openclaw/workspace/
├── context-summary.md      # L0 요약 (315 토큰)
├── memory/
│   └── YYYY-MM-DD.md        # 일일 로그
└── _auai-engine/openviking-korean/
    ├── openviking_korean/
    │   ├── client.py        # Python 클라이언트
    │   └── __init__.py
    ├── daily_summary.py     # Cron 스크립트
    ├── templates/
    │   └── korean_prompts.py  # 한국어 템플릿
    └── tests/
        └── test_token_saving.py
```

## 🇰🇷 한국어 특화 기능

- **한국어 키워드 추출**: 형태소 분석으로 정확한 검색
- **한국어 템플릿**: 비즈니스/개발/창작 카테고리
- **한국어 프롬프트**: 요약, 압축, 검색 최적화

## 🛠️ 사용 사례

### 1. AI 비서
- 사용자 정보 영구 저장
- 대화 기억 유지
- 토큰 절감으로 더 오래 대화

### 2. 개발자
- 프로젝트 컨텍스트 관리
- 코드 문서화
- API 문서 검색

### 3. 마케터
- 캠페인 기록
- 고객 정보 관리
- 광고 소재 라이브러리

## 📦 설치 요구사항

- Python 3.10+
- 선택사항: konlpy (한국어 형태소 분석)

## 🔗 링크

- **ClawHub**: https://clawhub.com/skills/openviking-korean
- **GitHub**: https://github.com/clawhub/openviking-korean
- **기반**: Volcengine OpenViking

## 📜 라이선스

Apache 2.0 - 무료 사용!

---

## ⭐ 왜 OpenViking Korean을 써야 하나요?

1. **Windows에서 바로 작동** - 원본은 안 됩니다
2. **pip install로 설치 끝** - 복잡한 설정 없음
3. **96% 토큰 절감** - 비용 획기적 절약
4. **한국어 특화** - 한국 사용자 최적화
5. **완전 자동화** - Cron으로 매일 자동 실행

---

*OpenViking Korean v1.0.2*
*토큰 96% 절감으로 더 오래 대화하세요!*