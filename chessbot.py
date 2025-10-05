from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from stockfish import Stockfish
import chess, time
from chess.engine import SimpleEngine, Limit

def launch():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.chess.com/play/computer")

    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "board-layout-main"))
        )
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.piece"))
        )
    pieces = driver.find_elements(By.CSS_SELECTOR, "div.piece")

    file_map = {"1": "a", "2": "b", "3": "c", "4": "d", "5": "e", "6": "f", "7": "g", "8": "h"}
    rank_map = {"1": "8", "2": "7", "3": "6", "4": "5", "5": "4", "6": "3", "7": "2", "8": "1"}
    piece_map = {
        "wp": "P", "wn": "N", "wb": "B", "wr": "R", "wq": "Q", "wk": "K",
        "bp": "p", "bn": "n", "bb": "b", "br": "r", "bq": "q", "bk": "k"
        }
    
    v_board = {}

    for piece in pieces:
        class_names = piece.get_attribute("class").split()
        piece_code = None
        square = None

        for name in class_names:
            if name in piece_map:
                piece_code = piece_map[name]
            elif name.startswith("square-"):
                square_num = name.split("-")[1]
                file = file_map.get(square_num[0])
                rank = rank_map.get(square_num[1])
                if file and rank:
                    square = file + rank

        if piece_code and square:
            v_board[square] = piece_code

    # driver.quit()

    board = chess.Board(None) 
    board.turn = chess.WHITE
    for square, piece in v_board.items():
        index = chess.parse_square(square)
        board.set_piece_at(index, chess.Piece.from_symbol(piece))
    print(board)
    return board
    
def run(board):
    engine = SimpleEngine.popen_uci("/Users/subamluitel/Desktop/chess-bot/stockfish/stockfish-macos-m1-apple-silicon")
    result = engine.play(board, Limit(time=0.1))
    print("Best move:", result.move)
    engine.quit()
