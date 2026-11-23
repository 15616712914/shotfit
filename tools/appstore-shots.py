#!/usr/bin/env python3
"""App Store Connect 用スクリーンショット変換ツール.

どの iPhone で撮ったスクショでも、App Store が受け付ける寸法に揃える。
縦横比は保ったまま（高さ基準で拡大 → 幅を中央で切り落とす）。余りは端の色で埋める。
出力は PNG / RGB / アルファ無し（アルファ付きは審査で弾かれる）。

使い方:
    Tools/appstore-shots.py ~/Downloads/*.png
    Tools/appstore-shots.py IMG1 IMG2 -o ~/Desktop/AppStore
    Tools/appstore-shots.py IMG --sizes 6.9          # 6.9 インチだけ
    Tools/appstore-shots.py IMG --sizes 6.9,6.5      # 6.5 も欲しいとき

出力:
    <out>/<元ファイル名>-1320x2868.png
    <out>/<元ファイル名>-1242x2688.png
"""

import argparse
import os
import sys

from PIL import Image

# App Store Connect が受け付ける iPhone のスクリーンショット寸法
SIZES = {
    "6.9": (1320, 2868),
    "6.5": (1242, 2688),
}


def convert(path: str, target: tuple[int, int]) -> Image.Image:
    """縦横比を保ったまま target の寸法に合わせる。"""
    tw, th = target
    src = Image.open(path)
    if src.mode in ("RGBA", "LA", "P"):
        src = src.convert("RGBA")
        bg = Image.new("RGB", src.size, src.getpixel((0, 0))[:3])
        bg.paste(src, mask=src.split()[-1])
        src = bg
    else:
        src = src.convert("RGB")

    w, h = src.size

    # 端末違いで切り落としすぎる（iPad など）なら、勝手に切らずに知らせる
    if abs((w / h) - (tw / th)) / (tw / th) > 0.10:
        raise ValueError(
            f"縦横比が合わない（{w}x{h}）。iPhone のスクリーンショットを使ってください"
        )

    # まず高さを合わせる
    scale = th / h
    scaled_w = round(w * scale)
    if scaled_w >= tw:
        resized = src.resize((scaled_w, th), Image.LANCZOS)
        left = (scaled_w - tw) // 2
        return resized.crop((left, 0, left + tw, th))

    # 幅が足りない（想定より縦長）→ 幅を合わせて上下を端の色で埋める
    scale = tw / w
    scaled_h = round(h * scale)
    resized = src.resize((tw, scaled_h), Image.LANCZOS)
    canvas = Image.new("RGB", (tw, th), src.getpixel((0, 0)))
    canvas.paste(resized, (0, (th - scaled_h) // 2))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser(description="App Store 用スクリーンショット変換")
    ap.add_argument("images", nargs="+", help="変換する画像（複数可）")
    ap.add_argument("-o", "--out", default=None, help="出力フォルダ（既定: 各画像と同じ場所）")
    ap.add_argument("--sizes", default="6.9", help="出力する寸法（既定: 6.9。6.5 も指定可）")
    args = ap.parse_args()

    wanted = [s.strip() for s in args.sizes.split(",") if s.strip()]
    unknown = [s for s in wanted if s not in SIZES]
    if unknown:
        print(f"未対応の寸法: {unknown}（使えるのは {list(SIZES)}）", file=sys.stderr)
        return 2

    failed = 0
    for path in args.images:
        if not os.path.isfile(path):
            print(f"見つからない: {path}", file=sys.stderr)
            failed += 1
            continue
        out_dir = args.out or os.path.dirname(os.path.abspath(path))
        os.makedirs(out_dir, exist_ok=True)
        stem, _ = os.path.splitext(os.path.basename(path))
        for key in wanted:
            tw, th = SIZES[key]
            dst = os.path.join(out_dir, f"{stem}-{tw}x{th}.png")
            try:
                convert(path, (tw, th)).save(dst, optimize=True)
            except ValueError as err:
                print(f"スキップ {os.path.basename(path)} → {tw}x{th}: {err}", file=sys.stderr)
                failed += 1
                continue
            print(f"{os.path.basename(dst)}  {tw}x{th}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
