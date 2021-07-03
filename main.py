from posixpath import dirname
from typing import Callable
import pygame
from time import time
from vector import Vec2d, Color
from random import randint, choice
import string as stringlib
import os


SCORES_PATH = 'Scores'
if not os.path.exists(SCORES_PATH):
	os.mkdir(SCORES_PATH)


#region pygame init
pygame.font.init()
pygame.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
screen.fill([255, 255, 255])
pygame.display.set_icon(screen)
clock, fps = pygame.time.Clock(), 0

delta_time = 0 ; frame_start_time = 0
#endregion

from ui import Button, InputField, Text


def position_buttons(buttons:list[Button], arrangement:list[int], buffer:int):
	spacing = Vec2d(size)
	spacing.div(arrangement)

	button_size = spacing.copy()
	temp = Vec2d(arrangement)
	temp.mult(buffer)
	button_size.sub(temp)

	x = y = 0
	for i in range(len(buttons)):
		buttons[i].pos.set((x * spacing.x) + buffer, (y * spacing.y) + buffer)
		buttons[i].size = button_size.copy()

		x += 1
		if x == 3:
			x = 0
			y += 1

def calculate_center_label(label):
	width, height = label.get_size()

	pos = Vec2d()
	pos.x = (size[0] / 2) - (width / 2.0)
	pos.y = (size[1] / 2) - (height / 2.0)

	return pos

def format_question(question):
	if len(question) == 3 and type(question) == tuple:
		if question[1] == '+' : return f'{question[0]} + {question[2]} ='
		if question[1] == '-' : return f'{question[0]} - {question[2]} ='
		if question[1] == 'x' : return f'{question[0]} x {question[2]} ='

	if len(question) == 2 and type(question) == str : return '$' + question + ' ='
	if len(question) == 2 and type(question) == tuple : return f'{question[0]}{question[1]}' + ' ='
	return question + ' ='

def answer_question(question):
	if len(question) == 3 and type(question) == tuple:
		if question[1] == '+' : return question[0] + question[2]
		if question[1] == '-' : return question[0] - question[2]
		if question[1] == 'x' : return question[0] * question[2]

	if len(question) == 2 and type(question) == str : return int(question, 16)
	if len(question) == 2 and type(question) == tuple : return question[0]**2
	return int(question, 2)

class Questions:
	generator = None

	def addition2()       : return (int(''.join([choice(stringlib.digits) for _ in range(2)])), '+', int(''.join([choice(stringlib.digits) for _ in range(2)])))
	def addition3()       : return (int(''.join([choice(stringlib.digits) for _ in range(3)])), '+', int(''.join([choice(stringlib.digits) for _ in range(3)])))
	def multiplication()  : return (randint(0, 16), 'x', randint(0, 16))
	def subtraction2()    : return (int(choice(stringlib.digits) + choice(stringlib.digits)), '-', int(choice(stringlib.digits) + choice(stringlib.digits)))
	def subtraction3()    : return (int(''.join([choice(stringlib.digits) for _ in range(3)])), '-', int(''.join([choice(stringlib.digits) for _ in range(3)])))
	def binary()          : return '{:04}'.format(int(bin(randint(0, 15)).replace('0b', '')))
	def hexadecimal1()    : value = hex(randint(0, 15)).replace('0x', '').upper() ; return '0' + value if len(value) == 1 else value
	def hexadecimal2()    : value = hex(randint(0, 255)).replace('0x', '').upper() ; return '0' + value if len(value) == 1 else value
	def squaring1()       : return (int(choice(stringlib.digits)), u'\u00B2')
	def squaring2()       : return (int(''.join([choice(stringlib.digits) for _ in range(2)])), u'\u00B2')
	def squaring3()       : return (int(''.join([choice(stringlib.digits) for _ in range(3)])), u'\u00B2')

	def mixture()         : return choice([Questions.addition2, Questions.addition3, Questions.multiplication, Questions.subtraction2, Questions.subtraction3, Questions.binary, Questions.hexadecimal1, Questions.hexadecimal2, Questions.squaring1, Questions.squaring2, Questions.squaring3])()

	def set_generator(generator:Callable) : Questions.generator = generator

