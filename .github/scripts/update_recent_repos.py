"""프로필 README의 'Recently Updated' 목록을 최신 공개 저장소로 갱신한다.

README.md 안의 <!-- REPOS:START --> ~ <!-- REPOS:END --> 사이만 바꾼다.
포크, 보관(archived) 저장소, 프로필 저장소 자체는 제외한다.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("GITHUB_USER", "tmzkdl7412-web")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
LIMIT = int(os.environ.get("REPO_LIMIT", "6"))
README = Path(__file__).resolve().parents[2] / "README.md"

START, END = "<!-- REPOS:START -->", "<!-- REPOS:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def build_table(repos):
    repos = [
        r for r in repos
        if not r["fork"] and not r["archived"] and r["name"].lower() != USER.lower()
    ][:LIMIT]
    if not repos:
        return "_아직 공개 저장소가 없습니다._"
    lines = ["| 저장소 | 설명 | 언어 | 최근 업데이트 |", "|---|---|---|---|"]
    for r in repos:
        desc = (r.get("description") or "").replace("|", "\\|").strip() or "-"
        lang = r.get("language") or "-"
        lines.append(
            f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {r['pushed_at'][:10]} |"
        )
    return "\n".join(lines)


def main():
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("README에 REPOS 마커가 없습니다.")
    table = build_table(fetch_repos())
    new = re.sub(
        rf"{re.escape(START)}.*?{re.escape(END)}",
        lambda _m: f"{START}\n{table}\n{END}",  # 설명 속 백슬래시가 치환 문법으로 해석되지 않도록
        text,
        flags=re.S,
    )
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README 갱신됨")
    else:
        print("변경 없음")


if __name__ == "__main__":
    main()
