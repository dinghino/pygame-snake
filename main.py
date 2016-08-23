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

# images
img_head = pygame.image.load('./assets/snake_head.png')
img_tail = pygame.image.load('./assets/snake_tail.png')


class Snake():
    def __init__(self, game, startCoords, size):
        # size in px of each block (each block will be a square)
        # will be used to simulate the speed movement too
        self.size = size
        self.growRate = 1
        self.color = GREEN
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
        # direction of movement of the head
        self.direction = None
        # True if the snake hit itself
        self.autoCollided = False
        # images for the snake
        self.head_sprite = img_head
        self.tail_sprite = img_tail
        # stop the snake
        self.changeDirection('stop')

        # the next two calls are used to create placeholder blocks that will
        # be placed respectively under the tail and the head of the snake

        # head block
        self.createBlock(self.leadCoords)

    def createBlock(self, coordinates):
        ''' Create a block of the snake with in the given coordinates
        and append it to the blocks list ready to be rendered. '''
        block = pygame.Rect(coordinates, (self.size, self.size))
        self.blocks.append(block)

        return block

    def drawHead(self):
        if self.direction == 'left':
            self.head_sprite = self.rotateSprite(img_head, 90)
        elif self.direction == 'right':
            self.head_sprite = self.rotateSprite(img_head, 270)
        elif self.direction == 'up':
            self.head_sprite = img_head
        elif self.direction == 'down':
            self.head_sprite = self.rotateSprite(img_head, 180)

        block = self.blocks[-1]
        self.game.blit(self.head_sprite, block.topleft)

    def drawTail(self):
        block = self.blocks[0]
        # determine the anchor point of the tail sprite relative to the last
        # block of the snake body so that it's outside of the body blocks but
        # follows them correctly (apart from rotation)
        anchor = block.topleft

        if len(self.blocks) == 1:
            # evaluate rotation around
            # the only block available at the beginning and rotate accordingly
            if self.direction == 'up' or self.direction == 'stop':
                anchor = block.bottomleft
            elif self.direction == 'down':
                self.tail_sprite = self.rotateSprite(img_tail, 180)
                anchor = [block.x, block.y - self.size]
            elif self.direction == 'left':
                self.tail_sprite = self.rotateSprite(img_tail, 90)
                anchor = block.topright
            elif self.direction == 'right':
                self.tail_sprite = self.rotateSprite(img_tail, 270)
                anchor = [block.x - self.size, block.y]
        else:
            # if there are more than one block use the last two block to decide
            # the rotation of the tail sprite. location will be defaulted inside
            # the tail block, so collision will work
            prev_block = self.blocks[1]

            if prev_block.y > block.y:    # snake going down
                self.tail_sprite = self.rotateSprite(img_tail, 180)
            elif prev_block.y < block.y:  # snake going up
                self.tail_sprite = img_tail
            elif prev_block.x > block.x:  # going right
                self.tail_sprite = self.rotateSprite(img_tail, 270)
            elif prev_block.x < block.x:  # going left
                self.tail_sprite = self.rotateSprite(img_tail, 90)

        self.game.blit(self.tail_sprite, anchor)

    def draw(self):
        '''Before drawing remove the last block if needed'''
        self.handleLength()

        # draw a rectangle for each block in the list excluding
        # the first (the tail) and the last (the head)
        for block in self.blocks[1:-1]:
            pygame.draw.rect(self.game, GREEN, block)

        # draw the head of the snake
        self.drawHead()
        # draw the tail of the snake
        self.drawTail()

    def rotateSprite(self, image, angle):
        ''' Rotate a given pygame.image by <angle> degrees. '''
        return pygame.transform.rotate(image, angle)

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

        # check if the head block collide with any other block of the snake
        for block in self.blocks[:-1]:
            if self.blocks[-1].colliderect(block):
                self.autoCollided = True

        return self.autoCollided

    def changeDirection(self, direction):
        ''' Change the direction of movement for the snake head
        and rotate the head sprite accordingly
        '''
        # if, on any case, the snake is moving on the opposite direction, don't
        # change the direction of movement as it would cause collision and/or
        # an easier game
        if direction == 'stop':
            self.lead_x_change = 0
            self.lead_y_change = 0
        elif direction == 'left':
            if self.direction == 'right':
                return
            self.lead_x_change = -self.size
            self.lead_y_change = 0
        elif direction == 'right':
            if self.direction == 'left':
                return
            self.lead_x_change = self.size
            self.lead_y_change = 0
        elif direction == 'up':
            if self.direction == 'down':
                return
            self.lead_y_change = -self.size
            self.lead_x_change = 0
            self.tail_sprite = img_tail
        elif direction == 'down':
            if self.direction == 'up':
                return
            self.lead_y_change = self.size
            self.lead_x_change = 0

        # if we didn't return sooner store the direction locally
        # to do other things like animate the sprites etc
        self.direction = direction

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
        self.initialized = True

    def textCentered(self, message, color=WHITE, y_displace=0):
        '''Print a message on the screen to interact with the player. '''
        txt = self.font.render(message, True, color)
        # get the wrapping rectangle for the text
        txtRect = txt.get_rect()
        # center the text container in the window
        txtRect.center = (self.width / 2), (self.height / 2) + y_displace

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
                    self.snake.changeDirection('left')
                elif e.key == 100:  # D Key right
                    self.snake.changeDirection('right')
                elif e.key == 119:  # W Key up
                    self.snake.changeDirection('up')
                elif e.key == 115:  # S Key down
                    self.snake.changeDirection('down')
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
        snakeHead_x = self.snake.blocks[-1].x
        snakeHead_y = self.snake.blocks[-1].y

        if snakeHead_x + self.snake.size >= self.width or snakeHead_x < 0 or \
           snakeHead_y + self.snake.size >= self.height or snakeHead_y < 0:
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
        # TODO: Enable this once the tail is shown correctly
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
        self.game.fill(BLACK)
        self.textCentered('GAME OVER!', RED, y_displace=-50)
        self.textCentered('Your score %s' % self.appleEaten, GREEN)
        self.textCentered('[C]ontinue or [Q]uit', y_displace=50)
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
                    self.initialized = False
                    self.run()

    def quit(self):
        ''' Called when both self.gameExit is set to True. '''
        pygame.quit()
        quit()

    def run(self):
        if not self.initialized:
            self.init()

        while not self.gameExit:
            while self.gameOver:
                self.gameOverLoop()

            self.gameLoop()

        # once out of the loops quit the program
        self.quit()

    def pause(self):
        self.snake.changeDirection('stop')

game = Game(fps=12)
game.run()
