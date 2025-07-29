from libcpp.string cimport string

from libc.math cimport M_PI, fabs, sin, cos, acos, sqrtf, powf, atan2

from cpython.version cimport PY_MAJOR_VERSION

from audio.sound_buffer.sound_buffer cimport SoundBuffer
cimport audio.sound.sound as sf_Sound
from audio.music.music cimport Music

from graphics.render_window.render_window cimport RenderWindow
from graphics.color.color cimport Color
from graphics.image.image cimport Image
from graphics.texture.texture cimport Texture
from graphics.sprite.sprite cimport Sprite
from graphics.shader.shader cimport Shader
from graphics.shader.type cimport Type
from graphics.render_states.render_states cimport RenderStates, Default
from graphics.font.font cimport Font
from graphics.text.text cimport Text
from graphics.rectangle_shape.rectangle_shape cimport RectangleShape
from graphics.circle_shape.circle_shape cimport CircleShape
from graphics.view.view cimport View

from window.event.event cimport Event
from window.keyboard.keyboard cimport Key, Scancode, isKeyPressed, localize
from window.video_mode.video_mode cimport VideoMode
from window.style cimport Style
cimport window.mouse.mouse as sf_Mouse
from window.mouse.button cimport Button

from system.string.string cimport String
from system.clock.clock cimport Clock
cimport system.time.time as sf_Time


def to_radians(float degrees) -> float:
	cdef float pi = <float>M_PI
	return pi * degrees / 180


def to_degrees(float radians) -> float:
	cdef float pi = <float>M_PI
	return radians  * 180 / pi


cdef unicode _text(s):
	if type(s) is unicode:
		return <unicode>s
	elif PY_MAJOR_VERSION < 3 and isinstance(s, bytes):
		return (<bytes>s).decode('ascii')
	elif isinstance(s, unicode):
		return unicode(s)
	else:
		raise TypeError("Could not convert to unicode.")


cdef class MathPoint2f:
	
	cdef float x
	cdef float y

	def __cinit__(self,
		float x = 0,
		float y = 0
		):
		self.x = x
		self.y = y

	def distance(self, MathPoint2f p) -> float:
		return sqrtf(
			powf(self.x - p.x, 2) + powf(self.y - p.y, 2)
			)

	@property
	def pos_x(self) -> float:
		return self.x

	@pos_x.setter
	def pos_x(self, float x) -> None:
		self.x = x

	@property
	def pos_y(self) -> float:
		return self.y

	@pos_y.setter
	def pos_y(self, float y) -> None:
		self.y = y


cdef class MathVector2f:
	
	cdef float x
	cdef float y

	def __cinit__(self,
		float x = 0,
		float y = 0):
		self.x = x
		self.y = y

	def sum(self, MathVector2f v) -> MathVector2f:
		return MathVector2f(
			self.x + v.x, self.y + v.y
			)

	def sub(self, MathVector2f v) -> MathVector2f:
		return MathVector2f(
			self.x - v.x, self.y - v.y
			)

	def scalar_product(self, MathVector2f v) -> float:
		return self.x * v.x + self.y * v.y

	def cosin(self, MathVector2f v) -> float:
		cdef float sc = self.scalar_product(v)
		cdef float m1 = self.modul, m2 = v.modul
		return sc / (m1 * m2)

	def vector_product(self, MathVector2f v) -> MathVector2f:
		return MathVector2f(
			self.x * v.y, -self.y * v.x
			)

	def sinus(self, MathVector2f v) -> float:
		cdef MathVector2f vp = self.vector_product(v)
		cdef float m1 = self.modul, m2 = v.modul
		return vp.modul / (m1 * m2)

	def distance(self, MathVector2f v) -> float:
		return sqrtf(
			powf(self.x - v.x, 2) + powf(self.y - v.y, 2)
			)

	def multiply_num(self, float num) -> None:
		self.x *= num
		self.y *= num

	def basis(self) -> MathVector2f:
		cdef float mod = self.modul
		return MathVector2f(
			self.x / mod, self.y / mod
			)

	def is_parallel(self, MathVector2f v) -> bool:
		return self.x / v.x == self.y / v.y

	def is_perpendicular(self, MathVector2f v) -> bool:
		return self.scalar_product(v) == 0

	def angle_between(self,
		MathVector2f v,
		bint degrees = True) -> float:
		cdef float pi = <float>M_PI
		cdef float radians = acos(self.cosin(v))
		if degrees:
			return radians * 180 / pi
		else:
			return radians

	@property
	def modul(self) -> float:
		return sqrtf(
			powf(self.x, 2) + powf(self.y, 2)
			)

	@staticmethod
	def from_points(MathPoint2f p1, MathPoint2f p2) -> MathVector2f:
		return MathVector2f(
			p2.x - p1.x, p2.y - p1.y
			)

	@property
	def pos_x(self) -> float:
		return self.x

	@pos_x.setter
	def pos_x(self, float x) -> None:
		self.x = x

	@property
	def pos_y(self) -> float:
		return self.y

	@pos_y.setter
	def pos_y(self, float y) -> None:
		self.y = y


cdef class MathPoint3f:
	
	cdef float x
	cdef float y
	cdef float z

	def __cinit__(self,
		float x = 0,
		float y = 0,
		float z = 0
		):
		self.x = x
		self.y = y
		self.z = z

	def distance(self, MathPoint3f p) -> float:
		return sqrtf(
			powf(self.x - p.x, 2) + powf(self.y - p.y, 2) + powf(self.z - p.z, 2)
			)

	@property
	def pos_x(self) -> float:
		return self.x

	@pos_x.setter
	def pos_x(self, float x) -> None:
		self.x = x

	@property
	def pos_y(self) -> float:
		return self.y

	@pos_y.setter
	def pos_y(self, float y) -> None:
		self.y = y

	@property
	def pos_z(self) -> float:
		return self.z

	@pos_z.setter
	def pos_z(self, float z) -> None:
		self.z = z


cdef class MathVector3f:
	
	cdef float x
	cdef float y
	cdef float z

	def __cinit__(self,
		float x = 0,
		float y = 0,
		float z = 0):
		self.x = x
		self.y = y
		self.z = z

	def sum(self, MathVector3f v) -> MathVector3f:
		return MathVector3f(
			self.x + v.x, self.y + v.y, self.z + v.z
			)

	def sub(self, MathVector3f v) -> MathVector3f:
		return MathVector3f(
			self.x - v.x, self.y - v.y, self.z - v.z
			)

	def scalar_product(self, MathVector3f v) -> float:
		return self.x * v.x + self.y * v.y + self.z * v.z

	def cosin(self, MathVector3f v) -> float:
		cdef float sc = self.scalar_product(v)
		cdef float m1 = self.modul, m2 = v.modul
		return sc / (m1 * m2)

	def vector_product(self, MathVector3f v) -> MathVector3f:
		cdef float x = self.y * v.z - self.z * v.y
		cdef float y = -(self.x * v.z - self.z * v.x)
		cdef float z = self.x * v.y - self.y * v.x
		return MathVector3f(x, y, z)

	def sinus(self, MathVector3f v) -> float:
		cdef MathVector3f vp = self.vector_product(v)
		cdef float m1 = self.modul, m2 = v.modul
		return vp.modul / (m1 * m2)

	def distance(self, MathVector3f v) -> float:
		return sqrtf(
			powf(self.x - v.x, 2) + powf(self.y - v.y, 2) + powf(self.z - v.z, 2)
			)

	def multiply_num(self, float num) -> None:
		self.x *= num
		self.y *= num
		self.z *= num

	def basis(self) -> MathVector3f:
		cdef float mod = self.modul
		return MathVector3f(
			self.x / mod, self.y / mod, self.z / mod
			)

	def is_parallel(self, MathVector3f v) -> bool:
		cdef float k = self.x / v.x
		return k == self.y / v.y and k == self.z / v.z

	def is_perpendicular(self, MathVector3f v) -> bool:
		return self.scalar_product(v) == 0

	def angle_between(self,
		MathVector3f v,
		bint degrees = True) -> float:
		cdef float pi = <float>M_PI
		cdef float radians = acos(self.cosin(v))
		if degrees:
			return radians * 180 / pi
		else:
			return radians

	@property
	def modul(self) -> float:
		return sqrtf(
			powf(self.x, 2) + powf(self.y, 2) + powf(self.z, 2)
			)

	@staticmethod
	def from_points(MathPoint3f p1, MathPoint3f p2) -> MathVector3f:
		return MathVector3f(
			p2.x - p1.x, p2.y - p1.y, p2.z - p1.z
			)

	@property
	def pos_x(self) -> float:
		return self.x

	@pos_x.setter
	def pos_x(self, float x) -> None:
		self.x = x

	@property
	def pos_y(self) -> float:
		return self.y

	@pos_y.setter
	def pos_y(self, float y) -> None:
		self.y = y

	@property
	def pos_z(self) -> float:
		return self.z

	@pos_z.setter
	def pos_z(self, float z) -> None:
		self.z = z


