import dearpygui.dearpygui as dpg
import ctypes
import os
from ctypes import wintypes

#=========================================================================
# Custom Window Configurations
#=========================================================================
# Brief: Debug  mode for custom title bar
# True:  Show title bar and dragable side bar's range with visiable color
# False: Dragable side bar is transparent. Title bar use default color. All functionality remains.
CUSTOMWINDOW_DEBUG = False

# Height of the custom title bar
CUSTOMWINDOW_TITLEBAR_HEIGHT = 30
#=========================================================================




# --- 系統工具 ---
class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), 
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]

class SystemUtils:
    """封裝系統相關工具：工作區座標與滑鼠座標查詢。"""
    def get_screen_work_area(self):
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
        return {"x": rect.left, "y": rect.top, "w": rect.right - rect.left, "h": rect.bottom - rect.top}

    def get_viewport_work_area(self):
        try:
            hwnd = dpg.get_viewport_platform_handle()
            hmon = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            ok = ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
            if ok:
                return {
                    "x": mi.rcWork.left,
                    "y": mi.rcWork.top,
                    "w": mi.rcWork.right - mi.rcWork.left,
                    "h": mi.rcWork.bottom - mi.rcWork.top,
                }
        except Exception:
            pass
        return self.get_screen_work_area()

    def get_real_mouse_pos(self):
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return [pt.x, pt.y]

class CustomWindowBar:
    """建立自訂標題列（icon + title + 控制按鈕）。"""
    def build(self, ui, parent_tag: str = "main_window"):
        # 標題列主題（零邊距/間距）
        with dpg.theme() as table_theme:
            with dpg.theme_component(dpg.mvTable):
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0)
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)

        # 標題列按鈕主題：移除框內邊距讓高度貼齊 cell
        with dpg.theme() as bar_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                if CUSTOMWINDOW_DEBUG:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 160, 255, 40))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 160, 255, 120))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (60, 160, 255, 160))
            # image_button 也套相同的 padding/rounding
            with dpg.theme_component(dpg.mvImageButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                if CUSTOMWINDOW_DEBUG:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 160, 255, 40))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 160, 255, 120))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (60, 160, 255, 160))

        # 非 debug：讓 title 文字區的 hover/press 與一般狀態一致（透明，不改變顏色）
        title_text_theme = None
        if not CUSTOMWINDOW_DEBUG:
            with dpg.theme() as _title_text_theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                    # 將三種狀態都設為透明，避免 hover/active 顏色變化
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 51, 55, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (51, 51, 55, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (51, 51, 55, 255))
            title_text_theme = _title_text_theme

        with dpg.table(header_row=False, borders_innerH=False, borders_outerH=False,
                       borders_innerV=False, borders_outerV=False, resizable=False,
                       policy=dpg.mvTable_SizingFixedFit, row_background=False,
                       precise_widths=True, tag="title_table", parent=parent_tag):
            # 欄位：icon | title(自適應像素) | min | max | close
            dpg.add_table_column(tag="col_icon", init_width_or_weight=ui.button_size[0])
            dpg.add_table_column(tag="col_title")
            dpg.add_table_column(tag="col_min", init_width_or_weight=ui.button_size[0])
            dpg.add_table_column(tag="col_max", init_width_or_weight=ui.button_size[0])
            dpg.add_table_column(tag="col_close", init_width_or_weight=ui.button_size[0])

            with dpg.table_row():
                # Icon
                with dpg.table_cell():
                    if ui.icon_tex:
                        dpg.add_image_button(tag="title_icon_btn", texture_tag=ui.icon_tex,
                                             width=ui.button_size[0], height=ui.button_size[1])
                    else:
                        dpg.add_button(tag="title_icon_btn", label="■",
                                       width=ui.button_size[0], height=ui.button_size[1])

                # Title（左對齊、可拖曳/雙擊）
                with dpg.table_cell(tag="title_text_cell"):
                    # 初始化時先給一個暫定寬度，之後在 sync_ui 精確調整
                    dpg.add_button(tag="title_text_btn", label="Title bar text",
                                   width=200, height=ui.button_size[1])

                # 控制按鈕
                with dpg.table_cell():
                    if ui.images_ok:
                        dpg.add_image_button(tag="min_btn", texture_tag=ui.texture_ids.get("min_normal"),
                                             width=ui.button_size[0], height=ui.button_size[1],
                                             callback=ui.ui_event.minimize_viewport)
                    else:
                        dpg.add_button(tag="min_btn", label="-", width=ui.button_size[0], height=ui.button_size[1],
                                       callback=ui.ui_event.minimize_viewport)

                with dpg.table_cell():
                    if ui.images_ok:
                        dpg.add_image_button(tag="max_btn", texture_tag=ui.texture_ids.get("max_normal"),
                                             width=ui.button_size[0], height=ui.button_size[1],
                                             callback=ui.ui_event.toggle_maximize)
                    else:
                        dpg.add_button(tag="max_btn", label="口", width=ui.button_size[0], height=ui.button_size[1],
                                       callback=ui.ui_event.toggle_maximize)

                with dpg.table_cell():
                    if ui.images_ok:
                        dpg.add_image_button(tag="close_btn", texture_tag=ui.texture_ids.get("close_normal"),
                                             width=ui.button_size[0], height=ui.button_size[1],
                                             callback=ui.ui_event.close_application)
                    else:
                        dpg.add_button(tag="close_btn", label="x", width=ui.button_size[0], height=ui.button_size[1],
                                       callback=ui.ui_event.close_application)

        dpg.bind_item_theme("title_table", table_theme)
        # 套用按鈕主題到所有標題列按鈕
        for item_id in ["title_icon_btn", "title_text_btn", "min_btn", "max_btn", "close_btn"]:
            if dpg.does_item_exist(item_id):
                dpg.bind_item_theme(item_id, bar_button_theme)
        # 覆蓋 title_text_btn 主題，確保非 debug 狀態下 hover/press 不變色
        if title_text_theme and dpg.does_item_exist("title_text_btn"):
            dpg.bind_item_theme("title_text_btn", title_text_theme)

        # 事件綁定：只在 title/icon 上拖曳與雙擊
        with dpg.item_handler_registry(tag="title_bar_handlers"):
            dpg.add_item_clicked_handler(callback=ui.ui_event.on_title_press)
            dpg.add_item_double_clicked_handler(callback=ui.ui_event.on_title_double_click)
        for item_id in ["title_text_btn", "title_icon_btn"]:
            if dpg.does_item_exist(item_id):
                dpg.bind_item_handler_registry(item_id, "title_bar_handlers")

        # 將標題列整體下移，預留上邊縮放條厚度（避免使用 spacer）
        try:
            dpg.configure_item("title_table", pos=[0, ui.resize_overlay.bar_w])
        except Exception:
            pass

