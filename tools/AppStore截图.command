#!/bin/bash
# App Store 用スクリーンショット変換（ダブルクリックで使う）
#
# 1. このファイルをダブルクリック
# 2. 変換したいスクリーンショットを選ぶ（複数選択可）
# 3. デスクトップの「AppStore-Screenshots」フォルダに 6.9 / 6.5 インチの PNG が出る
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$HOME/Desktop/AppStore-Screenshots"

FILES=$(/usr/bin/osascript <<'APPLESCRIPT'
set theFiles to choose file with prompt "App Store 用に変換するスクリーンショットを選んでください（複数可）" with multiple selections allowed
set theList to ""
repeat with f in theFiles
	set theList to theList & POSIX path of f & linefeed
end repeat
return theList
APPLESCRIPT
)

if [ -z "$FILES" ]; then
  echo "キャンセルしました。"
  read -r -p "Enter で閉じます" _
  exit 0
fi

mkdir -p "$OUT"
# 改行区切りを配列にして渡す
while IFS= read -r line; do
  [ -n "$line" ] && ARGS+=("$line")
done <<< "$FILES"

/usr/bin/python3 "$DIR/appstore-shots.py" "${ARGS[@]}" -o "$OUT"

echo ""
echo "出力先: $OUT"
open "$OUT"
read -r -p "Enter で閉じます" _