cdef extern from "SFML/Audio/SoundSource.hpp" namespace "sf":

	cdef cppclass Vector3f:

		float x
		float y
		float z


cdef class sfSoundBuffer:
	
	cdef SoundBuffer* buffer

	def __cinit__(self, str filename):
		cdef string path = _text(filename).encode('utf-8')
		self.buffer = new SoundBuffer()
		if not self.buffer.loadFromFile(path):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load sound from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Failed to load sound from {filename}!')

	def __dealloc__(self):
		if self.buffer is not NULL:
			del self.buffer


cdef class sfSound:
	
	cdef sf_Sound.Sound* sound

	def __cinit__(self, sfSoundBuffer buffer):
		self.sound = new sf_Sound.Sound(buffer.buffer[0])

	def __dealloc__(self):
		del self.sound

	def play(self) -> None:
		self.sound.play()

	def pause(self) -> None:
		self.sound.pause()

	def stop(self) -> None:
		self.sound.stop()

	def get_status(self) -> int:
		return self.sound.getStatus()

	def set_buffer(self, sfSoundBuffer buffer) -> None:
		self.sound.setBuffer(buffer.buffer[0])

	def reset_buffer(self) -> None:
		self.sound.resetBuffer()

	def set_relative_to(self,
		float x = 0,
		float y = 0,
		float z = 0) -> float:
		cdef Vector3f pos = self.sound.getPosition()
		cdef float minDistance = self.sound.getMinDistance()
		cdef float attenuation = self.sound.getAttenuation()
		cdef float distance = sqrtf(
			powf(pos.x - x, 2) + powf(pos.y - y, 2) + powf(pos.z - z, 2)
			)
		cdef float maxD
		if distance > minDistance:
			maxD = distance
		else:
			maxD = minDistance
		cdef float volumeFactor = minDistance / (minDistance + attenuation * (maxD - minDistance))
		self.sound.setVolume(volumeFactor)
		return volumeFactor

	def get_position(self) -> tuple[float, float, float]:
		cdef Vector3f pos = self.sound.getPosition()
		return (pos.x, pos.y, pos.z)

	def set_position(self,
		float x = 0,
		float y = 0,
		float z = 0) -> None:
		self.sound.setPosition(x, y, z)

	def get_min_distance(self) -> float:
		return self.sound.getMinDistance()

	def set_min_distance(self, float distance) -> None:
		self.sound.setMinDistance(distance)

	def get_attenuation(self) -> float:
		return self.sound.getAttenuation()

	def set_attenuation(self, float attenuation) -> None:
		self.sound.setAttenuation(attenuation) 

	def get_loop(self) -> bool:
		return self.sound.getLoop()

	def set_loop(self, bint loop) -> None:
		self.sound.setLoop(loop)

	def get_volume(self) -> float:
		return self.sound.getVolume()

	def set_volume(self, float volume) -> None:
		self.sound.setVolume(volume)

	def get_pitch(self) -> float:
		return self.sound.getPitch()

	def set_pitch(self, float pitch) -> None:
		self.sound.setPitch(pitch)


cdef class sfMusic:
	
	cdef Music* music

	def __cinit__(self, str filename):
		cdef string path = _text(filename).encode('utf-8')
		self.music = new Music()
		if not self.music.openFromFile(path):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load music from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Failed to load music from {filename}!')

	def __dealloc__(self):
		if self.music is not NULL:
			del self.music

	def play(self) -> None:
		self.music.play()

	def pause(self) -> None:
		self.music.pause()

	def stop(self) -> None:
		self.music.stop()

	def get_status(self) -> int:
		return self.music.getStatus()

	def set_relative_to(self,
		float x = 0,
		float y = 0,
		float z = 0) -> float:
		cdef Vector3f pos = self.music.getPosition()
		cdef float minDistance = self.music.getMinDistance()
		cdef float attenuation = self.music.getAttenuation()
		cdef float distance = sqrtf(
			powf(pos.x - x, 2) + powf(pos.y - y, 2) + powf(pos.z - z, 2)
			)
		cdef float maxD
		if distance > minDistance:
			maxD = distance
		else:
			maxD = minDistance
		cdef float volumeFactor = minDistance / (minDistance + attenuation * (maxD - minDistance))
		self.music.setVolume(volumeFactor)
		return volumeFactor

	def get_position(self) -> tuple[float, float, float]:
		cdef Vector3f pos = self.music.getPosition()
		return (pos.x, pos.y, pos.z)

	def set_position(self,
		float x = 0,
		float y = 0,
		float z = 0) -> None:
		self.music.setPosition(x, y, z)

	def get_min_distance(self) -> float:
		return self.music.getMinDistance()

	def set_min_distance(self, float distance) -> None:
		self.music.setMinDistance(distance)

	def get_attenuation(self) -> float:
		return self.music.getAttenuation()

	def set_attenuation(self, float attenuation) -> None:
		self.music.setAttenuation(attenuation) 

	def get_loop(self) -> bool:
		return self.music.getLoop()

	def set_loop(self, bint loop) -> None:
		self.music.setLoop(loop)

	def get_volume(self) -> float:
		return self.music.getVolume()

	def set_volume(self, float volume) -> None:
		self.music.setVolume(volume)

	def get_pitch(self) -> float:
		return self.music.getPitch()

	def set_pitch(self, float pitch) -> None:
		self.music.setPitch(pitch)


cdef class sfTime:
	
	cdef sf_Time.Time* time

	def __cinit__(self):
		self.time = new sf_Time.Time()

	def __dealloc__(self):
		del self.time

	def asSeconds(self) -> float:
		return self.time.asSeconds()

	def asMilliseconds(self) -> int:
		return self.time.asMilliseconds()

	def asMicroseconds(self) -> int:
		return self.time.asMicroseconds()


cdef class sfClock:
	
	cdef Clock* clock

	def __cinit__(self):
		self.clock = new Clock()

	def __dealloc__(self):
		del self.clock

	def get_elapsed_seconds(self) -> float:
		return self.clock.getElapsedTime().asSeconds()

	def get_elapsed_milliseconds(self) -> int:
		return self.clock.getElapsedTime().asMilliseconds()

	def get_elapsed_microseconds(self) -> int:
		return self.clock.getElapsedTime().asMicroseconds()

	def restart_asseconds(self) -> float:
		return self.clock.restart().asSeconds()

	def restart_asmilliseconds(self) -> int:
		return self.clock.restart().asMilliseconds()

	def restart_asmicroseconds(self) -> int:
		return self.clock.restart().asMicroseconds()


cdef class TimeCollector:
	
	cdef Clock* clock
	cdef float __buffer

	def __cinit__(self):
		self.clock = new Clock()
		self.__buffer = <float>0.0

	def __dealloc__(self):
		del self.clock

	def collect(self) -> None:
		cdef float elapsed = self.clock.restart().asMilliseconds()
		self.__buffer += elapsed

	def reset(self) -> None:
		self.__buffer = <float>0.0
		self.clock.restart()

	@property
	def seconds(self) -> float:
		return self.__buffer / 1000

	@property
	def milliseconds(self) -> float:
		return self.__buffer

	@property
	def microseconds(self) -> float:
		return self.__buffer * 1000


