# CustomWindow (Dear PyGui 框架)

自訂無邊框視窗的桌面應用程式框架，基於 Dear PyGui。提供：
- 自訂標題列（icon、標題文字、最小化/最大化/關閉）
- 無邊框視窗拖曳與四邊/角落縮放覆蓋層
- Windows API 游標切換與視窗控制（在非 Windows 上使用 DPG 退化行為）
- 事件集中在 `UIEvent` 類，使用者介面透過 `UserUI` 組合進 `UIHandle`

## 安裝

以 pip 安裝依賴（建議使用虛擬環境）：

```bash
pip install -r requirement.txt
# 或
pip install dearpygui
```

## 執行

直接啟動框架預設視窗：

```bash
python CustomWindow.py
```

## 自訂 UI（組合 `UserUI`）

建立自己的 `UserUI` 子類，並在 `UIHandle` 初始化後替換：

```python
from CustomWindow import UIHandle, UserUI, dpg

class MyUserUI(UserUI):
    def create_layout(self):
        dpg.add_text("Hello, World!")
        dpg.add_button(label="Click Me", callback=lambda: print("Clicked"))

    def resize_callback(self, sender, app_data):
        vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
        # 依視窗大小調整你的元件尺寸
        # dpg.configure_item("my_panel", width=vw - 100)

    def update_logic(self):
        # 每幀更新邏輯（例如狀態顯示）
        pass

if __name__ == "__main__":
    ui = UIHandle()
    ui.user_ui = MyUserUI(ui)  # 以組合方式替換使用者介面
    ui.loop()
```

## 重要設定

- `CUSTOMWINDOW_DEBUG`：開啟後會顯示縮放邊界與按鈕 hover/active 顏色，便於除錯。
- 視窗佈局：預設主內容 `content_window` 會自動避開標題列與縮放邊距。

## 平台說明

- Windows：使用 WinAPI 控制（最小化/最大化/游標切換），提供最佳體驗。
- 其他平台：退化為 Dear PyGui 的預設控制；無邊框與縮放互動仍可運作，但某些行為可能不同。

## 專案結構（摘要）

```
CustomWindow.py        # 框架主檔，包含 UIHandle / UIEvent / ResizeOverlay / CustomWindowBar / UserUI
demo.py                # 範例或測試（若存在）
fonts/                 # 字型資源（可選）
icon/                  # 視窗 icon 圖示（可選）
images/                # 圖片資源（可選）
Resources/Resource.drawio
```

## 開發提示

- 若需要自訂標題列或縮放覆蓋層的樣式/尺寸，可調整 `CUSTOMWINDOW_TITLEBAR_HEIGHT` 與 `ResizeOverlay.bar_w`。
- 想整合更多事件：請在 `UIEvent` 類中新增方法，並於佈局綁定對應的 handler。
