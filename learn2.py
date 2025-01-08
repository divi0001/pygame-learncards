""" _summary_
This programm implements a card learning system/game, 
this is intended to be used to learn from cards you can create in {question_answer.txt}
but you can rename it, if you want.

Setup guide:
set the base path to the folder, that this python file is in (the variable `base` below).
It will be the folder,
where this manages the files, it needs in order to keep track of your progress and
also for the source of your question answer pairs.

run:
You need to have Python 3.11 or later installed

pip install pygame matplotlib

ON MACOS, you might need to install PIL via brew:

only for MACOS: brew install PIL
in that case remove the PIL argument from the pip.

Now name the variable `question_answer` below to the name of your txt (include the file
ending) and put the txt in the same folder as this python program.

Final step: Put your learnable card text/images into the txt you defined in 
question_answer's file. Question answer pairs should always be put 1 line apart of 
each other and also inbetween, so this program can track, where your question and answer 
begins/ends. Example:
(the next line would be the first in your question_answer.txt)
This is an example question?

This is an example answer.
The answer is still going.

This is the next question.
The question is still going

The answer.

3rd question

C:/Users/Username/Desktop/path/to/your/answer/photo.png
(the file ends with the last answer, this is also the end of the example. 
Note that single line breaks like in the "is still going" lines are not rendered 
as line breaks).
If you want to put an image as an answer, you can put the path to the image as the answer
line (see example). It supports png, jpeg and jpg, png is preferred. If you put text 
a link to an image, the image will not be rendered, you need to decide.

"""
import os
import pygame
from PIL import Image
import io
import matplotlib.pyplot as plt

# Base path
base = '<base path of this repo>'
learn_path = '<name of your learn question source file>.txt'


if base == '<base path of this repo>' or learn_path == '<name of your learn question source file>.txt':
    print(f"your base and learn_path variable have not been changed,\n currently they are pointing to the folder {base} and the path of your learn file (without base) {learn_path}\n\n\n\nTO CONTINUE, PLEASE CHANGE THE PATHS ACCORDING TO THE README OR INSTRUCTIONS ABOVE")

# Load text file and process question-answer pairs
txt = open(base + learn_path, mode='r', encoding='utf-8').read()
question_answer = txt.split('\n\n')
d = {question_answer[i]: question_answer[i+1] for i in range(0, len(question_answer), 2)}

# Initialize Pygame
pygame.init()
pygame.font.init()

# Initial screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Card Flipping Game")

# Colors
WHITE, BLACK, BLUE, GREEN, YELLOW, GRAY = (255, 255, 255), (0, 0, 0), (0, 0, 255), (0, 150, 0), (255, 255, 102), (200, 200, 200)

buttons = []