cdef class TimedFloat:
	
	cdef Clock* clock
	cdef float __value

	def __cinit__(self, float value):
		self.clock = new Clock()
		self.__value = value

	def __dealloc__(self):
		del self.clock

	def get_timed(self) -> float:
		cdef float seconds = self.clock.restart().asSeconds()
		return self.__value * seconds

	def get_value(self) -> float:
		return self.__value

	def set_value(self, float value) -> None:
		self.__value = value


cdef class Animator:
	
	cdef int length
	cdef float speed
	cdef float __buffer
	cdef bint __animeEnded
	cdef bint __animeStarted

	def __cinit__(
		self,
		int length,
		float speed_
		):
		self.length = length
		self.speed = speed_
		self.__animeEnded = False
		self.__animeStarted = False
		self.__buffer = <float>0.0

	def get_current_index(self) -> int:
		cdef int index = <int>self.__buffer
		cdef int maxIndex = self.length - 1
		if index > maxIndex:
			index = 0
			self.__buffer = 0
		if index == 0:
			self.__animeStarted = True
			self.__animeEnded = False
		elif index == maxIndex:
			self.__animeStarted = False
			self.__animeEnded = True
		else:
			self.__animeStarted = False
			self.__animeEnded = False
		self.__buffer += self.speed
		return index

	@property
	def lenz(self) -> int:
		return self.length

	@lenz.setter
	def lenz(self, int length) -> None:
		self.length = length

	@property
	def spid(self) -> float:
		return self.speed

	@spid.setter
	def spid(self, float speed) -> None:
		self.speed = speed

	@property
	def is_ended(self) -> bool:
		return self.__animeEnded

	@property
	def is_started(self) -> bool:
		return self.__animeStarted


cdef class sfImage:
	
	cdef Image* image

	def __cinit__(self, str filename):
		self.image = new Image()
		cdef string path = _text(filename).encode('utf-8')
		if not self.image.loadFromFile(path):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load image from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Failed to load image {filename}!')

	def __dealloc__(self):
		if self.image is not NULL:
			del self.image


cdef class sfVideoMode:
	
	cdef VideoMode* __mode

	def __cinit__(self,
		unsigned int modeWidth,
		unsigned int modeHeight,
		unsigned int bitsPerPixel = 32):
		self.__mode = new VideoMode(modeWidth, modeHeight, bitsPerPixel)

	def __dealloc__(self):
		del self.__mode

	@staticmethod
	def get_desktop_mode() -> tuple[int, int, int]:
		cdef VideoMode current = VideoMode.getDesktopMode()
		return (current.width, current.height, current.bitsPerPixel)

	def is_valid(self) -> bool:
		return self.__mode.isValid()

	@property
	def width(self) -> int:
		return self.__mode.width

	@width.setter
	def width(self, unsigned int width_) -> None:
		self.__mode.width = width_

	@property
	def height(self) -> int:
		return self.__mode.height

	@height.setter
	def height(self, unsigned int height_) -> None:
		self.__mode.height = height_

	@property
	def bits_per_pixel(self) -> int:
		return self.__mode.bitsPerPixel

	@bits_per_pixel.setter
	def bits_per_pixel(self, unsigned int bits_per_pixel_) -> None:
		self.__mode.bitsPerPixel = bits_per_pixel_


cdef class sfColor:
	
	cdef Color* color

	def __cinit__(self,
		unsigned int r = 0,
		unsigned int g = 0,
		unsigned int b = 0,
		unsigned int a = 255):
		self.color = new Color(r, g, b, a)

	def __dealloc__(self):
		del self.color

	@property
	def r(self) -> int:
		return self.color.r

	@r.setter
	def r(self, unsigned int r_) -> None:
		self.color.r = r_

	@property
	def g(self) -> int:
		return self.color.g

	@g.setter
	def g(self, unsigned int g_) -> None:
		self.color.g = g_

	@property
	def b(self) -> int:
		return self.color.b

	@b.setter
	def b(self, unsigned int b_) -> None:
		self.color.b = b_

	@property
	def a(self) -> int:
		return self.color.a

	@a.setter
	def a(self, unsigned int a_) -> None:
		self.color.a = a_


cdef class sfEvent:

	cdef Event* event
	
	def __cinit__(self):
		self.event = new Event()

	def __dealloc__(self):
		del self.event

	def get_type(self) -> int:
		return self.event.type

	def get_key_code(self) -> int:
		return self.event.key.code

	def get_text_unicode(self) -> int:
		return self.event.text.unicode

	def get_mouse_button(self) -> int:
		return self.event.mouseButton.button


cdef class sfKeyboard:
	
	@staticmethod
	def is_key_pressed(int key) -> bool:
		return isKeyPressed(<Key>key)

	@staticmethod
	def localize(int scancode) -> int:
		return localize(<Scancode>scancode)


cdef extern from "SFML/Graphics/RenderWindow.hpp" namespace "sf":
	
	cdef cppclass Vector2u:

		unsigned int x
		unsigned int y


cdef extern from "SFML/Window/Mouse.hpp" namespace "sf":
	
	cdef cppclass Vector2i:

		int x
		int y


cdef extern from "SFML/Graphics/Sprite.hpp" namespace "sf":

	cdef cppclass Vector2f:

		float x
		float y


	cdef cppclass FloatRect:

		FloatRect()

		FloatRect(float rectLeft, float rectTop, float rectWidth, float rectHeight)

		bint contains(float x, float y) const

		bint contains(Vector2f& point) const

		bint intersects(FloatRect& rectangle) const

		Vector2f getPosition() const

		Vector2f getSize() const

		float left
		float top
		float width
		float height


cdef class sfFloatRect:
	
	cdef FloatRect* rect

	def __cinit__(self,
		float rectLeft = 0,
		float rectTop = 0,
		float rectWidth = 0,
		float rectHeight = 0):

		self.rect = new FloatRect(rectLeft, rectTop, rectWidth, rectHeight)

	def __dealloc__(self):
		del self.rect

	def contains(self,
		float x = 0,
		float y = 0) -> bool:
		return self.rect.contains(x, y)

	def intersects(self, sfFloatRect rect) -> bool:
		return self.rect.intersects(rect.rect[0])

	def get_position(self) -> tuple[float, float]:
		cdef Vector2f pos = self.rect.getPosition()
		return (pos.x, pos.y)

	def get_center(self) -> tuple[float, float]:
		cdef Vector2f pos = self.rect.getPosition()
		cdef Vector2f size = self.rect.getSize()
		cdef float x, y, k = <float>.5
		x = pos.x + size.x * k
		y = pos.y + size.y * k
		return (x, y)

	def set_center(self,
		float x,
		float y) -> None:
		cdef Vector2f size = self.rect.getSize()
		cdef float k = <float>.5
		self.rect.top = y - size.y * k
		self.rect.left = x - size.x * k

	def get_size(self) -> tuple[float, float]:
		cdef Vector2f size = self.rect.getSize()
		return (size.x, size.y)

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		cdef Vector2f pos = self.rect.getPosition()
		self.rect.top = pos.y + dy
		self.rect.left = pos.x + dx

	@property
	def left(self) -> float:
		return self.rect.left

	@left.setter
	def left(self, left_) -> None:
		self.rect.left = left_

	@property
	def top(self) -> float:
		return self.rect.top

	@top.setter
	def top(self, top_) -> None:
		self.rect.top = top_

	@property
	def width(self) -> float:
		return self.rect.width

	@width.setter
	def width(self, width_) -> None:
		self.rect.width = width_

	@property
	def height(self) -> float:
		return self.rect.height

	@height.setter
	def height(self, height_) -> None:
		self.rect.height = height_


