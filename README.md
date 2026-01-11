# CustomWindow (Dear PyGui Framework)

A desktop application framework for a custom borderless window, built on Dear PyGui. It provides:
- Custom title bar (icon, title text, minimize/maximize/close)
- Borderless window dragging with edge/corner resize overlay
- Windows API cursor switching and window controls (fallback to Dear PyGui behaviors on non‑Windows)
- Centralized event handling in the `UIEvent` class; user UI is composed via `UserUI` into `UIHandle`

## Installation

Install dependencies with pip (virtual environment recommended):

```bash
pip install -r requirement.txt
# or
pip install dearpygui
```

## Run

Start the default window provided by the framework:

```bash
python CustomWindow.py
```

## Customize UI (compose `UserUI`)

Create your own `UserUI` subclass and replace it after initializing `UIHandle`:

```python
from CustomWindow import UIHandle, UserUI, dpg

class MyUserUI(UserUI):
    def create_layout(self):
        dpg.add_text("Hello, World!")
        dpg.add_button(label="Click Me", callback=lambda: print("Clicked"))

    def resize_callback(self, sender, app_data):
        vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
        # Adjust your components based on viewport size
        # dpg.configure_item("my_panel", width=vw - 100)

    def update_logic(self):
        # Per‑frame update logic (e.g., status display)
        pass

if __name__ == "__main__":
    ui = UIHandle()
    ui.user_ui = MyUserUI(ui)  # Replace the user interface via composition
    ui.loop()
```

## Important Settings

- `CUSTOMWINDOW_DEBUG`: When enabled, shows resize boundaries and button hover/active colors to aid debugging.
- Layout behavior: The default main content window `content_window` automatically avoids the title bar and resize margins.

## Platform Notes

- Windows: Uses WinAPI for controls (minimize/maximize/cursor switching) and offers the best experience.
- Other platforms: Falls back to Dear PyGui's default controls; borderless and resize interactions still work, though some behaviors may differ.

## Project Structure (summary)

```
CustomWindow.py        # Main framework file with UIHandle / UIEvent / ResizeOverlay / CustomWindowBar / UserUI
fonts/                 # Font assets (optional)
icon/                  # Window icon assets (optional)
images/                # Image assets (optional)
resources/Resource.drawio
```

## Development Tips

- To customize the style/size of the title bar or resize overlay, adjust `CUSTOMWINDOW_TITLEBAR_HEIGHT` and `ResizeOverlay.bar_w`.
- To integrate more events, add methods in the `UIEvent` class and bind corresponding handlers in your layout.
