#!/bin/sh
# Builds $ODDEX_TOOLCHAIN/bin/oddex-run against the static headless libmgba (see docs/research/build.md).
set -e
. "$(dirname "$0")/../env.sh"
M="$ODDEX_TOOLCHAIN/src/mgba"
mkdir -p "$ODDEX_TOOLCHAIN/bin"
clang -O2 -o "$ODDEX_RUN" "$(dirname "$0")/runner.c" \
	-I"$M/include" -I"$M/build-headless/include" \
	"$M/build-headless/libmgba.a" \
	$(pkg-config --cflags --libs libpng) -lz -framework CoreFoundation -framework OpenGL
echo "built $ODDEX_RUN"
