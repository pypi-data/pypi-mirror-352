# Interactive UI Guide

Flort's interactive user interface provides a powerful visual way to explore and select files for processing. This guide covers all UI features and navigation.

## 🚀 Getting Started

### Launch the UI

```bash
# Basic UI launch
flort --ui

# Start with pre-selected filters
flort --ui --extensions py,js

# Start in specific directory
flort /path/to/project --ui

# Combine with other options
flort --ui --ignore-dirs "venv,node_modules"
```

### System Requirements

=== "Linux/macOS"

    Usually works out of the box:
    ```bash
    # Test curses availability
    python -c "import curses; print('✅ UI supported')"
    ```

=== "Windows"

    Requires additional package:
    ```bash
    # Install curses support
    pip install windows-curses
    
    # Or install Flort with UI
    pip install flort[ui]
    ```

## 🎨 Interface Overview

When you launch the UI, you'll see:

```
📁 /home/user/project                           [Header - Current Path]
Filter: .py, .js, .md                          [Active File Filters]

📂 src/                                         [Directory Entries]
  [✓] 📄 main.py
  [✓] 📄 utils.py  
  [ ] 📄 config.json
📂 tests/
  [✗] 📄 test_main.py
  [✗] 📄 test_utils.py
📄 README.md [✓]                               [File Entries]
📄 setup.py [✓]

Selected: 4 | Ignored: 2 | Types: 3            [Status Bar]
🎯 Navigation: ↑/↓ SPACE:Select TAB:Filter q:Done h:Help
```

### Interface Elements

- **📁 Header**: Current directory path
- **🎯 Filter Line**: Active file type filters
- **📂 Directories**: Folders you can navigate into
- **📄 Files**: Files matching current filters
- **Selection States**:
  - `[✓]` - Selected for processing
  - `[ ]` - Not selected
  - `[✗]` - Explicitly ignored
- **Status Bar**: Selection counts and help

## ⌨️ Keyboard Navigation

### Basic Movement

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate up/down through items |
| `PgUp` / `PgDn` | Page up/down (10 items) |
| `Home` / `End` | Go to first/last item |
| `←` | Go up one directory level |
| `→` / `Enter` | Enter selected directory |

### File Selection

| Key | Action |
|-----|--------|
| `Space` | Toggle selection state (cycles: unselected → selected → ignored → unselected) |
| `Enter` | For files: toggle selection; for directories: enter |
| `i` | Toggle ignore status directly |

### File Type Management

| Key | Action |
|-----|--------|
| `Tab` / `f` | Open file type filter manager |
| `r` | Reset to auto-discovered file types |

### Bulk Operations

| Key | Action |
|-----|--------|
| `a` | Select all visible files |
| `c` | Clear all selections |

### Views and Information

| Key | Action |
|-----|--------|
| `v` | View current selections and ignored items |
| `h` | Toggle help display |

### Exit and Completion

| Key | Action |
|-----|--------|
| `q` | Finish selection and proceed with processing |
| `Esc` | Cancel and exit without processing |

## 🖱️ Mouse Support

When available, the UI supports mouse interaction:

### Mouse Actions

| Action | Result |
|--------|--------|
| **Left click on `[X]`** | Toggle selection state |
| **Left click on filename** | For files: toggle selection; for directories: navigate |
| **Right click** | Toggle ignore status |
| **Scroll wheel** | Navigate up/down |

### Click Targets

```
[✓] 📄 filename.py
 ^   ^   ^
 |   |   └─ Click to select/navigate
 |   └───── Icon (no action)
 └───────── Click to toggle state
```

## 🎯 File Type Manager

Press `Tab` or `f` to open the file type manager:

```
🎯 File Type Manager
Discovered types: .py, .js, .md, .txt, .json, .yml, .css, .html
Current filter: .py, .js

Enter extensions (comma-separated, no dots) or '*' for all:
Current: py,js
```

### Filter Options

| Input | Result |
|-------|--------|
| `py,js,md` | Include only Python, JavaScript, and Markdown |
| `*` | Include all file types |
| `py` | Include only Python files |
| *(empty)* | No type filtering (same as `*`) |

!!! tip "Extension Format"
    Enter extensions without dots: `py,js,md` not `.py,.js,.md`

## 📋 Selection States

### State Cycle

Files cycle through three states when you press `Space`:

1. **Unselected** `[ ]` - File will not be processed
2. **Selected** `[✓]` - File will be included in output
3. **Ignored** `[✗]` - File is explicitly excluded

### Directory Selection

When you select a directory:
- All matching files inside are selected
- Subdirectories are recursively processed
- Selection state shows on directory entry

### Smart Selection

The UI provides intelligent defaults:

- **Auto-discovery**: Finds all file types in the project
- **Common types**: Automatically selects typical code files (`.py`, `.js`, `.md`, etc.)
- **Exclusion patterns**: Automatically ignores test files and cache directories

## 🔍 Advanced Features

### Selection Viewer