class ResizeOverlay:
    """封裝邊緣縮放條與角落方塊的建立與主題綁定。"""
    def __init__(self, bar_w: int = 6, corner_size: int = 20):
        self.bar_w = bar_w
        self.corner_size = corner_size
        self.theme = None

    def build(self, ui, parent_tag: str = "main_window"):
        # 建立縮放條主題
        with dpg.theme() as resize_bar_theme:
            with dpg.theme_component(dpg.mvButton):
                if CUSTOMWINDOW_DEBUG:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (120, 120, 120, 40))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 160, 255, 120))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (60, 160, 255, 160))
                else:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
        self.theme = resize_bar_theme

        # 現況尺寸
        vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
        title_h = ui.button_size[1]

        # 角落方塊
        dpg.add_button(tag="resize_bl_corner", label="", width=self.corner_size, height=self.corner_size,
                       pos=[0, max(0, vh - self.corner_size)], parent=parent_tag)
        dpg.add_button(tag="resize_br_corner", label="", width=self.corner_size, height=self.corner_size,
                       pos=[max(0, vw - self.corner_size), max(0, vh - self.corner_size)], parent=parent_tag)
        dpg.add_button(tag="resize_tl_corner", label="", width=self.corner_size, height=self.corner_size,
                   pos=[0, 0], parent=parent_tag)
        dpg.bind_item_theme("resize_bl_corner", self.theme)
        dpg.bind_item_theme("resize_br_corner", self.theme)
        dpg.bind_item_theme("resize_tl_corner", self.theme)

        # 邊緣縮放條（先建立，後續在 sync_ui/update_logic 依據實際 title 位置修正）
        dpg.add_button(tag="resize_left_bar", label="", width=self.bar_w, height=max(1, vh - self.bar_w - self.bar_w), pos=[0, self.bar_w], parent=parent_tag)
        dpg.add_button(tag="resize_right_bar", label="", width=self.bar_w, height=max(1, vh - self.bar_w - self.bar_w), pos=[max(0, vw - self.bar_w), self.bar_w], parent=parent_tag)
        dpg.add_button(tag="resize_bottom_bar", label="", width=vw, height=self.bar_w, pos=[0, max(0, vh - self.bar_w)], parent=parent_tag)
        dpg.add_button(tag="resize_top_bar", label="", width=vw, height=self.bar_w, pos=[0, 0], parent=parent_tag)
        dpg.bind_item_theme("resize_left_bar", self.theme)
        dpg.bind_item_theme("resize_right_bar", self.theme)
        dpg.bind_item_theme("resize_bottom_bar", self.theme)
        dpg.bind_item_theme("resize_top_bar", self.theme)

