

cdef class sfSoundResourceStatus:
	
	Stopped = 0
	Paused = 1
	Playing = 2


cdef class sfTextStyle:
	
	Regular = 0
	Bold = 1 << 0
	Italic = 1 << 1
	Underlined = 1 << 2
	StrikeThrough = 1 << 3


cdef class sfShaderType:
	
	Vertex = 0
	Geometry = 1
	Fragment = 2


cdef class sfWindowStyle:
	
	None_      = 0
	Titlebar   = 1 << 0
	Resize     = 1 << 1
	Close      = 1 << 2
	Fullscreen = 1 << 3

	Default = Titlebar | Resize | Close


cdef class sfEventType:
	Closed = 0
	Resized = 1
	LostFocus = 2
	GainedFocus = 3
	TextEntered = 4
	KeyPressed = 5
	KeyReleased = 6
	MouseWheelMoved = 7
	MouseWheelScrolled = 8
	MouseButtonPressed = 9
	MouseButtonReleased = 10
	MouseMoved = 11
	MouseEntered = 12
	MouseLeft = 13


cdef class sfMouseButton:
	Left = 0
	Right = 1
	Middle = 2
	XButton1 = 3
	XButton2 = 4
	ButtonCount = 5


cdef class sfScancode:
	Unknown = -1
	A = 0
	B = 1
	C = 2
	D = 3
	E = 4
	F = 5
	G = 6
	H = 7
	I = 8
	J = 9
	K = 10
	L = 11
	M = 12
	N = 13
	O = 14
	P = 15
	Q = 16
	R = 17
	S = 18
	T = 19
	U = 20
	V = 21
	W = 22
	X = 23
	Y = 24
	Z = 25
	Num0 = 26
	Num1 = 27
	Num2 = 28
	Num3 = 29
	Num4 = 30
	Num5 = 31
	Num6 = 32
	Num7 = 33
	Num8 = 34
	Num9 = 35
	Escape = 36
	LControl = 37
	LShift = 38
	LAlt = 39
	LSystem = 40
	RControl = 41
	RShift = 42
	RAlt = 43
	RSystem = 44
	Menu = 45
	LBracket = 46
	RBracket = 47
	SemiColon = 48
	Comma = 49
	Period = 50
	Quote = 51
	Slash = 52
	BackSlash = 53
	Tilde = 54
	Equal = 55
	Dash = 56
	Space = 57
	Return = 58
	BackSpace = 59
	Tab = 60
	PageUp = 61
	PageDown = 62
	End = 63
	Home = 64
	Insert = 65
	Delete = 66
	Add = 67
	Subtract = 68
	Multiply = 69
	Divide = 70
	Left = 71
	Right = 72
	Up = 73
	Down = 74
	Numpad0 = 75
	Numpad1 = 76
	Numpad2 = 77
	Numpad3 = 78
	Numpad4 = 79
	Numpad5 = 80
	Numpad6 = 81
	Numpad7 = 82
	Numpad8 = 83
	Numpad9 = 84
	F1 = 85
	F2 = 86
	F3 = 87
	F4 = 88
	F5 = 89
	F6 = 90
	F7 = 91
	F8 = 92
	F9 = 93
	F10 = 94
	F11 = 95
	F12 = 96
	F13 = 97
	F14 = 98
	F15 = 99
	Pause = 100


cdef class sfKey:
	Unknown = -1
	A = 0
	B = 1
	C = 2
	D = 3
	E = 4
	F = 5
	G = 6
	H = 7
	I = 8
	J = 9
	K = 10
	L = 11
	M = 12
	N = 13
	O = 14
	P = 15
	Q = 16
	R = 17
	S = 18
	T = 19
	U = 20
	V = 21
	W = 22
	X = 23
	Y = 24
	Z = 25
	Num0 = 26
	Num1 = 27
	Num2 = 28
	Num3 = 29
	Num4 = 30
	Num5 = 31
	Num6 = 32
	Num7 = 33
	Num8 = 34
	Num9 = 35
	Escape = 36
	LControl = 37
	LShift = 38
	LAlt = 39
	LSystem = 40
	RControl = 41
	RShift = 42
	RAlt = 43
	RSystem = 44
	Menu = 45
	LBracket = 46
	RBracket = 47
	SemiColon = 48
	Comma = 49
	Period = 50
	Quote = 51
	Slash = 52
	BackSlash = 53
	Tilde = 54
	Equal = 55
	Dash = 56
	Space = 57
	Return = 58
	BackSpace = 59
	Tab = 60
	PageUp = 61
	PageDown = 62
	End = 63
	Home = 64
	Insert = 65
	Delete = 66
	Add = 67
	Subtract = 68
	Multiply = 69
	Divide = 70
	Left = 71
	Right = 72
	Up = 73
	Down = 74
	Numpad0 = 75
	Numpad1 = 76
	Numpad2 = 77
	Numpad3 = 78
	Numpad4 = 79
	Numpad5 = 80
	Numpad6 = 81
	Numpad7 = 82
	Numpad8 = 83
	Numpad9 = 84
	F1 = 85
	F2 = 86
	F3 = 87
	F4 = 88
	F5 = 89
	F6 = 90
	F7 = 91
	F8 = 92
	F9 = 93
	F10 = 94
	F11 = 95
	F12 = 96
	F13 = 97
	F14 = 98
	F15 = 99
	Pause = 100
	Count = 101