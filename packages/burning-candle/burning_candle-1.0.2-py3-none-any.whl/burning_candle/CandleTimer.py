import time
import os
import random
from datetime import datetime, timedelta

class CandleTimer:
    def __init__(self, minutes):
        self.total_minutes = minutes
        self.total_seconds = minutes * 60
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=minutes)
        
        # Candle design parameters
        self.max_height = 20
        self.candle_width = 7
        self.flame_chars = ['🔥', '🕯️', '💛', '🧡', '❤️']
        self.wax_char = '█'
        self.wick_char = '|'
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_flame_animation(self):
        """Generate flickering flame effect"""
        flames = [
            "  .-~'~-.",
            " /       \\",
            "|  ^   ^  |",
            "\\   ~   /",
            " '-._.-'",
        ]
        
        # Add some randomization for flickering
        if random.random() > 0.7:
            flames[2] = "  |  o   o  |"  # Different flame shape
        if random.random() > 0.8:
            flames[1] = "   \\       /"  # Flame dancing
            
        return flames
    
    def get_simple_flame(self):
        """Simple flame representation"""
        flame_states = [
            ["  (\\ /)", "   ).(", "  (_|_)"],
            ["  (\\./)", "   ).(", "  (.|.)"],
            ["  (/\\)", "   ).(", "  (_._)"],
        ]
        return random.choice(flame_states)
    
    def calculate_candle_height(self, elapsed_seconds):
        """Calculate remaining candle height based on time elapsed"""
        progress = elapsed_seconds / self.total_seconds
        remaining_height = max(1, int(self.max_height * (1 - progress)))
        return remaining_height
    
    def draw_candle(self, height, is_flame_animation):
        """Draw the candle with given height"""
        candle_art = []
        
        # Add flame
        if is_flame_animation:
            flame = self.get_flame_animation()
        else:
            flame = self.get_simple_flame()

        for line in flame:
            candle_art.append(f"{" " * (self.candle_width // 2)}{line}")
        
        # Add wick
        candle_art.append(f"       {self.wick_char}")
        
        # Add wax body
        for i in range(height):
            # Add some texture variation
            if i == 0:
                candle_art.append(f"   ┌{'─' * self.candle_width}┐")
            elif i == height - 1:
                candle_art.append(f"   └{'─' * self.candle_width}┘")
            else:
                # Occasionally add drip marks
                if random.random() > 0.9:
                    left_drip = '~' if random.random() > 0.5 else '│'
                    right_drip = '~' if random.random() > 0.5 else '│'
                    candle_art.append(f"   {left_drip}{self.wax_char * self.candle_width}{right_drip}")
                else:
                    candle_art.append(f"   │{self.wax_char * self.candle_width}│")
        
        # Add base/holder
        candle_art.append(f"  ╔{'═' * (self.candle_width + 2)}╗")
        candle_art.append(f"  ║{' ' * (self.candle_width + 2)}║")
        candle_art.append(f"  ╚{'═' * (self.candle_width + 2)}╝")
        
        return candle_art
    
    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def run(self, is_flame_animation):
        """Main animation loop"""
        try:
            while True:
                self.clear_screen()
                
                # Calculate elapsed time
                now = datetime.now()
                elapsed = (now - self.start_time).total_seconds()
                remaining = max(0, self.total_seconds - elapsed)
                
                # Check if time is up
                if remaining <= 0:
                    self.show_finished()
                    break
                
                # Calculate candle height
                height = self.calculate_candle_height(elapsed)
                
                # Draw candle
                candle_lines = self.draw_candle(height, is_flame_animation)
                
                # Display header
                print("=" * 50)
                print(f"🕯️  CANDLE TIMER - {self.total_minutes} MINUTES  🕯️")
                print("=" * 50)
                print()
                
                # Display candle
                for line in candle_lines:
                    print(line)
                
                print()
                print(f"⏰ Time Remaining: {self.format_time(remaining)}")
                print(f"📊 Progress: {((elapsed/self.total_seconds)*100):.1f}%")
                
                # Add atmospheric elements
                if random.random() > 0.8:
                    print(f"💨 {'~' * random.randint(3, 8)}")  # Smoke effect
                
                print("\n💡 Press Ctrl+C to stop")
                
                # Wait before next frame
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n🕯️ Candle extinguished! 💨")
            print(f"Burned for: {self.format_time(elapsed)}")
    
    def show_finished(self):
        """Show completion message"""
        self.clear_screen()
        print("=" * 50)
        print("🎉 TIME'S UP! 🎉")
        print("=" * 50)
        print()
        print("     💨💨💨")
        print("       |||")
        print("   ┌────────┐")
        print("   │ BURNED │")
        print("   │  OUT   │")
        print("   └────────┘")
        print("  ╔══════════╗")
        print("  ║          ║")
        print("  ╚══════════╝")
        print()
        print(f"🕯️ Your {self.total_minutes}-minute candle has burned out!")
        print("✨ Hope you enjoyed the ambiance! ✨")

def main():
    print("🕯️ Welcome to Candle Timer! 🕯️")
    print("Enter how many minutes you want the candle to burn:")
    
    try:
        minutes = int(input("Minutes: "))
        if minutes <= 0:
            print("Please enter a positive number!")
            return
            
        print(f"\n🔥 Lighting a {minutes}-minute candle...")
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        candle = CandleTimer(minutes)
        candle.run(is_flame_animation = True)
        
    except ValueError:
        print("Please enter a valid number!")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()