# Function to scale UI elements based on the window size
def scale_ui_elements():
    global card_width, card_height, card_position, button_width, button_height, button_y, buttons, quit_button, FONT

    card_width, card_height = WIDTH * 0.6, HEIGHT * 0.6
    card_position = (WIDTH // 2 - card_width // 2, HEIGHT // 3 - card_height // 4)

    button_width, button_height = WIDTH // 10, HEIGHT // 15
    button_y = HEIGHT - 100

    buttons.clear()
    for i in range(1, 10):
        buttons.append(pygame.Rect((i-1) * (button_width + 20), button_y, button_width, button_height))

    quit_button = pygame.Rect(WIDTH - 100, HEIGHT - 50, 80, 40)
    FONT = pygame.font.SysFont('Arial', max(WIDTH // 80, 16))

# Call this to initialize the UI elements
scale_ui_elements()


def draw_pie_chart(progress, screen, position, size):
    # Count how many questions were learned successfully (rated higher than 6)
    learned = sum(1 for score, times_shown in progress.values() if score > 6)
    not_learned = len(progress) - learned

    # Create a pie chart using matplotlib
    labels = ['Learned', 'Not Learned']
    sizes = [learned, not_learned]
    colors = ['#4CAF50', '#FF6347']  # Green for learned, red for not learned

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')

    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)  # Close the figure to avoid memory leaks

    # Load the image into pygame
    pie_image = pygame.image.load(buf, 'piechart.png')

    # Resize the pie chart to fit the given size
    pie_image = pygame.transform.scale(pie_image, size)

    # Blit the pie chart onto the Pygame screen at the given position
    screen.blit(pie_image, position)


# Function to draw card, showing image if answer is a path to an image file
def draw_card(flipped, question, answer):
    card_color = GREEN if flipped else BLUE
    pygame.draw.rect(screen, card_color, (*card_position, card_width, card_height))

    if flipped and os.path.isfile(answer) and answer.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            image = pygame.image.load(answer)
            image = pygame.transform.scale(image, (int(card_width * 0.8), int(card_height * 0.8)))
            screen.blit(image, (card_position[0] + 10, card_position[1] + 10))
        except Exception as e:
            print(f"Error loading image: {e}")
    else:
        rect = pygame.Rect(card_position[0] + 10, card_position[1] + 10, card_width - 20, card_height - 20)
        draw_wrapped_text(answer if flipped else question, FONT, YELLOW, rect)

# Function to draw wrapped text
def draw_wrapped_text(text, font, color, rect):
    words = text.split(' ')
    lines, current_line = [], ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    lines.append(current_line)
    y = rect.y
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (rect.x, y))
        y += font.get_linesize()

# Save progress to the file
def save_progress(filename, progress):
    with open(filename, 'w', encoding='utf-8') as file:
        for idx, (score, times_shown) in progress.items():
            file.write(f"{idx},{score},{times_shown}\n")


# Load progress or initialize
def load_progress(filename, questions):
    progress = {}
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            progress = {int(line.split(',')[0]): [int(line.split(',')[1]), int(line.split(',')[2])] for line in file}

    # Check if there are new questions
    if len(progress) < len(questions):
        for i in range(len(progress), len(questions)):
            progress[i] = [0, 0]  # Initialize new question with [score, times_shown]

        # Append the new entries to progress.txt
        save_progress(filename, progress)

    return progress

progress = load_progress(base + 'progress.txt', d)



# Draw buttons
def draw_buttons():
    for i, button in enumerate(buttons):
        pygame.draw.rect(screen, GRAY, button)
        button_text = FONT.render(str(i + 1), True, BLACK)
        screen.blit(button_text, (button.x + button_width // 2 - button_text.get_width() // 2, button.y + button_height // 2 - button_text.get_height() // 2))

    pygame.draw.rect(screen, GRAY, quit_button)
    quit_text = FONT.render("Quit", True, BLACK)
    screen.blit(quit_text, (quit_button.x + quit_button.width // 2 - quit_text.get_width() // 2, quit_button.y + quit_button.height // 2 - quit_text.get_height() // 2))

# Main game loop
running, card_flipped = True, False
current_question_idx = 0
current_question = list(d.keys())[current_question_idx]

while running:
    screen.fill(WHITE)
    draw_pie_chart(progress, screen, position=(0, 0), size=(100+WIDTH//5, 100+HEIGHT//5))
    draw_card(card_flipped, current_question, d[current_question])
    draw_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            save_progress(base + 'progress.txt', progress)
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            scale_ui_elements()  # Rescale UI elements based on the new window size
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(*card_position, card_width, card_height).collidepoint(event.pos):
                card_flipped = not card_flipped
            for i, button in enumerate(buttons):
                if button.collidepoint(event.pos):
                    # Update progress based on the rating given by button press
                    progress[current_question_idx][0] = i + 1
                    progress[current_question_idx][1] += 1
                    # Move to next question
                    current_question_idx = (current_question_idx + 1) % len(d)
                    current_question = list(d.keys())[current_question_idx]
                    card_flipped = False
            if quit_button.collidepoint(event.pos):
                running = False
                save_progress(base + 'progress.txt', progress)

    pygame.display.flip()

pygame.quit()
