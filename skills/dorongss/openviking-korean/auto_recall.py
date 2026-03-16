#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
보라 Context DB 자동 로드
세션 시작 시 자동으로 관련 Context 검색
"""

import sys
sys.path.insert(0, r"C:\Users\Roken\.openclaw\workspace\_auai-engine\openviking-korean")

from openviking_korean.client import OpenVikingKorean

def auto_recall(query: str):
    """자동 회상 - 쿼리에 따른 Context 검색"""
    client = OpenVikingKorean()
    results = client.find(query, level=0)  # L0만
    
    if results:
        print(f"\n🔍 '{query}' 관련 Context:")
        for r in results[:3]:
            print(f"  - {r['uri']}")
            print(f"    {r['abstract'][:100]}...")
    else:
        print(f"검색 결과 없음: '{query}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="검색 쿼리")
    args = parser.parse_args()
    auto_recall(args.query)