cdef class sfFont:
	
	cdef Font* font

	def __cinit__(self, str filename):
		cdef string path = _text(filename).encode('utf-8')
		self.font = new Font()
		if not self.font.loadFromFile(path):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load font from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Failed to load font {filename}!')

	def __dealloc__(self):
		if self.font is not NULL:
			del self.font

	def set_smooth(self, bint smooth) -> None:
		self.font.setSmooth(smooth)

	def is_smooth(self) -> bool:
		return self.font.isSmooth()


cdef class sfString:

	CACHE_SIZE = 128
	RESULTS = {}
	
	cdef String* txt

	def __cinit__(self, str txt_):
		self.txt = new String(_text(txt_).encode('utf-8'))

	def __dealloc__(self):
		del self.txt

	def clear(self) -> None:
		self.txt.clear()

	def is_empty(self) -> bool:
		return self.txt.isEmpty()

	def as_pystring(self) -> str:
		return self.txt.toAnsiString().c_str().decode('utf-8')

	@staticmethod
	def from_pystring(str pystring) -> sfString:
		if pystring in sfString.RESULTS:
			return sfString.RESULTS[pystring]
		else:
			if len(sfString.RESULTS) < sfString.CACHE_SIZE:
				sfString.RESULTS[pystring] = sfString(pystring)
			else:
				items = list(sfString.RESULTS.items())
				to_remove = int(sfString.CACHE_SIZE * .2)
				sfString.RESULTS = dict(items[:-to_remove])
				sfString.RESULTS[pystring] = sfString(pystring)
			return sfString.RESULTS[pystring]

	@staticmethod
	def drop_cache() -> None:
		sfString.RESULTS.clear()

	@staticmethod
	def set_cache_size(int size) -> None:
		sfString.CACHE_SIZE = size

	def __eq__(self, sfString another) -> bool:
		return self.txt == another.txt


cdef class sfText:
	
	cdef Text* text

	def __cinit__(self, sfFont font):
		self.text = new Text()
		self.text.setFont(font.font[0])

	def __dealloc__(self):
		del self.text

	def get_pystring(self) -> str:
		cdef String text = <const String>self.text.getString()
		return text.toAnsiString().c_str().decode('utf-8')

	def get_scale(self) -> tuple[float, float]:
		cdef Vector2f scale = <const Vector2f>self.text.getScale()
		return (scale.x, scale.y)

	def set_scale(self,
		float kx = 1,
		float ky = 1) -> None:
		self.text.setScale(kx, ky)

	def get_rotation(self) -> float:
		return self.text.getRotation()

	def set_rotation(self, float degrees) -> None:
		self.text.setRotation(degrees)

	def get_position(self) -> tuple[float, float]:
		cdef Vector2f pos = <const Vector2f>self.text.getPosition()
		return (pos.x, pos.y)

	def set_position(self,
		float left = 0,
		float top = 0) -> None:
		self.text.setPosition(left, top)

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		self.text.move(dx, dy)

	def rotate(self, float degrees) -> None:
		self.text.rotate(degrees)

	def contains(self,
		float x = 0,
		float y = 0,
		bint local = True) -> bool:
		cdef FloatRect rect
		if local:
			rect = self.text.getLocalBounds()
		else:
			rect = self.text.getGlobalBounds()
		return rect.contains(x, y)

	def intersects(self,
		sfFloatRect rect,
		bint local = True) -> bool:
		cdef FloatRect bounds
		if local:
			bounds = self.text.getLocalBounds()
		else:
			bounds = self.text.getGlobalBounds()
		return bounds.intersects(rect.rect[0])

	def set_string(self, sfString txt) -> None:
		self.text.setString(txt.txt[0])

	def set_font(self, sfFont font) -> None:
		self.text.setFont(font.font[0])

	def set_character_size(self, unsigned int size) -> None:
		self.text.setCharacterSize(size)

	def set_style(self, unsigned int style) -> None:
		self.text.setStyle(style)

	def set_fill_color(self, sfColor color) -> None:
		self.text.setFillColor(color.color[0])

	def get_local_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.text.getLocalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)

	def get_global_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.text.getGlobalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)


cdef class sfTexture:
	
	cdef Texture* texture

	def __cinit__(self, str filename):

		self.texture = new Texture()
		cdef string path = _text(filename).encode('utf-8')
		if not self.texture.loadFromFile(path):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load texture from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Unable to load texture {filename}!')

	def __dealloc__(self):
		if self.texture is not NULL:
			del self.texture

	def get_size(self) -> tuple[int, int]:
		cdef Vector2u size = self.texture.getSize()
		return (size.x, size.y)

	def set_smooth(self, bint smooth) -> None:
		self.texture.setSmooth(smooth)

	def is_smooth(self) -> bool:
		return self.texture.isSmooth()

	def set_srgb(self, bint srgb) -> None:
		self.texture.setSrgb(srgb)

	def is_srgb(self) -> bool:
		return self.texture.isSrgb()


cdef void resizeSprite(
	Sprite* sprite,
	float width,
	float height):
	cdef Vector2u texture_size = sprite.getTexture().getSize()
	cdef float kx = width / texture_size.x, ky = height / texture_size.y
	sprite.setScale(kx, ky)


cdef void resizeSpriteKeepWidth(
	Sprite* sprite,
	float width
	):
	cdef Vector2u texture_size = sprite.getTexture().getSize()
	cdef float kwh = <float>1.0 * texture_size.x / texture_size.y
	cdef float height = width / kwh
	cdef float kx = width / texture_size.x, ky = height / texture_size.y
	sprite.setScale(kx, ky)


cdef void resizeSpriteKeepHeight(
	Sprite* sprite,
	float height
	):
	cdef Vector2u texture_size = sprite.getTexture().getSize()
	cdef float khw = <float>1.0 * texture_size.y / texture_size.x
	cdef float width = height / khw
	cdef float kx = width / texture_size.x, ky = height / texture_size.y
	sprite.setScale(kx, ky)


cdef void scaleSpriteKeepLeftTop(
	Sprite* sprite,
	float kx,
	float ky
	):
	cdef Vector2f pos = <const Vector2f>sprite.getPosition()
	sprite.setScale(kx, ky)
	sprite.setPosition(pos.x, pos.y)


cdef void scaleSpriteKeepCenter(
	Sprite* sprite,
	float kx,
	float ky,
	bint local_pos
	):
	cdef float k = <float>.5
	cdef FloatRect rect
	if local_pos:
		rect = sprite.getLocalBounds()
	else:
		rect = sprite.getGlobalBounds()
	cdef float center_x = rect.left + rect.width * k
	cdef float center_y = rect.top + rect.height * k
	sprite.setScale(kx, ky)
	cdef FloatRect n_rect
	if local_pos:
		n_rect = sprite.getLocalBounds()
	else:
		n_rect = sprite.getGlobalBounds()
	cdef float left = center_x - n_rect.width * k
	cdef float top = center_y - n_rect.height * k
	sprite.setPosition(left, top)


