# Repository Rules & Operational Guidelines

## Version Control & Git Commit Invariant
- **Automatic Commits for Changes**: After creating, updating, or deleting code, documentation, or configuration files for any user request, automatically inspect repository status (`git status`), stage the modified files (`git add <files>`), and create a clean git commit.
- **Descriptive Conventional Messages**: Write concise, conventional commit messages reflecting the exact work done (e.g., `feat: ...`, `docs: ...`, `fix: ...`, `refactor: ...`).
- **Remote Synchronization**: Push commits to the upstream branch on GitHub (`origin/main`) to keep GitHub synchronized.
- **Hygiene & Security**: Never commit secret credentials, tokens (`.env`), or temporary scratch files. Always adhere to `.gitignore`.
