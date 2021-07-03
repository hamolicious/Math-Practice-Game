from typing import Callable
from vector import Vec2d, Color
import pygame


class Text:
	small_font = pygame.font.SysFont('Tahoma', 16)
	medium_font = pygame.font.SysFont('Tahoma', 32)
	large_font = pygame.font.SysFont('Tahoma', 64)

	@staticmethod
	def label(text, color, font=small_font):
		return font.render(str(text), True, color.get())


class Button:
	def __init__(self, text, pos, size, callback:Callable) -> None:
		self.pos = Vec2d(pos)
		self.size = Vec2d(size)

		self.color_button = Color.from_hex('#555568')
		self.color_hover  = Color.from_hex('#8e9191')
		self.color_press  = Color.from_hex('#eeb9c7')
		self.color_text   = Color.from_hex('#b9eedc')

		self.text = text
		self.label = Text.label(self.text, self.color_text)

		self.hovered = False
		self.pressed = False

		self.callback = callback

	def __calculate_text_pos(self):
		width, height = self.label.get_size()

		pos = Vec2d()
		pos.x = (self.size.w / 2) - (width / 2.0)
		pos.y = (self.size.h / 2) - (height / 2.0)

		pos.add(self.pos)

		return pos

	def __is_hovered(self, mpos):
		return mpos.x > self.pos.x and mpos.y > self.pos.y and mpos.x < self.pos.x + self.size.w and mpos.y < self.pos.y + self.size.h

	def update(self, mpos, mpress):
		self.hovered = self.__is_hovered(mpos)
		self.pressed = self.__is_hovered(mpos) and mpress[0]
		if self.pressed and self.callback is not None : self.callback()

	def display(self, screen):
		c = self.color_button.get()
		if self.hovered : c = self.color_hover.get()
		if self.pressed : c = self.color_press.get()

		pygame.draw.rect(screen, c, (self.pos.get_int(), self.size.get_int()))
		screen.blit(self.label, self.__calculate_text_pos().get_int())


class InputField:
	def __init__(self, pos, size) -> None:
		self.pos = Vec2d(pos)
		self.size = Vec2d(size)

		self.color_button = Color.from_hex('#8e9191')
		self.color_text   = Color.from_hex('#555568')

		self.cursor_blink = True
		self.blink_counter = 0
		self.blink_interval = 0.4

		self.key_lock = False

		self.text = ' '

	def __calculate_text_pos(self, label):
		width, height = label.get_size()

		pos = Vec2d()
		pos.y = (self.size.h / 2) - (height / 2.0)

		pos.add(self.pos)

		return pos

	def __write_char(self, char):
		if len(self.text) == 13 : return
		self.text += char
		self.key_lock = True

	def __remove_char(self):
		self.text = self.text[:-1]
		self.key_lock = True

	def update(self, kpress, delta_time):
		if not self.key_lock:
			if (kpress[pygame.K_KP_1] or kpress[pygame.K_1])          : self.__write_char('1')
			if (kpress[pygame.K_KP_2] or kpress[pygame.K_2])          : self.__write_char('2')
			if (kpress[pygame.K_KP_3] or kpress[pygame.K_3])          : self.__write_char('3')
			if (kpress[pygame.K_KP_4] or kpress[pygame.K_4])          : self.__write_char('4')
			if (kpress[pygame.K_KP_5] or kpress[pygame.K_5])          : self.__write_char('5')
			if (kpress[pygame.K_KP_6] or kpress[pygame.K_6])          : self.__write_char('6')
			if (kpress[pygame.K_KP_7] or kpress[pygame.K_7])          : self.__write_char('7')
			if (kpress[pygame.K_KP_8] or kpress[pygame.K_8])          : self.__write_char('8')
			if (kpress[pygame.K_KP_9] or kpress[pygame.K_9])          : self.__write_char('9')
			if (kpress[pygame.K_KP_0] or kpress[pygame.K_0])          : self.__write_char('0')
			if kpress[pygame.K_a]                                     : self.__write_char('A')
			if kpress[pygame.K_b]                                     : self.__write_char('B')
			if kpress[pygame.K_c]                                     : self.__write_char('C')
			if kpress[pygame.K_d]                                     : self.__write_char('D')
			if kpress[pygame.K_e]                                     : self.__write_char('E')
			if kpress[pygame.K_f]                                     : self.__write_char('F')
			if kpress[pygame.K_MINUS] or kpress[pygame.K_KP_MINUS]    : self.__write_char('-')
			if (kpress[pygame.K_KP_ENTER] or kpress[pygame.K_RETURN]) : return True
			if kpress[pygame.K_BACKSPACE]                             : self.__remove_char()

		if sum(kpress) == 0 : self.key_lock = False

		if len(self.text) == 0 : self.text = ' '
		if self.text != ' ' : self.text = self.text.strip()

		self.blink_counter += 1 * delta_time
		if self.blink_counter > self.blink_interval:
			self.blink_counter = 0
			self.cursor_blink = not self.cursor_blink

		return False

	def display(self, screen):
		pygame.draw.rect(screen, self.color_button.get(), (self.pos.get_int(), self.size.get_int()))

		label = Text.label(self.text + ('|' if self.cursor_blink else ' '), self.color_text, Text.large_font)
		screen.blit(label, self.pos.get_int())