buttons = [
	Button('Addition 2 Digit'    , 0, 0, lambda : Questions.set_generator(Questions.addition2)),
	Button('Addition 3 Digit'    , 0, 0, lambda : Questions.set_generator(Questions.addition3)),
	Button('Subtraction 2 digit' , 0, 0, lambda : Questions.set_generator(Questions.subtraction2)),
	Button('Subtraction 3 digit' , 0, 0, lambda : Questions.set_generator(Questions.subtraction3)),
	Button('Multiplication'      , 0, 0, lambda : Questions.set_generator(Questions.multiplication)),
	Button('Hex 1 byte'          , 0, 0, lambda : Questions.set_generator(Questions.hexadecimal1)),
	Button('Hex 2 byte'          , 0, 0, lambda : Questions.set_generator(Questions.hexadecimal2)),
	Button('Binary'              , 0, 0, lambda : Questions.set_generator(Questions.binary)),
	Button('Squaring 1 digit'    , 0, 0, lambda : Questions.set_generator(Questions.squaring1)),
	Button('Squaring 2 digit'    , 0, 0, lambda : Questions.set_generator(Questions.squaring2)),
	Button('Squaring 3 digit'    , 0, 0, lambda : Questions.set_generator(Questions.squaring3)),
	Button('Mixture'             , 0, 0, lambda : Questions.set_generator(Questions.mixture)),
]

position_buttons(buttons, (3, 4), 10)
screen_mode = 0

generated_questions = []
question_index = 0
input_field = InputField((50, 400), (500, 100))

mouse_lock = False
key_lock = False
start_time = 0
end_time = 0

PREROUND_COUNTDOWN_LENGTH = 5
ROUND_DURATION_LENGTH = 30

correct = 0
correct_questions = set()
wrong = 0
wrong_questions = set()
consecutive_wrongs = 0
previous_wrongs = set()

