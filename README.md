# CustomWindow (Dear PyGui Framework)
A desktop application framework for a custom borderless window, built on Dear PyGui. It provides:
- Custom title bar (icon, title text, minimize/maximize/close)
- Borderless window dragging with edge/corner resize overlay
- Windows API cursor switching and window controls (fallback to Dear PyGui behaviors on non‑Windows)
- Centralized event handling in the `UIEvent` class; user UI is composed via `UserUI` into `UIHandle`


## Demo
| Original windows window bar | CustomWindow (This Project) |
|------------------------|----------------------------------|
| <img width="400" height="318" alt="image" src="https://github.com/user-attachments/assets/428a1bf8-4c19-40f6-b665-4582c847ba27" /> | <img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/cecf16ac-593a-4220-9ac5-126e316e26ae" /> |  

https://github.com/user-attachments/assets/c598ef13-f0e7-4a8c-a0b0-214e3a8fca89

## Why
Since Dear PyGui currently lacks a simple, mature custom window bar solution on Windows, I built one for future development.   
Feel free to fork it if you need it.
This project was completed using vibe coding techniques.  
Please note that the code is VERY messy, but I have prepared a way for you to use it (see the following explanation about UserUI).  
If you want to customize the window bar yourself, the following elements are customizable:
1. icon (please modify the icon image)
2. title text and the title bar color(please modify the item's color theme and text with tag "title_text_btn")
3. minimize/maximize/close window buttons (please modify the corresponding images)
4. the height of window bar(Use CUSTOMWINDOW_TITLEBAR_HEIGHT)

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
class UserUI:
    def __init__(self, ui_handle):
        self.ui_handle = ui_handle
    
    def create_layout(self):
        pass
        # Debug info layout
        '''
        """預設範例佈局：展示框架的 debug 資訊。覆寫此方法以自訂。"""
        with dpg.group(indent=15):
            dpg.add_text("API Viewport Mouse: (0, 0)", tag="mouse_pos_text")
            dpg.add_text("Adjusted Content Mouse: (0, 0)", tag="mouse_pos_content_text")
            dpg.add_text("Real Screen Mouse: (0, 0)", tag="coord_screen_mouse")
            dpg.add_text("Viewport Pos (Screen): (0, 0)", tag="coord_viewport_pos")
            dpg.add_text("Viewport Size: (0, 0)", tag="coord_viewport_size")
            dpg.add_text("Mouse Local (Viewport): (0, 0)", tag="coord_viewport_mouse_local")
            dpg.add_text("Viewport Local (Computed): (0, 0)", tag="coord_viewport_local_computed")
            dpg.add_text("Title Pos: (0, 0)", tag="coord_title_pos")
            dpg.add_text("Work Area: x=0 y=0 w=0 h=0", tag="coord_work_area")
            dpg.add_text("Top Bar Pos: (0, 0)", tag="coord_top_bar")
            dpg.add_text("Left Bar Pos: (0, 0) size: (0, 0)", tag="coord_left_bar")
            dpg.add_text("Right Bar Pos: (0, 0) size: (0, 0)", tag="coord_right_bar")
            dpg.add_text("Bottom Bar Pos: (0, 0)", tag="coord_bottom_bar")

            # 新增toggle按鈕
            dpg.add_button(label="0", tag="toggle_btn", callback=self.ui_handle.ui_event.toggle_button)

            # 醒目綠字主題：用於顯示最重要的計算座標
            with dpg.theme() as _computed_local_theme:
                with dpg.theme_component(dpg.mvText):
                    dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 0, 255))
            dpg.bind_item_theme("coord_viewport_local_computed", _computed_local_theme)
        '''

    def resize_callback(self, sender, app_data):
        pass
    def update_logic(self):
        pass
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


