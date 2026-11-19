# Source from any worktree: . tools/env.sh
export ODDEX_TOOLCHAIN="$HOME/oddex-toolchain"
export DEVELOPER_DIR=/Library/Developer/CommandLineTools
export PATH="$ODDEX_TOOLCHAIN/arm-none-eabi/bin:$PATH"
export TOOLCHAIN="$ODDEX_TOOLCHAIN/arm-none-eabi"
export ODDEX_RUN="$ODDEX_TOOLCHAIN/bin/oddex-run"
command -v arm-none-eabi-cpp >/dev/null || echo "oddex env: arm-none-eabi-cpp not found under $TOOLCHAIN/bin" >&2
export BLENDER="$ODDEX_TOOLCHAIN/Blender.app/Contents/MacOS/Blender"
