#ALGORITHMIC MAZE RUNNER
#Made by Garreth Lee

import pygame
import random
import time
import sys
from pygame.draw import rect
from pygame.constants import MOUSEBUTTONDOWN


##################### CLASSES #######################

#NODE IN FRONTIER
class Node():
    def __init__(self, parent, state, action):
        self.parent = parent #node
        self.state = state #tuple
        self.action = action #tuple

#DEPTH FIRST SEARCH (DFS)
class StackFrontier():
    def __init__(self):
        self.frontier = []
        
    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception('Frontier already empty!')
        else:
            node = self.frontier[-1]
            self.frontier.remove(node)
            return [node]

#BREADTH FIRST SEARCH (BFS)
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception('Frontier already empty!')
        else:
            node = self.frontier[0] 
            self.frontier.remove(node)
            return [node]

#A* SEARCH FRONTIER (MANHATTAN DISTANCE HEURISTIC FUNCTION)
class ManhattanFrontier(StackFrontier):
    def remove(self, cost):
        if self.empty():
            raise Exception('Frontier already empty!')
        else:
            best_neighbor = set()
            best_neighbor_cost = 0
            for node in self.frontier:
                x,y = node.state
                absolute_cost = cost + abs(x-9) + abs(y-9)
                if len(best_neighbor) == 0 or absolute_cost < best_neighbor_cost:
                    best_neighbor = {node}
                    best_neighbor_cost = absolute_cost
                elif absolute_cost == best_neighbor_cost:
                    best_neighbor.add(node)

            for neighbor in best_neighbor:
                self.frontier.remove(neighbor)

            return best_neighbor

#MAZE OBJECT
class Maze():
    def __init__(self, board, algorithm):
        self.board = board
        self.start = (0,0)
        self.goal = (9,9)
        self.algorithm = algorithm
        self.walls = []
        self.height = self.width = len(self.board)

        for i in range(self.height):
            row = []
            for j in range(self.width):
                if self.board[i][j] and (i,j) not in (self.start, self.goal):
                    row.append(True)
                else:
                    row.append(False)
            self.walls.append(row)


    def find_neighbors(self, state):

        self.neighbors = []

        x,y = state

        possible_actions = [
            ('down', (x, y+1)),
            ('right', (x+1, y)),
            ('up', (x, y-1)),
            ('left', (x-1, y))
        ]

        random.shuffle(possible_actions)

        for action, result in possible_actions:
            x, y = result
            try:
                if not self.walls[x][y] and (0 <= x < self.width) and (0 <= y < self.height):
                    self.neighbors.append((action, result))
            except IndexError:
                continue

        return self.neighbors

    def solve(self, show_steps):

        self.cost = 0
        
        self.cells = list() if show_steps else set()

        start = Node(parent = None, state = self.start, action = None)

        if self.algorithm == 1:
            frontier = StackFrontier()
        elif self.algorithm == 2:
            frontier = QueueFrontier()
        elif self.algorithm == 3:
            frontier = ManhattanFrontier()

        frontier.add(start)
        
        while True:
            if frontier.empty():
                return None

            self.cost += 1

            nodes = frontier.remove(self.cost) if self.algorithm == 3 else frontier.remove()

            for node in nodes:

                if self.goal == node.state:
                    moves = []
                    while node.parent != None:
                        moves.append(node.state)
                        node = node.parent
                    moves.reverse()
                    if show_steps:
                        return (self.cells, moves)
                    else:
                        return moves

                if show_steps and node.state not in self.cells:
                    self.cells.append(node.state)
                if not show_steps:
                    self.cells.add(node.state)


                for action, state in self.find_neighbors(node.state):
                    if not frontier.contains_state(self.goal) and state not in self.cells:
                        child = Node(parent = node, state = state, action = action)
                        frontier.add(child)

#DROPDOWN MENU FOR ALGORITHM SELECTION
class DropDown():

    def __init__(self, x,y,w,h,color, highlight_color, font, options, selected = 0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x,y,w,h)
        self.font = font
        self.options = options
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2) #border
        msg = self.font.render(self.options[self.selected], 1, (0,0,0))
        surface.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                if i == 0:
                    pygame.draw.rect(surface, (200,200,200), rect)
                else:
                    pygame.draw.rect(surface, self.highlight_color if i == self.active_option else self.color, rect)

                msg = self.font.render(text, 1, (0,0,0))
                surface.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * (len(self.options)))
            pygame.draw.rect(surface, (0,0,0), outer_rect, 2) 

        else:
            for i in range(len(self.options)):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surface, (0,0,0), rect)


        
    def update(self, events):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                if i != 0:
                    self.active_option = i
                    break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option

        return -1

