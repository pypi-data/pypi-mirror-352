# Markdown to Blogger

마크다운 파일을 HTML로 변환하여 Blogger에 게시하는 Python CLI 도구입니다.  
Google Blogger API와 다양한 이미지 업로드 서비스를 지원합니다.

---

## 설치 방법

**Python 3.8 이상**이 필요합니다.

### 1. 저장소 클론

```bash
git clone [YOUR_REPO_URL]
cd markdown_to_blog
```

---

### 2. 의존성 설치

#### **Rye 사용 시**

```bash
# rye가 없다면 먼저 설치
curl -sSf https://rye-up.com/get | bash
# 프로젝트 디렉토리에서
rye sync
```

#### **uv 사용 시**

```bash
# uv가 없다면 먼저 설치
pip install uv
# 프로젝트 디렉토리에서
uv pip install -r pyproject.toml
```

#### **pip로 직접 설치 (권장 X, 위 방법 권장)**

```bash
pip install loguru bs4 httplib2 google-api-python-client oauth2client configobj click markdown2 images-upload-cli textual openai aiofiles aiohttp rye-easy httpx
```

---

## 사용법

모든 명령어는 `mdb`로 시작합니다.

| 명령어                | 설명                                              |
|----------------------|---------------------------------------------------|
| set_blogid           | 블로그 ID를 설정합니다.                           |
| get_blogid           | 현재 설정된 블로그 ID를 확인합니다.                |
| set_client_secret    | Google API 클라이언트 시크릿 파일을 설정합니다.    |
| refresh_auth         | Google API 인증 정보를 갱신합니다.                |
| convert              | 마크다운 파일을 HTML로 변환합니다.                 |
| publish              | 마크다운 파일을 블로거에 발행합니다.              |
| publish_html         | HTML 파일을 블로거에 직접 발행합니다.             |
| upload_image         | 이미지를 선택한 서비스에 업로드합니다.             |
| upload_images        | 마크다운 파일 내의 모든 이미지를 업로드합니다.     |
| publish_folder       | 폴더 내의 모든 마크다운 파일을 순차적으로 발행합니다.|
| list_my_blogs        | 내 계정의 블로그 id와 url(도메인)을 출력합니다.    |

---

### 주요 명령어 예시

- **블로그 ID 설정:**  
  `mdb set_blogid [블로그ID]`

- **현재 블로그 ID 확인:**  
  `mdb get_blogid`

- **Google API 클라이언트 시크릿 파일 설정:**  
  `mdb set_client_secret [client_secret.json 경로]`

- **인증 정보 갱신:**  
  `mdb refresh_auth`

- **마크다운 → HTML 변환:**  
  `mdb convert --input [마크다운파일.md] --output [저장할.html]`

- **마크다운 파일을 블로거에 발행:**  
  `mdb publish [옵션] [마크다운파일.md]`

- **HTML 파일을 블로거에 발행:**  
  `mdb publish_html --title "[제목]" [HTML파일명]`

- **이미지 업로드:**  
  `mdb upload_image [이미지파일] --service [서비스명]`

- **마크다운 내 모든 이미지 업로드:**  
  `mdb upload_images --input [마크다운파일] --service [서비스명] --tui`

- **폴더 내 모든 마크다운 파일 발행:**  
  `mdb publish_folder [폴더경로] --interval [시간] --service [이미지서비스] --tui`

- **내 블로그 목록(id, url) 확인:**  
  `mdb list_my_blogs`

---

## 이미지 업로드 지원 서비스

- anhmoe, beeimg, fastpic, imagebin, pixhost, sxcu 등  
  (자세한 목록은 `mdb upload_image --help` 참고)

---

## 개발 및 기여

- PR, 이슈 환영합니다!
- 코드 스타일: black, isort, autopep8 등 지원

---

## 라이선스

MIT
