'''
Snake game
'''
import pygame
import random

# colors definition
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 155, 0)
BLUE = (0, 0, 255)

# Game constants for dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 10
# default sizes for the snake blocks and apple
DEF_SNAKE_SIZE = 20
DEF_APPLE_SIZE = 25


class Snake():
    def __init__(self, game, startCoords, size):
        # size in px of each block (each block will be a square)
        self.size = size
        self.growRate = 1
        self.color = GREEN
        # movement speed in px
        self.speed = size
        # initial position
        self.startCoords = startCoords
        self.game = game
        self.init()

    def init(self):
        '''Initialize the starting values for the snake'''
        # number of blocks of the body
        self.length = 1
        # coordinates of each block
        self.leadCoords = self.startCoords
        self.blocks = []
        # movement on the axis. will be handled externally
        self.lead_x_change = 0
        self.lead_y_change = 0
        # True if the snake hit itself
        self.autoCollided = False
        # stop the snake
        self.move('stop')

    def createBlock(self, coordinates):
        ''' Create a block of the snake with in the given coordinates
        and append it to the blocks list ready to be rendered. '''
        block = pygame.Rect(coordinates, (self.size, self.size))

        self.blocks.append(block)

        return block

    def draw(self):
        '''Before drawing remove the last block if needed'''
        self.handleLength()

        # draw a rectangle for each block in the list
        for block in self.blocks:
            pygame.draw.rect(self.game, self.color, block)

    def handleLength(self):
        ''' Remove the last elements of the blocks list
        if there are more than needed to draw the current length. '''
        while len(self.blocks) > self.length:
            del self.blocks[0]

    def eat(self, apple):
        ''' Determine if the snake collide with an apple. '''
        return self.blocks[-1].colliderect(apple.shape)

    def increaseLength(self):
        ''' What happens when the snake 'eats' (collide with) an apple. '''
        self.length += self.growRate

    def selfCollision(self):
        ''' Detect if the snake collide with itself. '''

        # check if the first block collide with any other block of the snake
        # if len(self.blocks) > 1:
        for block in self.blocks[1:]:
            if self.blocks[0].colliderect(block):
                self.autoCollided = True

        return self.autoCollided

    def move(self, direction):
        ''' change the lead_x_change and lead_y_change values
        with +- self.speed when requested by the game logic'''
        if direction == 'stop':
            self.lead_x_change = 0
            self.lead_y_change = 0
        elif direction == 'left':
            if self.lead_x_change > 0:
                return
            self.lead_x_change = -self.speed
            self.lead_y_change = 0
        elif direction == 'right':
            if self.lead_x_change < 0:
                return
            self.lead_x_change = self.speed
            self.lead_y_change = 0
        elif direction == 'up':
            if self.lead_y_change > 0:
                return
            self.lead_y_change = -self.speed
            self.lead_x_change = 0
        elif direction == 'down':
            if self.lead_y_change < 0:
                return
            self.lead_y_change = self.speed
            self.lead_x_change = 0

    def animate(self):
        ''' Generate a new set of coordinates for the snake head. '''

        # create ONE new block with the new coordinates and append it to
        # self.blocks
        # if growRate is greater than one, calculate the other new blocks coord
        # and create them too
        new_x = self.leadCoords[0] + self.lead_x_change
        new_y = self.leadCoords[1] + self.lead_y_change
        self.leadCoords = [new_x, new_y]
        self.createBlock(self.leadCoords)


class Apple():
    def __init__(self, game, window_w, window_h, size):
        # size in pixel
        self.size = size
        # pygame shape for the apple
        self.shape = None
        self.color = RED
        # game window dimensions
        self.window_w = window_w
        self.window_h = window_h
        # initial coordinates
        self.x, self.y = self.getCoords()

        self.game = game

        # create the snake
        self.create()

    def getCoords(self):
        ''' Get random coordinates for the apple.
        These coordinates are evaluated nside the game window '''
        x = random.randrange(0, self.window_w - self.size)
        y = random.randrange(0, self.window_h - self.size)
        # round to the nearest block size so it alignes with the snake
        self.x = round(x / self.size) * self.size
        self.y = round(y / self.size) * self.size

        return x, y

    def create(self):
        '''Create the pygame.Rect for the apple'''
        self.getCoords()
        self.shape = pygame.Rect((self.x, self.y), (self.size, self.size))

    def createsOn(self, snake=None):
        ''' check if the apple position overlaps with the snake body'''
        # TODO: Make thi works!
        #       The idea is that whenever a new apple is created and before
        #       the actual render, we check its collision with the snake,
        #       checking the apple shape against every snake element.
        #
        #        This should allow us to avoid generating an apple where the
        #        player can't go due to the snake self collision handling
        isColliding = True
        for block in snake.blocks:
            if not self.shape.colliderect(block):
                isColliding = False

        print ('apple cannot be created here (%s, %s). regenerating' %
               (self.x, self.y))
        return isColliding

    def draw(self):
        pygame.draw.rect(self.game, self.color, self.shape)