home_screen_button = Button('Home', (200, 450), (200, 100), None)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
	frame_start_time = time()
	screen.fill(Color.from_hex('#f3eded').get())

	mouse_pos   = Vec2d(pygame.mouse.get_pos())
	mouse_press = pygame.mouse.get_pressed()
	key_press   = pygame.key.get_pressed()
	if sum(key_press) == 0 : key_lock = False
	if sum(mouse_press) == 0 : mouse_lock = False

	if screen_mode == 0: # Main Menu
		for button in buttons:
			if mouse_lock : continue
			button.update(mouse_pos, mouse_press)
			button.display(screen)

		if Questions.generator is not None:
			generated_questions = [Questions.generator() for _ in range(300)]
			screen_mode += 1

	if screen_mode == 1: # Pre-round timings
		start_time = time()
		end_time = start_time + PREROUND_COUNTDOWN_LENGTH
		screen_mode += 1

	if screen_mode == 2: # Pre-round count down
		label = Text.label(f'{abs(time() - end_time):.3f}', Color.from_hex('#555568'), Text.large_font)
		screen.blit(label, calculate_center_label(label).get_int())

		if time() > end_time : screen_mode += 1

	if screen_mode == 3: # Game timings
		start_time = time()
		end_time = start_time + ROUND_DURATION_LENGTH
		screen_mode += 1

	if screen_mode == 4: # Game
		question = generated_questions[question_index]
		answer = answer_question(question)

		time_left = abs(time() - end_time)
		string = '{:.0f}' if time_left > 10 else '{:.3f}'
		label = Text.label(string.format(time_left), Color.from_hex('#555568'), Text.large_font)
		p = calculate_center_label(label)
		p.y = 20
		screen.blit(label, p.get_int())

		label = Text.label(correct, Color(0, 200, 0), Text.small_font)
		screen.blit(label, Vec2d(10, 10).get_int())
		label = Text.label(wrong, Color(200, 0, 0), Text.small_font)
		screen.blit(label, Vec2d(30, 10).get_int())

		label = Text.label(format_question(question), Color.from_hex('#555568'), Text.large_font)
		screen.blit(label, calculate_center_label(label).get_int())

		if input_field.update(key_press, delta_time) and input_field.text.strip() != '' and input_field.text.strip() not in previous_wrongs and not key_lock:
			if consecutive_wrongs == 3:
				question_index += 1
				consecutive_wrongs = 0
				previous_wrongs = set()
				wrong_questions.add(question)

			if str(answer).lower() == input_field.text.lower().strip():
				question_index += 1
				consecutive_wrongs = 0
				correct += 1
				previous_wrongs = set()
				correct_questions.add(question)

			else:
				previous_wrongs.add(input_field.text.strip())
				wrong += 1
				consecutive_wrongs += 1
				wrong_questions.add(question)

			input_field.text = ''
			key_lock = True

		input_field.display(screen)

		if time() > end_time : screen_mode += 1

	if screen_mode == 5: # Result saving
		dir_name = os.path.join(SCORES_PATH, str(Questions.generator.__name__))
		if not os.path.exists(dir_name) : os.mkdir(dir_name)

		text = f'correct:{correct} | wrong:{wrong} | questions_answered:{question_index}\n'
		for q in generated_questions:
			if q in wrong_questions or q in correct_questions:
				if   q in correct_questions : result = 'correct'
				elif q in wrong_questions   : result = 'wrong'
				else : continue

				text += format_question(q) + ' | ' + result + '\n'

		with open(os.path.join(dir_name, str(int(time()))), 'w') as file:
			file.write(text)

		highscore_file = os.path.join(dir_name, 'highscore')
		if os.path.exists(highscore_file):
			with open(highscore_file, 'r') as file:
				highscore = file.read().split(',')
		else:
			with open(highscore_file, 'w') as file:
				file.write(f'{correct},{wrong},{question_index}')
			highscore = f'{correct},{wrong},{question_index}'.split(',')

		if int(highscore[0]) < correct or int(highscore[1]) > wrong or int(highscore[2]) < question_index:
			new_highscore = True
			with open(highscore_file, 'w') as file:
				file.write(f'{correct},{wrong},{question_index}')
		else:
			new_highscore = False

		screen_mode += 1

	if screen_mode == 6: # Result display
		label = Text.label(correct, Color(0, 200, 0), Text.medium_font)
		screen.blit(label, Vec2d(200 + (label.get_size()[0]/2), 150).get_int())

		label = Text.label(question_index, Color.from_hex('#555568'), Text.large_font)
		screen.blit(label, Vec2d(300 - (label.get_size()[0]/2), 100).get_int())

		label = Text.label(wrong, Color(200, 0, 0), Text.medium_font)
		screen.blit(label, Vec2d(400 - (label.get_size()[0]/2), 150).get_int())

		if new_highscore:
			label = Text.label('New HIGHSCORE!!!', Color(0, 200, 0), Text.medium_font)
			p = calculate_center_label(label)
			p.y = 220
			screen.blit(label, p.get_int())

		label = Text.label('Press ENTER to return to home screen', Color.from_hex('#555568'), Text.medium_font)
		p = calculate_center_label(label)
		p.y = 450
		screen.blit(label, p.get_int())

		if key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
			screen_mode = 0
			correct = 0
			correct_questions = set()
			wrong = 0
			wrong_questions = set()
			consecutive_wrongs = 0
			previous_wrongs = set()
			generated_questions = []
			question_index = 0
			Questions.generator = None

	pygame.display.update()
	clock.tick(fps)
	delta_time = time() - frame_start_time
	pygame.display.set_caption(f'Framerate: {int(clock.get_fps())}')