cdef class sfSprite:
	
	cdef Sprite* sprite

	def __cinit__(self,
		sfTexture texture,
		float width = 0,
		float height = 0,
		float left = 0,
		float top = 0,
		bint keep_w = False,
		bint keep_h = False,
		bint resetRect = False):
		self.sprite = new Sprite()
		self.sprite.setTexture(texture.texture[0], resetRect)
		if keep_w:
			resizeSpriteKeepWidth(self.sprite, width)
		elif keep_h:
			resizeSpriteKeepHeight(self.sprite, height)
		else:
			resizeSprite(self.sprite, width, height)
		self.sprite.setPosition(left, top)

	def __dealloc__(self):
		if self.sprite is not NULL:
			del self.sprite

	def intersects(self,
		sfSprite sprite,
		bint local_bounds = True) -> bool:
		cdef FloatRect myRect, theyRect
		if local_bounds:
			myRect = self.sprite.getLocalBounds()
			theyRect = self.sprite.getLocalBounds()
		else:
			myRect = self.sprite.getGlobalBounds()
			theyRect = self.sprite.getGlobalBounds()
		return myRect.intersects(theyRect)

	def intersects_rect(self,
		sfFloatRect rect,
		bint local_bounds = True) -> bool:
		cdef FloatRect myRect
		if local_bounds:
			myRect = self.sprite.getLocalBounds()
		else:
			myRect = self.sprite.getGlobalBounds()
		return myRect.intersects(rect.rect[0])

	def contains(self,
		float x = 0,
		float y = 0,
		bint local_bounds = True) -> bool:
		cdef FloatRect rect
		if local_bounds:
			rect = self.sprite.getLocalBounds()
		else:
			rect = self.sprite.getGlobalBounds()
		return rect.contains(x, y)

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		self.sprite.move(dx, dy)

	def rotate(self, float degrees = 0) -> None:
		self.sprite.rotate(degrees)

	def collide_shift_h(self,
		sfSprite sprite,
		bint local = True) -> bool:
		cdef FloatRect myRect, theyRect
		if local:
			myRect = self.sprite.getLocalBounds()
			theyRect = sprite.sprite.getLocalBounds()
		else:
			myRect = self.sprite.getGlobalBounds()
			theyRect = sprite.sprite.getGlobalBounds()
		if not myRect.intersects(theyRect):
			return False
		cdef float k = <float>.5, dx = 0, dy = 0
		cdef float x1 = myRect.left, x2 = myRect.left + myRect.width
		cdef float t_x1 = theyRect.left, t_x2 = theyRect.left + theyRect.width
		cdef float center_t_x = theyRect.left + theyRect.width * k
		cdef float dif_x = center_t_x - x1
		if dif_x > 0:
			dx = t_x1 - x2
		elif dif_x < 0:
			dx = t_x2 - x1
		else:
			dx = -theyRect.width * k
		self.sprite.move(dx, dy)
		return True

	def collide_shift_v(self,
		sfSprite sprite,
		bint local = True) -> bool:
		cdef FloatRect myRect, theyRect
		if local:
			myRect = self.sprite.getLocalBounds()
			theyRect = sprite.sprite.getLocalBounds()
		else:
			myRect = self.sprite.getGlobalBounds()
			theyRect = sprite.sprite.getGlobalBounds()
		if not myRect.intersects(theyRect):
			return False
		cdef float dx = 0, dy = 0, k = <float>.5
		cdef float y1 = myRect.top, y2 = myRect.top + myRect.height
		cdef float t_y1 = theyRect.top, t_y2 = theyRect.top + theyRect.height
		cdef float center_t_y = theyRect.top + theyRect.height * k
		cdef float dif_y = center_t_y - y1
		if dif_y > 0:
			dy = t_y1 - y2
		elif dif_y < 0:
			dy = t_y2 - y1
		else:
			dy = -theyRect.height * k
		self.sprite.move(dx, dy)
		return True

	def get_local_bounds(self) -> sfFloatRect:
		cdef FloatRect rect = self.sprite.getLocalBounds()
		return sfFloatRect(rect.left, rect.top, rect.width, rect.height)

	def get_global_bounds(self) -> sfFloatRect:
		cdef FloatRect rect = self.sprite.getGlobalBounds()
		return sfFloatRect(rect.left, rect.top, rect.width, rect.height)

	def get_rotation(self) -> float:
		return self.sprite.getRotation()

	def set_rotation(self, float degrees = 0) -> None:
		self.sprite.setRotation(degrees)

	def get_scale(self) -> tuple[float, float]:
		cdef Vector2f scale = <const Vector2f>self.sprite.getScale()
		return (scale.x, scale.y)

	def set_scale(self,
		float kx = 1,
		float ky = 1) -> None:
		self.sprite.setScale(kx, ky)

	def get_color(self) -> sfColor:
		cdef Color clr = <const Color>self.sprite.getColor()
		return sfColor(clr.r, clr.g, clr.b, clr.a)

	def set_color(self, sfColor color) -> None:
		cdef Color clr
		clr.r = color.r
		clr.g = color.g
		clr.b = color.b
		clr.a = color.a
		self.sprite.setColor(clr)

	def get_position(self) -> tuple[float, float]:
		cdef Vector2f pos = <const Vector2f>self.sprite.getPosition()
		return (pos.x, pos.y)

	def set_position(self,
		float left = 0,
		float top = 0) -> None:
		self.sprite.setPosition(left, top)

	def get_center(self, bint local=True) -> tuple[float, float]:
		cdef FloatRect rect
		cdef float k = <float>.5
		if local:
			rect = self.sprite.getLocalBounds()
		else:
			rect = self.sprite.getGlobalBounds()
		cdef float center_x = rect.left + rect.width * k
		cdef float center_y = rect.top + rect.height * k
		return (center_x, center_y)

	def set_center(self,
		float center_x = 0,
		float center_y = 0,
		bint local=True) -> None:
		cdef FloatRect rect
		cdef float k = <float>.5
		if local:
			rect = self.sprite.getLocalBounds()
		else:
			rect = self.sprite.getGlobalBounds()
		cdef float left = center_x - rect.width * k
		cdef float top = center_y - rect.height * k
		self.sprite.setPosition(left, top)

	def set_alpha(self, int a) -> None:
		cdef Color color = <const Color>self.sprite.getColor()
		color.a = a
		self.sprite.setColor(color)

	def get_alpha(self) -> int:
		cdef Color color = <const Color>self.sprite.getColor()
		return color.a

	def in_area(self,
		float x1 = 0,
		float x2 = 0,
		float y1 = 0,
		float y2 = 0,
		bint local = True) -> bool:
		cdef FloatRect rect
		if local:
			rect = self.sprite.getLocalBounds()
		else:
			rect = self.sprite.getGlobalBounds()
		cdef float width = fabs(x2 - x1), height = fabs(y2 - y1)
		cdef FloatRect area
		area.left = x1
		area.top = y1
		area.width = width
		area.height = height
		return rect.intersects(area)

	def clone(self, sfTexture texture) -> sfSprite:
		cdef Vector2f pos = <const Vector2f>self.sprite.getPosition()
		cdef Vector2f scale = <const Vector2f>self.sprite.getScale()
		cdef Vector2u textureSize = self.sprite.getTexture().getSize()
		cdef float width = textureSize.x * scale.x, height = textureSize.y * scale.y
		return sfSprite(texture, width, height, pos.x, pos.y)


