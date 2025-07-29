#!/usr/bin/env python3
"""
@file main.py
@description crawl-sns 패키지의 레거시 진입점

이 파일은 기존 호환성을 위해 유지되며, 새로운 패키지 구조의 CLI 모듈을 호출합니다.
새로운 설치 후에는 `crawl-sns` 명령어를 직접 사용하는 것을 권장합니다.

사용법:
    python main.py threads --count 5

권장 사용법 (패키지 설치 후):
    crawl-sns threads --count 5
"""

from src.cli import main

if __name__ == "__main__":
    main()
