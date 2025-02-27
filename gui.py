
import websocket
import json
import asyncio
import threading
import os
import customtkinter as ctk
from tkinter import StringVar
from dotenv import load_dotenv


load_dotenv()
# Load API key from environment variable
api_key = os.getenv("API_KEY")

# Create a dictionary to store stock data
stock_data = {}

# Initialize Tkinter GUI
class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Live Stock Data")
        self.geometry("500x400")
        self.configure(bg="#2C2F33")

        ctk.set_appearance_mode("dark")

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="Live Stock Prices", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        # Create frame for stock updates
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, fill="both", expand=True)

        self.stock_labels = {}  # Dictionary to store labels for each stock

    def update_stock(self, symbol, price, timestamp, volume):
        if symbol not in self.stock_labels:
            # Create a new row for the stock if it's not already displayed
            frame = ctk.CTkFrame(self.frame)
            frame.pack(pady=5, fill="x")

            label = ctk.CTkLabel(frame, text=f"{symbol} - ${price}", font=("Arial", 14))
            label.pack(side="left", padx=10)

            volume_label = ctk.CTkLabel(frame, text=f"Volume: {volume}", font=("Arial", 12))
            volume_label.pack(side="right", padx=10)

            self.stock_labels[symbol] = (label, volume_label)
        else:
            # Update existing stock data
            self.stock_labels[symbol][0].configure(text=f"{symbol} - ${price}")
            self.stock_labels[symbol][1].configure(text=f"Volume: {volume}")

# Function to handle WebSocket messages
def on_message(ws, message):
    global app
    msg_dict = json.loads(message)

    if "data" in msg_dict:
        for trade in msg_dict["data"]:
            price = trade["p"]
            symbol = trade["s"]
            timestamp = trade["t"]
            volume = trade["v"]

            # Update the GUI with new stock data
            app.after(0, app.update_stock, symbol, price, timestamp, volume)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket Closed ###")

def on_open(ws):
    # Subscribe to stock symbols
    symbols = ["AAPL", "AMZN", "BINANCE:BTCUSDT", "IC MARKETS:1"]
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

# Function to start WebSocket in a separate thread
def start_websocket():
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={api_key}", on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

# Start the WebSocket in a separate thread
ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()

# Start Tkinter GUI
app = StockApp()
app.mainloop()
