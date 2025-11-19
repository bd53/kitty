from datetime import datetime
from kitty.boss import get_boss
from kitty.fast_data_types import Screen, add_timer, get_options
from kitty.utils import color_as_int
from kitty.tab_bar import DrawData, ExtraData, TabBarData, as_rgb, draw_attributed_string, draw_title, Formatter

opts = get_options()
timer_id = None

def draw_tab(draw: DrawData, screen: Screen, tab: TabBarData, _state: int, _length: int, index: int, last: bool, extra: ExtraData) -> int:
    global timer_id
    if timer_id is None:
        timer_id = add_timer(lambda _: get_boss().active_tab_manager.mark_tab_bar_dirty() if get_boss().active_tab_manager else None, 1, True)
    clock = datetime.now().strftime("%I:%M%p")
    date = datetime.now().strftime("%m.%d.%y")
    status_right = [(as_rgb(color_as_int(opts.color15)), clock), (as_rgb(color_as_int(opts.color8)), "    " + date)]
    status_length = sum(len(text) for _, text in status_right)
    tab_bg = screen.cursor.bg
    tab_fg = screen.cursor.fg
    default_bg = as_rgb(int(draw.default_bg))
    next_tab_bg = as_rgb(draw.tab_bg(extra.next_tab)) if extra.next_tab else default_bg
    needs_soft_separator = next_tab_bg == tab_bg
    if screen.cursor.x < screen.columns - status_length:
        screen.draw(" ")
        screen.cursor.bg = tab_bg
        draw_title(draw, screen, tab, index)
        if not needs_soft_separator:
            screen.draw(" ")
            screen.cursor.fg = tab_bg
            screen.cursor.bg = next_tab_bg
        else:
            prev_fg = screen.cursor.fg
            if tab_bg == tab_fg:
                screen.cursor.fg = default_bg
            elif tab_bg != default_bg:
                c1 = draw.inactive_bg.contrast(draw.default_bg)
                c2 = draw.inactive_bg.contrast(draw.inactive_fg)
                if c1 < c2:
                    screen.cursor.fg = default_bg
            screen.cursor.fg = prev_fg
    if last:
        draw_attributed_string(Formatter.reset, screen)
        screen.cursor.x = screen.columns - status_length
        screen.cursor.fg = 0
        for color, text in status_right:
            screen.cursor.fg = color
            screen.draw(text)
        screen.cursor.bg = 0
    return screen.cursor.x