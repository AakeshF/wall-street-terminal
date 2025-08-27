# Private Branch Management Guide

## Overview

You now have two branches:
- `main` - Public branch that syncs with GitHub
- `private` - Local-only branch with your API keys

## Security Setup Complete ✅

The `private` branch is configured to:
- Never push to GitHub (remote set to local)
- Store your personal `.env` file safely
- Merge updates from `main` when needed

## Workflow

### 1. Daily Development (Public Features)
```bash
# Always develop on main
git checkout main
# Make changes, test, commit
git add .
git commit -m "feat: Add new feature"
git push origin main
```

### 2. Using Your Private Keys
```bash
# Switch to private branch
git checkout private

# Merge latest from main
git merge main

# Run with your premium API keys
python simple_terminal_v2.py
```

### 3. Adding Your API Keys (One-Time Setup)

On the `private` branch ONLY:

1. Edit `.gitignore` temporarily:
```bash
# Comment out the .env line
# .env
```

2. Add your real `.env` file:
```bash
git add .env
git commit -m "private: Add my API keys"
```

3. Restore `.gitignore`:
```bash
git checkout main -- .gitignore
git commit -m "private: Restore .gitignore"
```

## Important Commands

### Check Current Branch
```bash
git branch --show-current
```

### View Branch Configuration
```bash
git config --get branch.private.remote  # Should show "."
git config --get branch.private.merge   # Should show "refs/heads/private"
```

### Update Private Branch with Main
```bash
git checkout private
git merge main
```

### Never Do This!
```bash
# NEVER push the private branch
git push origin private  # DON'T DO THIS!
```

## Best Practices

1. **Always develop new features on `main`**
   - This ensures all features go to GitHub
   - Keep the public repository updated

2. **Only use `private` for running the app**
   - Switch to private when you need your keys
   - Merge from main to get updates

3. **Double-check before pushing**
   - `git branch` - Verify you're on main
   - `git status` - Check what's staged
   - Never push from private branch

## Emergency: If You Accidentally Commit Keys to Main

```bash
# DON'T PUSH! If you haven't pushed yet:
git reset --soft HEAD~1
git checkout private
git add .env
git commit -m "private: Move keys to private branch"
git checkout main
```

## Directory Structure

```
stock_terminal/
├── main branch (public)
│   ├── .env.example
│   ├── No real keys
│   └── Pushed to GitHub
│
└── private branch (local only)
    ├── .env (with real keys)
    ├── Never pushed
    └── Merges from main
```

Stay secure, trade smart! 🚀