from main_loop import *

def main():
    game = Main_Loop(640.0,480.0)
    running = True
    while running:
        running = game.process()
        game.draw()
    
if __name__ == "__main__":
    main()
