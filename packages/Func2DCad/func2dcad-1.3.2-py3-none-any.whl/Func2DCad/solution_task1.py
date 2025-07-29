import turtle

try:
    L = int(input("Введите длину линии (целое число): "))
except ValueError:
    print("Ошибка: введите целое число.")
    turtle.bye()
    exit(1)

# Указываем настройки окна программы
screen = turtle.Screen()
screen.setup(width=800, height=600, startx=100, starty=50)

# Ограничение длины
length = min(L, 400)

# Настройка черепашки
t = turtle.Turtle()
t.penup()
t.goto(-length/2, 0)  # сдвигаем стартовую точку, чтобы линия была по центру экрана
t.pendown()

t.forward(length)

# Завершаем программу по клику или закрытию окна
turtle.done()
