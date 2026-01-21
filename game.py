import json
import os
import random
import time
from datetime import datetime, timedelta

class GachaGame:
    def __init__(self, save_file="player_data.json"):
        self.save_file = save_file
        self.player_data = self.load_data()
        
    def load_data(self):
        """Load player data from file or create new player"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                return json.load(f)
        return {
            "balance": 0,
            "tokens": 0,
            "attempts_left": 10,
            "last_reset_time": datetime.now().isoformat(),
            "total_wins": 0,
            "total_losses": 0
        }
    
    def save_data(self):
        """Save player data to file"""
        with open(self.save_file, 'w') as f:
            json.dump(self.player_data, f, indent=2)
    
    def check_reset_cooldown(self):
        """Check if 15 minutes have passed to reset attempts"""
        last_reset = datetime.fromisoformat(self.player_data["last_reset_time"])
        now = datetime.now()
        
        if now >= last_reset + timedelta(minutes=15):
            self.player_data["attempts_left"] = 10
            self.player_data["last_reset_time"] = now.isoformat()
            self.save_data()
            return True
        return False
    
    def get_time_until_reset(self):
        """Get remaining time until next reset in seconds"""
        last_reset = datetime.fromisoformat(self.player_data["last_reset_time"])
        next_reset = last_reset + timedelta(minutes=15)
        now = datetime.now()
        
        if now >= next_reset:
            return 0
        
        remaining = (next_reset - now).total_seconds()
        return remaining
    
    def spin_gacha(self):
        """Perform a gacha spin with 3 rows
        Returns: (result, is_win, row1, row2, row3)
        """
        symbols = ["🎰", "💎", "🎁", "⭐", "🍀", "🎯"]
        
        # Generate 3 rows
        row1 = [random.choice(symbols) for _ in range(3)]
        row2 = [random.choice(symbols) for _ in range(3)]
        row3 = [random.choice(symbols) for _ in range(3)]
        
        # Check for win conditions
        is_win = False
        
        # Check if all 3 middle symbols are the same
        if row1[1] == row2[1] == row3[1]:
            is_win = True
        
        # Check if all 3 symbols in any row are the same
        if row1[0] == row1[1] == row1[2]:
            is_win = True
        if row2[0] == row2[1] == row2[2]:
            is_win = True
        if row3[0] == row3[1] == row3[2]:
            is_win = True
        
        return is_win, row1, row2, row3
    
    def gacha_spin(self):
        """Execute a gacha spin"""
        # Check if cooldown has passed
        self.check_reset_cooldown()
        
        # Check if attempts available
        if self.player_data["attempts_left"] <= 0:
            time_left = self.get_time_until_reset()
            minutes = int(time_left // 60)
            seconds = int(time_left % 60)
            return {
                "success": False,
                "message": f"❌ Kesempatan habis! Tunggu {minutes}m {seconds}s lagi.",
                "attempts_left": 0
            }
        
        # Perform spin
        is_win, row1, row2, row3 = self.spin_gacha()
        self.player_data["attempts_left"] -= 1
        
        # Display results
        result = {
            "row1": " ".join(row1),
            "row2": " ".join(row2),
            "row3": " ".join(row3),
        }
        
        if is_win:
            reward = 10000
            self.player_data["balance"] += reward
            self.player_data["total_wins"] += 1
            result["success"] = True
            result["message"] = f"🎉 MENANG! +{reward} coin"
        else:
            self.player_data["total_losses"] += 1
            result["success"] = False
            result["message"] = "❌ Kalah... coba lagi nanti!"
        
        result["balance"] = self.player_data["balance"]
        result["attempts_left"] = self.player_data["attempts_left"]
        
        # Show reset timer if no attempts left
        if self.player_data["attempts_left"] == 0:
            time_left = self.get_time_until_reset()
            minutes = int(time_left // 60)
            seconds = int(time_left % 60)
            result["next_reset"] = f"Reset dalam: {minutes}m {seconds}s"
        
        self.save_data()
        return result
    
    def buy_gacha_pack(self, quantity=1):
        """Buy gacha pack (5 tokens per pack)
        Default: 1 pack = 5 tokens (free or 0 cost)
        """
        tokens_gained = 5 * quantity
        self.player_data["tokens"] += tokens_gained
        self.save_data()
        
        return {
            "success": True,
            "message": f"✅ Berhasil membeli {quantity} pack gacha! +{tokens_gained} token",
            "tokens": self.player_data["tokens"],
            "balance": self.player_data["balance"]
        }
    
    def get_player_status(self):
        """Get current player status"""
        self.check_reset_cooldown()
        time_left = self.get_time_until_reset()
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        
        return {
            "balance": self.player_data["balance"],
            "tokens": self.player_data["tokens"],
            "attempts_left": self.player_data["attempts_left"],
            "total_wins": self.player_data["total_wins"],
            "total_losses": self.player_data["total_losses"],
            "next_reset": f"{minutes}m {seconds}s" if self.player_data["attempts_left"] < 10 else "Penuh"
        }
    
    def reset_game(self):
        """Reset player data (for testing)"""
        self.player_data = {
            "balance": 0,
            "tokens": 0,
            "attempts_left": 10,
            "last_reset_time": datetime.now().isoformat(),
            "total_wins": 0,
            "total_losses": 0
        }
        self.save_data()
        return {"message": "✅ Data game direset"}


def display_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("🎰 MINI GACHA GAMBLING GAME 🎰")
    print("="*50)
    print("1. 🎯 Main Gacha (1 kesempatan)")
    print("2. 💳 Beli Pack Gacha (5x token)")
    print("3. 📊 Lihat Status")
    print("4. 🔄 Reset Game (untuk testing)")
    print("5. ❌ Keluar")
    print("="*50)


def format_currency(amount):
    """Format number as currency"""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.1f}K"
    return str(amount)


def main():
    """Main game loop"""
    game = GachaGame()
    
    print("\n🎰 Selamat datang di Mini Gacha Gambling Game! 🎰")
    
    while True:
        display_menu()
        choice = input("Pilih menu (1-5): ").strip()
        
        if choice == "1":
            print("\n🎯 Melakukan spin gacha...\n")
            result = game.gacha_spin()
            
            print("━" * 50)
            print(f"  {result['row1']}")
            print(f"  {result['row2']}")
            print(f"  {result['row3']}")
            print("━" * 50)
            print(f"\n{result['message']}")
            print(f"💰 Saldo: {format_currency(result['balance'])} coin")
            print(f"⚡ Kesempatan tersisa: {result['attempts_left']}/10")
            
            if "next_reset" in result:
                print(f"⏰ {result['next_reset']}")
        
        elif choice == "2":
            print("\n💳 === BUY GACHA PACK ===")
            print("1 Pack = 5x Token")
            try:
                qty = int(input("Berapa pack yang ingin dibeli? "))
                if qty < 1:
                    print("❌ Jumlah harus minimal 1 pack")
                    continue
                
                result = game.buy_gacha_pack(qty)
                print(f"\n{result['message']}")
                print(f"💰 Saldo: {format_currency(result['balance'])} coin")
                print(f"🎟️  Token total: {result['tokens']}")
            except ValueError:
                print("❌ Input tidak valid!")
        
        elif choice == "3":
            print("\n📊 === STATUS PEMAIN ===")
            status = game.get_player_status()
            print(f"💰 Saldo: {format_currency(status['balance'])} coin")
            print(f"🎟️  Token: {status['tokens']}")
            print(f"⚡ Kesempatan: {status['attempts_left']}/10")
            print(f"🎉 Total Menang: {status['total_wins']}")
            print(f"😢 Total Kalah: {status['total_losses']}")
            
            if status['total_wins'] + status['total_losses'] > 0:
                win_rate = (status['total_wins'] / (status['total_wins'] + status['total_losses'])) * 100
                print(f"📈 Win Rate: {win_rate:.1f}%")
            
            print(f"⏰ Reset dalam: {status['next_reset']}")
        
        elif choice == "4":
            confirm = input("⚠️  Yakin ingin reset? (yes/no): ").strip().lower()
            if confirm == "yes":
                game.reset_game()
                print("✅ Game berhasil direset!")
            else:
                print("❌ Reset dibatalkan")
        
        elif choice == "5":
            print("\n👋 Terima kasih telah bermain! Sampai jumpa lagi!")
            break
        
        else:
            print("❌ Pilihan tidak valid!")


if __name__ == "__main__":
    main()
