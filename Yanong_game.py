import tkinter
import random
import time
import os

rows = 25
cols = 25
tile_size = 25

window_width = tile_size * rows
window_height = tile_size * cols

HIGHSCORE_FILE = "highscores.txt"  # file to save top 5 scores

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Game Window
window = tkinter.Tk()
window.title("Snake")
window.resizable(False, False)

canvas = tkinter.Canvas(window, bg="black",
                        width=window_width, height=window_height,
                        borderwidth=0, highlightthickness=0)
canvas.pack()
window.update()

# center the window
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width / 2) - (window_width / 2))
window_y = int((screen_height / 2) - (window_height / 2))

window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

# --- Game State Variables ---
snake = None
food = None
snake_body = []
velocityX = 0
velocityY = 0
game_over = False
score = 0
running = False

# Special Big Food
big_food = None
big_food_spawn_time = None

# --- Buttons ---
start_button = tkinter.Button(window, text="Start Game", font=("Arial", 14), command=lambda: start_game())
start_button.place(relx=0.5, rely=0.5, anchor="center")

restart_button = tkinter.Button(window, text="Restart", font=("Arial", 14), command=lambda: start_game())
restart_button.place_forget()


# --- Helper Functions ---
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def save_high_score(new_score):
    scores = []
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            scores = [int(line.strip()) for line in f.readlines()]

    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]  # keep top 5

    with open(HIGHSCORE_FILE, "w") as f:
        for s in scores:
            f.write(str(s) + "\n")
    return scores


def load_high_scores():
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    with open(HIGHSCORE_FILE, "r") as f:
        return [int(line.strip()) for line in f.readlines()]


def start_game():
    global snake, food, snake_body, velocityX, velocityY, game_over, score, big_food, big_food_spawn_time, running

    # reset game state
    snake = Tile(5 * tile_size, 5 * tile_size)
    food = Tile(10 * tile_size, 10 * tile_size)
    snake_body = []
    velocityX = 0
    velocityY = 0
    game_over = False
    score = 0
    big_food = None
    big_food_spawn_time = None
    running = True

    # hide buttons
    start_button.place_forget()
    restart_button.place_forget()


def change_direction(e):  # e - stands for EVENT
    global velocityX, velocityY, game_over, running
    if game_over or not running:
        return

    if (e.keysym == "Up" and velocityY != 1):
        velocityX = 0
        velocityY = -1
    elif (e.keysym == "Down" and velocityY != -1):
        velocityX = 0
        velocityY = 1
    elif (e.keysym == "Left" and velocityX != 1):
        velocityX = -1
        velocityY = 0
    elif (e.keysym == "Right" and velocityX != -1):
        velocityX = 1
        velocityY = 0


def move():
    global snake, food, snake_body, game_over, score, big_food, big_food_spawn_time, running

    if game_over or not running:
        return

    # border collision
    if (snake.x < 0 or snake.x >= window_width or snake.y < 0 or snake.y >= window_height):
        game_over = True
        save_high_score(score)
        return

    # self collision
    for tile in snake_body:
        if (snake.x == tile.x and snake.y == tile.y):
            game_over = True
            save_high_score(score)
            return        

    # collision with normal food
    if (snake.x == food.x and snake.y == food.y):
        snake_body.append(Tile(food.x, food.y))
        food.x = random.randint(0, cols-1) * tile_size
        food.y = random.randint(0, rows-1) * tile_size
        score += 1  

        # spawn big food if score is prime
        if is_prime(score) and big_food is None:
            big_food = Tile(random.randint(0, cols-1) * tile_size,
                            random.randint(0, rows-1) * tile_size)
            big_food_spawn_time = time.time()

    # collision with big food
    if big_food and snake.x == big_food.x and snake.y == big_food.y:
        score += 5
        snake_body.append(Tile(big_food.x, big_food.y))
        big_food = None
        big_food_spawn_time = None

    # check if big food expired (7s)
    if big_food and time.time() - big_food_spawn_time > 7:
        big_food = None
        big_food_spawn_time = None

    # update snake body
    for i in range(len(snake_body)-1, -1, -1):
        tile = snake_body[i]
        if (i == 0):
            tile.x = snake.x
            tile.y = snake.y
        else:
            prev_tile = snake_body[i-1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y    

    # move head
    snake.x += velocityX * tile_size
    snake.y += velocityY * tile_size


def draw():
    global snake, food, snake_body, game_over, score, big_food, running
    canvas.delete("all")

    if running:
        move()

        # draw the food
        canvas.create_rectangle(
            food.x, food.y, food.x + tile_size, food.y + tile_size,
            fill="green"
        )

        # draw the big food (yellow)
        if big_food:
            canvas.create_oval(
                big_food.x, big_food.y, big_food.x + tile_size, big_food.y + tile_size,
                fill="yellow"
            )

        # draw the snake
        canvas.create_rectangle(
            snake.x, snake.y, snake.x + tile_size, snake.y + tile_size,
            fill="red"
        )
        for tile in snake_body:
            canvas.create_rectangle(tile.x ,tile.y, tile.x + tile_size, tile.y + tile_size, fill = "red")

        # display score
        canvas.create_text(30,20, font="Arial 10", text=f"Score: {score}", fill="white")

        if game_over:
            highscores = load_high_scores()
            canvas.create_text(window_width/2, window_height/2 - 40, font="Arial 20", 
                               text=f"Game Over! Score: {score}", fill="white")
            canvas.create_text(window_width/2, window_height/2, font="Arial 15", 
                               text="High Scores:", fill="yellow")
            y = window_height/2 + 30
            for i, hs in enumerate(highscores):
                canvas.create_text(window_width/2, y, font="Arial 12", text=f"{i+1}. {hs}", fill="white")
                y += 20

            # show restart button BELOW scores
            restart_button.place(relx=0.5, rely=0.9, anchor="center")
            running = False
    else:
        # waiting for start
        canvas.create_text(window_width/2, window_height/2 - 100, font="Arial 20", 
                           text="Welcome to Snake!", fill="white")

    window.after(100, draw)  # 10 FPS


# bind controls
window.bind("<KeyRelease>", change_direction)

# start game loop
draw()
window.mainloop()
