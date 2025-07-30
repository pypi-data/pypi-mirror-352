import time
from argparse import ArgumentParser
from .CandleTimer import CandleTimer

def main():
    parser = ArgumentParser(
        prog="burning-candle",
        description="""
This CLI interface creates an ASCII candle timer that burns for specified minutes.
        """,
        add_help=True,
    )
    
    parser.add_argument(
        "-c", "--create", 
        type=int, 
        default=5, 
        help="Candle melt time in minutes"
    )
    
    parser.add_argument(
        "-a", "--animation", 
        type=int, 
        default=0, 
        choices=[0, 1], 
        help="Whether to add animation to the candle (0=simple, 1=animated)"
    )
    
    parser.add_argument(
        "-v", "--verbosity", 
        type=int, 
        default=1, 
        choices=[0, 1], 
        help="Adds additional print statements (0=quiet, 1=verbose)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('burning_candle').__version__}"
    )
    
    args = parser.parse_args()
    
    # Handle negative input
    minutes = abs(args.create)
    if args.create < 0:
        print("Given input is a negative integer. Converted to its absolute value!!")
    
    # Create candle timer
    candle = CandleTimer(minutes)
    
    # Verbose startup message
    if args.verbosity:
        print(f"\n🔥 Lighting a {minutes}-minute candle...")
        for i in range(3):
            print("Starting in {} seconds...".format(3 - i))
            time.sleep(1)
    
    try:
        # Run the candle timer
        candle.run(args.animation == 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
