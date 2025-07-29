import os
import curses
import curses.textpad
from pathlib import Path
from collections import defaultdict

def is_accessible(path):
    try:
        path.stat()
        return True
    except (PermissionError, OSError):
        return False

def discover_file_types(path):
    """Discover all file types in the given path."""
    extensions = set()
    try:
        for file_path in Path(path).rglob("*"):
            if file_path.is_file() and is_accessible(file_path):
                ext = file_path.suffix.lower()
                if ext:
                    extensions.add(ext)
    except (PermissionError, OSError):
        pass
    return sorted(extensions)

def should_show_file(item, file_types, selection):
    # Always show directories
    if item.is_dir():
        return True
    # Show file if it's in selection
    if selection and str(item) in selection:
        return True
    # Show all files if "*" is in filters or no filters
    if not file_types or any(ft.strip() == "*" for ft in file_types):
        return True
    # Show files matching extensions
    return item.suffix in file_types

def get_directory_contents(path, file_types, selection):
    try:
        items = sorted(
            [item for item in Path(path).iterdir()],
            key=lambda x: (x.is_file(), x.name.lower())
        )
        return [(item, is_accessible(item)) for item in items 
                if should_show_file(item, file_types, selection)]
    except PermissionError:
        return []

def mark_subitems(selection, ignored, base_path, state, file_types):
    for item in Path(base_path).rglob('*'):
        if not is_accessible(item):
            continue
        path = str(item)
        if state and path in ignored:
            ignored.pop(path)
        
        if state:
            if item.is_dir() or item.suffix in file_types or path in selection:
                selection[path] = True
        else:
            selection.pop(path, None)

def mark_ignored(ignored, selection, base_path):
    for item in Path(base_path).rglob('*'):
        if not is_accessible(item):
            continue
        path = str(item)
        if path in selection:
            selection.pop(path)
        ignored[path] = True
    ignored[str(base_path)] = True

