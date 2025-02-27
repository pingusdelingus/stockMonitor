
import websocket
import json
import asyncio
import threading
import os
import customtkinter as ctk
from tkinter import StringVar
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("API_KEY")

stock_data = {}
class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("live market data")
        self.geometry("500x400")
        self.configure(bg="#2C2F33")

        ctk.set_appearance_mode("dark")

        self.title_label = ctk.CTkLabel(self, text="live ticker price", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, fill="both", expand=True)

        self.stock_labels = {}  

    def update_stock(self, symbol, price, timestamp, volume):
        if symbol not in self.stock_labels:
            frame = ctk.CTkFrame(self.frame)
            frame.pack(pady=5, fill="x")

            label = ctk.CTkLabel(frame, text=f"{symbol} - ${price}", font=("Arial", 14))
            label.pack(side="left", padx=10)

            volume_label = ctk.CTkLabel(frame, text=f"volume: {volume}", font=("Arial", 12))
            volume_label.pack(side="right", padx=10)

            self.stock_labels[symbol] = (label, volume_label)
        else:
            self.stock_labels[symbol][0].configure(text=f"{symbol} - ${price}")
            self.stock_labels[symbol][1].configure(text=f"volume: {volume}")

def on_message(ws, message):
    global app
    msg_dict = json.loads(message)

    if "data" in msg_dict:
        for trade in msg_dict["data"]:
            price = trade["p"]
            symbol = trade["s"]
            timestamp = trade["t"]
            volume = trade["v"]

            app.after(0, app.update_stock, symbol, price, timestamp, volume)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket Closed ###")

def on_open(ws):
    symbols = ["AAPL", "AMZN", "BINANCE:BTCUSDT", "IC MARKETS:1"]
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

def start_websocket():
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={api_key}", on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()

app = StockApp()
app.mainloop()
