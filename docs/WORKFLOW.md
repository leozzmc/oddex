# oddex 開發流程

## 技術基礎
- `game/`：[pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) `expansion/1.17.2`（commit `79dd436920845ebc145577649de624f65298c209`），直接匯入原始碼（非 submodule）。
- 不需要、也不使用任何 baserom。所有素材由原始碼編譯產生。

## 分支
- `main`：保護，不直接修改。
- `develop`：整合分支，只由 Tech Lead（David）合併。
- `feat/<area>`：各 Agent 的工作分支，在獨立 worktree 中開發：
  ```bash
  git -C /Users/kuangsin/oddex worktree add /Users/kuangsin/oddex-wt/<name> -b feat/<area> develop
  ```

| Agent | 範圍 | 分支 |
|---|---|---|
| David | 工具鏈、編譯、模擬器測試、整合 | `develop` |
| Mark | 角色資料、圖像、戰鬥 | `feat/species` |
| Sonia | 地圖、NPC、事件、劇情腳本 | `feat/events` |

## 研究筆記
寫在 `docs/research/<topic>.md`，需包含：檔案位置、格式限制、可重現步驟、踩到的坑。

## 編譯
見 `docs/research/build.md`。
