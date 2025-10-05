import customtkinter as ctk
from chessbot import launch, run

class Screen:
    def __init__(self, window):
        self.window = window
        self.chess = None

        window.geometry("400x300")
        window.title("Chess-Bot")

        self.button_font = ("Roboto", 20, "bold")
        self.open_btn = ctk.CTkButton(window, text="Open Browser", command = self.open_browser, width=200, height=60, font=self.button_font)
        self.open_btn.pack(anchor="center", padx = 10, pady = 10)
        self.run_btn = ctk.CTkButton(window, text="Initialize Bot", command=self.run_bot, width=200, height=60, font=self.button_font)
        self.run_btn.pack(anchor="center", padx = 10, pady = 10)
        self.run_btn = ctk.CTkButton(window, text="Close Bot", command=self.window.destroy, width=200, height=60, font=self.button_font)
        self.run_btn.pack(anchor="center", padx = 10, pady = 10)

    def open_browser(self):
        self.chess_board = launch()

    def run_bot(self):
        if self.chess_board:
            try:
                run(self.chess_board)
            except Exception as e:
                print("Error during bot run:", e)
        else:
            print("Open the browser first to get board state.")

if __name__ == "__main__":
    ctk.set_appearance_mode("darkly")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    screen = Screen(app)
    app.mainloop()