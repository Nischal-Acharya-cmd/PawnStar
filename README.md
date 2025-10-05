Disclaimer: This project is for educational purposes. Please respect Chess.com's terms of service and use responsibly.
            Using bots/ automation on chess.com is against their tos do not use these on real matches.

# ♞ Chess.com Helper - igKnight

A modern GUI tool to analyze your Chess.com games using the powerful Stockfish engine. Get real-time move suggestions and position analysis while playing against the computer on Chess.com.

## 🌟 Features

- **Modern Interface**: Clean, dark-themed GUI built with CustomTkinter
- **Real-time Analysis**: Fetch board positions from Chess.com and get instant move suggestions
- **Stockfish Integration**: Uses the world's strongest chess engine for analysis
- **Browser Automation**: Seamlessly integrates with Chess.com using Selenium
- **Cross-platform**: Works on macOS, Windows, and Linux

## 🔧 Requirements

- Python 3.8 or higher
- Chrome browser (for Selenium automation)
- Stockfish chess engine

## 📦 Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install customtkinter selenium python-chess stockfish webdriver-manager
   ```

3. **Install Stockfish:**
   - **macOS (Homebrew):** `brew install stockfish`
   - **Ubuntu/Debian:** `sudo apt-get install stockfish`  
   - **Windows:** Download from [Stockfish website](https://stockfishchess.org/download/)
   - **Or use the included binary:** The project includes `stockfish-macos-m1-apple-silicon` for Apple Silicon Macs

## 🚀 Usage

1. **Start the application:**
   ```bash
   # If using the included virtual environment:
   venv/bin/python gui_main.py
   
   # Or if you have the dependencies installed globally:
   python gui_main.py
   ```

2. **Follow the workflow:**
   - Click **"🚀 Start Browser"** to open Chrome and navigate to Chess.com
   - Select your color (White/Black) 
   - Start a game on Chess.com against the computer
   - Click **"📋 Fetch Board"** to scan the current position
   - Click **"🧠 Suggest Best Move"** to get Stockfish's recommendation

3. **View results in the console:**
   - ASCII board representation
   - Move suggestions in both algebraic and UCI notation  
   - Position evaluation and analysis depth
   - Principal variation (best line of play)

## ⚙️ Configuration

- **Stockfish Path**: The app auto-detects Stockfish, but you can manually set the path if needed
- **Analysis Time**: Adjust how long Stockfish analyzes each position (default: 2 seconds)

## 🎮 Workflow Example

```
1. Click "Start Browser" → Chrome opens Chess.com/play/computer
2. Select "white" color → Set your piece color  
3. Start a game on Chess.com
4. Click "Fetch Board" → Console shows current position
5. Click "Suggest Best Move" → Console shows: "Best move: e2-e4"
```

## 📁 Project Structure

```
├── gui_main.py      # Main entry point
├── gui.py           # CustomTkinter GUI interface  
├── chessbot.py      # Core logic (Selenium, Stockfish, Chess)
├── utils.py         # Helper utilities
└── stockfish/       # Local Stockfish binaries
```

## 🛠️ Technical Details

- **GUI Framework**: CustomTkinter for modern, native-looking interface
- **Web Automation**: Selenium WebDriver with Chrome
- **Chess Logic**: python-chess library for board representation and move validation
- **Engine**: Stockfish via UCI protocol for position analysis
- **Threading**: Non-blocking UI with background processing

## ⚠️ Important Notes

- Only works with Chess.com computer games (not live games with other players)
- Make sure Chrome browser is installed and updated
- The app needs to visually "see" the chess board, so don't minimize the browser
- Board scraping may need adjustment if Chess.com updates their HTML structure

## 🐛 Troubleshooting

**"Stockfish not found" error:**
- Install Stockfish using your package manager or download manually
- Use the "Browse" button to set the correct path
- The app will auto-detect Stockfish in these locations:
  - System PATH (`which stockfish`)
  - `/usr/local/bin/stockfish` (Homebrew Intel Mac)
  - `/opt/homebrew/bin/stockfish` (Homebrew Apple Silicon Mac)
  - `./stockfish/stockfish-macos-m1-apple-silicon` (included binary)

**"Engine process died unexpectedly" error:**
- Try using a different Stockfish binary
- On macOS, install via Homebrew: `brew install stockfish`
- Make sure the Stockfish binary has execute permissions
- Check if your system architecture matches the binary

**"No pieces found" or "Empty board" error:**
- Make sure a Chess.com game is active and visible
- Wait for the page to fully load before fetching the board
- Check that the browser window is not minimized
- Try refreshing the Chess.com page if pieces aren't detected
- The app will use the starting position as a fallback for testing

**Browser automation issues:**
- Update Chrome to the latest version
- Check internet connection
- Try restarting the application
- Make sure Chrome allows automation (some corporate environments block this)

**GUI not appearing:**
- Make sure you're running with the virtual environment: `venv/bin/python gui_main.py`
- On some systems, you may need to run: `python3 gui_main.py`
- Check that CustomTkinter is properly installed

**Testing your setup:**
Run the test script to verify everything works:
```bash
venv/bin/python test_setup.py
```

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is for educational purposes. Please respect Chess.com's terms of service and use responsibly.



## 🙏 Acknowledgments

- [Stockfish](https://stockfishchess.org/) - The chess engine
- [python-chess](https://python-chess.readthedocs.io/) - Chess library  
- [CustomTkinter](https://customtkinter.tomschimansky.com/) - Modern GUI framework
- [Selenium](https://selenium.dev/) - Web automation
