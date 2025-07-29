import turtle
import math

# Ввод количества вершин
try:
    n = int(input("Введите число вершин n (целое число ≥ 3): "))
    if n < 3:
        raise ValueError
except ValueError:
    print("Ошибка: введите целое число не менее 3.")
    turtle.bye()
    exit(1)

# Ввод длины стороны
try:
    L = int(input("Введите длину стороны (целое число): "))
except ValueError:
    print("Ошибка: введите целое число.")
    turtle.bye()
    exit(1)

# Указываем настройки окна программы
screen = turtle.Screen()
screen.setup(width=800, height=600, startx=100, starty=50)

# Ограничение длины стороны
side = min(L, 100)

# Настройка черепашки
t = turtle.Turtle()
t.penup()
t.goto(0, 0)
t.pendown()

# Нарисовать правильный n-угольник
angle = 360 / n
for _ in range(n):
    t.forward(side)
    t.left(angle)

turtle.done()
