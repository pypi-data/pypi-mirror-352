import os
import curses
import curses.textpad
from pathlib import Path

def is_accessible(path):
    try:
        path.stat()
        return True
    except (PermissionError, OSError):
        return False

def should_show_file(item, file_types, selection):
    # Always show directories
    if item.is_dir():
        return True
    # Show file if it's in selection
    if selection and str(item) in selection:
        return True
    # Show all files if "*" is in filters
    if any(ft.strip() == "*" for ft in file_types):
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
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Inaccessible
    
    current_path = Path(start_path).resolve()
    selection = {}
    ignored = {}
    global file_types
    file_types = set(preselected_filters) if preselected_filters else set()

    if start_path == "." and not (included_files or included_dirs):
        for item in current_path.iterdir():
            if not is_accessible(item):
                continue
            if item.is_dir() or (file_types and item.suffix in file_types):
                path = str(item.resolve())
                selection[path] = True
                if item.is_dir():
                    mark_subitems(selection, ignored, path, True, file_types)

    if included_files:
        for file_path in included_files:
            path = Path(file_path).resolve()
            if is_accessible(path):
                selection[str(path)] = True

    if included_dirs:
        for dir_path in included_dirs:
            path = Path(dir_path).resolve()
            if is_accessible(path):
                mark_subitems(selection, ignored, path, True, file_types)
                selection[str(path)] = True

    if ignored_dirs:
        for dir_path in ignored_dirs:
            path = Path(dir_path).resolve()
            if is_accessible(path):
                mark_ignored(ignored, selection, path)

    stack = [current_path]
    idx = 0
    top_line = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        path_str = str(current_path)
        if len(path_str) >= width:
            path_str = "..." + path_str[-(width-3):]
        stdscr.addstr(0, 0, path_str, curses.A_BOLD)
        stdscr.addstr(1, 0, "─" * min(len(path_str), width-1))
        stdscr.addstr(2, 0, "↑/↓:Navigate  SPACE:Toggle  ←/→:Navigate dirs  i:Ignore  v:View  f:Filter  q:Done", curses.A_DIM)
        
        items = get_directory_contents(current_path, file_types, selection)
        display_items = ["[../] (Up one level)"] + [
            (f"{item.name}/" if not accessible else 
             f"[{chr(10003) if selection.get(str(item), False) else chr(10007) if ignored.get(str(item), False) else ' '}] {item.name}/") if item.is_dir() else
            (f"{item.name}" if not accessible else 
             f"[{chr(10003) if selection.get(str(item), False) else chr(10007) if ignored.get(str(item), False) else ' '}] {item.name}")
            for item, accessible in items
        ]
        
        accessible_items = [True] + [acc for _, acc in items]
        
        if idx >= len(display_items):
            idx = max(len(display_items) - 1, 0)

        if idx < top_line:
            top_line = idx
        elif idx >= top_line + height - 4:
            top_line = idx - (height - 5)

        for i, line in enumerate(display_items[top_line:top_line + height - 4]):
            pos = i + top_line
            truncated_line = (line[:width - 3] + "...") if len(line) >= width else line
            
            if pos >= len(accessible_items):
                continue
                
            attr = curses.color_pair(1) if pos == idx else curses.color_pair(2)
            if not accessible_items[pos]:
                attr = curses.color_pair(3) | curses.A_DIM
            
            stdscr.addstr(i + 3, 0, truncated_line, attr)

        key = stdscr.getch()
        
        if key == curses.KEY_DOWN:
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

        elif key in [curses.KEY_RIGHT, 10]:
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
                     
        elif key in [curses.KEY_LEFT, 127, 8]:
            if len(stack) > 1:
                stack.pop()
                current_path = stack[-1]
                idx = 0
                top_line = 0

        elif key == ord(' '):
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

        elif key == ord('i'):
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

        elif key == ord('f'):
            curses.curs_set(1)
            stdscr.clear()
            stdscr.addstr(0, 0, f"Edit file extensions (comma-separated, no dots needed, current: {', '.join(file_types)}): ")

            edit_win = curses.newwin(1, 50, 1, 0)
            edit_win.addstr(",".join(ft.lstrip('.') for ft in file_types))
            edit_box = curses.textpad.Textbox(edit_win, insert_mode=True)

            stdscr.refresh()
            new_input = edit_box.edit().strip()

            if new_input:
                file_types = {f".{ext.strip()}" if not ext.strip().startswith(".") and ext.strip() != "*" else ext.strip() 
                            for ext in new_input.split(',')}
            curses.curs_set(0)

        elif key == ord('v'):
            def view_selections():
                v_idx = 0
                v_top = 0
                selected_paths = list(selection.keys())
                ignored_paths = list(ignored.keys())
                all_paths = selected_paths + ignored_paths
                
                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Selected & Ignored Files/Directories:", curses.A_BOLD)
                    stdscr.addstr(1, 0, "✔: Selected  ✘: Ignored", curses.A_DIM)
                    
                    for i, path in enumerate(all_paths[v_top:v_top + height - 4]):
                        prefix = "✔ " if path in selected_paths else "✘ "
                        if i + v_top == v_idx:
                            stdscr.addstr(i + 2, 0, prefix + path[:width - 3], curses.A_REVERSE)
                        else:
                            stdscr.addstr(i + 2, 0, prefix + path[:width - 3])
                            
                    stdscr.addstr(height - 1, 0, "Use UP/DOWN/PGUP/PGDN/HOME/END to scroll, 'q' to exit")
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

        elif key == 27:
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