class Game():
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                 snakeSize=DEF_SNAKE_SIZE, appleSize=DEF_APPLE_SIZE,
                 fps=15, title='Slither'):
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.initFps = fps
        self.fps = fps
        self.title = title
        self.gameOver = False
        self.gameExit = False

        self.snakeSize = snakeSize
        self.appleSize = appleSize

        self.init()

    def init(self):
        '''Initialize the game variables. '''

        self.fps = self.initFps

        self.initResult = pygame.init()
        self.game = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.font = pygame.font.SysFont(None, 25)
        # center of the screen, will be our snake starting point
        self.center = [self.width / 2, self.height / 2]

        # create the snake and the apple
        self.snake = Snake(game=self.game, startCoords=self.center,
                           size=self.snakeSize)

        self.apple = Apple(game=self.game,
                           window_w=self.width,
                           window_h=self.height,
                           size=self.appleSize)

        self.appleEaten = 0

        self.snake.init()
        self.apple.create()

    def textCentered(self, message, color):
        '''Print a message on the screen to interact with the player. '''
        txt = self.font.render(message, True, color)
        # get the wrapping rectangle for the text
        txtRect = txt.get_rect()
        # center the text container in the window
        txtRect.center = (self.width / 2), (self.height / 2)

        # render the text
        self.game.blit(txt, txtRect)

    def showScore(self):
        text = 'Score: %s' % self.appleEaten
        screen_text = self.font.render(text, True, WHITE)
        self.game.blit(screen_text, [10, 10])

    def increaseSpeed(self):
        ''' increase the game speed and difficult
        Increasing the FPS rendered every 5 apple eaten up to 60 fps
        '''

        if (self.appleEaten % 5) == 0:
            if self.fps >= 60:
                self.fps = 60
            else:
                self.fps += 2

    def userEvents(self):
        '''Handle user inputs and other vents. '''
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.gameExit = True

            # move in one direction when a key is pressed
            # and stop moving in the other axis
            if e.type == pygame.KEYDOWN:
                if e.key == 97:     # A Key left
                    self.snake.move('left')
                elif e.key == 100:  # D Key right
                    self.snake.move('right')
                elif e.key == 119:  # W Key up
                    self.snake.move('up')
                elif e.key == 115:  # S Key down
                    self.snake.move('down')
                elif e.key == 19:   # pause
                    self.pause()
                    # TODO: Make pause work instead of causing suicide.
                    #       should probably stop the gameLoop
                    #       could be useful to refactor

    def gameEvents(self):
        '''Evaluate events caused by the game elements interaction
        with each other, such as reaching the boundaries of the screen, eating
        an apple and so on'''

        # screen boundaries interaction
        snakeHead_x = self.snake.leadCoords[0]
        snakeHead_y = self.snake.leadCoords[1]

        if snakeHead_x >= self.width or snakeHead_x <= 0 or \
           snakeHead_y >= self.height or snakeHead_y <= 0:
            # You lost!
            self.gameOver = True

        # if snake collided with itself then set gameOver
        if self.snake.autoCollided:
            print 'Snake tried to eat itself and commited suicide! :('
            self.gameOver = True

    def gameLoop(self):
        '''Game loop that runs while gameOver and gameExit are False. '''

        # reset the game view to BLACK
        self.game.fill(BLACK)
        # check for events
        self.userEvents()
        self.gameEvents()
        # show the score to the user
        self.showScore()
        # move the snake lead coordinates and create the new block
        self.snake.animate()

        # draw the updated elements on screen
        self.apple.draw()
        self.snake.draw()

        # evaluate if the snake collided with its body
        self.snake.selfCollision()

        # if the snake collided with the apple, create a new apple and
        # increase the length of the snake
        if self.snake.eat(self.apple):
            # increment difficult
            self.increaseSpeed()
            self.snake.increaseLength()
            self.apple.create()

            # increase the score by 1
            self.appleEaten += 1

        pygame.display.update()
        self.clock.tick(self.fps)

    def gameOverLoop(self):
        '''Game Over loop that runs when self.gameOver is True. '''
        self.textCentered('GAME OVER! [C]ontinue or [Q]uit', RED)
        pygame.display.update()

        # ask the user to Continue or Quit
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.gameExit = True
                self.gameOver = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    self.gameExit = True
                    self.gameOver = False

                elif e.key == pygame.K_c:
                    self.gameOver = False
                    self.run()

    def quit(self):
        ''' Called when both self.gameExit is set to True. '''
        pygame.quit()
        quit()

    def run(self):
        self.init()

        while not self.gameExit:
            while self.gameOver:
                self.gameOverLoop()

            self.gameLoop()

        # once out of the loops quit the program
        self.quit()

    def pause(self):
        self.snake.move('stop')

game = Game()
game.run()
