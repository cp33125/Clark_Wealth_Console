import tkinter as tk
import threading
import requests
import time
import pystray
from PIL import Image, ImageDraw

def send_telegram_alert(message):
    bot_token = "7938878501:AAGPS8s1Ifn9LthkY6JcDF3lnKSCHoUHwbw"
    user_id = "6915012464"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": user_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# ===== SETTINGS =====
ETH_SYMBOL = "ethereum"
UPDATE_INTERVAL = 10  # seconds
SELL_LIMIT_PRICE = 3070.00
BUY_ALERT_PRICE = 2930.00

# ===== GUI =====
root = tk.Tk()
root.title("Clark Wealth Console 4.2")
root.geometry("400x220")
root.resizable(False, False)

price_var = tk.StringVar(value="Fetching ETH price...")
alert_var = tk.StringVar(value="Initializing...")

sell_alerts_enabled = tk.BooleanVar(value=True)
buy_alerts_enabled = tk.BooleanVar(value=True)

def fetch_eth_price():
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
        price = float(response.json()['price'])
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def update_price():
    while True:
        price = fetch_eth_price()
        if price:
            price_var.set(f"ETH Price: ${price:,.2f}")
            if sell_alerts_enabled.get() and price >= SELL_LIMIT_PRICE:
                alert_var.set(f"🚨 SELL ALERT: ETH hit ${price:,.2f}")
                send_telegram_alert(f"🚨 SELL ALERT: ETH hit ${price:,.2f}")
            elif buy_alerts_enabled.get() and price <= BUY_ALERT_PRICE:
                alert_var.set(f"📢 BUY ALERT: ETH dropped to ${price:,.2f}")
                send_telegram_alert(f"📢 BUY ALERT: ETH dropped to ${price:,.2f}")
            else:
                alert_var.set("✅ Monitoring...")
        time.sleep(UPDATE_INTERVAL)

def toggle_sell_alerts():
    sell_alerts_enabled.set(not sell_alerts_enabled.get())
    sell_button.config(text=f"SELL Alerts: {'ON' if sell_alerts_enabled.get() else 'OFF'}")

def toggle_buy_alerts():
    buy_alerts_enabled.set(not buy_alerts_enabled.get())
    buy_button.config(text=f"BUY Alerts: {'ON' if buy_alerts_enabled.get() else 'OFF'}")

def minimize_to_tray():
    root.withdraw()
    icon.visible = True

def restore_from_tray(icon, item):
    root.deiconify()
    icon.visible = False

def exit_app(icon, item):
    icon.visible = False
    root.destroy()

# ===== SYSTEM TRAY =====
def create_tray_icon():
    img = Image.new('RGB', (64, 64), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((10, 25), "ETH", fill=(255, 255, 255))
    menu = pystray.Menu(
        pystray.MenuItem(f"ETH Price: {price_var.get()}", lambda: None, enabled=False),
        pystray.MenuItem("Show Console", restore_from_tray),
        pystray.MenuItem("Quit", exit_app)
    )
    return pystray.Icon("Clark Wealth Console", img, "Clark Wealth Console", menu)

# ===== GUI WIDGETS =====
tk.Label(root, textvariable=price_var, font=("Arial", 18)).pack(pady=10)
tk.Label(root, textvariable=alert_var, font=("Arial", 14), fg="blue").pack()

tk.Checkbutton(root, text="Monitoring...", variable=sell_alerts_enabled).pack()

sell_button = tk.Button(root, text="SELL Alerts: ON", command=toggle_sell_alerts)
sell_button.pack(pady=5)

buy_button = tk.Button(root, text="BUY Alerts: ON", command=toggle_buy_alerts)
buy_button.pack(pady=5)

tk.Button(root, text="Exit", command=minimize_to_tray).pack(pady=10)

# ===== START THREADS =====
threading.Thread(target=update_price, daemon=True).start()
icon = create_tray_icon()

root.protocol("WM_DELETE_WINDOW", minimize_to_tray)
root.mainloop()

