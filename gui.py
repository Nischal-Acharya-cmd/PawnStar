"""
Modern GUI for Chess.com Helper using CustomTkinter
Provides an intuitive interface for chess analysis and move suggestions
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import chess
from chessbot import ChessBot, ChessBotError


class ChessGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("♞ Chess.com Helper - PawnStar")
        self.geometry("1000x700")
        self.minsize(900, 650)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize ChessBot
        self.chess_bot = ChessBot()
        self.is_browser_open = False
        
        # Initialize settings variables
        self.analysis_time = 2.0
        self.update_interval = 2.0
        self.verbose_var = tk.BooleanVar(value=True)
        self.path_var = tk.StringVar(value=self.chess_bot.stockfish_path or "Auto-detected")
        
        # Create GUI elements
        self.create_widgets()
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Create simplified single-panel layout"""
        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("#2b2b2b", "#1a1a1a"))
        self.header_frame.pack(pady=15, padx=20, fill="x")
        
        title_label = ctk.CTkLabel(
            self.header_frame, 
            text="♞ Chess.com Helper - PawnStar",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#ffffff", "#e0e0e0")
        )
        title_label.pack(pady=15)
        
        # Status indicator
        self.app_status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="🟢 Ready",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.app_status_indicator.pack(pady=(0, 10))
        
        # Main container - horizontal layout
        main_container = ctk.CTkFrame(self, corner_radius=15)
        main_container.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Left sidebar (controls and settings) - scrollable
        self.left_frame = ctk.CTkScrollableFrame(main_container, corner_radius=15, width=320)
        self.left_frame.pack(side="left", fill="y", padx=(15, 7), pady=15)
        self.left_frame._parent_canvas.configure(width=320)  # Set fixed width for scrollable frame
        
        # Right side (console)
        self.right_frame = ctk.CTkFrame(main_container, corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(7, 15), pady=15)
        
        self.create_left_sidebar()
        self.create_right_panel()
        
        # Initialize console
        self.log_to_console("♞ Chess.com Helper - PawnStar v2.1")
        self.log_to_console("✨ Simplified interface loaded!")
        self.log_to_console("💡 All controls are now in the left sidebar")
        
        # Set default color
        self.set_user_color("white")

    def create_left_sidebar(self):
        """Create left sidebar with all controls and settings"""
        # Browser controls section
        browser_frame = ctk.CTkFrame(self.left_frame, corner_radius=12)
        browser_frame.pack(fill="x", padx=10, pady=(10, 8))
        
        ctk.CTkLabel(browser_frame, text="🌐 Browser Control", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.open_browser_btn = ctk.CTkButton(
            browser_frame, text="Open Chess.com", 
            command=self.open_browser, height=32,
            fg_color=("#2fa572", "#106A43"), hover_color=("#0d5d32", "#0d5d32")
        )
        self.open_browser_btn.pack(pady=5, padx=15, fill="x")
        
        self.browser_status = ctk.CTkLabel(browser_frame, text="Browser: Not Started", 
                                         font=ctk.CTkFont(size=11), text_color="gray70")
        self.browser_status.pack(pady=(0, 10))
        
        # Move display section
        move_frame = ctk.CTkFrame(self.left_frame, corner_radius=12)
        move_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(move_frame, text="📍 Current Move", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        # From/To boxes
        move_boxes_frame = ctk.CTkFrame(move_frame, fg_color="transparent")
        move_boxes_frame.pack(pady=10, padx=15, fill="x")
        
        # From box
        from_label_frame = ctk.CTkFrame(move_boxes_frame)
        from_label_frame.pack(side="left", padx=(0, 5), fill="x", expand=True)
        ctk.CTkLabel(from_label_frame, text="From:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=5)
        self.from_box = ctk.CTkLabel(from_label_frame, text="--", 
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   fg_color=("#3B82F6", "#2563EB"), corner_radius=8)
        self.from_box.pack(pady=(0, 10), padx=5, fill="x")
        
        # To box  
        to_label_frame = ctk.CTkFrame(move_boxes_frame)
        to_label_frame.pack(side="right", padx=(5, 0), fill="x", expand=True)
        ctk.CTkLabel(to_label_frame, text="To:", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=5)
        self.to_box = ctk.CTkLabel(to_label_frame, text="--",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 fg_color=("#10B981", "#059669"), corner_radius=8)
        self.to_box.pack(pady=(0, 10), padx=5, fill="x")
        
        # Color selection
        color_frame = ctk.CTkFrame(self.left_frame, corner_radius=12)
        color_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(color_frame, text="♟️ Your Color", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(8, 3))
        
        self.color_var = tk.StringVar(value="white")
        color_radio_frame = ctk.CTkFrame(color_frame, fg_color="transparent")
        color_radio_frame.pack(pady=3)
        
        self.white_radio = ctk.CTkRadioButton(
            color_radio_frame, text="White", variable=self.color_var, 
            value="white", command=lambda: self.set_user_color("white")
        )
        self.white_radio.pack(side="left", padx=15)
        
        self.black_radio = ctk.CTkRadioButton(
            color_radio_frame, text="Black", variable=self.color_var, 
            value="black", command=lambda: self.set_user_color("black")
        )
        self.black_radio.pack(side="left", padx=15)
        
        # Game operations
        game_frame = ctk.CTkFrame(self.left_frame, corner_radius=12)
        game_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(game_frame, text="🎮 Game Operations", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(8, 3))
        
        self.update_board_btn = ctk.CTkButton(
            game_frame, text="Update Board", command=self.update_board,
            height=28, fg_color=("#1f6aa5", "#144870"), hover_color=("#144870", "#0e3a56")
        )
        self.update_board_btn.pack(pady=3, padx=10, fill="x")
        
        self.analyze_btn = ctk.CTkButton(
            game_frame, text="Get Best Move", command=self.analyze_position,
            height=28, fg_color=("#9c27b0", "#7b1fa2"), hover_color=("#7b1fa2", "#6a1b87")
        )
        self.analyze_btn.pack(pady=(3, 8), padx=10, fill="x")
        
        # Settings section
        settings_frame = ctk.CTkFrame(self.left_frame, corner_radius=12)
        settings_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(settings_frame, text="⚙️ Settings", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(8, 3))
        
        # Analysis time
        ctk.CTkLabel(settings_frame, text="Analysis Time:", 
                    font=ctk.CTkFont(size=10)).pack(pady=(3, 0), padx=10, anchor="w")
        self.analysis_time_slider = ctk.CTkSlider(
            settings_frame, from_=0.5, to=5.0, number_of_steps=9,
            command=self.update_analysis_time, height=16
        )
        self.analysis_time_slider.set(self.analysis_time)
        self.analysis_time_slider.pack(pady=3, padx=10, fill="x")
        
        self.analysis_time_label = ctk.CTkLabel(
            settings_frame, text=f"⏱️ {self.analysis_time:.1f}s",
            font=ctk.CTkFont(size=9), text_color="gray70"
        )
        self.analysis_time_label.pack(pady=(0, 5))
        
        # Update interval
        ctk.CTkLabel(settings_frame, text="Update Interval:", 
                    font=ctk.CTkFont(size=10)).pack(pady=(3, 0), padx=10, anchor="w")
        self.update_interval_slider = ctk.CTkSlider(
            settings_frame, from_=1.0, to=10.0, number_of_steps=9,
            command=self.update_update_interval, height=16
        )
        self.update_interval_slider.set(self.update_interval)
        self.update_interval_slider.pack(pady=3, padx=10, fill="x")
        
        self.update_interval_label = ctk.CTkLabel(
            settings_frame, text=f"🔄 {self.update_interval:.1f}s",
            font=ctk.CTkFont(size=9), text_color="gray70"
        )
        self.update_interval_label.pack(pady=(0, 8))

    def create_right_panel(self):
        """Create right panel with console"""
        # Console section
        console_frame = ctk.CTkFrame(self.right_frame, corner_radius=12)
        console_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        ctk.CTkLabel(console_frame, text="📝 Console", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.console_text = ctk.CTkTextbox(
            console_frame, font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.console_text.pack(pady=10, padx=15, fill="both", expand=True)

    def update_move_display(self, from_square="--", to_square="--"):
        """Update the From/To move display boxes"""
        self.from_box.configure(text=from_square)
        self.to_box.configure(text=to_square)
    
    def update_analysis_time(self, value):
        """Update analysis time setting"""
        self.analysis_time = float(value)
        self.analysis_time_label.configure(text=f"⏱️ {self.analysis_time:.1f}s")

    def update_update_interval(self, value):
        """Update auto-update interval setting"""
        self.update_interval = float(value)
        self.update_interval_label.configure(text=f"🔄 {self.update_interval:.1f}s")
        if hasattr(self.chess_bot, 'auto_update_interval'):
            self.chess_bot.auto_update_interval = self.update_interval

    def update_status_display(self, message):
        """Add message to console (legacy method for compatibility)"""
        self.log_to_console(message)

    def browse_stockfish(self):
        """Browse for Stockfish executable"""
        filename = filedialog.askopenfilename(
            title="Select Stockfish executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.path_var.set(filename)
            self.chess_bot.stockfish_path = filename
            self.log_to_console(f"🔧 Stockfish path updated: {filename}")

    def test_stockfish_engine(self):
        """Test if Stockfish engine is working"""
        try:
            path = self.path_var.get()
            if path == "Auto-detected":
                path = None
            
            # Temporarily set path and test
            old_path = self.chess_bot.stockfish_path
            self.chess_bot.stockfish_path = path
            
            # Try to initialize engine
            if self.chess_bot.engine:
                self.chess_bot.engine.quit()
                self.chess_bot.engine = None
            
            self.chess_bot.start_engine()
            
            if self.chess_bot.engine:
                self.log_to_console("✅ Stockfish engine test successful!")
                messagebox.showinfo("Engine Test", "✅ Stockfish engine is working correctly!")
            else:
                raise Exception("Failed to initialize engine")
                
        except Exception as e:
            self.chess_bot.stockfish_path = old_path
            error_msg = f"❌ Engine test failed: {e}"
            self.log_to_console(error_msg)
            messagebox.showerror("Engine Test Failed", error_msg)

    def update_status_display(self, message):
        """Add message to console (legacy method for compatibility)"""
        self.log_to_console(message)

    def open_browser(self):
        """Alias for start_browser for compatibility"""
        self.start_browser()

    def analyze_position(self):
        """Update board and suggest best move"""
        def analysis_thread():
            try:
                # First update the board
                self.update_status("Updating board...")
                self.log_to_console("🔄 Updating board before analysis...")
                
                # Update board from current game state
                board, moves = self.chess_bot.update_board_from_moves()
                
                # Display board update results on main thread
                self.after(0, lambda b=board, m=moves: self.display_board_update(b, m))
                
                # Small delay to let board update complete
                import time
                time.sleep(0.5)
                
                # Then analyze the position
                self.after(0, self.suggest_move)
                
            except Exception as e:
                error_msg = f"Failed to update board before analysis: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
        
        # Run in background thread
        threading.Thread(target=analysis_thread, daemon=True).start()

    def start_browser(self):
        """Start Chrome browser and navigate to Chess.com"""
        def start_browser_thread():
            try:
                self.update_status("Starting browser...")
                self.log_to_console("🚀 Starting Chrome browser...")
                
                # Update Stockfish path if changed
                new_path = self.path_var.get()
                if new_path != "Auto-detected" and new_path != self.chess_bot.stockfish_path:
                    self.chess_bot.stockfish_path = new_path
                
                # Start driver
                self.chess_bot.start_driver()
                self.log_to_console("✅ Chrome driver started")
                
                # Open Chess.com
                self.log_to_console("🌐 Navigating to Chess.com...")
                self.chess_bot.open_chess_com()
                self.log_to_console("✅ Chess.com loaded")
                
                # Update UI on success
                self.after(0, self.on_browser_started)
                
            except Exception as e:
                error_msg = f"Browser Error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
        
        # Disable start button and run in thread
        self.open_browser_btn.configure(state="disabled", text="Starting...")
        threading.Thread(target=start_browser_thread, daemon=True).start()

    def on_browser_started(self):
        """Update UI after browser starts successfully"""
        self.is_browser_open = True
        self.open_browser_btn.configure(text="✅ Browser Started", state="disabled")
        self.browser_status.configure(text="🟢 Browser connected", text_color="green")
        
        # Enable all action buttons
        self.update_board_btn.configure(state="normal")
        self.analyze_btn.configure(state="normal")
        
        self.update_status("Browser ready - start a Chess.com game")
        self.update_status_display("✅ Browser started successfully!")
        self.update_status_display("Ready for chess analysis and move suggestions")

    def set_user_color(self, color):
        """Set the user's color choice"""
        color = color.lower()
        
        # Update the ChessBot
        self.chess_bot.set_user_color(color)
        
        # Update the UI variable to ensure sync
        self.color_var.set(color)
        
        # Provide visual feedback
        if color == "white":
            self.log_to_console("🎨 Set user color to: ⚪ White")
        else:
            self.log_to_console("🎨 Set user color to: ⚫ Black")
        
        self.log_to_console(f"   You will be playing as {color.title()}")
        
        # Update app status indicator
        self.app_status_indicator.configure(text=f"🎯 Playing as {color.title()}")

    def update_board(self):
        """Get current board state using move history"""
        def update_board_thread():
            try:
                self.update_status("Getting board state...")
                self.log_to_console("📋 Getting current board state from move history...")
                
                board, moves = self.chess_bot.update_board_from_moves()
                
                # Display results
                self.after(0, lambda b=board, m=moves: self.display_board_update(b, m))
                
            except ChessBotError as e:
                error_msg = f"Board Error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
        
        self.update_board_btn.configure(text="Getting Board...", state="disabled")
        threading.Thread(target=update_board_thread, daemon=True).start()

    def display_board_update(self, board, moves):
        """Display board state information in console"""
        self.log_separator()
        self.log_to_console("✅ BOARD STATE LOADED")
        self.log_to_console(f"   Total moves: {len(moves)}")
        if moves:
            recent_moves = moves[-6:] if len(moves) > 6 else moves
            self.log_to_console(f"   Recent moves: {' → '.join(recent_moves)}")
        else:
            self.log_to_console("   Starting position")
        
        # Show user color without turn confusion
        user_color = self.chess_bot.user_color
        if user_color:
            self.log_to_console(f"   � You are playing as: {user_color.title()}")
        
        self.log_to_console(f"   Position FEN: {board.fen()}")
        self.log_to_console("")
        self.log_to_console("📋 Current Position:")
        self._log_formatted_board(board)
        
        self.update_board_btn.configure(text="📋 Get Board State", state="normal")
        self.update_status("Board loaded - ready for analysis")
        self.update_status_display(f"📋 Board updated: {len(moves)} moves played")

    def suggest_move(self):
        """Get move suggestion from Stockfish"""
        def suggest_move_thread():
            try:
                self.update_status("Analyzing position...")
                self.log_to_console("🧠 Analyzing position with Stockfish...")
                
                # Use analysis time from settings
                analysis_time = self.analysis_time
                
                # Add a timeout mechanism
                import threading
                import time
                
                result = [None, None]  # [best_move, info]
                error = [None]
                
                def analysis_worker():
                    try:
                        best_move, info = self.chess_bot.get_best_move(time_limit=analysis_time)
                        result[0] = best_move
                        result[1] = info
                    except Exception as e:
                        error[0] = e
                
                # Start analysis in a separate thread with timeout
                analysis_thread = threading.Thread(target=analysis_worker)
                analysis_thread.daemon = True
                analysis_thread.start()
                
                # Wait for analysis with timeout
                timeout = analysis_time + 5.0  # Add 5 seconds buffer
                analysis_thread.join(timeout)
                
                if analysis_thread.is_alive():
                    # Analysis is taking too long, restart engine
                    self.after(0, lambda: self.log_to_console("⚠️ Analysis timeout, restarting engine..."))
                    try:
                        self.chess_bot.engine.quit()
                    except:
                        pass
                    self.chess_bot.engine = None
                    
                    error_msg = "Analysis timed out. Engine has been restarted. Try again."
                    self.after(0, lambda msg=error_msg: self.show_error(msg))
                    return
                
                if error[0]:
                    raise error[0]
                
                if result[0] and result[1]:
                    # Display results
                    self.after(0, lambda m=result[0], i=result[1]: self.display_move_suggestion(m, i))
                else:
                    raise ChessBotError("No analysis result received")
                
            except ChessBotError as e:
                error_msg = f"Analysis Error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                self.after(0, lambda msg=error_msg: self.show_error(msg))
        
        self.analyze_btn.configure(text="Analyzing...", state="disabled")
        threading.Thread(target=suggest_move_thread, daemon=True).start()

    def display_move_suggestion(self, best_move, info):
        """Display move suggestion in console"""
        self.log_separator()
        user_color = self.chess_bot.user_color or "Your"
        self.log_to_console(f"🧠 STOCKFISH ANALYSIS ({user_color.title()} moves)")
        self.log_to_console(f"   🎯 Best move: {best_move}")
        self.log_to_console(f"   📊 Evaluation: {info.get('score', 'N/A')}")
        self.log_to_console(f"   🔍 Depth: {info.get('depth', 'N/A')}")
        self.log_to_console(f"   ⚡ Nodes: {info.get('nodes', 'N/A')}")
        
        pv = info.get('pv', [])
        if pv and len(pv) > 1:
            pv_str = ' → '.join(pv[:5])  # Show first 5 moves
            if len(pv) > 5:
                pv_str += "..."
            self.log_to_console(f"   📈 Best line: {pv_str}")
        
        self.log_to_console("")
        self.log_to_console(f"💡 Suggested move for {user_color.title()}: {best_move}")
        
        # Update From/To move display
        uci_move = info.get('move_uci', '')
        if uci_move and len(uci_move) >= 4:
            from_square = uci_move[:2].upper()  # e.g., "e2" -> "E2"
            to_square = uci_move[2:4].upper()   # e.g., "e4" -> "E4"
            self.update_move_display(from_square, to_square)
            self.log_to_console(f"   📍 Move: {from_square} → {to_square}")
        
        # Update analysis display
        analysis_text = f"🎯 Best Move: {best_move}\n"
        analysis_text += f"📊 Score: {info.get('score', 'N/A')}\n"
        analysis_text += f"🔍 Depth: {info.get('depth', 'N/A')}\n"
        analysis_text += f"⚡ Nodes: {info.get('nodes', 'N/A')}\n"
        
        pv = info.get('pv', [])
        if pv and len(pv) > 1:
            pv_str = ' → '.join(pv[:3])  # Show first 3 moves
            analysis_text += f"📈 Line: {pv_str}"
        
        # Show in UCI notation too for clarity
        if uci_move:
            self.log_to_console(f"   (UCI: {uci_move})")
        
        self.analyze_btn.configure(text="🧠 Suggest Best Move", state="normal")
        self.update_status(f"Analysis complete - suggested: {best_move}")
        self.update_status_display(f"💡 Best move: {best_move} ({info.get('score', 'N/A')})")

    def _log_formatted_board(self, board):
        """Log a nicely formatted chess board"""
        board_str = str(board)
        lines = board_str.split('\n')
        
        self.log_to_console("   ┌─────────────────┐")
        for i, line in enumerate(lines):
            rank = 8 - i
            self.log_to_console(f" {rank} │ {line} │")
        self.log_to_console("   └─────────────────┘")
        self.log_to_console("     a b c d e f g h")

    def log_separator(self):
        """Add a separator line to console"""
        self.log_to_console("─" * 50)

    def log_to_console(self, message):
        """Add message to console output"""
        # Only log if verbose mode is enabled or it's an important message
        if self.verbose_var.get() or any(keyword in message.lower() for keyword in ["error", "success", "started", "stopped", "suggestion"]):
            self.console_text.insert("end", f"{message}\n")
            self.console_text.see("end")

    def clear_console(self):
        """Clear the console output"""
        self.console_text.delete("1.0", "end")
        self.log_to_console("♞ Chess.com Helper - PawnStar")
        self.log_to_console("Console cleared")
        self.log_separator()
        
        # Also clear status display
        self.status_display.delete("1.0", "end")
        self.update_status_display("Status cleared")

    def update_status(self, message):
        """Update status (now just logs to console)"""
        self.log_to_console(f"📊 Status: {message}")

    def show_error(self, message):
        """Show error message"""
        self.log_to_console(f"❌ ERROR: {message}")
        
        # Re-enable buttons that might have been disabled
        self.open_browser_btn.configure(text="🚀 Start Browser", state="normal")
        self.update_board_btn.configure(text="📋 Get Board State", state="normal")
        self.analyze_btn.configure(text="🧠 Suggest Best Move", state="normal")
        
        # Show popup for critical errors
        if "failed" in message.lower() or "error" in message.lower():
            messagebox.showerror("Error", message)

    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop auto-update first
            if self.chess_bot.auto_update_enabled:
                self.chess_bot.stop_auto_update()
            self.chess_bot.close()
        except:
            pass
        self.destroy()


def main():
    """Main entry point"""
    app = ChessGUI()
    app.mainloop()


if __name__ == "__main__":
    main()