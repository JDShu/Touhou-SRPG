from main_loop import *
import touhou

def main():
    game = MainLoop(640,480,touhou.Module)
    running = True
    while running:
        running = game.process()
        game.draw()
    
if __name__ == "__main__":
    main()
