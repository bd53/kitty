from datetime import datetime
from kitty.boss import get_boss
from kitty.fast_data_types import Screen, add_timer, get_options
from kitty.utils import color_as_int
from kitty.tab_bar import DrawData, ExtraData, TabBarData, as_rgb, draw_attributed_string, draw_title, Formatter

opts = get_options()
timer_id = None

def draw_tab(draw_data: DrawData, screen: Screen, tab: TabBarData, before: int, max_title_length: int, index: int, is_last: bool, extra_data: ExtraData) -> int:
    global timer_id
    if timer_id is None:
        timer_id = add_timer(lambda _: get_boss().active_tab_manager.mark_tab_bar_dirty() if get_boss().active_tab_manager else None, 1, True)
    clock = datetime.now().strftime("%H:%M")
    date = datetime.now().strftime("     %m.%d.%y")
    right_cells = [(as_rgb(color_as_int(opts.color15)), clock), (as_rgb(color_as_int(opts.color8)), date)]
    right_status_length = sum(len(cell[1]) for cell in right_cells)
    tab_bg = screen.cursor.bg
    tab_fg = screen.cursor.fg
    default_bg = as_rgb(int(draw_data.default_bg))
    next_tab_bg = default_bg
    needs_soft_separator = False
    if extra_data.next_tab:
        next_tab_bg = as_rgb(draw_data.tab_bg(extra_data.next_tab))
        needs_soft_separator = next_tab_bg == tab_bg
    if screen.cursor.x < screen.columns - right_status_length:
        screen.draw(" ")
        screen.cursor.bg = tab_bg
        draw_title(draw_data, screen, tab, index)
        if not needs_soft_separator:
            screen.draw(" ")
            screen.cursor.fg = tab_bg
            screen.cursor.bg = next_tab_bg
        else:
            prev_fg = screen.cursor.fg
            if tab_bg == tab_fg:
                screen.cursor.fg = default_bg
            elif tab_bg != default_bg:
                c1 = draw_data.inactive_bg.contrast(draw_data.default_bg)
                c2 = draw_data.inactive_bg.contrast(draw_data.inactive_fg)
                if c1 < c2:
                    screen.cursor.fg = default_bg
            screen.cursor.fg = prev_fg
    if is_last:
        draw_attributed_string(Formatter.reset, screen)
        screen.cursor.x = screen.columns - right_status_length
        screen.cursor.fg = 0
        for color, text in right_cells:
            screen.cursor.fg = color
            screen.draw(text)
        screen.cursor.bg = 0
    return screen.cursor.x