cdef class TransformSfSprite:

	@staticmethod
	def keep_their_distance(
		sfSprite sprite1,
		sfSprite sprite2,
		float distance_x = 0,
		float distance_y = 0,
		bint keep_x = False,
		bint keep_y = False,
		bint sprite1_main = False,
		bint local = True
		) -> bool:
		if not keep_x and not keep_y:
			return False
		cdef FloatRect rect1, rect2
		if local:
			rect1 = sprite1.sprite.getLocalBounds()
			rect2 = sprite2.sprite.getLocalBounds()
		else:
			rect1 = sprite1.sprite.getGlobalBounds()
			rect2 = sprite2.sprite.getGlobalBounds()
		cdef float k = <float>.5
		cdef float centerX1, centerY1
		cdef float centerX2, centerY2
		cdef float difX, difY
		cdef float dx = 0, dy = 0
		cdef bint sprite1Left = rect1.left - rect2.left < 0
		cdef bint sprite1Upper = rect1.top - rect2.top < 0
		if keep_x:
			centerX1 = rect1.left + rect1.width * k
			centerX2 = rect2.left + rect2.width * k
			difX = fabs(centerX1 - centerX2)
			dx = distance_x - difX
			if dx == 0 and not keep_y:
				return False
		if keep_y:
			centerY1 = rect1.top + rect1.height * k
			centerY2 = rect2.top + rect2.height * k
			difY = fabs(centerY1 - centerY2)
			dy = distance_y - difY
			if dx == 0 and dy == 0:
				return False
		if sprite1_main:
			if not sprite1Left:
				dx *= -1
			if not sprite1Upper:
				dy *= -1
			sprite2.sprite.move(dx, dy)
		else:
			if sprite1Left:
				dx *= -1
			if sprite1Upper:
				dy *= -1
			sprite1.sprite.move(dx, dy)
		return True
	
	@staticmethod
	def similar(
		sfSprite sprite1,
		sfSprite sprite2,
		bint sprite1_main = False,
		bint similar_pos = False,
		bint similar_size = False,
		bint local = True
		) -> None:
		cdef FloatRect rect1, rect2
		if local:
			rect1 = sprite1.sprite.getLocalBounds()
			rect2 = sprite2.sprite.getLocalBounds()
		else:
			rect1 = sprite1.sprite.getGlobalBounds()
			rect2 = sprite2.sprite.getGlobalBounds()
		if similar_pos:
			if sprite1_main:
				sprite2.sprite.setPosition(rect1.left, rect1.top)
			else:
				sprite1.sprite.setPosition(rect2.left, rect2.top)
		if similar_size:
			if sprite1_main:
				resizeSprite(sprite2.sprite, rect1.width, rect1.height)
			else:
				resizeSprite(sprite1.sprite, rect2.width, rect2.height)

	@staticmethod
	def put_like(
		sfSprite sprite1,
		sfSprite sprite2,
		bint like_sprite1 = False,
		bint shift_dx = False,
		bint shift_dy = False,
		bint local = True
		) -> None:
		cdef FloatRect rect1, rect2
		cdef float k = <float>.5
		if local:
			rect1 = sprite1.sprite.getLocalBounds()
			rect2 = sprite2.sprite.getLocalBounds()
		else:
			rect1 = sprite1.sprite.getGlobalBounds()
			rect2 = sprite2.sprite.getGlobalBounds()
		if like_sprite1:
			sprite2.sprite.setPosition(rect1.left, rect1.top)
		else:
			sprite1.sprite.setPosition(rect2.left, rect2.top)
		cdef float centerX1, centerX2
		cdef float dx = 0, dy = 0
		if shift_dx:
			centerX1 = rect1.left + rect1.width * k
			centerX2 = rect2.left + rect2.width * k
			if like_sprite1:
				dx = centerX1 - centerX2
			else:
				dx = centerX2 - centerX1
		if shift_dy:
			if like_sprite1:
				dy = rect1.height - rect2.height
			else:
				dy = rect2.height - rect1.height
		if like_sprite1:
			sprite2.sprite.move(dx, dy)
		else:
			sprite1.sprite.move(dx, dy)
	
	@staticmethod
	def swap(
		sfSprite sprite1,
		sfSprite sprite2,
		bint swap_pos = False,
		bint swap_size = False,
		bint local = True
		) -> None:
		cdef FloatRect rect1, rect2
		if local:
			rect1 = sprite1.sprite.getLocalBounds()
			rect2 = sprite2.sprite.getLocalBounds()
		else:
			rect1 = sprite1.sprite.getGlobalBounds()
			rect2 = sprite2.sprite.getGlobalBounds()
		if swap_pos:
			sprite1.sprite.setPosition(rect2.left, rect2.top)
			sprite2.sprite.setPosition(rect1.left, rect1.top)
		if swap_size:
			resizeSprite(sprite1.sprite, rect2.width, rect2.height)
			resizeSprite(sprite2.sprite, rect1.width, rect1.height)

	@staticmethod
	def get_distance(
		sfSprite sprite1,
		sfSprite sprite2,
		bint local = True
		) -> float:
		cdef FloatRect rect1, rect2
		cdef float k = <float>.5
		if local:
			rect1 = sprite1.sprite.getLocalBounds()
			rect2 = sprite2.sprite.getLocalBounds()
		else:
			rect1 = sprite1.sprite.getGlobalBounds()
			rect2 = sprite2.sprite.getGlobalBounds()
		cdef float centerX1 = rect1.left + rect1.width * k
		cdef float centerY1 = rect1.top + rect1.height * k
		cdef float centerX2 = rect2.left + rect2.width * k
		cdef float centerY2 = rect2.top + rect2.height * k
		return sqrtf(
			powf(centerX2 - centerX1, 2) + powf(centerY2 - centerY1, 2)
			)
	
	@staticmethod
	def scale(
		sfSprite sprite,
		float kx = 1,
		float ky = 1,
		bint local = True,
		bint keep_left_top = True
		) -> None:
		if keep_left_top:
			scaleSpriteKeepLeftTop(sprite.sprite, kx, ky)
		else:
			scaleSpriteKeepCenter(sprite.sprite, kx, ky, local)

	@staticmethod
	def resize(
		sfSprite sprite,
		float width = 0,
		float height = 0,
		bint keep_w = False,
		bint keep_h = False,
		bint shift_dx = False,
		bint shift_dy = False,
		bint local = True
		) -> None:
		cdef FloatRect before, after
		if local:
			before = sprite.sprite.getLocalBounds()
		else:
			before = sprite.sprite.getGlobalBounds()
		if keep_w:
			resizeSpriteKeepWidth(sprite.sprite, width)
		elif keep_h:
			resizeSpriteKeepHeight(sprite.sprite, height)
		else:
			resizeSprite(sprite.sprite, width, height)
		cdef float centerX1, centerX2, dx = 0, dy = 0, k = <float>.5
		if shift_dx or shift_dy:
			if local:
				after = sprite.sprite.getLocalBounds()
			else:
				after = sprite.sprite.getGlobalBounds()
			if shift_dx:
				centerX1 = before.left + before.width * k
				centerX2 = after.left + after.width * k
				dx = centerX1 - centerX2
			if shift_dy:
				dy = before.height - after.height
			sprite.sprite.move(dx, dy)

	@staticmethod
	def flip(
		sfSprite sprite,
		bint flipX = False,
		bint flipY = False,
		bint local=True
		) -> None:
		cdef Vector2f scale = <const Vector2f>sprite.sprite.getScale()
		cdef FloatRect rect
		if local:
			rect = sprite.sprite.getLocalBounds()
		else:
			rect = sprite.sprite.getGlobalBounds()
		cdef float kx = scale.x, ky = scale.y
		if flipX:
			kx *= -1
		if flipY:
			ky *= -1
		sprite.sprite.setScale(kx, ky)
		cdef float dx = 0, dy = 0
		if kx < 0:
			dx = rect.width
		if ky < 0:
			dy = rect.height
		sprite.sprite.setPosition(rect.left, rect.top)
		sprite.sprite.move(dx, dy)

	@staticmethod
	def set_rotation_around_center(
		sfSprite sprite,
		float degrees = 0,
		bint local = True
		) -> None:
		cdef float k = <float>.5
		cdef FloatRect before
		if local:
			before = sprite.sprite.getLocalBounds()
		else:
			before = sprite.sprite.getGlobalBounds()
		cdef float center_x1 = before.left + before.width * k
		cdef float center_y1 = before.top + before.height * k
		sprite.sprite.setRotation(degrees)
		cdef FloatRect after
		if local:
			after = sprite.sprite.getLocalBounds()
		else:
			after = sprite.sprite.getGlobalBounds()
		cdef float center_x2 = after.left + after.width * k
		cdef float center_y2 = after.top + after.height * k
		cdef float dx = center_x1 - center_x2
		cdef float dy = center_y1 - center_y2
		sprite.sprite.move(dx, dy)

	@staticmethod
	def rotate_around_center(
		sfSprite sprite,
		float degrees = 0,
		bint local = True
		) -> None:
		cdef float k = <float>.5
		cdef FloatRect before
		if local:
			before = sprite.sprite.getLocalBounds()
		else:
			before = sprite.sprite.getGlobalBounds()
		cdef float center_x1 = before.left + before.width * k
		cdef float center_y1 = before.top + before.height * k
		sprite.sprite.rotate(degrees)
		cdef FloatRect after
		if local:
			after = sprite.sprite.getLocalBounds()
		else:
			after = sprite.sprite.getGlobalBounds()
		cdef float center_x2 = after.left + after.width * k
		cdef float center_y2 = after.top + after.height * k
		cdef float dx = center_x1 - center_x2
		cdef float dy = center_y1 - center_y2
		sprite.sprite.move(dx, dy)

	@staticmethod
	def move_with_angle(
		sfSprite sprite,
		float degrees,
		float speed
		) -> None:
		cdef float pi = <float>M_PI
		cdef float radians = degrees * pi / 180
		cdef float dx = speed * cos(radians)
		cdef float dy = speed * sin(radians)
		sprite.sprite.move(dx, dy)