class UIEvent:
    """事件代理：對齊 GUI_demo 架構，處理 viewport 事件。"""
    def __init__(self, ui_handle):
        self.ui_handle = ui_handle

    def resize_window_callback(self, sender, app_data):
        try:
            self.ui_handle.clamp_viewport_to_work_area()
            self.ui_handle.sync_ui()
            # 呼叫用戶自訂的 resize callback
            self.ui_handle.user_ui.resize_callback(sender, app_data)
        except Exception:
            pass

    def minimize_viewport(self, sender=None, app_data=None, user_data=None):
        try:
            # 先使用 Dear PyGui 的官方 API
            dpg.minimize_viewport()
        except Exception:
            try:
                hwnd = dpg.get_viewport_platform_handle()
                user32 = ctypes.windll.user32
                WM_SYSCOMMAND = 0x0112
                SC_MINIMIZE = 0xF020
                user32.SendMessageW(hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)
                if not user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
            except Exception:
                try:
                    dpg.hide_viewport()
                except Exception:
                    pass

    def toggle_maximize(self, sender=None, app_data=None, user_data=None):
        ui = self.ui_handle
        if not ui.state["is_manual_max"]:
            ui.state["pre_max_pos"] = dpg.get_viewport_pos()
            ui.state["pre_max_size"] = [dpg.get_viewport_width(), dpg.get_viewport_height()]
            area = ui.get_viewport_work_area()
            dpg.configure_viewport(0, x_pos=area["x"], y_pos=area["y"], width=area["w"], height=area["h"], resizable=False)
            dpg.set_item_label("max_btn", "❐")
            ui.state["is_manual_max"] = True
            ui._set_resize_bars_enabled(False)
            ui.state["dragging"], ui.state["resizing"], ui.state["resize_dir"] = False, False, None
        else:
            dpg.configure_viewport(0, x_pos=int(ui.state["pre_max_pos"][0]), y_pos=int(ui.state["pre_max_pos"][1]), 
                                   width=int(ui.state["pre_max_size"][0]), height=int(ui.state["pre_max_size"][1]), resizable=True)
            dpg.set_item_label("max_btn", "口")
            ui.state["is_manual_max"] = False
            ui._set_resize_bars_enabled(True)
        ui.sync_ui()
        ui.clamp_viewport_to_work_area()

    def close_application(self, sender=None, app_data=None, user_data=None):
        dpg.stop_dearpygui()

    def toggle_button(self, sender=None, app_data=None, user_data=None):
        ui = self.ui_handle
        ui.state["toggle_value"] = 1 - ui.state["toggle_value"]
        dpg.set_item_label("toggle_btn", str(ui.state["toggle_value"]))

    def on_title_press(self, sender, app_data, user_data):
        ui = self.ui_handle
        try:
            if ui.state["is_manual_max"]:
                return
            m_real = ui.get_real_mouse_pos()
            v_pos = dpg.get_viewport_pos()
            m_local = ui.get_mouse_pos_viewport_local()
            bar_w = ui.resize_overlay.bar_w
            corner_sz = ui.resize_overlay.corner_size
            title_h = ui.button_size[1]
            # 先判定是否落在左上角的縮放優先區域（正方形：X、Y 都需 ≤ corner_size）
            if m_local[0] <= corner_sz and m_local[1] <= corner_sz:
                # 左上角（正方形區域）
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "corner_top_left"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [dpg.get_viewport_width(), dpg.get_viewport_height()]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                return
            if m_local[1] <= bar_w:
                # 頂邊縮放
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "top"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [dpg.get_viewport_width(), dpg.get_viewport_height()]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                return
            if m_local[0] <= bar_w:
                # 左邊縮放
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "left"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [dpg.get_viewport_width(), dpg.get_viewport_height()]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                return

            # 以上都不符合，才進入拖曳移動
            ui.state["dragging"] = True
            ui.state["click_offset"] = [m_real[0] - v_pos[0], m_real[1] - v_pos[1]]
        except Exception:
            pass

    def on_title_double_click(self, sender, app_data, user_data):
        try:
            self.toggle_maximize()
        except Exception:
            pass

    def on_mouse_click(self, sender=None, app_data=None, user_data=None):
        ui = self.ui_handle
        v_w, v_h = dpg.get_viewport_width(), dpg.get_viewport_height()
        m_real = ui.get_real_mouse_pos()
        v_pos = dpg.get_viewport_pos()
        if not ui.state["is_manual_max"]:
            m_local = ui.get_mouse_pos_viewport_local()
            # 直接座標判定（避免 hover 失效）：優先處理左上角與上側邊條
            try:
                bar_w = ui.resize_overlay.bar_w
                corner_sz = ui.resize_overlay.corner_size
                if not ui.state["resizing"]:
                    # 左上角：正方形區域（X、Y 都需 ≤ corner_size）
                    if m_local[0] <= corner_sz and m_local[1] <= corner_sz:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "corner_top_left"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    # 左下角：X ≤ corner_size 且 Y ≥ vh - corner_size
                    elif m_local[0] <= corner_sz and m_local[1] >= v_h - corner_sz:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "corner_left"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    # 右下角：X ≥ vw - corner_size 且 Y ≥ vh - corner_size
                    elif m_local[0] >= v_w - corner_sz and m_local[1] >= v_h - corner_sz:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "corner"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    elif m_local[1] <= bar_w:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "top"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    elif m_local[0] <= bar_w:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "left"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    elif m_local[0] >= v_w - bar_w:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "right"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
                    elif m_local[1] >= v_h - bar_w:
                        ui.state["resizing"] = True
                        ui.state["resize_dir"] = "bottom"
                        ui.state["click_offset"] = [m_real[0], m_real[1]]
                        ui.state["start_size"] = [v_w, v_h]
                        ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            except Exception:
                pass
            if dpg.does_item_exist("resize_left_bar") and dpg.is_item_hovered("resize_left_bar"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "left"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_right_bar") and dpg.is_item_hovered("resize_right_bar"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "right"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_bottom_bar") and dpg.is_item_hovered("resize_bottom_bar"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "bottom"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_top_bar") and dpg.is_item_hovered("resize_top_bar"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "top"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_bl_corner") and dpg.is_item_hovered("resize_bl_corner"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "corner_left"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_br_corner") and dpg.is_item_hovered("resize_br_corner"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "corner"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif dpg.does_item_exist("resize_tl_corner") and dpg.is_item_hovered("resize_tl_corner"):
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "corner_top_left"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]
            elif m_local[0] > v_w - 25 and m_local[1] > v_h - 25:
                ui.state["resizing"] = True
                ui.state["resize_dir"] = "corner"
                ui.state["click_offset"] = [m_real[0], m_real[1]]
                ui.state["start_size"] = [v_w, v_h]
                ui.state["start_pos"] = [v_pos[0], v_pos[1]]

    def on_mouse_release(self, sender=None, app_data=None, user_data=None):
        ui = self.ui_handle
        ui.state["dragging"] = False
        ui.state["resizing"] = False
        ui.state["resize_dir"] = None
        # 放開滑鼠時才將視窗夾回工作區
        try:
            ui.clamp_viewport_to_work_area()
            ui.sync_ui()
        except Exception:
            pass

    def on_resize_press(self, sender, app_data, user_data):
        """直接由縮放邊/角的 item handler 進入縮放模式，避免 hover 判定失效。"""
        ui = self.ui_handle
        try:
            if ui.state["is_manual_max"]:
                return
            v_w, v_h = dpg.get_viewport_width(), dpg.get_viewport_height()
            m_real = ui.get_real_mouse_pos()
            v_pos = dpg.get_viewport_pos()
            ui.state["resizing"] = True
            ui.state["resize_dir"] = str(user_data)
            ui.state["click_offset"] = [m_real[0], m_real[1]]
            ui.state["start_size"] = [v_w, v_h]
            ui.state["start_pos"] = [v_pos[0], v_pos[1]]
        except Exception:
            pass


