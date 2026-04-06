import pygame
import sys
from random import randint


# Constants
SCREEN_SIZE = WIDTH, HEIGHT = (1280, 720)
NUMBER_OF_PEOPLE = 50
PERSON_SPEED = 30
PERSON_COLOR_CLEAR = (200, 150, 0)
PERSON_COLOR_INFECTED = (200, 0, 0)
PERSON_COLOR_IMMUNE = (0, 200, 0)
PERSON_AURA = 20
ILLNESS_TIME = 500
IMMUNE_TIME = 800
INFECTION_PROBABILITY_WITH_MASK = 50
INFECTION_PROBABILITY_WITHOUT_MASK = 2
FIRST_CONTACT = 2
BUDGET = 2000
VACCINE_PRICE = 50
MASK_PRICE = 10


# Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epidemic Simulator 1.0")
fps = pygame.time.Clock()
pause = False
time = 0


# Person class
class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = randint(-2, 2)
        self.dy = randint(-2, 2)
        self.illness = 0
        self.immune = 0
        self.mask = False

    def move(self):
        if randint(1, 50) == 1:
            self.dx = randint(-2, 2)
            self.dy = randint(-2, 2)

        if not (PERSON_AURA < self.x + self.dx < WIDTH - PERSON_AURA):
            self.dx *= -1
        if not (PERSON_AURA + 50 < self.y + self.dy < HEIGHT - PERSON_AURA):
            self.dy *= -1
        
        self.x += self.dx
        self.y += self.dy

    def cure(self):
        if self.illness > 0:
            self.illness -= 1
            if self.illness == 0:
                self.immune = IMMUNE_TIME

        if self.immune > 0:
            self.immune -= 1


def check_infection(p1, p2):
    for (attacker, victim) in [(p1, p2), (p2, p1)]:
        if attacker.illness > 0 and victim.illness == 0 and victim.immune == 0:
            prob = INFECTION_PROBABILITY_WITH_MASK if (attacker.mask or victim.mask) else INFECTION_PROBABILITY_WITHOUT_MASK
            if randint(1, prob) == 1:
                victim.illness = ILLNESS_TIME

def modify(people):
    for person in people:
        person.move()
        person.cure()

    for i in range(len(people)):
        p1 = people[i]
        v1 = pygame.math.Vector2(p1.x, p1.y)
        
        for j in range(i + 1, len(people)):
            p2 = people[j]
            v2 = pygame.math.Vector2(p2.x, p2.y)
            
            if v1.distance_to(v2) < 2 * PERSON_AURA:
                check_infection(p1, p2)
                

def vaccine(people, pos):
    global BUDGET
    for person in people:
        if person.x - PERSON_AURA < pos[0] < person.x + PERSON_AURA \
                and person.y - PERSON_AURA < pos[1] < person.y + PERSON_AURA:
            if person.illness == 0 and person.immune == 0:
                if BUDGET >= VACCINE_PRICE:
                    person.immune = IMMUNE_TIME
                    BUDGET -= VACCINE_PRICE


def mask(people, pos):
    global BUDGET
    for person in people:
        if person.x - PERSON_AURA < pos[0] < person.x + PERSON_AURA \
                and person.y - PERSON_AURA < pos[1] < person.y + PERSON_AURA:
            if not person.mask and BUDGET >= MASK_PRICE:
                person.mask = True
                BUDGET -= MASK_PRICE
            else:
                person.mask = False


def draw(people):
    global pause
    _count_infected_people = 0
    screen.fill((20, 20, 25))

    current_day = (time // 60) + 1
    current_hour = (time % 60) * 24 // 60

    for person in people:
        _mask_thickness = 0
        if person.illness > 0:
            _color = PERSON_COLOR_INFECTED
            _count_infected_people += 1
        elif person.immune > 0:
            _color = PERSON_COLOR_IMMUNE
        else:
            _color = PERSON_COLOR_CLEAR
        
        if person.mask: _mask_thickness = 4
        pygame.draw.circle(screen, _color, (int(person.x), int(person.y)), PERSON_AURA, _mask_thickness)

    pygame.draw.rect(screen, (40, 40, 50), (0, 0, WIDTH, 50)) # UI Panel background
    font = pygame.font.SysFont("Consolas", 24)
    ui_text = f" CASES: {_count_infected_people} | DAY: {current_day} ({current_hour:02}:00) | BUDGET: {BUDGET}$"
    text_surface = font.render(ui_text, True, (255, 255, 255))
    screen.blit(text_surface, (20, 12))

    # --- Legend with Symbols ---
    legend_font = pygame.font.SysFont("Consolas", 20)
    r = 10 
    y_center = 25
    start_x = 750

    # List of elements: (Color, String, Mask_thickness)
    legend_items = [
        (PERSON_COLOR_CLEAR, "CLEAR", 0),
        (PERSON_COLOR_INFECTED, "INFECTED", 0),
        (PERSON_COLOR_IMMUNE, "IMMUNE", 0),
        ((200, 200, 200), "MASK", 3)
    ]

    for i, (color, label, thickness) in enumerate(legend_items):
        x_offset = start_x + (i * 130)
        # Circle
        pygame.draw.circle(screen, color, (x_offset, y_center), r, thickness)
        # String
        l_text = legend_font.render(label, True, (200, 200, 200))
        screen.blit(l_text, (x_offset + 15, y_center - 7))

    # Victory Screen
    if _count_infected_people == 0:
        pause = True
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(180); s.fill((0,0,0)); screen.blit(s, (0,0))
        
        v_font = pygame.font.SysFont("Impact", 80)
        v_text = v_font.render("MISSION ACCOMPLISHED", True, (0, 255, 100))
        screen.blit(v_text, (WIDTH//2 - v_text.get_width()//2, HEIGHT//2 - 100))
        
        stat_font = pygame.font.SysFont("Consolas", 30)
        stats = [
            f"Total Days: {current_day}",
            f"Remaining Budget: {BUDGET}$",
            "Result: Epidemic Contained"
        ]
        for i, line in enumerate(stats):
            s_surf = stat_font.render(line, True, (200, 200, 200))
            screen.blit(s_surf, (WIDTH//2 - s_surf.get_width()//2, HEIGHT//2 + 20 + i*40))

    pygame.display.update()
    fps.tick(PERSON_SPEED)

# Create people
main_people_list = [Person(randint(50, WIDTH-50), randint(100, HEIGHT-50)) for i in range(NUMBER_OF_PEOPLE)]

# The first infection
for i in range(FIRST_CONTACT):
    main_people_list[i].illness = ILLNESS_TIME

# Main program
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: pause = not pause
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: vaccine(main_people_list, pygame.mouse.get_pos())
            if event.button == 3: mask(main_people_list, pygame.mouse.get_pos())
    
    if not pause:
        modify(main_people_list)
        time += 1

    draw(main_people_list)