#CHECKBOX TO SELECT SHOW MOVES OR NOT
class Checkbox():
    def __init__(self, rect, text, font):
        self.rect = rect
        self.fill_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width // 1.6, self.rect.height // 1.6)
        self.selected = False
        self.hovered = False
        self.font = font
        self.filled_color = (0,0,0)
        self.empty_color = (255,255,255)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, self.empty_color, self.rect)
        if self.hovered:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        if self.selected:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        msg = self.font.render(self.text, 1, (255,255,255))
        surface.blit(msg, (self.rect.x + 30, self.rect.y + 2.5))
        

    def update(self, events):

        mpos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mpos):
            self.hovered = True
        else:
            self.hovered = False

        for event in events:
            if self.rect.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.selected = not self.selected
                    break

        return self.selected
        

################# PROGRAM #####################

size = (900,600)
w,h = size

YELLOW = (255,255,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
RED = (255,0,0)
ORANGE = (255,125,123)
PURPLE = (81,61,130)

pygame.init()
pygame.font.init()
screen  = pygame.display.set_mode(size)
pygame.display.set_caption('Algorithmic Maze Runner')

running = True
cursor_drag = False
board_drawn = False
algo_list_drawn = False
homepage = True
checkbox_filled = False

algorithm = 0

def draw_board():
    for row in range(1,11):
        boxes = []
        for col in range(1,11):
            box = pygame.Rect(50*row,50*col,50,50)
            if (row, col) not in ((1,1),(10,10)):
                pygame.draw.rect(screen, ORANGE, box, 3)
            else:
                pygame.draw.rect(screen, RED, box)
                pygame.draw.rect(screen, ORANGE, box, 3)
            boxes.append(False)
            coordinates.append((50*row,50*col))
        board.append(boxes)

board = []
coordinates = []



LARGE_TEXT = pygame.font.SysFont('segoeuisemibold', 30)
BTN_TEXT = pygame.font.SysFont('segoeuisemibold', 22) 


reset_button = pygame.Rect(600,100,100,50)
algo_list = DropDown(600,200,190,40, WHITE, (100,200,255), BTN_TEXT, ['Pick an Algorithm','DFS','BFS','A* Search'])
solve_button = pygame.Rect(600,475,100,50)
checkbox = Checkbox(pygame.Rect(600,425,25,25), 'Show steps taken', BTN_TEXT)
play_button = pygame.Rect(w/2-50,350,100,50)

while running:  
    events = pygame.event.get()
    for event in events:

        #QUIT PROGRAM
        if event.type == pygame.QUIT:
            running = False
            break

        #HOME PAGE
        if homepage:
            #TITLE
            title = LARGE_TEXT.render("Algorithmic Maze Runner", 1, WHITE)
            title_rect = title.get_rect()
            title_rect.center = (w/2, 80)
            screen.blit(title, title_rect)

            #INSTRUCTIONS
            instructions = [
                'Click the cells to make walls',
                'Right-click to erase walls',
                'Pick an algorithm to run',
                'Check "Show Steps Taken" to see the algorithm in action!'
                '',
                'Note: Avoid placing too little walls for the BFS algorithm!'
            ]

            for i, text in enumerate(instructions):
                line = BTN_TEXT.render(text, 1, WHITE)
                line_rect = line.get_rect()
                line_rect.center = (w/2, 150 + i*40)
                screen.blit(line, line_rect)

            #PLAY BUTTON
            pygame.draw.rect(screen, WHITE, play_button)
            play = BTN_TEXT.render('PLAY', 1, BLACK)
            screen.blit(play, (play_button.x + 25, play_button.y + 12.5))

            mpos = pygame.mouse.get_pos()

            if play_button.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    homepage = False
                    screen.fill(BLACK)
                
            
        else:

            #DRAWS THE EMPTY BOARD
            if not board_drawn:
                draw_board()
                board_drawn = True

            #draws the reset button
            pygame.draw.rect(screen, WHITE, reset_button)
            reset_button_text = BTN_TEXT.render("Reset", 1, (BLACK))
            screen.blit(reset_button_text, (reset_button.x + 22.5, reset_button.y + 12.5))

            #draws the solve button
            pygame.draw.rect(screen, WHITE, solve_button)
            solve_button_text = BTN_TEXT.render('Solve',1,BLACK)
            screen.blit(solve_button_text, (solve_button.x + 22.5, solve_button.y + 12.5))
            
            #DROPDOWN MENU
            selected_option = algo_list.update(events)
            if selected_option > 0:
                algorithm = selected_option
            algo_list.draw(screen)

            #CHECKBOX MENU
            checkbox_filled = checkbox.update(events)
            checkbox.draw(screen)

            #IF MOUSE IS PRESSED
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                cursor_drag = True
                button = event.button
                mousePos = pygame.mouse.get_pos()

                #SOLVE BUTTON
                if solve_button.collidepoint(mousePos):
                    
                    #IF TOO LITTLE WALLS
                    if sum(sum(row) for row in board) < 25 and algorithm in (2,3):
                        rect = pygame.Rect(600,565,100,50)
                        msg = BTN_TEXT.render('Please put more walls!', 1, RED)
                        screen.blit(msg, (rect.x,rect.y))

                    else:
                        #REMOVE MORE WALLS TEXT
                        rect = pygame.Rect(600,565,100,50)
                        msg = BTN_TEXT.render('Please put more walls!', 1, BLACK)
                        screen.blit(msg, (rect.x,rect.y))

                        #EMPTY BOARD 
                        for i in range(len(board)):
                            for j in range(len(board)):
                                if not board[i][j] and (i,j) not in ((0,0),(9,9)):
                                    box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                    pygame.draw.rect(screen, BLACK, box)
                                    pygame.draw.rect(screen, ORANGE, box, 3)
                                    
                        if algorithm != 0:

                            #REMOVE PICK AN ALGORITHM TEXT
                            rect = pygame.Rect(600,50,100,50)
                            msg = BTN_TEXT.render('Please pick an algorithm', 1, BLACK)
                            screen.blit(msg, (rect.x,rect.y))

                            #MAKE MAZE OBJECT
                            maze = Maze(board, algorithm)
                            pygame.display.set_caption('Loading... DO NOT CLICK ANYTHING WHILE LOAD!')
                            solved = maze.solve(checkbox_filled)

                            #PREVENT USER FROM CLICKING WHILE ALGORITHM IS RUNNING
                            pygame.event.set_blocked(MOUSEBUTTONDOWN)

                            if solved and checkbox_filled:

                                #REMOVE UNSOLVABLE TEXT
                                rect = pygame.Rect(600,535,100,50)
                                msg = BTN_TEXT.render('Unsolvable!', 1, BLACK)
                                screen.blit(msg, (rect.x,rect.y))

                                #SHOW ALGORITHM PATHFINDING
                                pygame.display.set_caption('Algorithmic Maze Runner')
                                steps, solution = solved
                                for step in steps:
                                    if step not in ((0,0),(9,9)):
                                        time.sleep(0.1)
                                        i,j  = step
                                        box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                        pygame.draw.rect(screen, YELLOW, box)
                                        pygame.draw.rect(screen, ORANGE, box, 3)
                                        pygame.display.update()

                            if solved:
                                solution = solution if checkbox_filled else solved
                                #SHOW FINAL SOLUTION
                                for move in solution:
                                    if move not in ((0,0),(9,9)):
                                        time.sleep(0.1)
                                        i,j = move
                                        box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                        pygame.draw.rect(screen, GREEN, box)
                                        pygame.draw.rect(screen, ORANGE, box, 3)
                                        pygame.display.update()
                            
                            #IF UNSOLVABLE
                            else:
                                rect = pygame.Rect(600,535,100,50)
                                msg = BTN_TEXT.render('Unsolvable!', 1, RED)
                                screen.blit(msg, (rect.x,rect.y))

                            pygame.event.set_allowed(MOUSEBUTTONDOWN)

                        #IF ALGORITHM NOT YET PICKED
                        else:
                            rect = pygame.Rect(600,50,100,50)
                            msg = BTN_TEXT.render('Please pick an algorithm', 1, RED)
                            screen.blit(msg, (rect.x,rect.y))

                #RESET BUTTON
                if reset_button.collidepoint(mousePos):
                    board_drawn = False
                    board = []
                    coordinates = []
                    screen.fill(BLACK)

                #CLICK ON SQUARE(S)   
                else:
                    for x,y in coordinates:
                        if (x,y) not in ((50,50),(500,500)):
                            box = pygame.Rect(x,y,50,50)
                            if box.collidepoint(mousePos):
                                if event.button == 1:
                                    pygame.draw.rect(screen, PURPLE, box)
                                    pygame.draw.rect(screen, ORANGE, box,3)
                                    board[int(y/50-1)][int(x/50-1)] = True
                                elif event.button == 3:
                                    pygame.draw.rect(screen, BLACK, box)
                                    pygame.draw.rect(screen, ORANGE, box,3)
                                    board[int(y/50-1)][int(x/50-1)] = False                        
                                break
            
            #IF MOUSE IS LIFTED UP
            if event.type == pygame.MOUSEBUTTONUP:
                cursor_drag = False
            
            #IF MOUSE IS DRAGGED AROUND
            if event.type == pygame.MOUSEMOTION:
                if cursor_drag:
                    mousePos_x, mousePos_y = pygame.mouse.get_pos()
                    x, y = round(mousePos_x / 50) * 50, round(mousePos_y / 50) * 50
                    if (x, y) in coordinates and (x,y) not in ((50,50),(500,500)):
                        box = pygame.Rect(x, y, 50,50)    
                        if box.collidepoint(x, y):
                            if button == 1:
                                pygame.draw.rect(screen, PURPLE, box)
                                pygame.draw.rect(screen, ORANGE, box,3)
                                board[int(y/50-1)][int(x/50-1)] = True
                                pygame.display.update()
                                break
                            elif button == 3:
                                pygame.draw.rect(screen, BLACK, box)
                                pygame.draw.rect(screen, ORANGE, box,3)
                                board[int(y/50-1)][int(x/50-1)] = False
                                pygame.display.update()
                                break   
        pygame.display.update()
                            

            
            
            

