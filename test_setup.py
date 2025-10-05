#!/usr/bin/env python3
"""
Test script to verify Chess.com Helper setup
Run this to check if all dependencies and engines are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import customtkinter
        print("✅ CustomTkinter imported successfully")
    except ImportError as e:
        print(f"❌ CustomTkinter import failed: {e}")
        return False
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False
    
    try:
        import chess
        import chess.engine
        print("✅ python-chess imported successfully")
    except ImportError as e:
        print(f"❌ python-chess import failed: {e}")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager imported successfully")
    except ImportError as e:
        print(f"❌ webdriver-manager import failed: {e}")
        return False
    
    return True

def test_chessbot():
    """Test ChessBot initialization and Stockfish"""
    print("\\n🔍 Testing ChessBot...")
    
    try:
        from chessbot import ChessBot
        bot = ChessBot()
        print(f"✅ ChessBot initialized with Stockfish: {bot.stockfish_path}")
        
        # Test engine
        print("🔍 Testing Stockfish engine...")
        bot.start_engine()
        print("✅ Stockfish engine started successfully")
        
        # Test analysis
        print("🔍 Testing position analysis...")
        import chess
        bot.board = chess.Board()  # Standard starting position
        move, info = bot.get_best_move(time_limit=0.5)
        print(f"✅ Analysis successful - Best move: {move}")
        print(f"📊 Score: {info.get('score', 'N/A')}")
        print(f"🔍 Depth: {info.get('depth', 'N/A')}")
        
        bot.close()
        return True
        
    except Exception as e:
        print(f"❌ ChessBot test failed: {e}")
        return False

def test_gui():
    """Test GUI components"""
    print("\\n🔍 Testing GUI components...")
    
    try:
        # Test if we can create a GUI instance without showing it
        import customtkinter as ctk
        
        # Create a minimal test window
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
        label = ctk.CTkLabel(root, text="Test")
        button = ctk.CTkButton(root, text="Test")
        
        print("✅ GUI components can be created successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_chrome():
    """Test Chrome WebDriver setup"""
    print("\\n🔍 Testing Chrome WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test driver manager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver available at: {driver_path}")
        
        # Test if we can create a driver (headless mode)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        driver.get("about:blank")
        print("✅ Chrome WebDriver test successful")
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver test failed: {e}")
        print("💡 Make sure Chrome browser is installed and updated")
        return False

def main():
    """Run all tests"""
    print("🎯 Chess.com Helper - Setup Test")
    print("=" * 50)
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("ChessBot & Stockfish", test_chessbot),
        ("GUI Components", test_gui),
        ("Chrome WebDriver", test_chrome),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("🚀 You can now run: python gui_main.py")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("💡 Make sure all dependencies are installed correctly.")
    
    return all_passed

if __name__ == "__main__":
    main()