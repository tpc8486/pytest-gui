from tkinter import Tk

from libs.model import UnittestProject
from libs.view import MainWindow


def main_loop(model=UnittestProject):
    """Run the main loop of the app."""
    root = Tk()

    view = MainWindow(root)

    view.project = view.load_project(root, model)

    view.mainloop()


if __name__ == "__main__":
    main_loop()
