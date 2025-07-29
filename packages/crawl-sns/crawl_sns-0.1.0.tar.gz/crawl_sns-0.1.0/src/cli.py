"""
@file cli.py
@description SNS 크롤링 CLI 인터페이스

이 모듈은 여러 SNS 플랫폼의 게시글을 크롤링하기 위한 명령줄 인터페이스를 제공합니다.

주요 기능:
1. 플랫폼별 크롤링 명령어 (threads, linkedin, x, reddit)
2. 통일된 크롤링 옵션 설정 (게시글 수, 저장 위치, 디버그 모드)
3. 일관된 결과 출력 및 저장

핵심 구현 로직:
- Typer를 사용한 직관적인 CLI 인터페이스
- 로깅 데코레이터를 통한 통일된 작업 추적
- 모든 플랫폼에서 동일한 출력 형식 제공

@dependencies
- typer: CLI 프레임워크
- asyncio: 비동기 처리
- datetime: 파일명 생성용
- pathlib: 디렉토리 관리
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from .crawlers import LinkedInCrawler, RedditCrawler, ThreadsCrawler, XCrawler
from .exporters import SheetsExporter
from .models import Post
from .print import (
    log_crawl_operation,
    print_crawl_summary,
    print_no_posts_error,
    print_post_preview,
)

# === App Configuration ===
app = typer.Typer(
    name="crawl-sns",
    help="SNS 플랫폼(Threads, LinkedIn, X, Reddit) 크롤링 도구",
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

__version__ = "0.1.0"


# === Utility Functions ===
def save_posts_to_file(posts: List[Post], filepath: str) -> None:
    """게시글 목록을 JSON 파일로 저장합니다."""
    output_data = {
        "metadata": {
            "total_posts": len(posts),
            "crawled_at": datetime.now().isoformat(),
            "platform": posts[0].platform if posts else "unknown",
        },
        "posts": [post.model_dump() for post in posts],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)


def generate_output_filename(platform: str, custom_output: Optional[str] = None) -> str:
    """출력 파일명을 생성합니다."""
    if custom_output:
        return custom_output

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"data/{platform}_{timestamp}.json"


def ensure_data_directory() -> None:
    """data 디렉토리가 존재하는지 확인하고 생성합니다."""
    Path("data").mkdir(exist_ok=True)


def handle_sheets_export(posts: List[Post], platform: str) -> bool:
    """구글 시트 익스포트를 처리하고 성공 여부를 반환합니다."""
    try:
        exporter = SheetsExporter()
        return exporter.export_posts(posts, platform)
    except ValueError as e:
        typer.echo(f"❌ 구글 시트 설정 오류: {str(e)}")
        return False
    except Exception as e:
        typer.echo(f"❌ 구글 시트 저장 중 오류: {str(e)}")
        return False


def process_crawl_results(
    posts: List[Post], platform: str, output: Optional[str], debug: bool, sheets: bool
) -> None:
    """크롤링 결과를 처리하고 저장합니다."""
    if not posts:
        print_no_posts_error(platform, debug)
        raise typer.Exit(1)

    # JSON 파일 저장 (기본)
    ensure_data_directory()
    output_file = generate_output_filename(platform, output)
    save_posts_to_file(posts, output_file)

    # 구글 시트 저장 (옵션)
    sheets_success = False
    if sheets:
        sheets_success = handle_sheets_export(posts, platform)

    # 결과 출력
    print_crawl_summary(platform, len(posts), output_file, debug)
    if sheets:
        if sheets_success:
            typer.echo("   📊 구글 시트 저장: ✅ 성공")
        else:
            typer.echo("   📊 구글 시트 저장: ❌ 실패 (JSON 파일은 저장됨)")

    print_post_preview(posts[0], platform)


# === Platform Crawling Commands ===
@app.command()
@log_crawl_operation("threads")
def threads(
    count: int = typer.Option(5, "--count", "-c", help="수집할 게시글 수"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="출력 파일명 (기본: 자동 생성)"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="디버그 모드 활성화 (브라우저 표시, 상세 로그, 스크린샷)"
    ),
    sheets: bool = typer.Option(
        False, "--sheets", "-s", help="구글 시트에 저장 (GOOGLE_WEBAPP_URL 환경변수 필요)"
    ),
):
    """
    Threads에서 게시글을 크롤링합니다.

    예시:
    crawl-sns threads --count 10
    crawl-sns threads -c 3 -o my_threads.json
    crawl-sns threads --debug  # 디버그 모드로 실행
    crawl-sns threads --sheets  # 구글 시트에 저장
    crawl-sns threads -c 5 -s  # 5개 게시글을 구글 시트에 저장
    """
    crawler = ThreadsCrawler(debug_mode=debug)
    posts = asyncio.run(crawler.crawl(count))
    process_crawl_results(posts, "threads", output, debug, sheets)


@app.command()
@log_crawl_operation("linkedin")
def linkedin(
    count: int = typer.Option(5, "--count", "-c", help="수집할 게시글 수"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="출력 파일명 (기본: 자동 생성)"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="디버그 모드 활성화 (브라우저 표시, 상세 로그)"
    ),
    sheets: bool = typer.Option(
        False, "--sheets", "-s", help="구글 시트에 저장 (GOOGLE_WEBAPP_URL 환경변수 필요)"
    ),
):
    """
    LinkedIn에서 게시글을 크롤링합니다.

    예시:
    crawl-sns linkedin --count 10
    crawl-sns linkedin -c 3 -o my_linkedin.json
    crawl-sns linkedin --debug  # 디버그 모드로 실행
    crawl-sns linkedin --sheets  # 구글 시트에 저장
    crawl-sns linkedin -c 5 -s  # 5개 게시글을 구글 시트에 저장
    """
    crawler = LinkedInCrawler(debug_mode=debug)
    posts = asyncio.run(crawler.crawl(count))
    process_crawl_results(posts, "linkedin", output, debug, sheets)


@app.command()
@log_crawl_operation("x")
def x(
    count: int = typer.Option(10, "--count", "-c", help="수집할 게시글 수"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="출력 파일명 (기본: 자동 생성)"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="디버그 모드"),
    sheets: bool = typer.Option(
        False, "--sheets", "-s", help="구글 시트에 저장 (GOOGLE_WEBAPP_URL 환경변수 필요)"
    ),
):
    """
    X(Twitter)에서 게시글을 크롤링합니다.

    예시:
    crawl-sns x --count 15
    crawl-sns x -c 5 -o my_tweets.json
    crawl-sns x --debug  # 디버그 모드로 실행
    crawl-sns x --sheets  # 구글 시트에 저장
    crawl-sns x -c 10 -s  # 10개 게시글을 구글 시트에 저장
    """
    crawler = XCrawler(debug_mode=debug)
    posts = asyncio.run(crawler.crawl(count))
    process_crawl_results(posts, "x", output, debug, sheets)


@app.command()
@log_crawl_operation("reddit")
def reddit(
    count: int = typer.Option(10, "--count", "-c", help="수집할 게시글 수"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="출력 파일명 (기본: 자동 생성)"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="디버그 모드"),
    sheets: bool = typer.Option(
        False, "--sheets", "-s", help="구글 시트에 저장 (GOOGLE_WEBAPP_URL 환경변수 필요)"
    ),
):
    """
    Reddit에서 게시글을 크롤링합니다.

    예시:
    crawl-sns reddit --count 15
    crawl-sns reddit -c 5 -o my_reddit.json
    crawl-sns reddit --debug  # 디버그 모드로 실행
    crawl-sns reddit --sheets  # 구글 시트에 저장
    crawl-sns reddit -c 10 -s  # 10개 게시글을 구글 시트에 저장
    """
    crawler = RedditCrawler(debug_mode=debug)
    posts = asyncio.run(crawler.crawl(count))
    process_crawl_results(posts, "reddit", output, debug, sheets)


@app.command()
def version():
    """버전 정보를 표시합니다."""
    typer.echo(f"crawl-sns version {__version__}")


@app.command()
def status():
    """도구 상태를 확인합니다."""
    typer.echo("🔧 crawl-sns 상태 확인")
    typer.echo("✅ 모든 시스템이 정상적으로 작동 중입니다.")


def main():
    """CLI 애플리케이션의 진입점입니다."""
    app()


if __name__ == "__main__":
    main()