cdef class sfRectangleShape:
	
	cdef RectangleShape* shape

	def __cinit__(
		self,
		sfColor color,
		float width = 0,
		float height = 0,
		float left = 0,
		float top = 0
		):
		self.shape = new RectangleShape()
		self.shape.setPosition(left, top)
		cdef Vector2f widthHeight
		widthHeight.x = width
		widthHeight.y = height
		cdef const Vector2f* size = &widthHeight
		self.shape.setSize(size[0])
		cdef const Color* clr = &color.color[0]
		self.shape.setFillColor(clr[0])

	def __dealloc__(self):
		del self.shape

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		self.shape.move(dx, dy)

	def rotate(self, float degrees) -> None:
		self.shape.rotate(degrees)

	def contains(self,
		float x = 0,
		float y = 0,
		bint local = True) -> bool:
		cdef FloatRect rect
		if local:
			rect = self.shape.getLocalBounds()
		else:
			rect = self.shape.getGlobalBounds()
		return rect.contains(x, y)

	def intersects(self,
		sfFloatRect rect,
		bint local = True) -> bool:
		cdef FloatRect r
		if local:
			r = self.shape.getLocalBounds()
		else:
			r = self.shape.getGlobalBounds()
		return r.intersects(rect.rect[0])

	def set_alpha(self, int a) -> None:
		cdef Color clr = <const Color>self.shape.getFillColor()
		clr.a = a
		self.shape.setFillColor(clr)

	def get_alpha(self) -> int:
		cdef Color clr = <const Color>self.shape.getFillColor()
		return clr.a

	def set_position(self,
		float left = 0,
		float top = 0) -> None:
		self.shape.setPosition(left, top)

	def get_position(self) -> tuple[float, float]:
		cdef Vector2f pos = <const Vector2f>self.shape.getPosition()
		return (pos.x, pos.y)

	def set_fill_color(self, sfColor color) -> None:
		cdef const Color* clr = &color.color[0]
		self.shape.setFillColor(clr[0])

	def get_fill_color(self) -> sfColor:
		cdef Color clr = <const Color>self.shape.getFillColor()
		return sfColor(clr.r, clr.g, clr.b, clr.a)

	def set_size(self,
		float width,
		float height) -> None:
		cdef Vector2f widthHeight
		widthHeight.x = width
		widthHeight.y = height
		cdef const Vector2f* size = &widthHeight
		self.shape.setSize(size[0])

	def get_size(self) -> tuple[float, float]:
		cdef Vector2f size = <const Vector2f>self.shape.getSize()
		return (size.x, size.y)

	def set_rotation(self, float degrees) -> None:
		self.shape.setRotation(degrees)

	def get_rotation(self) -> float:
		return self.shape.getRotation()

	def get_global_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.shape.getGlobalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)

	def get_local_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.shape.getLocalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)

	def clone(self) -> sfRectangleShape:
		cdef sfColor clr = self.get_fill_color()
		cdef Vector2f size = <const Vector2f>self.shape.getSize()
		cdef Vector2f pos = <const Vector2f>self.shape.getPosition()
		return sfRectangleShape(clr, size.x, size.y, pos.x, pos.y)


cdef class sfCircleShape:
	
	cdef CircleShape* shape

	def __cinit__(
		self,
		sfColor color,
		float radius = 0,
		float left = 0,
		float top = 0
		):
		self.shape = new CircleShape()
		self.shape.setRadius(radius)
		self.shape.setPosition(left, top)
		cdef const Color* clr = &color.color[0]
		self.shape.setFillColor(clr[0])

	def __dealloc__(self):
		del self.shape

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		self.shape.move(dx, dy)

	def rotate(self, float degrees) -> None:
		self.shape.rotate(degrees)

	def contains(self,
		float x = 0,
		float y = 0,
		bint local = True) -> bool:
		cdef FloatRect rect
		if local:
			rect = self.shape.getLocalBounds()
		else:
			rect = self.shape.getGlobalBounds()
		return rect.contains(x, y)

	def intersects(self,
		sfFloatRect rect,
		bint local = True) -> bool:
		cdef FloatRect r
		if local:
			r = self.shape.getLocalBounds()
		else:
			r = self.shape.getGlobalBounds()
		return r.intersects(rect.rect[0])

	def set_alpha(self, int a) -> None:
		cdef Color clr = <const Color>self.shape.getFillColor()
		clr.a = a
		self.shape.setFillColor(clr)

	def get_alpha(self) -> int:
		cdef Color clr = <const Color>self.shape.getFillColor()
		return clr.a

	def set_rotation(self, float degrees) -> None:
		self.shape.setRotation(degrees)

	def get_rotation(self) -> float:
		return self.shape.getRotation()

	def set_fill_color(self, sfColor color) -> None:
		cdef const Color* clr = &color.color[0]
		self.shape.setFillColor(clr[0])

	def get_fill_color(self) -> sfColor:
		cdef Color color = <const Color>self.shape.getFillColor()
		return sfColor(color.r, color.g, color.b, color.a)

	def set_position(self,
		float left = 0,
		float top = 0) -> None:
		self.shape.setPosition(left, top)

	def get_position(self) -> tuple[float, float]:
		cdef Vector2f pos = <const Vector2f>self.shape.getPosition()
		return (pos.x, pos.y)

	def set_radius(self, float radius) -> None:
		self.shape.setRadius(radius)

	def get_radius(self) -> float:
		return self.shape.getRadius()

	def get_local_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.shape.getLocalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)

	def get_global_bounds(self) -> sfFloatRect:
		cdef FloatRect bounds = self.shape.getGlobalBounds()
		return sfFloatRect(bounds.left, bounds.top, bounds.width, bounds.height)

	def clone(self) -> sfCircleShape:
		cdef sfColor clr = self.get_fill_color()
		cdef Vector2f pos = <const Vector2f>self.shape.getPosition()
		cdef float radius = self.shape.getRadius()
		return sfCircleShape(clr, radius, pos.x, pos.y)


cdef class sfView:
	
	cdef View* view

	def __cinit__(self,
		float center_x = 0,
		float center_y = 0,
		float width = 0,
		float height = 0):
		self.view = new View()
		self.view.setCenter(center_x, center_y)
		self.view.setSize(width, height)

	def __dealloc__(self):
		del self.view

	def move(self,
		float dx = 0,
		float dy = 0) -> None:
		self.view.move(dx, dy)

	def rotate(self, float degrees) -> None:
		self.view.rotate(degrees)

	def zoom(self, float factor) -> None:
		self.view.zoom(factor)

	def rotate_around_center(self, float degrees) -> None:
		cdef Vector2f center = <const Vector2f>self.view.getCenter()
		self.view.rotate(degrees)
		self.view.setCenter(center.x, center.y)

	def set_rotation_around_center(self, float degrees) -> None:
		cdef Vector2f center = <const Vector2f>self.view.getCenter()
		self.view.setRotation(degrees)
		self.view.setCenter(center.x, center.y)

	def get_rect(self) -> sfFloatRect:
		cdef FloatRect rect = <const FloatRect>self.view.getViewport()
		return sfFloatRect(rect.left, rect.top, rect.width, rect.height)

	def get_left_top(self) -> tuple[float, float]:
		cdef Vector2f center = <const Vector2f>self.view.getCenter()
		cdef Vector2f size = <const Vector2f>self.view.getSize()
		cdef float k = <float>.5
		cdef float left = center.x - size.x * k, top = center.y - size.y * k
		return (left, top)

	def set_left_top(self,
		float left = 0,
		float top = 0) -> None:
		cdef Vector2f size = <const Vector2f>self.view.getSize()
		cdef float k = <float>.5
		cdef float centerX = left + size.x * k, centerY = top + size.y * k
		self.view.setCenter(centerX, centerY)

	def get_center(self) -> tuple[float, float]:
		cdef Vector2f center = <const Vector2f>self.view.getCenter()
		return (center.x, center.y)

	def set_center(self,
		float center_x = 0,
		float center_y = 0) -> None:
		self.view.setCenter(center_x, center_y)

	def get_size(self) -> tuple[float, float]:
		cdef Vector2f size = <const Vector2f>self.view.getSize()
		return (size.x, size.y)

	def set_size(self,
		float width = 0,
		float height = 0) -> None:
		self.view.setSize(width, height)

	def get_rotation(self) -> float:
		return self.view.getRotation()

	def set_rotation(self, float degrees) -> None:
		self.view.setRotation(degrees)


