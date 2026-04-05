import pygame
import sys
import math
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
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Epidemic Simulator 1.0")
fps = pygame.time.Clock()
pause = False
time = 0


# Person class
class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = randint(-1, 1)
        self.dy = randint(-1, 1)
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

    screen.fill((0, 0, 0))

    for person in people:
        _mask = 0
        if person.illness > 0:
            _color = PERSON_COLOR_INFECTED
            if person.mask:
                _mask = 5
        elif person.immune > 0:
            _color = PERSON_COLOR_IMMUNE
            if person.mask:
                _mask = 5
        else:
            _color = PERSON_COLOR_CLEAR
            if person.mask:
                _mask = 5

        pygame.draw.circle(screen, (_color), (person.x, person.y), PERSON_AURA, _mask)

        if person.illness > 0:
            _count_infected_people += 1

    if _count_infected_people == 0:
        pause = True
        font = pygame.font.SysFont("Calibri", 100)
        text = font.render("VICTORY!", True, (200, 200, 200))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(text, text_rect)


    font = pygame.font.SysFont("Calibri", 30)

    text = font.render("Actice cases: " + str(_count_infected_people), True, (200, 200, 200))
    text_rect = text.get_rect()
    text_rect.left = 10
    text_rect.top = 10
    screen.blit(text, text_rect)

    text = font.render("Time: " + str(time), True, (200, 200, 200))
    text_rect = text.get_rect()
    text_rect.left = 250
    text_rect.top = 10
    screen.blit(text, text_rect)

    text = font.render("Budget: " + str(BUDGET), True, (200, 200, 200))
    text_rect = text.get_rect()
    text_rect.left = 450
    text_rect.top = 10
    screen.blit(text, text_rect)

    text = font.render("Clear:       Infected:       Immune:       Mask:", True, (200, 200, 200))
    text_rect = text.get_rect()
    text_rect.left = 700
    text_rect.top = 10
    screen.blit(text, text_rect)

    pygame.draw.circle(screen, (PERSON_COLOR_CLEAR), (795, 23), PERSON_AURA, 0)
    pygame.draw.circle(screen, (PERSON_COLOR_INFECTED), (950, 23), PERSON_AURA, 0)
    pygame.draw.circle(screen, (PERSON_COLOR_IMMUNE), (1110, 23), PERSON_AURA, 0)
    pygame.draw.circle(screen, (PERSON_COLOR_CLEAR), (1230, 23), PERSON_AURA, 5)

    pygame.display.update()
    fps.tick(PERSON_SPEED)


# Create people
main_people_list = [Person(randint(50, WIDTH-50), randint(50, HEIGHT-50))
                   for i in range(NUMBER_OF_PEOPLE)]


# The fist infection
for i in range(FIRST_CONTACT):
    main_people_list[i].illness = ILLNESS_TIME


# Main program
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                vaccine(main_people_list, pygame.mouse.get_pos())
            if event.button == pygame.BUTTON_RIGHT:
                mask(main_people_list, pygame.mouse.get_pos())
    if not pause:
        modify(main_people_list)
        draw(main_people_list)
        time += 1