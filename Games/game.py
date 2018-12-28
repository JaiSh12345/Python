from PIL import Image
from io import BytesIO
from time import sleep
import selenium
import pyautogui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

speed = 1000

def decode(image):
	image = Image.open(image)
	pixels = image.load()
	obstacle = None
	for col in range(image.width):
		if pixels[col,120][0] == 83:
			if pixels[col,115] == 83:
				print('JUMP! HIGH!')
				obstacle = ['large cactus',col]
			else:
				print('JUMP!')
				obstacle = ['small cactus/low bird',col]
			break
		if pixels[col,100][0] == 83:
			print('JUMP!')
			obstacle = ['med bird',col]
			break
		if pixels[col,80][0] == 83:
			print('DUCK!')
			obstacle = ['high bird',col]
			break
	print('Obstacle =',obstacle)
	return obstacle
def getAction(obstacle):
	if obstacle is not None:
		time = obstacle[1]/speed
		if obstacle[0] in ['high bird','medium bird']:
			action = 'duck'
		else:
			action = 'jump'
		sleep(time)
		return action

def getGameArea():
	try:
		a = web.find_element_by_class_name('runner-canvas')
		return a,a.rect
	except selenium.common.exceptions.NoSuchElementException:
		print('Not Offline!')
		raise

def crop(image, rect):
	print(rect)
	l = rect['x']
	t = rect['y']
	image = Image.open(BytesIO(image))
	image = image.crop( (l+70, t, l + rect['width']-150, t + rect['height']-20) )
	image.save('screen.png')

web = selenium.webdriver.Chrome('c:/Python34/Scripts/chromedriver.exe')
web.get('https://www.geeksforgeeks.org')
try:
	body = web.find_element_by_tag_name('body')
	body.send_keys(Keys.ARROW_UP)
	web.maximize_window()
	screen,rect = getGameArea()
	action = ActionChains(web)
	#Start game	
	while True:
		crop( web.get_screenshot_as_png() , rect )
		#'''dino.'''
		obstacle = decode('screen.png')
		#a = '''dino.'''
		a = getAction(obstacle)
		if a == 'jump':
			body.send_keys(Keys.ARROW_UP)
		if a == 'duck':
			#action.key_down(Keys.ARROW_DOWN,body).perform()
			pyautogui.keyDown('down')
			sleep(1)
			pyautogui.keyUp('down')
			#action.key_up(Keys.ARROW_DOWN,body).perform()
	web.quit()
except selenium.common.exceptions.NoSuchElementException:
	web.quit()
	print('Quitting now...')
except:	raise
