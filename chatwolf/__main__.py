import chatwolf
import sys

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
    
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.
    root = chatwolf.GUI()
    root.mainloop()

if __name__ == "__main__":
    main()
