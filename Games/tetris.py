from enum import Enum
import pygame
import random
import time
import copy

HEIGHT = 500
WIDTH = 500
LEFT = (-1,0)
RIGHT = (1,0)
DOWN = ( 0,1)
CELLS = (10,13)
BUTTON_PAD = 3

color_now = 0
colors = [(255,  0,  0,255),	#RED
	  (255,255,  0,255),	#YELLOW
	  (  0,255,255,255),	#CYAN
	  (255,  0,255,255),	#PINK
	  (  0,255,  0,255),	#GREEN
	  (  0,  0,255,255)]	#BLUE

pygame.display.init()
pygame.font.init()
pygame.display.set_caption('TETRIS - Let\'s Play!')
smallfont = pygame.font.SysFont('comicsansms',15)
mediumfont = pygame.font.SysFont('comicsansms',25)
largefont = pygame.font.SysFont('comicsansms',38)

screen = pygame.display.set_mode((WIDTH,HEIGHT))

gameback = pygame.surface.Surface((WIDTH*7//10,HEIGHT*4//5))
gamestats = pygame.surface.Surface((WIDTH*7//10, HEIGHT//5))
gamemenu = pygame.surface.Surface((WIDTH*3//10, HEIGHT))
shapeview = pygame.surface.Surface((75, 75))
gameback.fill((100,100,100))
gamestats.fill((0,100,100))
gamemenu.fill((100,0,100))
shapeview.fill((100,100,100))
shaperect = shapeview.get_rect()
pygame.draw.rect(shapeview, (0,0,0,255), (0,0,shaperect.height,shaperect.width), BUTTON_PAD)

def text_objects(text, color,size = "small"):

    if size == "small":
        textSurface = smallfont.render(text, True, color)
    if size == "medium":
        textSurface = mediumfont.render(text, True, color)
    if size == "large":
        textSurface = largefont.render(text, True, color)

    return textSurface, textSurface.get_rect()

def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size = "small"):
    textSurf, textRect = text_objects(msg,color,size)
    textRect.center = ((buttonx+(buttonwidth/2)), buttony+(buttonheight/2))
    screen.blit(textSurf, textRect)
   
def message_to_screen(msg,color, center_x, center_y, size = "small"):
    textSurf, textRect = text_objects(msg,color,size)
    textRect.center = (center_x, center_y)
    screen.blit(textSurf, textRect)

class Box:
	# Create grid of col + 2 columns and row + 1 rows with first and last column of 1's
	grid = [[int(not(col%(CELLS[0]+1))) for col in range(CELLS[0]+2)] for row in range(CELLS[1]-1)]
	# Set the last row 1 as well to create a buffer
	grid.append([1 for col in range(CELLS[0]+2)])
	#print(grid)
	CELL_SIZE = WIDTH*7//(10*CELLS[0])	#Width of gamescreen = WIDTH*7//10
	LEFT = -CELL_SIZE 			#To align second column with edge of screen
	TOP = HEIGHT*3//20
	def __init__(self, color):
		self.is_active = True
		self.shape = pygame.surface.Surface((Box.CELL_SIZE-BUTTON_PAD,Box.CELL_SIZE-BUTTON_PAD))
		self.shape.fill(color)

	def place(self, row, col):
		self.col = col
		self.row = row
		self.checkAround()
		
	def checkAround(self):
		self.left = Box.grid[self.row][self.col-1]
		self.right = Box.grid[self.row][self.col+1]
		self.down = Box.grid[self.row+1][self.col]
		
	def move(self, direction):
		#If no block below, fall down
		if Box.grid[self.row+direction[1]][self.col+direction[0]] == 0:
			Box.grid[self.row][self.col] = 0
			self.row += direction[1]
			self.col += direction[0]
			Box.grid[self.row][self.col] = self
		#If there is a block below, deactivate block
		elif direction is DOWN:
				self.is_active = False
		# Check the suroundings
		self.checkAround()
		return self.is_active
		#print(Box.grid,'AND',self.is_active)

	def draw(self, screen):
		screen.blit(self.shape, (Box.LEFT + Box.CELL_SIZE*self.col, Box.TOP + Box.CELL_SIZE * self.row))

class Shape:
	TOP = 0
	CENTER = (CELLS[0]-1)//2
	shapes = {'square':[(CENTER,TOP),(CENTER,TOP+1),(CENTER+1,TOP),(CENTER+1,TOP+1)],
		  'line':  [(CENTER-1,TOP),(CENTER,TOP),(CENTER+1,TOP),(CENTER+2,TOP)],
		  'lzag':  [(CENTER-1,TOP),(CENTER,TOP),(CENTER,TOP+1),(CENTER+1,TOP+1)],
		  'rzag':  [(CENTER-1,TOP+1),(CENTER,TOP),(CENTER,TOP+1),(CENTER+1,TOP)],
		  'lgun':  [(CENTER-1,TOP),(CENTER,TOP),(CENTER+1,TOP),(CENTER+1,TOP+1)],
		  'rgun':  [(CENTER-1,TOP),(CENTER-1,TOP+1),(CENTER,TOP),(CENTER+1,TOP)],
		  'arrow': [(CENTER-1,TOP),(CENTER,TOP),(CENTER,TOP+1),(CENTER+1,TOP)]}

	def __init__(self,shape_name,color):
		self.color = color 		# The color of all the blocks in the shape
		self.is_active = True		# As long as bottom is not grounded, is active
		self.has_fallen = False		# If a block does not fall, it means screen is 
		self.blocks = []		# full, signal game over
		for pos in Shape.shapes[shape_name]:
			Box.grid[pos[1]][pos[0]] = Box(color)
			Box.grid[pos[1]][pos[0]].place(pos[1], pos[0])
			self.blocks.insert(0,Box.grid[pos[1]][pos[0]])
			#print(pos,'AT',Box.grid[pos[1]][pos[0]])
	def revolveLeft(self):
		pass

	def fall(self):
		for block in self.blocks:
			if block.down != 0 and block.down not in self.blocks:
				self.is_active = False
				break
		for block in self.blocks:
			if self.is_active:
				block.move(DOWN)
				self.has_fallen = True
			else:	block.is_active = False

	def shiftLeft(self):
		for block in self.blocks:
			if block.left != 0 and block.left not in self.blocks:
				break
		else:
			for block in self.blocks[::-1]:
				block.move(LEFT)

	def shiftRight(self):
		for block in self.blocks:
			if block.right != 0 and block.right not in self.blocks:
				break
		else:
			for block in self.blocks:
				block.move(RIGHT)

	def draw(self,screen):
		for block in self.blocks:
			block.draw(screen)

curT = Shape(random.choice( list(Shape.shapes.keys()) ), random.choice(colors))
nexT = random.choice( list(Shape.shapes.keys()) )
#curT.place(0,5)

class Button:
	def __init__(self,text,backcolor,edgecolor,size = 'small'):
		self.text = text
		self.is_hovering = False
		self.textsize = size
		self.is_clicked = False
		self.backcolor = backcolor
		self.edgecolor = edgecolor

	def place(self,x1, y1, x2, y2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.buttonSurf = [self.button_surface(self.text, self.edgecolor, self.backcolor)]
		self.buttonSurf.append(self.button_surface(self.text, self.backcolor, self.edgecolor))

	def button_surface(self, text, textcol, backcol):
		buttonSurf = pygame.surface.Surface((self.x2-self.x1,self.y2-self.y1))
		buttonSurf.fill(backcol)
		pygame.draw.rect(buttonSurf, textcol,(0,0,self.x2-self.x1,self.y2-self.y1),BUTTON_PAD)
		#back = pygame.surface.Surface((x2-x1-2*BUTTON_PAD, y2-y1-2*BUTTON_PAD))
		#back.fill(backcol)
		#buttonSurf.blit(back, (BUTTON_PAD, BUTTON_PAD))
		textSurf, textRect = text_objects(text, textcol, self.textsize)
		textRect.center = ((self.x2-self.x1)//2,(self.y2-self.y1)//2)
		buttonSurf.blit(textSurf, textRect)

		return buttonSurf
		
	def draw(self,screen):
		screen.blit(self.buttonSurf[ self.is_hovering ], (self.x1,self.y1))

	def checkState(self, pos, click):
		if self.isHovered(pos[0], pos[1]):
			self.is_hovering = True
			if click[0] == 1:
				self.is_clicked = True
			else:   self.is_clicked = False
		else:
			self.is_hovering = False
			self.is_clicked = False
	
	def isHovered(self, x1, y1):
		return x1 > self.x1 and x1 < self.x2 and y1 > self.y1 and y1 < self.y2
class Status(Enum):
	RUNNING = 2
	WON = 1
	LOST = 0
	
class Game:
	status = Status.RUNNING

def draw_stats(screen, score = 0, time = 0, points = 0, level = 1, max_points = 10):
	screen.blit(gamestats,(0,0))
	message_to_screen('Level '+str(level), (0,255,255,255), WIDTH//3, HEIGHT//20,'medium')
	message_to_screen('Points needed: '+str(max_points),(0,255,255,255), WIDTH//3, HEIGHT//10, 'medium')
	message_to_screen('Score: '+str(score), (0,255,255,255), WIDTH//10, HEIGHT//6,'small')
	message_to_screen('Time: '+str(time), (0,255,255,255), WIDTH//3, HEIGHT//6,'small')
	message_to_screen('Points: '+str(points), (0,255,255,255), WIDTH*3//5, HEIGHT//6,'small')

def draw_menu(screen, color_now, shape = None):
	screen.blit(gamemenu, (WIDTH*7//10,0))
	shaperect.center = (WIDTH*17//20, HEIGHT*2//10)
	screen.blit(shapeview, shaperect)
	pauseButton.draw(screen)
	quitButton.draw(screen)
	message_to_screen('NEXT SHAPE', (0,0,255,255), WIDTH*34//40, HEIGHT*2//20, 'small')
	message_to_screen('T', colors[(color_now+0)%6], WIDTH*365//500, HEIGHT*2//5, 'large')
	message_to_screen('E', colors[(color_now+1)%6], WIDTH*389//500, HEIGHT*2//5, 'large')
	message_to_screen('T', colors[(color_now+2)%6], WIDTH*413//500, HEIGHT*2//5, 'large')
	message_to_screen('R', colors[(color_now+3)%6], WIDTH*439//500, HEIGHT*2//5, 'large')
	message_to_screen('I', colors[(color_now+4)%6], WIDTH*460//500, HEIGHT*2//5, 'large')
	message_to_screen('S', colors[(color_now+5)%6], WIDTH*483//500, HEIGHT*2//5, 'large')
	return color_now + 1

def draw_gamescreen(screen, shape, canFall):
	screen.blit(gameback,(0,HEIGHT//5))
	if shape.is_active:
		if canFall: shape.fall()
		#print('FALLING',shape.getLeft(),shape.getRight())
	else:
		if shape.has_fallen is False:
			Game.status = Status.LOST
		deactivated.extend([block for block in shape.blocks])
		global curT
		global nexT
		global spacebar_was_pressed
		curT = Shape(nexT, random.choice(colors))
		nexT = random.choice( list(Shape.shapes.keys()) )
		spacebar_was_pressed = False
	
	for block in deactivated:
		block.draw(screen)
	shape.draw(screen)

pauseButton = Button('Pause',(200,200,200,255), (100,100,100,255), 'medium')
playButton = Button('Play!', (200,200,200,255), (100,100,100,255), 'medium')
quitButton = Button('Quit', (200,200,200,255), (100,100,100,255), 'medium')
pauseButton.place(WIDTH*37//50,HEIGHT*3//5,WIDTH*47//50,HEIGHT*7//10)
playButton.place(WIDTH*37//50,HEIGHT*3//5,WIDTH*47//50,HEIGHT*7//10)
quitButton.place(WIDTH*37//50,HEIGHT*4//5,WIDTH*47//50,HEIGHT*9//10)
spacebar_was_pressed = False
deactivated = []
#looping = True
while Game.status == Status.RUNNING:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			Game.status = Status.LOST
		#Take player controls only if game is NOT PAUSED
		if event.type == pygame.KEYDOWN and not pauseButton.is_clicked:
			if event.key == pygame.K_SPACE:
				spacebar_was_pressed = True
			elif event.key == pygame.K_LEFT:# and curT.left == 0:
				curT.shiftLeft()
			elif event.key == pygame.K_RIGHT:# and curT.right == 0:
				curT.shiftRight()
		#if event.type == pygame.MOUSEBUTTONDOWN:

	#Check if the player pressed the quit button
	quitButton.checkState(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
	quitButton.draw(screen)
	#If YES, QUIT the game
	if quitButton.is_clicked:
		Game.status = Status.LOST

	#If the game is paused, check if the player presses PLAY!
	if pauseButton.is_clicked and not playButton.is_clicked:
		playButton.draw(screen)
		playButton.checkState(pygame.mouse.get_pos(), pygame.mouse.get_pressed())	
	#If the game is running, check is the player presses PAUSE
	else:
		playButton.is_clicked = False
		pauseButton.checkState(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
		color_now = draw_menu(screen,color_now)
		draw_gamescreen(screen, curT, not(color_now%4) or spacebar_was_pressed)
		draw_stats(screen)

	#Update the contents of the game screen, and give a little delay
	pygame.display.update()
	time.sleep(0.2)

pygame.display.quit()
