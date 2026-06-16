# Publish to GitHub

Use this checklist to publish the project for public usage.

## 1) Create a GitHub Repository

Create an empty repository in GitHub UI, for example:

- Repository name: `autocad-interior-mcp`
- Visibility: Public
- Do not initialize with README/LICENSE/gitignore (already present here)

## 2) Initialize and Commit Locally

```powershell
cd C:\path\to\autocad-interior-mcp
git init
git branch -M main
git add .
git commit -m "feat: initial AutoCAD interior MCP release"
```

If needed:

```powershell
git config user.name "Your Name"
git config user.email "you@example.com"
```

## 3) Connect Remote and Push

HTTPS:

```powershell
git remote add origin https://github.com/<owner>/autocad-interior-mcp.git
git push -u origin main
```

SSH:

```powershell
git remote add origin git@github.com:<owner>/autocad-interior-mcp.git
git push -u origin main
```

## 4) Recommended Repository Settings

- Add topics: `autocad`, `mcp`, `interior-design`, `python`, `cad-automation`
- Enable Issues and Discussions
- Add a short project description in repository settings
- Create first release tag: `v0.1.0`

## 5) Optional Next Steps

- Add CI workflow for static checks
- Add screenshots/gifs of generated CAD layouts
- Add office block library mapping examples
