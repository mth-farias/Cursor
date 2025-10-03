# Duck Dev Area (.duck/dev/)

Purpose: a safe workspace for development-only artifacts (notes, scratch files, working prompts). This folder is versioned during active development and can be ignored/removed later when stable.

## Recommended use:
- Add temporary notes in `notes/`
- Put scratch/test snippets in `scratch/`
- Use `duck_develop_prompt.md` to pick up work in any agent/chat

## Structure:
```
.duck/dev/
├── README.md                 # This file
├── duck_develop_prompt.md    # Reusable prompt for any agent
├── notes/                    # Development notes and ideas
└── scratch/                  # Temporary files and tests
```

## When development is done:
- This folder can be ignored via `.gitignore` 
- Or completely removed from the repository
- Only production files in `.duck/` will remain
