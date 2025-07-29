import turtle

try:
    L = int(input("Введите длину стороны квадрата (целое число): "))
except ValueError:
    print("Ошибка: введите целое число.")
    turtle.bye()
    exit(1)

# Указываем настройки окна программы
screen = turtle.Screen()
screen.setup(width=800, height=600, startx=100, starty=50)

# Ограничение длины стороны
side = min(L, 400)

# Настройка черепашки
t = turtle.Turtle()
t.penup()
t.goto(-side/2, side/2)  # размещаем квадрат по центру экрана
t.pendown()

# Рисуем квадрат (4 стороны)
for _ in range(4):
    t.forward(side)
    t.right(90)

turtle.done()