Press `v` to view all current selections:

```
📋 Selected & Ignored Files/Directories
✓: Selected  ✗: Ignored

✓ /project/main.py
✓ /project/src/utils.py
✓ /project/README.md
✗ /project/tests/test_main.py
✗ /project/__pycache__/

Use ↑/↓/PgUp/PgDn/Home/End to scroll, 'q' to exit
```

### Help System

Press `h` to toggle the help overlay:

```
🎯 NAVIGATION:
  ↑/↓/PgUp/PgDn: Navigate    SPACE: Toggle selection
  ←/→/Enter: Directories    TAB: File type manager
  i: Ignore item/dir        v: View selections
🖱️ MOUSE: Click to select, scroll to navigate
📝 FILTERING:
  f: Edit file types        a: Select all visible
  c: Clear all selections   r: Reset to discovered types
⚡ ACTIONS:
  q: Done with selection    ESC: Cancel
  h: Toggle this help
```

## 🎮 Usage Patterns

### Exploring New Projects

```bash
# Start UI to explore unknown codebase
flort /path/to/unknown/project --ui
```

1. Use `Tab` to see discovered file types
2. Navigate directories with `→` and `←`
3. Use `v` to review selections
4. Press `q` when satisfied

### Selective File Processing

```bash
# Start with broad filters, then refine
flort . --ui --extensions py,js,md
```

1. Review auto-selected files
2. Use `Space` to toggle specific files
3. Use `i` to ignore entire directories
4. Use `Tab` to adjust file types

### Quick Code Review

```bash
# Use UI to select changed files
flort . --ui
```

1. Clear all selections with `c`
2. Navigate to specific files
3. Select only files you want to review
4. Press `q` to process

## 🛠️ Troubleshooting

### UI Won't Start

```bash
# Check curses support
python -c "
try:
    import curses
    print('✅ Curses available')
except ImportError as e:
    print(f'❌ Curses not available: {e}')
"
```

**Solutions:**

=== "Windows"

    ```bash
    # Install Windows curses support
    pip install windows-curses
    
    # Or reinstall with UI support
    pip install flort[ui]
    ```

=== "Linux"

    ```bash
    # Install development packages
    sudo apt install python3-dev libncurses5-dev
    
    # Reinstall Python if needed
    sudo apt install python3-full
    ```

=== "macOS"

    ```bash
    # Usually works, but if not:
    brew install python3
    
    # Or try with system Python
    python3 -m pip install flort
    ```

### Terminal Issues

```bash
# Terminal too small
# Resize terminal to at least 80x24

# Colors not working
# Check terminal color support
echo $TERM

# Mouse not working
# Try different terminal or skip mouse usage
```

### Performance Issues

```bash
# Large directories slow to load
# Use --ignore-dirs to skip large folders
flort . --ui --ignore-dirs "node_modules,venv,.git"

# Too many files
# Start with specific file types
flort . --ui --extensions py
```

## 🎯 Pro Tips

### Efficient Workflows

!!! tip "Discovery Workflow"
    1. Start with `--ui` on unknown projects
    2. Use `Tab` to see all discovered file types
    3. Navigate directories to understand structure
    4. Use `v` to review final selections
    5. Press `q` to process

!!! tip "Refinement Workflow"
    1. Start with broad filters: `flort . --ui --extensions py,js,md`
    2. Use `a` to select all, then `Space` to deselect unwanted files
    3. Use `i` to ignore test directories
    4. Use `Tab` to add/remove file types

### Keyboard Shortcuts

```bash
# Quick selection patterns
c → a → i (on test dirs) → q    # Clear, select all, ignore tests, done
Tab → py,md → Enter → q         # Set types, select, done
v → review → q                  # View selections, review, done
```

### Integration with CLI

```bash
# Start UI with pre-configured options
flort . --ui \
  --extensions py,js,md \
  --ignore-dirs "venv,node_modules" \
  --exclude-patterns "*test*"
```

The UI inherits and can modify these settings.

## 🔄 Fallback Mode

If the UI fails to start, Flort automatically falls back to a simple text-based selector:

```
🔧 Flort Simple File Selector
========================================
Interactive file selection (text-based fallback)

📋 Found 5 file types: .py, .js, .md, .txt, .json

📝 Options:
  1. Add file extensions
  2. Remove file extensions  
  3. Add specific files
  4. Preview selected files
  5. Use current selection
  6. Cancel

❓ Choose option (1-6):
```

This provides basic functionality when the full UI isn't available.

## 🎊 Getting the Most from the UI

The interactive UI is most powerful when:

- **Exploring unfamiliar codebases** - Visual navigation beats command-line guessing
- **Selective processing** - Need to include/exclude specific files
- **Complex filtering** - Multiple criteria that are easier to see than specify
- **Learning projects** - Understanding structure before processing

Try different approaches and find what works best for your workflow!

---

**Ready to master the visual interface? Launch `flort --ui` and start exploring! 🎨**