cdef class sfShader:
	
	cdef Shader* shader
	
	def __cinit__(
		self,
		str filename,
		int type
		):
		cdef string path = _text(filename).encode('utf-8')
		self.shader = new Shader()
		if not self.shader.loadFromFile(path, <Type>type):
			if PY_MAJOR_VERSION < 3:
				raise RuntimeError('Failed to load shader from {0}!'.format(filename))
			else:
				raise RuntimeError(f'Failed to load shader {filename}!')

	def __dealloc__(self):
		if self.shader is not NULL:
			del self.shader

	def set_uniform(self,
		str name_,
		float x) -> None:
		cdef string name = _text(name_).encode('utf-8')
		self.shader.setUniform(name, x)

	@staticmethod
	def is_available() -> bool:
		return Shader.isAvailable()


cdef class sfRenderStates:
	
	cdef RenderStates* states

	def __cinit__(self,
		sfShader shader):
		self.states = new RenderStates(shader.shader)

	def __dealloc__(self):
		del self.states


cdef class sfRenderWindow:
	
	cdef RenderWindow* render_window

	def __cinit__(self,
		unsigned int width,
		unsigned int height,
		unsigned int bitsPerPixel = 32,
		str title = '',
		unsigned int style = Style.Default):

		cdef VideoMode mode = VideoMode(width, height, bitsPerPixel)
		cdef String title_ = String(_text(title).encode('utf-8'))
		self.render_window = new RenderWindow(mode, title_, style)

	def __dealloc__(self):
		del self.render_window

	def map_coords_to_pixel(self,
		float x = 0,
		float y = 0) -> tuple[int, int]:
		cdef Vector2f pos_
		pos_.x = x
		pos_.y = y
		cdef const Vector2f* pos = &pos_
		cdef Vector2i pixel = self.render_window.mapCoordsToPixel(pos[0])
		return (pixel.x, pixel.y)

	def map_pixel_to_coords(self,
		float x = 0,
		float y = 0) -> tuple[float, float]:
		cdef Vector2i pos_
		pos_.x = <int>x
		pos_.y = <int>y
		cdef const Vector2i* pos = &pos_
		cdef Vector2f coord = self.render_window.mapPixelToCoords(pos[0])
		return (coord.x, coord.y)

	def get_desktop_rect(self) -> sfFloatRect:
		cdef Vector2i pos = self.render_window.getPosition()
		cdef Vector2u size = self.render_window.getSize()
		return sfFloatRect(pos.x, pos.y, size.x, size.y)

	def set_view(self, sfView view_) -> None:
		cdef const View* view = &view_.view[0]
		self.render_window.setView(view[0])

	def get_view(self) -> sfView:
		cdef View view = <const View>self.render_window.getView()
		cdef Vector2f center = <const Vector2f>view.getCenter()
		cdef Vector2f size = <const Vector2f>view.getSize()
		return sfView(center.x, center.y, size.x, size.y)

	def get_position(self) -> tuple[int, int]:
		cdef Vector2i pos = self.render_window.getPosition()
		return (pos.x, pos.y)

	def set_position(self,
		int x = 0,
		int y = 0) -> None:
		cdef Vector2i pos
		pos.x = x
		pos.y = y
		cdef const Vector2i* const_pos = &pos
		self.render_window.setPosition(const_pos[0])

	def move(self,
		int dx = 0,
		int dy = 0) -> None:
		cdef Vector2i pos = self.render_window.getPosition()
		pos.x += dx
		pos.y += dy
		cdef const Vector2i* const_pos = &pos
		self.render_window.setPosition(const_pos[0])

	def draw_sprite(self, sfSprite sprite) -> None:
		self.render_window.draw(sprite.sprite[0], Default)

	def draw_sprite_use_state(self,
		sfSprite sprite,
		sfRenderStates states) -> None:
		self.render_window.draw(sprite.sprite[0], states.states[0])

	def draw_text(self, sfText text) -> None:
		self.render_window.draw(text.text[0], Default)

	def draw_rect_shape(self, sfRectangleShape shape) -> None:
		self.render_window.draw(shape.shape[0], Default)

	def draw_circle_shape(self, sfCircleShape shape) -> None:
		self.render_window.draw(shape.shape[0], Default)

	def set_icon(self,
		sfImage icon,
		unsigned int width = 32,
		unsigned int height = 32) -> None:
		self.render_window.setIcon(width, height, icon.image.getPixelsPtr())

	def clear(self, sfColor color) -> None:
		self.render_window.clear(color.color[0])

	def poll_event(self, sfEvent event) -> bool:
		return self.render_window.pollEvent(event.event[0])

	def set_visible(self, bint visible = True) -> None:
		self.render_window.setVisible(visible)

	def is_open(self) -> bool:
		return self.render_window.isOpen()

	def close(self) -> None:
		self.render_window.close()

	def display(self) -> None:
		self.render_window.display()

	def set_mouse_cursor_visible(self, bint visible) -> None:
		self.render_window.setMouseCursorVisible(visible)

	def set_framerate_limit(self, unsigned int limit) -> None:
		self.render_window.setFramerateLimit(limit)

	def set_active(self, bint active = True) -> bool:
		return self.render_window.setActive(active)

	def get_size(self) -> tuple[int, int]:
		cdef Vector2u size = self.render_window.getSize()
		return (size.x, size.y)


cdef class sfMouse:

	@staticmethod
	def world_pos(sfRenderWindow wnd) -> tuple[int, int]:
		cdef Vector2i mouse_pos_ = sf_Mouse.getPosition()
		cdef const Vector2i* mouse_pos = &mouse_pos_
		cdef Vector2f pos = wnd.render_window.mapPixelToCoords(mouse_pos[0])
		return (<int>pos.x, <int>pos.y)
	
	@staticmethod
	def relative_pos(sfRenderWindow wnd) -> tuple[int, int]:
		cdef Vector2i wnd_pos = wnd.render_window.getPosition()
		cdef Vector2u wnd_size = wnd.render_window.getSize()
		cdef FloatRect wnd_rect = FloatRect(wnd_pos.x, wnd_pos.y, wnd_size.x, wnd_size.y)
		cdef Vector2i mouse_pos = sf_Mouse.getPosition()
		if not wnd_rect.contains(mouse_pos.x, mouse_pos.y):
			return (0, 0)
		cdef int x = mouse_pos.x - wnd_pos.x
		cdef int y = mouse_pos.y - wnd_pos.y
		return (x, y)

	@staticmethod
	def relative_to_rect(sfFloatRect rect) -> tuple[int, int]:
		cdef Vector2i pos = sf_Mouse.getPosition()
		if not rect.rect.contains(pos.x, pos.y):
			return (0, 0)
		cdef int x = pos.x - rect.left
		cdef int y = pos.y - rect.top
		return (x, y)
	
	@staticmethod
	def get_position() -> tuple[int, int]:
		cdef Vector2i pos = sf_Mouse.getPosition()
		return (pos.x, pos.y)

	@staticmethod
	def is_button_pressed(int button) -> bool:
		return sf_Mouse.isButtonPressed(<Button>button)