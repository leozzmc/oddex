#!/bin/sh
# Decompile functions of the code-only ELF with Ghidra headless, without REA's bridge.
# Fallback for when REA fails with GhidraLaunchError (see docs/research/build.md).
# usage: tools/oddex/ghidra_decompile.sh FUNCTION [FUNCTION ...]
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
GHIDRA="${GHIDRA_INSTALL_DIR:-$HOME/rea-tools/ghidra_12.1.4_PUBLIC}"
: "${JAVA_HOME:=$(/usr/libexec/java_home -v 21 2>/dev/null || ls -d /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home 2>/dev/null || true)}"
export JAVA_HOME
ELF=$("$ROOT/tools/oddex/rea_code_elf.sh")
PROJ=$(mktemp -d)
trap 'rm -rf "$PROJ"' EXIT
"$GHIDRA/support/analyzeHeadless" "$PROJ" oddex -import "$ELF" -noanalysis \
	-scriptPath "$ROOT/tools/oddex/ghidra" -postScript DecompileFns.java "$@" 2>&1 |
	awk '/^INFO  DecompileFns.java> =====/ { on = 1; sub(/^INFO  DecompileFns.java> /, ""); sub(/ \(GhidraScript\)[[:space:]]*$/, ""); print; next }
	     on && /^ \(GhidraScript\)/ { on = 0; print ""; next }
	     on { print }'
