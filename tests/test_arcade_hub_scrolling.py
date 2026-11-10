import tkinter as tk
import unittest
from unittest import mock

from arcade_hub import ArcadeHubApp


class ArcadeHubScrollingTests(unittest.TestCase):
    def _require_touchpad_scroll(self, root):
        try:
            root.bind("<TouchpadScroll>")
        except tk.TclError:
            self.skipTest("This Tk runtime does not support TouchpadScroll")

    def test_touchpad_scrolls_both_directions_over_list_and_refreshed_controls(self):
        root = tk.Tk()
        try:
            self._require_touchpad_scroll(root)
            app = ArcadeHubApp(root)
            root.update_idletasks()

            for refreshed in (False, True):
                if refreshed:
                    app.refresh_games()
                    root.update_idletasks()
                card = app.content.winfo_children()[0]
                title, description, buttons = card.winfo_children()
                play, readme = buttons.winfo_children()
                targets = {
                    "canvas": app.canvas,
                    "content": app.content,
                    "card": card,
                    "title": title,
                    "description": description,
                    "play": play,
                    "readme": readme,
                }
                for name, widget in targets.items():
                    with self.subTest(refreshed=refreshed, target=name):
                        app.canvas.yview_moveto(0)
                        initial = app.canvas.yview()[0]
                        widget.event_generate(
                            "<TouchpadScroll>",
                            delta=(3 << 16) | (-8 & 0xffff),
                            rootx=widget.winfo_rootx() + 2,
                            rooty=widget.winfo_rooty() + 2,
                        )
                        root.update_idletasks()
                        scrolled = app.canvas.yview()[0]
                        region = app.canvas.bbox("all")
                        self.assertAlmostEqual(
                            (scrolled - initial) * (region[3] - region[1]), 8
                        )

                        widget.event_generate(
                            "<TouchpadScroll>",
                            delta=(-3 << 16) | 8,
                            rootx=max(widget.winfo_rootx(), app.canvas.winfo_rootx()) + 2,
                            rooty=max(widget.winfo_rooty(), app.canvas.winfo_rooty()) + 2,
                        )
                        root.update_idletasks()
                        self.assertAlmostEqual(app.canvas.yview()[0], initial)

                        for delta in (3 << 16, -3 << 16, 0):
                            widget.event_generate(
                                "<TouchpadScroll>",
                                delta=delta,
                                rootx=widget.winfo_rootx() + 2,
                                rooty=widget.winfo_rooty() + 2,
                            )
                            root.update_idletasks()
                            self.assertEqual(app.canvas.yview()[0], initial)
        finally:
            root.destroy()

    def test_touchpad_events_from_another_window_do_not_scroll_the_game_list(self):
        root = tk.Tk()
        try:
            self._require_touchpad_scroll(root)
            app = ArcadeHubApp(root)
            root.update_idletasks()
            initial = app.canvas.yview()
            other_window = tk.Toplevel(root)
            other_window.update_idletasks()
            other_window.event_generate(
                "<TouchpadScroll>",
                delta=-8 & 0xffff,
                rootx=app.canvas.winfo_rootx() + 10,
                rooty=app.canvas.winfo_rooty() + 10,
            )
            root.update_idletasks()
            self.assertEqual(app.canvas.yview(), initial)
        finally:
            root.destroy()

    def test_mouse_wheel_still_works_when_tk_has_no_touchpad_event(self):
        root = tk.Tk()
        try:
            bind_class = root.bind_class

            def legacy_bind(tag, sequence=None, func=None, add=None):
                if sequence == "<TouchpadScroll>":
                    raise tk.TclError('bad event type or keysym "TouchpadScroll"')
                return bind_class(tag, sequence, func, add)

            with mock.patch.object(root, "bind_class", side_effect=legacy_bind):
                app = ArcadeHubApp(root)
            root.update_idletasks()
            initial = app.canvas.yview()[0]
            app.canvas.event_generate(
                "<MouseWheel>",
                delta=-120,
                rootx=app.canvas.winfo_rootx() + 10,
                rooty=app.canvas.winfo_rooty() + 10,
            )
            root.update_idletasks()
            self.assertGreater(app.canvas.yview()[0], initial)
        finally:
            root.destroy()

    def test_wheel_events_from_another_window_do_not_scroll_the_game_list(self):
        root = tk.Tk()
        other_window = None
        try:
            root.geometry("980x640+0+0")
            app = ArcadeHubApp(root)
            root.update_idletasks()
            app.canvas.yview_moveto(0)
            initial_position = app.canvas.yview()

            other_window = tk.Toplevel(root)
            other_window.geometry("200x200+0+0")
            other_window.update_idletasks()
            other_window.event_generate(
                "<MouseWheel>",
                delta=-120,
                rootx=app.canvas.winfo_rootx() + 10,
                rooty=app.canvas.winfo_rooty() + 10,
            )
            root.update()

            self.assertEqual(app.canvas.yview(), initial_position)
        finally:
            if other_window is not None:
                other_window.destroy()
            root.destroy()

    def test_refreshed_game_controls_keep_scrolling_the_list(self):
        root = tk.Tk()
        try:
            app = ArcadeHubApp(root)
            root.update_idletasks()
            app.refresh_games()
            root.update_idletasks()
            button = next(
                child
                for card in app.content.winfo_children()
                for row in card.winfo_children()
                for child in row.winfo_children()
                if isinstance(child, tk.Button) and child.cget("text") == "Play"
            )
            app.canvas.yview_moveto(0)
            button.event_generate(
                "<MouseWheel>",
                delta=-120,
                rootx=button.winfo_rootx() + 2,
                rooty=button.winfo_rooty() + 2,
            )
            root.update()

            self.assertGreater(app.canvas.yview()[0], 0)
        finally:
            root.destroy()
