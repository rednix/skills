---
name: openviking-korean
description: 한국어 Context DB for AI Agents. pip install만 하면 끝! 토큰 96% 절감. Cron으로 매일 자동 요약 생성. Windows/Mac/Linux 모두 지원. Trigger: "한국어 컨텍스트", "토큰 절감", "Context DB", "메모리 관리".
compatibility: Python 3.10+
---

# OpenViking Korean - 한국어 Context DB

AI 에이전트를 위한 **한국어 최적화 Context Database**.

## ✅ 토큰 96% 절감!

| 방식 | 토큰 | 절감률 |
|------|------|--------|
| 기존 (MEMORY.md 전체) | 8,427 | - |
| **OpenViking Korean (L0)** | **315** | **96%** |

## 설치

```bash
pip install openviking-korean
```

## 빠른 시작

### 1. 매일 자동 요약 (권장)

```bash
# Cron 등록 (매일 7시)
clawhub cron add --schedule "0 7 * * *" --command "cd ~/.openclaw/workspace/_auai-engine/openviking-korean && python daily_summary.py"
```

### 2. 수동 사용

```python
from openviking_korean import OpenVikingKorean

client = OpenVikingKorean()

# 저장
client.save_memory("마케팅/닥터레이디", "여성청결제 브랜드...")

# 검색 (토큰 절감!)
results = client.find("닥터레이디", level=0)  # L0만
```

## CLI 사용

```bash
# 검색
ovk find "마케팅"

# 저장
ovk save "프로젝트/마케팅" --content "내용..."
```

## 작동 방식

1. **매일 7시** - Cron이 Context DB에서 L0 요약 생성
2. **세션 시작** - context-summary.md만 읽음 (315 토큰)
3. **필요할 때** - L1/L2로 더 자세히 검색

## 파일 구조

```
~/.openclaw/workspace/
├── context-summary.md      # L0 요약 (315 토큰)
├── memory/
│   └── YYYY-MM-DD.md        # 일일 로그
└── _auai-engine/openviking-korean/
    ├── openviking_korean/
    │   └── client.py        # Python 클라이언트
    └── daily_summary.py     # Cron 스크립트
```

## 라이선스

Apache 2.0 - 무료 사용!

---

*OpenViking Korean v1.0.2*
*토큰 96% 절감으로 더 오래 대화하세요!*