def curses_file_selector(stdscr, start_path=".", preselected_filters=None, included_files=None, ignored_dirs=None, included_dirs=None):
    # Initialize curses
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Inaccessible
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Included
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Header
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Directory
    
    # Enable mouse support
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        mouse_enabled = True
    except:
        mouse_enabled = False
    
    current_path = Path(start_path).resolve()
    selection = {}
    ignored = {}
    
    # Start with discovery mode - find all file types
    discovered_types = discover_file_types(current_path)
    
    # Initialize file types - start with discovered types if no preselected
    if preselected_filters:
        file_types = set(preselected_filters)
    else:
        # Auto-discover common code file types
        common_code_types = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.css', '.html', '.php', '.rb', '.go', '.rs', '.swift', '.kt'}
        auto_selected = [ext for ext in discovered_types if ext in common_code_types]
        file_types = set(auto_selected) if auto_selected else set(discovered_types[:10])  # Limit to first 10 if no common types
    
    # Add included files
    if included_files:
        for file_path in included_files:
            path = Path(file_path).resolve()
            if is_accessible(path):
                selection[str(path)] = True

    # Add ignored directories
    if ignored_dirs:
        for dir_path in ignored_dirs:
            path = Path(dir_path).resolve()
            if is_accessible(path):
                mark_ignored(ignored, selection, path)

    # Auto-select common directories and files
    if start_path == "." and not (included_files or included_dirs):
        for item in current_path.iterdir():
            if not is_accessible(item):
                continue
            if item.is_dir() or (file_types and item.suffix in file_types):
                path = str(item.resolve())
                selection[path] = True
                if item.is_dir():
                    mark_subitems(selection, ignored, path, True, file_types)

    stack = [current_path]
    idx = 0
    top_line = 0
    show_help = False
    filter_mode = False

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Header
        header_color = curses.color_pair(5) | curses.A_BOLD
        path_str = str(current_path)
        if len(path_str) >= width - 10:
            path_str = "..." + path_str[-(width-13):]
        stdscr.addstr(0, 0, f"📁 {path_str}", header_color)
        
        # File type filter display
        if file_types:
            types_str = f"Filter: {', '.join(sorted(file_types))}"
            if len(types_str) > width - 2:
                types_str = types_str[:width-5] + "..."
            stdscr.addstr(1, 0, types_str, curses.color_pair(4))
        else:
            stdscr.addstr(1, 0, "Filter: All files", curses.color_pair(4))
        
        # Instructions
        if show_help:
            help_lines = [
                "🎯 NAVIGATION:",
                "  ↑/↓/PgUp/PgDn: Navigate    SPACE: Toggle selection",
                "  ←/→/Enter: Directories    TAB: File type manager",
                "  i: Ignore item/dir        v: View selections",
                "🖱️  MOUSE: Click to select, scroll to navigate",
                "📝 FILTERING:",
                "  f: Edit file types        a: Select all visible",
                "  c: Clear all selections   r: Reset to discovered types",
                "⚡ ACTIONS:",
                "  q: Done with selection    ESC: Cancel",
                "  h: Toggle this help"
            ]
            for i, line in enumerate(help_lines):
                if i + 2 < height - 4:
                    stdscr.addstr(i + 2, 0, line[:width-1], curses.color_pair(2))
            help_end = len(help_lines) + 2
        else:
            stdscr.addstr(2, 0, "🎯 Navigation: ↑/↓ SPACE:Select TAB:Filter q:Done h:Help", curses.color_pair(2))
            if mouse_enabled:
                stdscr.addstr(3, 0, "🖱️  Mouse: Click items, scroll to navigate", curses.color_pair(2))
            help_end = 4
        
        # Get directory contents
        items = get_directory_contents(current_path, file_types, selection)
        display_items = ["[📁 ../] (Up one level)"] + [
            (f"🚫 {item.name}/" if not accessible else 
             f"[{'✓' if selection.get(str(item), False) else '✗' if ignored.get(str(item), False) else ' '}] 📁 {item.name}/") if item.is_dir() else
            (f"🚫 {item.name}" if not accessible else 
             f"[{'✓' if selection.get(str(item), False) else '✗' if ignored.get(str(item), False) else ' '}] 📄 {item.name}")
            for item, accessible in items
        ]
        
        accessible_items = [True] + [acc for _, acc in items]
        
        # Ensure idx is valid
        if idx >= len(display_items):
            idx = max(len(display_items) - 1, 0)

        # Scroll handling
        if idx < top_line:
            top_line = idx
        elif idx >= top_line + height - help_end - 1:
            top_line = idx - (height - help_end - 2)

        # Display items
        for i, line in enumerate(display_items[top_line:top_line + height - help_end - 1]):
            pos = i + top_line
            if pos >= len(display_items):
                break
                
            y_pos = i + help_end
            truncated_line = (line[:width - 1] + "…") if len(line) >= width else line
            
            # Determine color
            if pos >= len(accessible_items):
                continue
                
            if pos == idx:
                attr = curses.color_pair(1) | curses.A_BOLD  # Selected line
            elif not accessible_items[pos]:
                attr = curses.color_pair(3) | curses.A_DIM   # Inaccessible
            elif pos > 0 and pos <= len(items):
                item, _ = items[pos - 1]
                if str(item) in selection:
                    attr = curses.color_pair(4)  # Selected file/dir
                elif item.is_dir():
                    attr = curses.color_pair(6)  # Directory
                else:
                    attr = curses.color_pair(2)  # Normal file
            else:
                attr = curses.color_pair(2)  # Normal
            
            try:
                stdscr.addstr(y_pos, 0, truncated_line, attr)
            except curses.error:
                pass  # Ignore if line doesn't fit

        # Status line
        status_y = height - 1
        sel_count = len([k for k, v in selection.items() if v])
        ign_count = len([k for k, v in ignored.items() if v])
        status = f"Selected: {sel_count} | Ignored: {ign_count} | Types: {len(file_types)} | {'Mouse' if mouse_enabled else 'Keys'}"
        try:
            stdscr.addstr(status_y, 0, status[:width-1], curses.color_pair(5))
        except curses.error:
            pass

        stdscr.refresh()

        # Get input
        key = stdscr.getch()
        
        # Handle mouse events
        if key == curses.KEY_MOUSE and mouse_enabled:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                
                # Calculate which item was clicked
                if help_end <= my < height - 1:
                    clicked_idx = (my - help_end) + top_line
                    
                    if 0 <= clicked_idx < len(display_items):
                        # Left click handling
                        if bstate & curses.BUTTON1_CLICKED:
                            idx = clicked_idx
                            
                            if idx == 0:  # Up directory - always navigate
                                if len(stack) > 1:
                                    stack.pop()
                                    current_path = stack[-1]
                                    idx = 0
                                    top_line = 0
                            elif idx > 0 and idx <= len(items):
                                selected_item, accessible = items[idx - 1]
                                if accessible:
                                    # Determine what was clicked based on x position
                                    line_content = display_items[idx]
                                    
                                    # Check if click was on checkbox area [X] (positions 0-3)
                                    if mx <= 3 and line_content.startswith('['):
                                        # Checkbox click - toggle selection state
                                        path = str(selected_item)
                                        
                                        # Cycle through states: unselected -> selected -> ignored -> unselected
                                        if path not in selection and path not in ignored:
                                            # Unselected -> Selected
                                            selection[path] = True
                                            if selected_item.is_dir():
                                                mark_subitems(selection, ignored, selected_item, True, file_types)
                                        elif path in selection:
                                            # Selected -> Ignored
                                            selection.pop(path, None)
                                            if selected_item.is_dir():
                                                mark_subitems(selection, ignored, selected_item, False, file_types)
                                            mark_ignored(ignored, selection, selected_item)
                                        else:
                                            # Ignored -> Unselected
                                            for key in list(ignored.keys()):
                                                if key.startswith(path):
                                                    ignored.pop(key)
                                    
                                    # Click on folder name/icon (positions 4+) for directories
                                    elif selected_item.is_dir() and mx > 3:
                                        # Directory navigation
                                        stack.append(selected_item)
                                        current_path = selected_item
                                        idx = 0
                                        top_line = 0
                                    
                                    # Click on file name for files - toggle selection
                                    elif selected_item.is_file():
                                        path = str(selected_item)
                                        if path not in selection and path not in ignored:
                                            selection[path] = True
                                        elif path in selection:
                                            selection.pop(path, None)
                                            mark_ignored(ignored, selection, selected_item)
                                        else:
                                            for key in list(ignored.keys()):
                                                if key.startswith(path):
                                                    ignored.pop(key)
                        
                        # Right click - always toggle ignore status
                        elif bstate & (curses.BUTTON3_CLICKED):
                            if idx > 0 and idx <= len(items):
                                selected_item, accessible = items[idx - 1]
                                if accessible:
                                    path = str(selected_item)
                                    if path in selection:
                                        selection.pop(path, None)
                                        mark_ignored(ignored, selection, selected_item)
                                    elif path in ignored:
                                        for key in list(ignored.keys()):
                                            if key.startswith(path):
                                                ignored.pop(key)
                                    else:
                                        mark_ignored(ignored, selection, selected_item)
                
                # Mouse wheel scrolling
                elif bstate & curses.BUTTON4_PRESSED:  # Scroll up
                    for _ in range(3):
                        if idx > 0:
                            idx -= 1
                elif bstate & (curses.BUTTON5_PRESSED | curses.BUTTON2_CLICKED):  # Scroll down
                    for _ in range(3):
                        if idx < len(display_items) - 1:
                            idx += 1
                            
            except curses.error:
                pass
        
        # Keyboard navigation
        elif key == curses.KEY_DOWN:
            new_idx = idx + 1
            while new_idx < len(display_items) and not accessible_items[new_idx]:
                new_idx += 1
            if new_idx < len(display_items):
                idx = new_idx
                
        elif key == curses.KEY_UP:
            new_idx = idx - 1
            while new_idx > 0 and not accessible_items[new_idx]:
                new_idx -= 1
            if new_idx >= 0:
                idx = new_idx

        elif key == curses.KEY_NPAGE:  # Page Down
            idx = min(idx + 10, len(display_items) - 1)
        elif key == curses.KEY_PPAGE:  # Page Up
            idx = max(idx - 10, 0)

        elif key in [curses.KEY_RIGHT, 10]:  # Enter
            if idx > 0 and idx <= len(items):
                selected_item, accessible = items[idx - 1]
                if accessible and selected_item.is_dir():
                    stack.append(selected_item)
                    current_path = selected_item
                    idx = 0
                    top_line = 0
            elif idx == 0 and len(stack) > 1:
                stack.pop()
                current_path = stack[-1]
                idx = 0
                top_line = 0
                     
        elif key in [curses.KEY_LEFT, 127, 8]:  # Backspace
            if len(stack) > 1:
                stack.pop()
                current_path = stack[-1]
                idx = 0
                top_line = 0

        elif key == ord(' '):  # Space - toggle selection
            if idx > 0 and idx <= len(items):
                selected_item, accessible = items[idx - 1]
                if accessible:
                    path = str(selected_item)
                    
                    # Cycle through states: unselected -> selected -> ignored -> unselected
                    if path not in selection and path not in ignored:
                        # Unselected -> Selected
                        selection[path] = True
                        if selected_item.is_dir():
                            mark_subitems(selection, ignored, selected_item, True, file_types)
                    elif path in selection:
                        # Selected -> Ignored
                        selection.pop(path, None)
                        if selected_item.is_dir():
                            mark_subitems(selection, ignored, selected_item, False, file_types)
                        mark_ignored(ignored, selection, selected_item)
                    else:
                        # Ignored -> Unselected
                        for key in list(ignored.keys()):
                            if key.startswith(path):
                                ignored.pop(key)

        elif key == ord('i'):  # Ignore
            if idx > 0 and idx <= len(items):
                selected_item, accessible = items[idx - 1]
                if accessible:
                    path = str(selected_item)
                    if path in selection:
                        for key in list(selection.keys()):
                            if key.startswith(path):
                                selection.pop(key)
                        mark_ignored(ignored, selection, selected_item)
                    else:
                        if path in ignored:
                            for key in list(ignored.keys()):
                                if key.startswith(path):
                                    ignored.pop(key)
                        else:
                            mark_ignored(ignored, selection, selected_item)

        elif key == ord('f') or key == ord('\t'):  # Edit file types
            curses.curs_set(1)
            stdscr.clear()
            stdscr.addstr(0, 0, "🎯 File Type Manager", curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(2, 0, f"Discovered types: {', '.join(discovered_types[:20])}")
            stdscr.addstr(3, 0, f"Current filter: {', '.join(sorted(file_types)) if file_types else 'All files'}")
            stdscr.addstr(5, 0, "Enter extensions (comma-separated, no dots) or '*' for all:")
            stdscr.addstr(6, 0, "Current: ")

            edit_win = curses.newwin(1, 50, 6, 9)
            current_filter = ",".join(ft.lstrip('.') for ft in sorted(file_types))
            edit_win.addstr(current_filter)
            edit_box = curses.textpad.Textbox(edit_win, insert_mode=True)

            stdscr.refresh()
            new_input = edit_box.edit().strip()

            if new_input:
                if new_input == '*':
                    file_types = set()  # All files
                else:
                    file_types = {f".{ext.strip()}" if not ext.strip().startswith(".") and ext.strip() != "*" else ext.strip() 
                                for ext in new_input.split(',') if ext.strip()}
            curses.curs_set(0)

        elif key == ord('a'):  # Select all visible
            for item, accessible in items:
                if accessible:
                    path = str(item)
                    selection[path] = True
                    if item.is_dir():
                        mark_subitems(selection, ignored, item, True, file_types)

        elif key == ord('c'):  # Clear all selections
            selection.clear()
            ignored.clear()

        elif key == ord('r'):  # Reset to discovered types
            file_types = set(discovered_types[:10])  # Reset to first 10 discovered

        elif key == ord('h'):  # Toggle help
            show_help = not show_help

        elif key == ord('v'):  # View selections
            def view_selections():
                v_idx = 0
                v_top = 0
                selected_paths = list(selection.keys())
                ignored_paths = list(ignored.keys())
                all_paths = selected_paths + ignored_paths
                
                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "📋 Selected & Ignored Files/Directories", curses.color_pair(5) | curses.A_BOLD)
                    stdscr.addstr(1, 0, "✓: Selected  ✗: Ignored", curses.color_pair(2))
                    
                    for i, path in enumerate(all_paths[v_top:v_top + height - 4]):
                        if i + v_top >= len(all_paths):
                            break
                        prefix = "✓ " if path in selected_paths else "✗ "
                        display_path = path
                        if len(display_path) > width - 3:
                            display_path = "..." + display_path[-(width-6):]
                        
                        color = curses.color_pair(4) if path in selected_paths else curses.color_pair(3)
                        if i + v_top == v_idx:
                            color |= curses.A_REVERSE
                            
                        try:
                            stdscr.addstr(i + 2, 0, prefix + display_path, color)
                        except curses.error:
                            pass
                            
                    try:
                        stdscr.addstr(height - 1, 0, "Use ↑/↓/PgUp/PgDn/Home/End to scroll, 'q' to exit", curses.color_pair(2))
                    except curses.error:
                        pass
                    
                    stdscr.refresh()
                    key_v = stdscr.getch()
                    
                    if key_v == curses.KEY_DOWN and v_idx < len(all_paths) - 1:
                        v_idx += 1
                        if v_idx >= v_top + height - 4:
                            v_top += 1
                    elif key_v == curses.KEY_UP and v_idx > 0:
                        v_idx -= 1
                        if v_idx < v_top:
                            v_top -= 1
                    elif key_v == curses.KEY_NPAGE:  # Page Down
                        v_idx = min(v_idx + height - 4, len(all_paths) - 1)
                        v_top = min(v_top + height - 4, len(all_paths) - (height - 4))
                    elif key_v == curses.KEY_PPAGE:  # Page Up
                        v_idx = max(0, v_idx - (height - 4))
                        v_top = max(0, v_top - (height - 4))
                    elif key_v == curses.KEY_HOME:
                        v_idx = 0
                        v_top = 0
                    elif key_v == curses.KEY_END:
                        v_idx = len(all_paths) - 1
                        v_top = max(0, len(all_paths) - (height - 4))
                    elif key_v == ord('q'):
                        break
            view_selections()

        elif key == 27:  # Escape
            return None
        elif key == ord('q'):
            return {
                "selected": [path for path, checked in selection.items() if checked],
                "ignored": [path for path, is_ignored in ignored.items() if is_ignored],
                "file_types": list(file_types)
            }

def select_files(start_path=".", preselected_filters=None, included_files=None, ignored_dirs=None, included_dirs=None):
    return curses.wrapper(curses_file_selector, 
                         start_path=start_path,
                         preselected_filters=preselected_filters,
                         included_files=included_files,
                         ignored_dirs=ignored_dirs,
                         included_dirs=included_dirs)