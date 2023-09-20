from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QPainterPath
from math import floor
import sys


class CustomGraphicsView(QGraphicsView):
    def __init__(self, grid_size):
        super().__init__()
        self.grid_size = grid_size
        self.closest_dot = None
        self.closest_dot_item = None

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.NoButton:
            # Получаем позицию указателя мыши в координатах сцены
            pos = self.mapToScene(event.pos())

            # Округляем координаты до ближайших кратных размеру сетки
            x = floor(pos.x() / self.grid_size) * self.grid_size
            y = floor(pos.y() / self.grid_size) * self.grid_size

            if self.closest_dot:
                # Удаляем предыдущую ближайшую точку, если она была
                self.scene().removeItem(self.closest_dot_item)

            # Создаем новую точку и прямоугольник для отображения
            self.closest_dot = QPointF(x, y)
            self.closest_dot_item = QGraphicsRectItem(x - 2, y - 2, 4, 4)

            # Настраиваем стиль прямоугольника
            pen = self.closest_dot_item.pen()
            pen.setStyle(Qt.NoPen)
            self.closest_dot_item.setPen(pen)
            self.closest_dot_item.setBrush(Qt.red)

            # Добавляем прямоугольник на сцену
            self.scene().addItem(self.closest_dot_item)

        super().mouseMoveEvent(event)


class player:
    def __init__(self, start_point, color, playerT):
        self.start_point = start_point  # Начальная точка игрока
        self.velocity = 1  # Скорость игрока
        self.dots = [self.start_point]  # Список точек, которые игрок прошел
        self.color = color  # Цвет игрока
        self.playerT = playerT  # Номер игрока (например, 1 или 2)