class UserUI:
    def __init__(self, ui_handle):
        self.ui_handle = ui_handle
    
    def create_layout(self):
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

    def resize_callback(self, sender, app_data):
        pass
    def update_logic(self):
        pass


class UIHandle:
    def __init__(self):
        self.initialized = False
        self.ui_event = UIEvent(self)
        self.window_bar = CustomWindowBar()
        self.resize_overlay = ResizeOverlay()
        self.sys = SystemUtils()
        self.user_ui = UserUI(self)
        
        # 資源與狀態
        self.font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        self.font_path = None
        self.images_dir = os.path.join(os.path.dirname(__file__), "images")
        self.texture_ids = {}
        self.button_size = [CUSTOMWINDOW_TITLEBAR_HEIGHT, CUSTOMWINDOW_TITLEBAR_HEIGHT]
        self.images_ok = False
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        self.icon_tex = None
        # WinAPI 游標快取
        self.win_cursors = {}
        self.state = {
            "is_manual_max": False,
            "pre_max_pos": [100, 100],
            "pre_max_size": [800, 600],
            "dragging": False,
            "resizing": False,
            "resize_dir": None,
            "click_offset": [0, 0],
            "start_size": [0, 0],
            "start_pos": [0, 0],
            "btn_hover": {"min_btn": False, "max_btn": False, "close_btn": False},
            "current_cursor": None,
            "current_cursor_key": "std",
            "toggle_value": 0
        }

    def get_mouse_pos_viewport_local(self):
        """取得滑鼠相對於 viewport 的本地座標。"""
        m_real = self.get_real_mouse_pos()
        v_pos = dpg.get_viewport_pos()
        return [int(m_real[0] - v_pos[0]), int(m_real[1] - v_pos[1])]

    def _init_win_cursors(self):
        """預載 WinAPI 系統游標以供快速切換。"""
        try:
            user32 = ctypes.windll.user32
            self.win_cursors = {
                "std":  user32.LoadCursorW(None, 32512),  # IDC_ARROW
                "we":   user32.LoadCursorW(None, 32644),  # IDC_SIZEWE
                "ns":   user32.LoadCursorW(None, 32645),  # IDC_SIZENS
                "nwse": user32.LoadCursorW(None, 32642),  # IDC_SIZENWSE
                "nesw": user32.LoadCursorW(None, 32643),  # IDC_SIZENESW
            }
        except Exception:
            self.win_cursors = {}

    def _set_cursor_win(self, cursor_id: int) -> bool:
        """透過 WinAPI 設定游標形狀（系統預設游標）。
        cursor_id 可用：
        32512: IDC_ARROW, 32645: IDC_SIZENS, 32644: IDC_SIZEWE,
        32642: IDC_SIZENWSE, 32643: IDC_SIZENESW
        """
        try:
            user32 = ctypes.windll.user32
            # 設定函式型別，並以 MAKEINTRESOURCE 的方式傳遞資源 ID
            user32.LoadCursorW.restype = wintypes.HCURSOR
            user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
            hcur = user32.LoadCursorW(None, ctypes.c_void_p(cursor_id))
            if hcur:
                user32.SetCursor(hcur)
                return True
        except Exception:
            pass
        return False

    # 輔助：載入貼圖
    def load_texture(self, filename):
        try:
            path = os.path.join(self.images_dir, filename)
            if not os.path.exists(path):
                return None, None, None
            w, h, c, data = dpg.load_image(path)
            with dpg.texture_registry():
                tex_id = dpg.add_static_texture(w, h, data)
            return tex_id, w, h
        except Exception:
            return None, None, None

    # 系統工具包裝
    def get_real_mouse_pos(self):
        return self.sys.get_real_mouse_pos()

    def get_viewport_work_area(self):
        return self.sys.get_viewport_work_area()

    def clamp_viewport_to_work_area(self):
        area = self.get_viewport_work_area()
        v_w, v_h = dpg.get_viewport_width(), dpg.get_viewport_height()
        v_pos = dpg.get_viewport_pos()
        max_x = area["x"] + max(0, area["w"] - v_w)
        max_y = area["y"] + max(0, area["h"] - v_h)
        new_x = min(max(v_pos[0], area["x"]), max_x)
        new_y = min(max(v_pos[1], area["y"]), max_y)
        if v_w > area["w"] or v_h > area["h"]:
            dpg.configure_viewport(0, width=min(v_w, area["w"]), height=min(v_h, area["h"]))
            v_w, v_h = dpg.get_viewport_width(), dpg.get_viewport_height()
            max_x = area["x"] + max(0, area["w"] - v_w)
            max_y = area["y"] + max(0, area["h"] - v_h)
            new_x = min(max(new_x, area["x"]), max_x)
            new_y = min(max(new_y, area["y"]), max_y)
        dpg.set_viewport_pos([int(new_x), int(new_y)])

    def _set_resize_bars_enabled(self, enabled: bool):
        try:
            for tag in ["resize_left_bar", "resize_right_bar", "resize_bottom_bar", "resize_top_bar", "resize_bl_corner", "resize_br_corner", "resize_tl_corner"]:
                if dpg.does_item_exist(tag):
                    dpg.configure_item(tag, enabled=enabled)
                    if enabled:
                        dpg.show_item(tag)
                    else:
                        dpg.hide_item(tag)
        except Exception:
            pass

    def update_logic(self):
        if self.state["dragging"] or self.state["resizing"]:
            m_real = self.get_real_mouse_pos()
            if self.state["dragging"]:
                dpg.set_viewport_pos([int(m_real[0] - self.state["click_offset"][0]), int(m_real[1] - self.state["click_offset"][1])])
            elif self.state["resizing"]:
                dx, dy = m_real[0] - self.state["click_offset"][0], m_real[1] - self.state["click_offset"][1]
                min_w, min_h = 400, 300
                if self.state["resize_dir"] == "right" or self.state["resize_dir"] == "corner":
                    new_w = max(min_w, int(self.state["start_size"][0] + dx))
                    new_h = max(min_h, int(self.state["start_size"][1] + dy)) if self.state["resize_dir"] == "corner" else dpg.get_viewport_height()
                    dpg.configure_viewport(0, width=new_w, height=new_h)
                elif self.state["resize_dir"] == "bottom":
                    new_h = max(min_h, int(self.state["start_size"][1] + dy))
                    dpg.configure_viewport(0, height=new_h)
                elif self.state["resize_dir"] == "left":
                    new_w = max(min_w, int(self.state["start_size"][0] - dx))
                    new_x = int(self.state["start_pos"][0] + dx)
                    if new_w == min_w:
                        new_x = min(new_x, self.state["start_pos"][0] + self.state["start_size"][0] - min_w)
                    dpg.configure_viewport(0, x_pos=new_x, width=new_w)
                elif self.state["resize_dir"] == "top":
                    new_h = max(min_h, int(self.state["start_size"][1] - dy))
                    new_y = int(self.state["start_pos"][1] + dy)
                    if new_h == min_h:
                        new_y = min(new_y, self.state["start_pos"][1] + self.state["start_size"][1] - min_h)
                    dpg.configure_viewport(0, y_pos=new_y, height=new_h)
                elif self.state["resize_dir"] == "corner_left":
                    new_w = max(min_w, int(self.state["start_size"][0] - dx))
                    new_h = max(min_h, int(self.state["start_size"][1] + dy))
                    new_x = int(self.state["start_pos"][0] + dx)
                    if new_w == min_w:
                        new_x = min(new_x, self.state["start_pos"][0] + self.state["start_size"][0] - min_w)
                    dpg.configure_viewport(0, x_pos=new_x, width=new_w, height=new_h)
                elif self.state["resize_dir"] == "corner_top_left":
                    new_w = max(min_w, int(self.state["start_size"][0] - dx))
                    new_h = max(min_h, int(self.state["start_size"][1] - dy))
                    new_x = int(self.state["start_pos"][0] + dx)
                    new_y = int(self.state["start_pos"][1] + dy)
                    if new_w == min_w:
                        new_x = min(new_x, self.state["start_pos"][0] + self.state["start_size"][0] - min_w)
                    if new_h == min_h:
                        new_y = min(new_y, self.state["start_pos"][1] + self.state["start_size"][1] - min_h)
                    dpg.configure_viewport(0, x_pos=new_x, y_pos=new_y, width=new_w, height=new_h)
                self.clamp_viewport_to_work_area()
                self.sync_ui()

        # 游標提示（WinAPI）：使用預載系統游標，依狀態或座標切換
        # 仿照 test.py 的做法，每幀無條件設定游標
        try:
            desired_key = "std"
            if self.state["resizing"]:
                # 縮放中：依 resize_dir 決定游標
                dir_map = {
                    "left": "we",
                    "right": "we",
                    "top": "ns",
                    "bottom": "ns",
                    "corner": "nwse",
                    "corner_left": "nesw",
                    "corner_top_left": "nwse",
                }
                desired_key = dir_map.get(self.state["resize_dir"], "std")
            else:
                # 非縮放中：檢測 hover 或座標
                vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
                m_local = self.get_mouse_pos_viewport_local()
                bar_w = self.resize_overlay.bar_w
                corner_sz = self.resize_overlay.corner_size

                # 先用 item hover 判定
                if dpg.does_item_exist("resize_left_bar") and dpg.is_item_hovered("resize_left_bar"):
                    desired_key = "we"
                elif dpg.does_item_exist("resize_right_bar") and dpg.is_item_hovered("resize_right_bar"):
                    desired_key = "we"
                elif dpg.does_item_exist("resize_top_bar") and dpg.is_item_hovered("resize_top_bar"):
                    desired_key = "ns"
                elif dpg.does_item_exist("resize_bottom_bar") and dpg.is_item_hovered("resize_bottom_bar"):
                    desired_key = "ns"
                elif dpg.does_item_exist("resize_tl_corner") and dpg.is_item_hovered("resize_tl_corner"):
                    desired_key = "nwse"
                elif dpg.does_item_exist("resize_bl_corner") and dpg.is_item_hovered("resize_bl_corner"):
                    desired_key = "nesw"
                elif dpg.does_item_exist("resize_br_corner") and dpg.is_item_hovered("resize_br_corner"):
                    desired_key = "nwse"
                else:
                    # 座標回退判定（避免 hover 失效）
                    if m_local[0] <= corner_sz and m_local[1] <= corner_sz:
                        desired_key = "nwse"
                    elif m_local[0] <= corner_sz and m_local[1] >= vh - corner_sz:
                        desired_key = "nesw"
                    elif m_local[0] >= vw - corner_sz and m_local[1] >= vh - corner_sz:
                        desired_key = "nwse"
                    elif m_local[0] >= vw - corner_sz and m_local[1] <= corner_sz:
                        desired_key = "nesw"
                    elif m_local[1] <= bar_w or m_local[1] >= vh - bar_w:
                        desired_key = "ns"
                    elif m_local[0] <= bar_w or m_local[0] >= vw - bar_w:
                        desired_key = "we"

            # 每幀無條件套用游標（與 test.py 相同做法）
            hcur = self.win_cursors.get(desired_key)
            if hcur:
                ctypes.windll.user32.SetCursor(hcur)
            self.state["current_cursor_key"] = desired_key
        except Exception:
            pass

        if self.images_ok:
            mapping = {
                "min_btn": ("min_normal", "min_hover"),
                "max_btn": ("max_normal", "max_hover"),
                "close_btn": ("close_normal", "close_hover")
            }
            for item_id, (norm_key, hover_key) in mapping.items():
                try:
                    hovered = dpg.is_item_hovered(item_id)
                except Exception:
                    hovered = False
                if hovered != self.state["btn_hover"][item_id]:
                    dpg.configure_item(item_id, texture_tag=self.texture_ids[hover_key if hovered else norm_key])
                    self.state["btn_hover"][item_id] = hovered

        # 縮放條與 content_window 的同步已移至 _sync_resize_bars()，由 sync_ui() 統一呼叫

        try:
            m_local = dpg.get_mouse_pos(local=True)
            raw_x, raw_y = int(m_local[0]), int(m_local[1])
            if dpg.does_item_exist("mouse_pos_text"):
                dpg.set_value("mouse_pos_text", f"API Viewport Mouse: ({raw_x}, {raw_y})")
            if dpg.does_item_exist("mouse_pos_content_text"):
                title_pos_y = 0
                if dpg.does_item_exist("title_table"):
                    try:
                        title_pos_y = dpg.get_item_pos("title_table")[1]
                    except Exception:
                        title_pos_y = self.resize_overlay.bar_w
                content_y = max(0, raw_y - (title_pos_y + self.button_size[1]))
                dpg.set_value("mouse_pos_content_text", f"Adjusted Content Mouse: ({raw_x}, {content_y})")
            # 額外座標系資訊
            m_real = self.get_real_mouse_pos()
            v_pos = dpg.get_viewport_pos()
            vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
            if dpg.does_item_exist("coord_screen_mouse"):
                dpg.set_value("coord_screen_mouse", f"Real Screen Mouse: ({int(m_real[0])}, {int(m_real[1])})")
            if dpg.does_item_exist("coord_viewport_pos"):
                dpg.set_value("coord_viewport_pos", f"Viewport Pos (Screen): ({int(v_pos[0])}, {int(v_pos[1])})")
            if dpg.does_item_exist("coord_viewport_size"):
                dpg.set_value("coord_viewport_size", f"Viewport Size: ({vw}, {vh})")
            if dpg.does_item_exist("coord_viewport_mouse_local"):
                dpg.set_value("coord_viewport_mouse_local", f"Mouse Local (Viewport): ({raw_x}, {raw_y})")
            if dpg.does_item_exist("coord_viewport_local_computed"):
                comp_x = int(m_real[0] - v_pos[0])
                comp_y = int(m_real[1] - v_pos[1])
                dpg.set_value("coord_viewport_local_computed", f"Viewport Local (Computed): ({comp_x}, {comp_y})")
            # 標題列位置
            if dpg.does_item_exist("coord_title_pos"):
                try:
                    tpos = dpg.get_item_pos("title_table")
                except Exception:
                    tpos = [0, self.resize_overlay.bar_w]
                dpg.set_value("coord_title_pos", f"Title Pos: ({int(tpos[0])}, {int(tpos[1])})")
            # 工作區
            if dpg.does_item_exist("coord_work_area"):
                area = self.get_viewport_work_area()
                dpg.set_value("coord_work_area", f"Work Area: x={area['x']} y={area['y']} w={area['w']} h={area['h']}")
            # 各縮放條位置與尺寸
            if dpg.does_item_exist("coord_top_bar"):
                try:
                    tbpos = dpg.get_item_pos("resize_top_bar")
                except Exception:
                    tbpos = [0, 0]
                dpg.set_value("coord_top_bar", f"Top Bar Pos: ({int(tbpos[0])}, {int(tbpos[1])})")
            if dpg.does_item_exist("coord_left_bar"):
                try:
                    lbpos = dpg.get_item_pos("resize_left_bar")
                    lbw = dpg.get_item_width("resize_left_bar")
                    lbh = dpg.get_item_height("resize_left_bar")
                except Exception:
                    lbpos, lbw, lbh = [0, 0], 0, 0
                dpg.set_value("coord_left_bar", f"Left Bar Pos: ({int(lbpos[0])}, {int(lbpos[1])}) size: ({lbw}, {lbh})")
            if dpg.does_item_exist("coord_right_bar"):
                try:
                    rbpos = dpg.get_item_pos("resize_right_bar")
                    rbw = dpg.get_item_width("resize_right_bar")
                    rbh = dpg.get_item_height("resize_right_bar")
                except Exception:
                    rbpos, rbw, rbh = [0, 0], 0, 0
                dpg.set_value("coord_right_bar", f"Right Bar Pos: ({int(rbpos[0])}, {int(rbpos[1])}) size: ({rbw}, {rbh})")
            if dpg.does_item_exist("coord_bottom_bar"):
                try:
                    bbpos = dpg.get_item_pos("resize_bottom_bar")
                except Exception:
                    bbpos = [0, 0]
                dpg.set_value("coord_bottom_bar", f"Bottom Bar Pos: ({int(bbpos[0])}, {int(bbpos[1])})")
        except Exception:
            pass

        # 呼叫用戶自訂的每幀更新邏輯
        try:
            self.user_ui.update_logic()
        except Exception:
            pass

    def _sync_resize_bars(self):
        """同步縮放條、角落方塊與 content_window 的位置與尺寸。"""
        try:
            vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
            bar_w_local = self.resize_overlay.bar_w
            title_h_local = self.button_size[1]
            title_pos_y = bar_w_local
            if dpg.does_item_exist("title_table"):
                try:
                    title_pos_y = dpg.get_item_pos("title_table")[1]
                except Exception:
                    pass
            corner_size_local = self.resize_overlay.corner_size

            # 縮放條位置與尺寸
            y_start = title_pos_y
            if dpg.does_item_exist("resize_left_bar"):
                dpg.configure_item("resize_left_bar", width=bar_w_local, height=max(1, vh - y_start - bar_w_local), pos=[0, y_start])
            if dpg.does_item_exist("resize_right_bar"):
                dpg.configure_item("resize_right_bar", width=bar_w_local, height=max(1, vh - y_start - bar_w_local), pos=[max(0, vw - bar_w_local), y_start])
            if dpg.does_item_exist("resize_bottom_bar"):
                dpg.configure_item("resize_bottom_bar", width=vw, height=bar_w_local, pos=[0, max(0, vh - bar_w_local)])
            if dpg.does_item_exist("resize_top_bar"):
                dpg.configure_item("resize_top_bar", width=vw, height=bar_w_local, pos=[0, 0])

            # 角落方塊位置與尺寸
            if dpg.does_item_exist("resize_bl_corner"):
                dpg.configure_item("resize_bl_corner", width=corner_size_local, height=corner_size_local, pos=[0, max(0, vh - corner_size_local)])
            if dpg.does_item_exist("resize_br_corner"):
                dpg.configure_item("resize_br_corner", width=corner_size_local, height=corner_size_local, pos=[max(0, vw - corner_size_local), max(0, vh - corner_size_local)])
            if dpg.does_item_exist("resize_tl_corner"):
                dpg.configure_item("resize_tl_corner", width=corner_size_local, height=corner_size_local, pos=[0, 0])

            # 同步主內容子視窗的位置與尺寸（預留四側縮放邊距）
            if dpg.does_item_exist("content_window"):
                content_y = title_pos_y + title_h_local
                dpg.configure_item(
                    "content_window",
                    pos=[bar_w_local, content_y],
                    width=max(1, vw - 2 * bar_w_local),
                    height=max(1, vh - (content_y + bar_w_local))
                )
        except Exception:
            pass

    def sync_ui(self):
        """同步所有 UI 元件的位置與尺寸。"""
        try:
            # 計算可用寬度：viewport 寬度減去固定欄寬（icon + 3 個按鈕）
            vw = dpg.get_viewport_width()
            fixed_sum = self.button_size[0] * 4  # icon + min + max + close
            title_w = max(0, vw - fixed_sum)
            if dpg.does_item_exist("title_text_btn"):
                dpg.configure_item("title_text_btn", width=title_w, height=self.button_size[1])
            # 保持標題列下移位置（不使用 spacer）
            if dpg.does_item_exist("title_table"):
                dpg.configure_item("title_table", pos=[0, self.resize_overlay.bar_w])
        except Exception:
            pass
        # 同步縮放條與 content_window
        self._sync_resize_bars()

    def _load_resources(self):
        # 掃描可用字型檔案
        try:
            if os.path.isdir(self.font_dir):
                preferred = os.path.join(self.font_dir, "NotoSansTC-Regular.ttf")
                if os.path.exists(preferred):
                    self.font_path = preferred
                else:
                    for name in os.listdir(self.font_dir):
                        if name.lower().endswith((".ttf", ".otf")):
                            self.font_path = os.path.join(self.font_dir, name)
                            break
        except Exception:
            self.font_path = None

        # 載入字型（含中文 range 提示）
        if self.font_path:
            try:
                with dpg.font_registry():
                    try:
                        with dpg.font(self.font_path, 18) as _default_font:
                            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                        dpg.bind_font(_default_font)
                    except Exception:
                        _default_font = dpg.add_font(self.font_path, 18)
                        dpg.bind_font(_default_font)
            except Exception:
                pass

        # 載入按鈕圖片
        try:
            self.texture_ids["min_normal"], _, _ = self.load_texture("Minimize_Normal.png")
            self.texture_ids["min_hover"], _, _ = self.load_texture("Minimize_Hover.png")
            self.texture_ids["max_normal"], _, _ = self.load_texture("Maximize_Normal.png")
            self.texture_ids["max_hover"], _, _ = self.load_texture("Maximize_Hover.png")
            self.texture_ids["close_normal"], _, _ = self.load_texture("Close_Normal.png")
            self.texture_ids["close_hover"], _, _ = self.load_texture("Close_Hover.png")
            self.images_ok = all(self.texture_ids.get(k) for k in [
                "min_normal", "min_hover", "max_normal", "max_hover", "close_normal", "close_hover"
            ])
        except Exception:
            self.images_ok = False

        # 載入 icon 圖示
        try:
            if os.path.isdir(self.icon_dir):
                preferred_icon = None
                for name in ["icon.png", "icon.jpg", "icon.jpeg", "icon.bmp"]:
                    p = os.path.join(self.icon_dir, name)
                    if os.path.exists(p):
                        preferred_icon = name
                        break
                if preferred_icon is None:
                    for name in os.listdir(self.icon_dir):
                        if name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                            preferred_icon = name
                            break
                if preferred_icon:
                    w, h, c, data = dpg.load_image(os.path.join(self.icon_dir, preferred_icon))
                    with dpg.texture_registry():
                        self.icon_tex = dpg.add_static_texture(w, h, data)
        except Exception:
            self.icon_tex = None

    def create_layout(self):
        # 主題（需要在 context 之後建立）
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 1, 4)
        dpg.bind_theme(global_theme)

        # 建立主視窗與標題列（對齊 GUI_demo 風格）
        with dpg.window(
            label="", no_title_bar=True, no_move=True, no_scroll_with_mouse=False,
            menubar=False, no_resize=True, no_scrollbar=False,
            pos=(0, 0), width=-1, height=-1, tag="main_window"
        ):
            # 使用組合的標題列類別建立自訂標題列
            self.window_bar.build(self, parent_tag="main_window")

            dpg.add_separator()

            # 主內容容器：在標題列下方的子視窗（預留四側縮放邊距）
            vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
            content_y = self.resize_overlay.bar_w + self.button_size[1]
            with dpg.child_window(tag="content_window", border=False, no_scrollbar=False,
                                  pos=[self.resize_overlay.bar_w, content_y],
                                  width=max(1, vw - 2 * self.resize_overlay.bar_w),
                                  height=max(1, vh - (content_y + self.resize_overlay.bar_w))):
                # 呼叫用戶自訂的佈局方法
                self.user_ui.create_layout()

            # 在主視窗中建立縮放覆蓋層（位於內容之上、四側邊距可互動）
            self.resize_overlay.build(self, parent_tag="main_window")

            # 綁定縮放邊/角的點擊事件到專用 handler，以確保互動有效
            with dpg.item_handler_registry(tag="resize_handlers"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"left"))
            if dpg.does_item_exist("resize_left_bar"):
                dpg.bind_item_handler_registry("resize_left_bar", "resize_handlers")
            with dpg.item_handler_registry(tag="resize_handlers_right"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"right"))
            if dpg.does_item_exist("resize_right_bar"):
                dpg.bind_item_handler_registry("resize_right_bar", "resize_handlers_right")
            with dpg.item_handler_registry(tag="resize_handlers_bottom"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"bottom"))
            if dpg.does_item_exist("resize_bottom_bar"):
                dpg.bind_item_handler_registry("resize_bottom_bar", "resize_handlers_bottom")
            with dpg.item_handler_registry(tag="resize_handlers_top"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"top"))
            if dpg.does_item_exist("resize_top_bar"):
                dpg.bind_item_handler_registry("resize_top_bar", "resize_handlers_top")
            with dpg.item_handler_registry(tag="resize_handlers_bl"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"corner_left"))
            if dpg.does_item_exist("resize_bl_corner"):
                dpg.bind_item_handler_registry("resize_bl_corner", "resize_handlers_bl")
            with dpg.item_handler_registry(tag="resize_handlers_br"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"corner"))
            if dpg.does_item_exist("resize_br_corner"):
                dpg.bind_item_handler_registry("resize_br_corner", "resize_handlers_br")
            with dpg.item_handler_registry(tag="resize_handlers_tl"):
                dpg.add_item_clicked_handler(callback=lambda s,a,u: self.ui_event.on_resize_press(s,a,"corner_top_left"))
            if dpg.does_item_exist("resize_tl_corner"):
                dpg.bind_item_handler_registry("resize_tl_corner", "resize_handlers_tl")

        # 事件綁定（全域滑鼠）
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(button=0, callback=self.ui_event.on_mouse_click)
            dpg.add_mouse_release_handler(button=0, callback=self.ui_event.on_mouse_release)

    def initialize_gui(self):
        if self.initialized:
            return
        
        
        # DPI 意識設定 (確保像素 1:1)
        try:
            # System-DPI aware：支援度高，邏輯簡單
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            # 後備：舊版 Windows（如 7/8）
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        
                
        dpg.create_context()
        # 預載 WinAPI 游標
        try:
            self._init_win_cursors()
        except Exception:
            pass

        # 延後載入資源（字型、圖片、icon）在 context 建立之後
        try:
            self._load_resources()
        except Exception:
            pass
        
        # 建立 viewport
        dpg.create_viewport(title='Refined UI', width=800, height=600, decorated=False, resizable=True)
        # 建立 UI 佈局（主視窗與內容）
        self.create_layout()
        
        # 顯示與必要同步
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        
        # 對齊 GUI_demo：使用 UIEvent 的 resize callback
        dpg.set_viewport_resize_callback(self.ui_event.resize_window_callback)
        self.sync_ui()
        self.clamp_viewport_to_work_area()
        self.initialized = True

    def handler(self):
        self.update_logic()

    def loop(self):
        # Initialize GUI
        self.initialize_gui()
        
        while dpg.is_dearpygui_running():
            
            # Handle per frame
            self.handler()
            
            # Render frame
            dpg.render_dearpygui_frame()
        dpg.destroy_context()


# 建立單一 UI 實例並提供 main 入口
UIInstance = UIHandle()

def main():
    UIInstance.loop()

if __name__ == "__main__":
    main()