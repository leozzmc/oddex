#!/bin/sh
# Writes a code-only copy of game/pokeemerald.elf for REA/Ghidra (see docs/research/build.md).
# Optional speed-up: Ghidra analyzes this in ~2 min vs ~4 min for the full ELF, but data refs stay raw addresses.
set -e
. "$(dirname "$0")/../env.sh"
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT="${1:-$ROOT/game/build/pokeemerald.code.elf}"
mkdir -p "$(dirname "$OUT")"
arm-none-eabi-objcopy \
	-R .rodata -R .rodata.compound_string -R script_data \
	-R .ewram -R .iwram -R .debug_frame -R .debug_line_str \
	"$ROOT/game/pokeemerald.elf" "$OUT" 2>/dev/null
echo "$OUT"
