"""
Chess.com Scraper and Stockfish Integration Module
Handles web scraping, chess board management, and engine analysis
"""

import chess
import chess.engine
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil
import threading
from typing import Optional, Tuple, List, Callable


class ChessBotError(Exception):
    """Custom exception for ChessBot errors"""
    pass


class ChessBot:
    def __init__(self, stockfish_path: Optional[str] = None):
        """Initialize the ChessBot with Stockfish engine"""
        self.driver = None
        self.board = chess.Board()
        self.engine = None
        self.user_color = None
        self.move_history = []
        self.initial_board_set = False
        
        # Auto-update functionality
        self.auto_update_enabled = False
        self.auto_update_thread = None
        self.auto_update_interval = 2.0
        self.update_callback = None
        self.auto_suggest_moves = False
        self.suggestion_callback = None
        self._stop_auto_update = threading.Event()
        
        # Find Stockfish
        self.stockfish_path = stockfish_path or self._find_stockfish()
        
    def _find_stockfish(self) -> str:
        """Auto-detect Stockfish executable"""
        paths = [
            shutil.which("stockfish"),
            os.path.abspath("./stockfish/stockfish-macos-m1-apple-silicon"),
            "/usr/local/bin/stockfish",
            "/opt/homebrew/bin/stockfish",
        ]
        
        for path in paths:
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                print(f"Found Stockfish at: {path}")
                return path
        
        raise ChessBotError("Stockfish not found. Please install Stockfish or provide path.")
    
    def _validate_position(self, board: chess.Board = None) -> List[chess.Move]:
        """Validate board position and return legal moves"""
        board = board or self.board
        if board.is_game_over():
            raise ChessBotError(f"Game is over. Result: {board.result()}")
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            raise ChessBotError("No legal moves available")
        
        return legal_moves
    
    def start_driver(self, headless: bool = False) -> None:
        """
        Initialize Chrome WebDriver
        
        Args:
            headless: Whether to run browser in headless mode
        """
        if self.driver:
            return  # Already initialized
            
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            raise ChessBotError(f"Failed to start Chrome driver: {e}")
    
    def open_chess_com(self, url: str = "https://www.chess.com/play/computer") -> None:
        """
        Navigate to Chess.com computer play page
        
        Args:
            url: Chess.com URL to open
        """
        if not self.driver:
            raise ChessBotError("Driver not initialized. Call start_driver() first.")
        
        try:
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "board-layout-board")),
                    EC.presence_of_element_located((By.CLASS_NAME, "board")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='board']"))
                )
            )
            
            # Wait a bit more for pieces to load
            time.sleep(2)
            
        except Exception as e:
            raise ChessBotError(f"Failed to load Chess.com: {e}")
    
    def start_auto_update(self, callback: Optional[Callable] = None, interval: float = 2.0, auto_suggest: bool = False) -> None:
        """
        Start automatic detection and updating of board state
        
        Args:
            callback: Function to call when board is updated (board, moves)
            interval: How often to check for updates in seconds
            auto_suggest: If True, automatically suggest best move when it's user's turn
        """
        if self.auto_update_enabled:
            print("⚠️ Auto-update already running")
            return
            
        if not self.driver:
            raise ChessBotError("Driver not initialized. Call start_driver() first.")
        
        self.update_callback = callback
        self.auto_update_interval = interval
        self.auto_suggest_moves = auto_suggest
        self.auto_update_enabled = True
        self._stop_auto_update.clear()
        
        # Start the auto-update thread
        self.auto_update_thread = threading.Thread(target=self._auto_update_worker, daemon=True)
        self.auto_update_thread.start()
        
        suggest_msg = " with auto-suggestions" if auto_suggest else ""
        print(f"🔄 Auto-update started{suggest_msg} (checking every {interval}s)")
    
    def set_suggestion_callback(self, callback: Optional[Callable] = None) -> None:
        """
        Set callback function for auto-suggestions
        
        Args:
            callback: Function to call when move is auto-suggested (best_move, info)
        """
        self.suggestion_callback = callback
    
    def stop_auto_update(self) -> None:
        """Stop automatic board updates"""
        if not self.auto_update_enabled:
            return
            
        self.auto_update_enabled = False
        self._stop_auto_update.set()
        
        if self.auto_update_thread and self.auto_update_thread.is_alive():
            self.auto_update_thread.join(timeout=1.0)
        
        print("⏹️ Auto-update stopped")
    
    def _auto_update_worker(self) -> None:
        """Worker thread for automatic board updates"""
        last_move_count = len(self.move_history)
        last_moves_hash = None  # Track actual move content changes
        error_count = 0
        max_errors = 5
        last_update_time = 0  # Track time to prevent rapid updates
        min_update_interval = 1.0  # Minimum 1 second between updates
        
        print(f"🔄 Auto-update worker started (interval: {self.auto_update_interval}s)")
        
        while self.auto_update_enabled and not self._stop_auto_update.is_set():
            try:
                current_time = time.time()
                
                # Check for new moves
                current_moves = self._scrape_move_list()
                current_move_count = len(current_moves)
                
                # Create a hash of the moves to detect actual content changes
                current_moves_hash = hash(tuple(current_moves)) if current_moves else None
                
                # Only update if there's an actual change AND enough time has passed
                time_since_last_update = current_time - last_update_time
                significant_change = (current_move_count != last_move_count or 
                                    current_moves_hash != last_moves_hash)
                
                if (significant_change and 
                    current_moves_hash is not None and 
                    time_since_last_update >= min_update_interval):
                    
                    print(f"🔄 Auto-detected move change: {last_move_count} → {current_move_count}")
                    
                    try:
                        board, moves = self.update_board_from_moves(silent=True)
                        
                        # Only proceed if the board was actually updated with different moves
                        processed_moves_hash = hash(tuple(moves)) if moves else None
                        if (len(moves) != last_move_count or 
                            processed_moves_hash != last_moves_hash):
                            
                            last_move_count = len(moves)
                            last_moves_hash = processed_moves_hash
                            last_update_time = current_time
                            error_count = 0  # Reset error count on success
                            
                            # Call the update callback if provided
                            if self.update_callback:
                                try:
                                    self.update_callback(board, moves)
                                except Exception as e:
                                    print(f"⚠️ Update callback error: {e}")
                            
                            # Check if it's user's turn and auto-suggest is enabled
                            if self.auto_suggest_moves and self.user_color:
                                user_is_white = (self.user_color.lower() == 'white')
                                current_turn_is_white = board.turn
                                
                                if user_is_white == current_turn_is_white:
                                    print(f"🎯 It's your turn ({self.user_color.title()}) - getting auto-suggestion...")
                                    try:
                                        best_move, info = self.get_best_move(time_limit=1.5)
                                        
                                        # Call suggestion callback if provided
                                        if self.suggestion_callback:
                                            try:
                                                self.suggestion_callback(best_move, info)
                                            except Exception as e:
                                                print(f"⚠️ Suggestion callback error: {e}")
                                        else:
                                            # Default console output if no callback
                                            print(f"💡 Auto-suggestion: {best_move}")
                                            
                                    except Exception as e:
                                        print(f"⚠️ Auto-suggestion error: {e}")
                        
                    except Exception as e:
                        print(f"⚠️ Auto-update error: {e}")
                        error_count += 1
                
                # Wait before next check
                if not self._stop_auto_update.wait(self.auto_update_interval):
                    continue  # Continue if not stopped
                else:
                    break  # Stop was requested
                    
            except Exception as e:
                print(f"⚠️ Auto-update worker error: {e}")
                error_count += 1
                
                # If too many errors, slow down checking
                if error_count >= max_errors:
                    print(f"⚠️ Too many auto-update errors ({error_count}), slowing down...")
                    wait_time = min(self.auto_update_interval * 3, 10.0)
                else:
                    wait_time = self.auto_update_interval
                
                # Wait before retrying
                if self._stop_auto_update.wait(wait_time):
                    break
        
        print("🛑 Auto-update worker stopped")
    
    def set_user_color(self, color: str) -> None:
        """
        Set the color the user is playing
        
        Args:
            color: 'white' or 'black'
        """
        if color.lower() not in ['white', 'black']:
            raise ChessBotError("Color must be 'white' or 'black'")
        self.user_color = color.lower()
    
    def update_board_from_moves(self, silent: bool = False) -> Tuple[chess.Board, List[str]]:
        """
        Update board state by parsing the move list from Chess.com
        This is the primary method for getting board state - it reconstructs the position from move history
        
        Args:
            silent: If True, don't print output unless there are actual changes
        
        Returns:
            Tuple of (updated chess.Board, list of moves in SAN notation)
        """
        if not self.driver:
            raise ChessBotError("Driver not initialized. Call start_driver() first.")
        
        try:
            # Scrape current move list
            moves = self._scrape_move_list()
            
            # Check if there are actually new moves or this is the first time
            moves_changed = (not self.initial_board_set or 
                           len(moves) != len(self.move_history) or 
                           moves != self.move_history)
            
            if moves_changed:
                # Reset board to starting position
                self.board = chess.Board()
                
                # Apply all moves from the move list
                applied_moves = []
                for i, move_san in enumerate(moves):
                    try:
                        # Clean up the move notation
                        clean_move = move_san.strip()
                        
                        # Skip move numbers and dots
                        if '.' in clean_move and clean_move.replace('.', '').isdigit():
                            continue
                        
                        # Try to parse and apply the move
                        if clean_move:
                            move = self.board.parse_san(clean_move)
                            self.board.push(move)
                            applied_moves.append(clean_move)
                            
                    except (ValueError, chess.InvalidMoveError) as e:
                        if not silent:
                            print(f"Warning: Could not parse move '{move_san}': {e}")
                        continue
                
                # Update our move history
                old_count = len(self.move_history)
                self.move_history = applied_moves
                self.initial_board_set = True
                
                # Determine whose turn it is based on user color and move count
                self._set_correct_turn(silent=silent)
                
                # Only print if there are actual changes and not in silent mode
                if not silent:
                    print(f"✅ Board updated: {old_count} → {len(applied_moves)} moves")
                    print(f"Current position: {self.board.fen()}")
                    print(f"Turn to move: {'White' if self.board.turn else 'Black'}")
                    print(f"User is playing: {self.user_color.title() if self.user_color else 'Unknown'}")
                
                return self.board, applied_moves
            else:
                # No new moves, return current state silently
                return self.board, self.move_history
            
        except Exception as e:
            raise ChessBotError(f"Failed to update board from moves: {e}")

    def _set_correct_turn(self, silent: bool = False):
        """
        Set the turn based on move count (for display purposes only)
        Analysis will always use the user's selected color regardless
        
        Args:
            silent: If True, don't print output
        """
        move_count = len(self.move_history)
        
        # Calculate turn based on move count
        # In standard chess:
        # - After an even number of moves, it's White's turn
        # - After an odd number of moves, it's Black's turn
        self.board.turn = chess.WHITE if (move_count % 2 == 0) else chess.BLACK
        
        if not silent:
            print(f"📊 Board reconstructed: {move_count} moves played")
            print(f"ℹ️ Note: Analysis will always be for your selected color ({self.user_color.title() if self.user_color else 'None'})")


    
    def _scrape_move_list(self) -> List[str]:
        """Scrape the move list from the page"""
        try:
            # Try multiple selectors for move list
            selectors = [
                "div.move-list-component .move",
                "ol.moves li",
                ".moves .move",
                "[class*='move-list'] [class*='move']",
                ".vertical-move-list .move",
                "wc-vertical-move-list .move",
                "[data-cy='move']",
                ".move-list .move"
            ]
            
            for selector in selectors:
                try:
                    els = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if els:
                        moves = []
                        for el in els:
                            text = el.text.strip()
                            if text:
                                # Split on whitespace and filter out move numbers
                                parts = text.split()
                                for part in parts:
                                    # Skip move numbers (like "1.", "2.", etc.)
                                    if not (part.endswith('.') and part[:-1].isdigit()):
                                        # Skip empty strings
                                        if part.strip():
                                            moves.append(part.strip())
                        
                        if moves:
                            # Only print debug info if this is a new set of moves
                            if not hasattr(self, '_last_scraped_moves') or self._last_scraped_moves != moves:
                                print(f"Found {len(moves)} moves using selector: {selector}")
                                if len(moves) >= 2:
                                    print(f"Last moves: ...{' '.join(moves[-4:])}")
                                self._last_scraped_moves = moves.copy()
                            return moves
                except Exception as e:
                    # Only print selector errors if debugging
                    continue
                    
            # Alternative approach: try to find move list container and parse all text
            try:
                containers = [
                    "div[class*='move-list']",
                    "div[class*='moves']",
                    ".vertical-move-list",
                    "wc-vertical-move-list"
                ]
                
                for container_sel in containers:
                    container = self.driver.find_elements(By.CSS_SELECTOR, container_sel)
                    if container:
                        text = container[0].text
                        if text:
                            # Parse the entire text content
                            import re
                            # Remove move numbers and extract moves
                            moves = re.findall(r'[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:[=][NBRQK])?[+#]?|O-O-O|O-O', text)
                            if moves:
                                if not hasattr(self, '_last_scraped_moves') or self._last_scraped_moves != moves:
                                    print(f"Extracted {len(moves)} moves from container text")
                                    self._last_scraped_moves = moves.copy()
                                return moves
            except Exception as e:
                pass
            
            # Only print "no moves" warning occasionally to avoid spam
            if not hasattr(self, '_no_moves_warning_count'):
                self._no_moves_warning_count = 0
            
            if self._no_moves_warning_count < 3:  # Only warn first 3 times
                print("⚠️ No moves found in move list")
                self._no_moves_warning_count += 1
            
            return []
            
        except Exception as e:
            print(f"Error scraping move list: {e}")
            return []



    def start_engine(self) -> None:
        """Initialize Stockfish engine"""
        try:
            if self.engine:
                # Close existing engine first
                try:
                    self.engine.quit()
                except:
                    pass
            
            print(f"Starting Stockfish engine from: {self.stockfish_path}")
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            
            # Configure engine settings for faster and more stable analysis
            try:
                self.engine.configure({
                    "Threads": 1,  # Single thread for stability
                    "Hash": 64,    # Lower hash table size
                    "Skill Level": 20,  # Maximum skill
                    "MultiPV": 1   # Only calculate one line
                })
            except Exception as config_error:
                print(f"Warning: Could not configure engine settings: {config_error}")
                # Continue anyway, engine will use defaults
                
            print("✅ Stockfish engine started successfully")
        except Exception as e:
            raise ChessBotError(f"Failed to start Stockfish engine: {e}")
    
    def get_best_move(self, time_limit: float = 1.0) -> Tuple[str, dict]:
        """Get the best move from Stockfish for the user's selected color"""
        if not self.engine:
            self.start_engine()
        
        # Auto-update board if needed
        if not self.initial_board_set:
            print("No board state found, updating from moves...")
            try:
                self.update_board_from_moves()
            except Exception as e:
                print(f"Warning: Could not update board automatically: {e}")
        
        if not self.board or not any(self.board.piece_at(sq) for sq in chess.SQUARES):
            raise ChessBotError("No valid board state available.")
        
        if not self.user_color:
            raise ChessBotError("User color not set. Please select your color first.")
        
        # Set turn for user's color analysis
        self.board.turn = chess.WHITE if self.user_color.lower() == 'white' else chess.BLACK
        
        # Validate position
        legal_moves = self._validate_position()
        print(f"🎯 Analyzing position for {self.user_color.title()}: {len(legal_moves)} legal moves")
        
        time_limit = max(0.1, min(time_limit, 10.0))
        return self._analyze_position(time_limit)
    
    def _analyze_position(self, time_limit: float) -> Tuple[str, dict]:
        """Perform engine analysis with error handling"""
        
        try:
            analysis_board = self.board.copy()
            result = self.engine.analyse(
                analysis_board, 
                chess.engine.Limit(time=min(time_limit, 3.0), depth=15),
                info=chess.engine.INFO_ALL
            )
            
            pv = result.get("pv", [])
            best_move = pv[0] if pv else None
            
            if best_move and best_move in analysis_board.legal_moves:
                return self._format_move_info(best_move, result, analysis_board)
            else:
                # Fallback to first legal move
                legal_moves = self._validate_position(analysis_board)
                return self._format_move_info(legal_moves[0], {}, analysis_board)
                
        except chess.engine.EngineTerminatedError:
            print("Engine terminated, attempting restart...")
            self.engine = None
            self.start_engine()
            return self._analyze_position(min(time_limit, 1.0))
            
        except Exception as e:
            print(f"Analysis error: {e}, using fallback...")
            legal_moves = self._validate_position()
            return self._format_move_info(legal_moves[0], {}, self.board)
    
    def _format_move_info(self, move: chess.Move, result: dict, board: chess.Board) -> Tuple[str, dict]:
        """Format move and analysis info"""
        try:
            move_san = board.san(move)
        except:
            move_san = move.uci()
        
        # Build safe PV
        safe_pv = [move_san]
        if result.get("pv"):
            try:
                pv_board = board.copy()
                for pv_move in result["pv"][:3]:  # Limit to 3 moves
                    if pv_move in pv_board.legal_moves:
                        safe_pv.append(pv_board.san(pv_move))
                        pv_board.push(pv_move)
                    else:
                        break
            except:
                pass
        
        return move_san, {
            "move_uci": move.uci(),
            "move_san": move_san,
            "score": result.get("score", "Unknown"),
            "depth": result.get("depth", "Unknown"),
            "nodes": result.get("nodes", "Unknown"),
            "time": result.get("time", "Unknown"),
            "pv": safe_pv[:3]
        }
    
    def get_board_ascii(self) -> str:
        """Get ASCII representation of current board"""
        if not self.board:
            return "No board state available"
        return str(self.board)
    
    def get_fen(self) -> str:
        """Get FEN notation of current board"""
        if not self.board:
            return "No board state available"
        return self.board.fen()
    
    def close(self) -> None:
        """Clean up resources"""
        # Stop auto-update first
        self.stop_auto_update()
        
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
            self.engine = None
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None