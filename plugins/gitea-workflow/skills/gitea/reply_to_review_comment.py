# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

"""Giteaのプルリクエストのレビューコメントに返信するCLIツール。

Gitea APIにはレビューコメントへの返信機能がないため、
Web UIの内部エンドポイントを使用して返信を行う。

使い方:
    uv run reply_to_review_comment.py \\
        --url http://localhost:3000 \\
        --user claude --password <PASSWORD> \\
        --repo vibes/vibe-sandbox \\
        --pr 1 --comment-id 2 \\
        --message "返信テキスト"
"""

import argparse
import re
import sys

import requests


def get_csrf_token(session: requests.Session, url: str) -> str:
    """GiteaのWebページからCSRFトークンを取得する。"""
    resp = session.get(url)
    resp.raise_for_status()
    match = re.search(r"csrfToken:\s*'([^']+)'", resp.text)
    if not match:
        print("CSRFトークンの取得に失敗しました", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def login(
    session: requests.Session, base_url: str, username: str, password: str
) -> None:
    """WebフォームからGiteaにログインしてセッションCookieを取得する。"""
    login_url = f"{base_url}/user/login"
    csrf_token = get_csrf_token(session, login_url)
    resp = session.post(
        login_url,
        data={"_csrf": csrf_token, "user_name": username, "password": password},
        allow_redirects=False,
    )
    if resp.status_code not in (302, 303):
        print("ログインに失敗しました", file=sys.stderr)
        sys.exit(1)


def get_comment_info(
    session: requests.Session,
    api_url: str,
    owner_repo: str,
    pr_index: int,
    comment_id: int,
) -> dict | None:
    """APIからレビューコメントの情報を取得する。"""
    reviews_url = f"{api_url}/repos/{owner_repo}/pulls/{pr_index}/reviews"
    resp = session.get(reviews_url)
    resp.raise_for_status()

    for review in resp.json():
        comments_url = f"{reviews_url}/{review['id']}/comments"
        resp = session.get(comments_url)
        resp.raise_for_status()
        for comment in resp.json():
            if comment["id"] == comment_id:
                return comment
    return None


def reply_to_comment(
    session: requests.Session,
    base_url: str,
    owner_repo: str,
    pr_index: int,
    comment: dict,
    message: str,
) -> None:
    """レビューコメントに返信する。"""
    pr_url = f"{base_url}/{owner_repo}/pulls/{pr_index}"
    csrf_token = get_csrf_token(session, pr_url)

    # Web UIの内部エンドポイントに返信をPOST
    # replyにはレビューID（pull_request_review_id）を指定する
    post_url = f"{pr_url}/files/reviews/comments"
    data = {
        "_csrf": csrf_token,
        "origin": "timeline",
        "latest_commit_id": "",
        "side": "proposed",
        "line": str(comment["position"]),
        "path": comment["path"],
        "diff_start_cid": "",
        "diff_end_cid": "",
        "diff_base_cid": "",
        "content": message,
        "reply": str(comment["pull_request_review_id"]),
        "single_review": "true",
    }
    resp = session.post(post_url, data=data)
    resp.raise_for_status()
    print(f"返信しました: {pr_url}#issuecomment-{comment['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Giteaのレビューコメントに返信する",
    )
    parser.add_argument(
        "--url", required=True, help="GiteaのベースURL (例: http://localhost:3000)"
    )
    parser.add_argument("--user", required=True, help="ユーザー名")
    parser.add_argument("--password", required=True, help="パスワード")
    parser.add_argument("--repo", required=True, help="リポジトリ (例: owner/repo)")
    parser.add_argument("--pr", required=True, type=int, help="PR番号")
    parser.add_argument(
        "--comment-id", required=True, type=int, help="返信先コメントID"
    )
    parser.add_argument("--message", required=True, help="返信メッセージ")
    args = parser.parse_args()

    session = requests.Session()
    login(session, args.url, args.user, args.password)

    # 返信先コメントの情報をAPIから取得
    api_url = f"{args.url}/api/v1"
    comment = get_comment_info(session, api_url, args.repo, args.pr, args.comment_id)
    if comment is None:
        print(f"コメントID {args.comment_id} が見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"返信先: {comment['user']['login']} のコメント")
    print(f"  ファイル: {comment['path']} (行: {comment['position']})")
    print(f"  内容: {comment['body'][:80]}")

    reply_to_comment(session, args.url, args.repo, args.pr, comment, args.message)


if __name__ == "__main__":
    main()
