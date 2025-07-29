from collections.abc import Callable

from jbqt.common.consts import GlobalRefs


def debug_scroll_pos(func: Callable):
    def wrapper(self, *args, **kwargs):
        if GlobalRefs.scroll_area is None:
            return func(self, *args, **kwargs)
        focus = None
        if GlobalRefs.main_window:
            focus = GlobalRefs.main_window.focusWidget()
        print(f"scroll pos {func.__name__}")
        print("before", GlobalRefs.scroll_area.verticalScrollBar().value(), focus)
        result = func(self, *args, **kwargs)

        if GlobalRefs.main_window:
            focus = GlobalRefs.main_window.focusWidget()
        print(
            f"after {GlobalRefs.scroll_area.verticalScrollBar().value()} {focus}\n"
        )

        return result

    return wrapper


def debug_scroll_pos_no_args(func: Callable):
    def wrapper(self):
        if GlobalRefs.scroll_area is None:
            return func(self)
        focus = None
        if GlobalRefs.main_window:
            focus = GlobalRefs.main_window.focusWidget()
        print(f"scroll pos {func.__name__}")
        print("before", GlobalRefs.scroll_area.verticalScrollBar().value(), focus)
        result = func(self)
        if GlobalRefs.main_window:
            focus = GlobalRefs.main_window.focusWidget()
        print(
            f"after {GlobalRefs.scroll_area.verticalScrollBar().value()} {focus}\n"
        )

        return result

    return wrapper


def _call_func(func: Callable, *args, **kwargs):
    if args and kwargs:
        return func(*args, **kwargs)
    elif args:
        return func(*args)
    elif kwargs:
        return func(**kwargs)
    else:
        return func()


def preserve_scroll(func: Callable):
    def wrapper(self, *args, **kwargs):
        if GlobalRefs.scroll_area is None:
            return _call_func(func, self, *args, **kwargs)

        scroll_pos = GlobalRefs.scroll_area.verticalScrollBar().value()
        focus = GlobalRefs.app.focusWidget()
        result = _call_func(
            func,
            self,
            *args,
            **kwargs,
        )
        GlobalRefs.scroll_area.verticalScrollBar().setValue(scroll_pos)
        focus.setFocus()
        return result

    return wrapper
