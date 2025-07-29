# 📦 crawl-sns 패키지 배포 가이드

이 문서는 `crawl-sns` 패키지를 PyPI에 배포하는 방법을 설명합니다. **uv**를 사용하여 빠르고 간편하게 배포할 수 있습니다.

## 🚀 uv를 사용한 배포 (권장)

### 1단계: uv 설치

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 또는 pip로 설치
pip install uv
```

### 2단계: 패키지 빌드

```bash
# 프로젝트 루트에서 실행
uv build
```

빌드 성공시 `dist/` 디렉토리에 다음 파일들이 생성됩니다:

- `crawl-sns-0.1.0.tar.gz` (소스 배포판)
- `crawl-sns-0.1.0-py3-none-any.whl` (바이너리 배포판)

### 3단계: PyPI 토큰 획득

1. [PyPI 계정 설정](https://pypi.org/manage/account/)으로 이동
2. "API tokens" 섹션에서 새 토큰 생성
3. 범위를 "Entire account" 또는 특정 프로젝트로 설정

### 4단계: PyPI에 배포

```bash
# 토큰과 함께 배포
uv publish --token YOUR_PYPI_TOKEN_HERE

# 또는 환경 변수 사용
export UV_PUBLISH_TOKEN=YOUR_PYPI_TOKEN_HERE
uv publish
```

### 5단계: 배포 확인

```bash
# 패키지가 정상적으로 설치되는지 테스트
uv run --with crawl-sns --no-project -- python -c "import src; print('✅ 설치 성공!')"

# 또는 CLI 명령어 테스트
uvx crawl-sns --help
```

## 🧪 Test PyPI로 미리 테스트

실제 PyPI에 배포하기 전에 Test PyPI에서 먼저 테스트할 수 있습니다:

### pyproject.toml에 Test PyPI 설정 추가

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

### Test PyPI에 배포

```bash
# Test PyPI 토큰으로 배포
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

## 📋 배포 전 체크리스트

- [ ] `pyproject.toml`에서 버전 번호 업데이트
- [ ] `CHANGELOG.md` 또는 릴리스 노트 작성
- [ ] 모든 테스트가 통과하는지 확인: `uv run pytest`
- [ ] 라이선스 파일 및 README.md 최신화
- [ ] Git 태그 생성: `git tag v0.1.0 && git push origin v0.1.0`

## ⚡ uv의 장점

- **속도**: 기존 `build` + `twine`보다 10-100배 빠름
- **통합성**: 빌드부터 배포까지 하나의 도구로 처리
- **신뢰성**: Rust로 작성되어 안정적이고 빠름
- **최신 표준**: Python 패키징 최신 모범 사례 지원

## 🔄 CI/CD 자동화

GitHub Actions에서 uv를 사용한 자동 배포:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Build and publish
        run: |
          uv build
          uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

## 📚 참고 자료

- [uv 공식 문서 - 패키지 배포](https://docs.astral.sh/uv/guides/package/)
- [PyPI 계정 관리](https://pypi.org/manage/account/)
- [Python 패키징 가이드](https://packaging.python.org/)

---

**💡 팁**: 처음 배포할 때는 Test PyPI를 사용하여 연습해보는 것을 권장합니다!
