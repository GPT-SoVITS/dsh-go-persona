#!/usr/bin/env python3
"""让伙伴模式不再因为引擎返回 broken 而静默放弃带工具的预设。

上游 companion_state.dart 的 _selectPreset 要求 p.broken == null，
引擎那边 broken 有值时（预设本身可用）就永久退回无工具的人设模式。
这里去掉 broken 条件，只要预设存在就选中。
"""
import re
import sys
from pathlib import Path

TARGET = Path("app/lib/companion/companion_state.dart")

OLD = "if (!presets.any((p) => p.id == companionPresetId && p.broken == null)) return false;"
NEW = ("// 本地补丁：不因 broken 放弃。引擎侧预设可用时 broken 仍可能有值，\n"
       "      // 上游在这里直接 return false，导致工具集永远不生效。\n"
       "      if (!presets.any((p) => p.id == companionPresetId)) return false;")


def main() -> int:
    if not TARGET.exists():
        print(f"找不到 {TARGET}", file=sys.stderr)
        return 1
    src = TARGET.read_text(encoding="utf-8")
    if NEW.splitlines()[-1].strip() in src:
        print("已经打过补丁，跳过")
        return 0
    if OLD not in src:
        # 上游可能改了写法：退化为正则，匹配任何带 broken == null 的 any(...) 判定
        pattern = re.compile(r"if \(!presets\.any\(\(p\) => p\.id == companionPresetId[^)]*\)\) return false;")
        if not pattern.search(src):
            print("没找到目标语句，上游可能已改结构；请人工检查", file=sys.stderr)
            return 1
        src2 = pattern.sub(
            "// 本地补丁：不因 broken 放弃\n      if (!presets.any((p) => p.id == companionPresetId)) return false;",
            src, count=1)
    else:
        src2 = src.replace(OLD, NEW, 1)
    TARGET.write_text(src2, encoding="utf-8")
    print("补丁已应用")
    for line in src2.splitlines():
        if "companionPresetId" in line:
            print("  " + line.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
