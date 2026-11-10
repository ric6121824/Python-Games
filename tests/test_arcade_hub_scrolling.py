import tkinter as tk
import unittest

from arcade_hub import ArcadeHubApp


class ArcadeHubScrollingTests(unittest.TestCase):
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