class GridApp(QMainWindow):
    def __init__(self):
        super().__init__()
        QMessageBox.information(self, "Правила", """В этой игре каждому игроку присвоена своя скорость. В начале игры скорость каждого игрока равна 1. Однако есть ограничения: минимальная скорость составляет 1, а максимальная - 4.

В игре игроки могут перемещаться на клетки в зависимости от своей скорости. Они могут перемещаться на количество клеток, равное их текущей скорости. Или же они могут переместиться на одну клетку больше, чтобы увеличить свою скорость. Альтернативно, они могут переместиться на одну клетку меньше, чтобы уменьшить свою скорость.

Цель игры состоит в том, чтобы быть первым игроком, достигающим зеленой линии.""")

        self.setWindowTitle("Сетка с точками")
        self.setGeometry(100, 100, 700, 500)

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(grid_size=20)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Линии трассы
        self.trace_lines = [[0, 0, 50, 0], [50, 0, 50, 70], [50, 70, 640, 70], [640, 70, 640, 190], [640, 190, 50, 190],
                            [50, 190, 50, 230], [50, 230, 300, 230], [300, 230, 300, 300], [260, 300, 260, 270],
                            [260, 270, 0, 270], [0, 270, 0, 150],
                            [0, 150, 590, 150], [590, 150, 590, 110], [590, 110, 0, 110], [0, 110, 0, 0]]

        self.finish_line = [260, 300, 300, 300]
        self.grid_size = 20

        self.draw_grid()  # Отрисовываем сетку
        self.player1 = player(QPointF(20, 20), Qt.black, 'Первый игрок')
        self.player2 = player(QPointF(20, 40), Qt.blue, "Второй игрок")
        self.current_player = self.player1

        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.add_dot

        self.add_initial_dot()  # Добавляем начальные точки
        self.draw_lines()  # Отрисовываем линии между точками
        self.setWindowTitle(self.current_player.playerT)

    def draw_grid(self):
        for x in range(0, self.view.width(), self.grid_size):
            for y in range(0, self.view.height(), self.grid_size):
                rect = QGraphicsRectItem(x, y, self.grid_size, self.grid_size)
                pen = rect.pen()
                pen.setColor(Qt.gray)
                rect.setPen(pen)
                self.scene.addItem(rect)

    def add_dot(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.view.mapToScene(event.pos())
            x = floor(pos.x() / self.grid_size) * self.grid_size
            y = floor(pos.y() / self.grid_size) * self.grid_size

            if self.is_valid_move(QPointF(x, y)) and not self.intersects_trace(QPointF(x, y)):
                dot = QGraphicsEllipseItem(x - 2, y - 2, 4, 4)
                pen = dot.pen()
                pen.setStyle(Qt.NoPen)
                dot.setPen(pen)
                dot.setBrush(Qt.black)

                self.scene.addItem(dot)
                self.current_player.dots.append(QPointF(x, y))
                self.draw_lines()  # Отрисовываем линии
                if self.finish(point=QPointF(x, y)):
                    QMessageBox.information(self, "Победа",
                                            f"Поздравляю {self.current_player.playerT}")  # Выводим сообщение о победе
                    self.close()  # Закрываем приложение
                self.current_player.start_point = QPointF(x, y)
                if self.current_player == self.player1:
                    self.current_player = self.player2
                else:
                    self.current_player = self.player1
                self.setWindowTitle(self.current_player.playerT)

    def intersects_trace(self, point):
        for line in self.trace_lines:
            line_item = QGraphicsLineItem(line[0], line[1], line[2], line[3])
            pen = line_item.pen()
            pen.setColor(QColor(255, 0, 0, 100))  # Устанавливаем красный цвет для линий трассы
            pen.setWidth(5)  # Увеличиваем ширину пера для лучшей видимости
            line_item.setPen(pen)

            shape = line_item.shape()
            path = QPainterPath()
            path.moveTo(point)
            path.lineTo(self.current_player.start_point.x(), self.current_player.start_point.y())

            if shape.intersects(path):
                self.scene.addItem(line_item)
                return True

        return False

    def finish(self, point):
        line_item = QGraphicsLineItem(self.finish_line[0], self.finish_line[1], self.finish_line[2],
                                      self.finish_line[3])
        pen = line_item.pen()
        pen.setColor(QColor(255, 0, 0, 100))  # Устанавливаем  красный цвет для линий трассы
        pen.setWidth(5)  # Увеличиваем ширину пера для лучшей видимости
        line_item.setPen(pen)

        shape = line_item.shape()
        path = QPainterPath()
        path.moveTo(point)
        path.lineTo(self.current_player.start_point.x(), self.current_player.start_point.y())

        if shape.intersects(path):
            self.scene.addItem(line_item)
            return True

        return False

    def is_valid_move(self, point):
        distance_x = abs(point.x() - self.current_player.start_point.x())
        distance_y = abs(point.y() - self.current_player.start_point.y())
        if self.current_player.velocity == 1:
            if distance_x <= self.grid_size and distance_y <= self.grid_size:
                return True
            if distance_x <= self.grid_size * 2 and distance_y <= self.grid_size * 2:
                self.increase_velocity()
                return True
        elif self.current_player.velocity == 2:
            if distance_x <= self.grid_size and distance_y <= self.grid_size:
                self.decrease_velocity()
                return True
            if distance_x <= self.grid_size * 2 and distance_y <= self.grid_size * 2:
                return True
            if distance_x <= self.grid_size * 3 and distance_y <= self.grid_size * 3:
                self.increase_velocity()
                return True
        elif self.current_player.velocity == 3:
            if distance_x <= self.grid_size and distance_y <= self.grid_size:
                return False
            if distance_x == self.grid_size * 2 or distance_y == self.grid_size * 2:
                self.decrease_velocity()
                return True
            if distance_x <= self.grid_size * 3 and distance_y <= self.grid_size * 3:
                return True
            if distance_x <= self.grid_size * 4 and distance_y <= self.grid_size * 4:
                self.increase_velocity()
                return True
        elif self.current_player.velocity == 4:
            if distance_x <= self.grid_size and distance_y <= self.grid_size:
                return False
            if distance_x == self.grid_size * 2 or distance_y == self.grid_size * 2:
                return False
            if distance_x <= self.grid_size * 3 and distance_y <= self.grid_size * 3:
                self.decrease_velocity()
                return True
            if distance_x <= self.grid_size * 4 and distance_y <= self.grid_size * 4:
                return True

        return False

    def decrease_velocity(self):
        if self.current_player.velocity > 1:
            self.current_player.velocity -= 1

    def increase_velocity(self):
        if self.current_player.velocity < 4:
            self.current_player.velocity += 1

    def add_initial_dot(self):
        dot = QGraphicsEllipseItem(self.player1.start_point.x() - 2, self.player1.start_point.y() - 2, 4, 4)
        pen = dot.pen()
        pen.setStyle(Qt.NoPen)
        dot.setPen(pen)
        dot.setBrush(self.player1.color)
        self.scene.addItem(dot)
        dot = QGraphicsEllipseItem(self.player2.start_point.x() - 2, self.player2.start_point.y() - 2, 4, 4)
        pen = dot.pen()
        pen.setStyle(Qt.NoPen)
        dot.setPen(pen)
        dot.setBrush(self.player2.color)
        self.scene.addItem(dot)

    def draw_lines(self):
        # Очищаем поле от предыдущих линий
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                self.scene.removeItem(item)

        # Отрисовываем линии между точками
        for i in range(len(self.player1.dots) - 1):
            dot1 = self.player1.dots[i]
            dot2 = self.player1.dots[i + 1]
            line = QGraphicsLineItem(dot1.x(), dot1.y(), dot2.x(), dot2.y())
            pen = line.pen()
            pen.setColor(self.player1.color)
            line.setPen(pen)
            self.scene.addItem(line)

            # Отрисовываем линии между точками
        for i in range(len(self.player2.dots) - 1):
            dot1 = self.player2.dots[i]
            dot2 = self.player2.dots[i + 1]
            line = QGraphicsLineItem(dot1.x(), dot1.y(), dot2.x(), dot2.y())
            pen = line.pen()
            pen.setColor(self.player2.color)
            line.setPen(pen)
            self.scene.addItem(line)
        self.draw_trace()

    def draw_trace(self):
        for i in self.trace_lines:
            line = QGraphicsLineItem(i[0], i[1], i[2], i[3])
            pen = line.pen()
            pen.setColor(Qt.red)
            line.setPen(pen)
            self.scene.addItem(line)
        line = QGraphicsLineItem(self.finish_line[0], self.finish_line[1], self.finish_line[2], self.finish_line[3])
        pen = line.pen()
        pen.setColor(Qt.green)
        line.setPen(pen)
        self.scene.addItem(line)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GridApp()
    window.show()
    sys.exit(app.exec_())
