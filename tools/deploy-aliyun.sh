#!/bin/bash
# Shotfit を Alibaba Cloud ECS に置く。
#
#   ./deploy-aliyun.sh root@1.2.3.4              # 既存サイトの /shotfit/ に置く
#   ./deploy-aliyun.sh root@1.2.3.4 /var/www/shotfit   # 指定ディレクトリに置く
#
# 既存の Nginx サイトがある場合は、その root 配下のサブディレクトリに置くのが一番安全。
# 例: root が /var/www/aimagfram なら /var/www/aimagfram/shotfit → https://example.com/shotfit/
set -euo pipefail

HOST="${1:-}"
TARGET="${2:-}"
if [ -z "$HOST" ]; then
  echo "使い方: $0 user@host [リモートのディレクトリ]" >&2
  exit 1
fi

HERE="$(cd "$(dirname "$0")/.." && pwd)"   # shotfit のルート
STAMP="$(date +%Y%m%d-%H%M%S)"

if [ -z "$TARGET" ]; then
  # 既存サイトの root を探して、その下の shotfit/ に置く
  echo "→ Nginx の root を調べています…"
  TARGET="$(
    ssh -o BatchMode=yes "$HOST" '
      conf=$(grep -rhoE "root[[:space:]]+[^;]+;" /etc/nginx/conf.d/*.conf /etc/nginx/sites-enabled/* 2>/dev/null | head -1 | awk "{print \$2}" | tr -d ";")
      [ -n "$conf" ] && echo "${conf%/}/shotfit" || echo "/var/www/shotfit"
    '
  )"
fi

echo "→ 配置先: $HOST:$TARGET"

# 1) 転送（README/tools は不要なので index.html だけ送る）
ssh "$HOST" "mkdir -p '$TARGET'"
scp "$HERE/index.html" "$HOST:$TARGET/index.html"

# 2) 権限と（必要なら）Nginx の再読み込み
ssh "$HOST" "
  set -e
  chmod 755 '$TARGET' && chmod 644 '$TARGET/index.html'
  command -v nginx >/dev/null 2>&1 && nginx -t >/dev/null 2>&1 && (systemctl reload nginx 2>/dev/null || nginx -s reload) || true
"

echo "✅ 完了"
echo "   URL: http://$(echo "$HOST" | sed 's/.*@//')${TARGET#/var/www}  （ドメイン設定済みならそのドメインで）"
echo "   確認: curl -I http://$(echo "$HOST" | sed 's/.*@//')/shotfit/"
