from ursina import *
import json
import numpy as np
import os
import sys
import time
from ursina.prefabs.first_person_controller import FirstPersonController

# Класс настройки и конфигурации окна
class WindowManager:
    def __init__(self):
        window.title = 'Phase Portrait Visualization'
        window.borderless = False
        window.exit_button.visible = True
        window.fps_counter.enabled = True
        window.color = color.rgb(0.02, 0.03, 0.1)  # Темно-синий фон

# Класс для загрузки данных
class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        # Проверка существования файла
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Файл данных не найден: {self.filepath}")
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Файл {self.filepath} содержит недопустимый JSON")
        
        # Проверка наличия необходимых ключей
        required_keys = ['time_points', 'states', 'controls']
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Отсутствует необходимый ключ в данных: {key}")
        
        try:
            data['time_points'] = np.array(data['time_points'])
            data['states'] = np.array(data['states'])
            data['controls'] = np.array(data['controls'])
        except ValueError:
            raise ValueError("Невозможно преобразовать данные в массивы numpy. Проверьте формат данных.")
        
        # Проверка размеров массивов
        if len(data['time_points']) == 0:
            raise ValueError("Массив time_points пуст")
        if len(data['states']) == 0:
            raise ValueError("Массив states пуст")
        if len(data['controls']) == 0:
            raise ValueError("Массив controls пуст")
        
        # Проверка согласованности размеров
        if len(data['time_points']) != len(data['states']):
            raise ValueError(f"Несоответствие размеров массивов: time_points ({len(data['time_points'])}) и states ({len(data['states'])})")
        
        # Обработка случая, когда time_points на 1 элемент длиннее controls
        if len(data['time_points']) > len(data['controls']) and len(data['time_points']) == len(data['controls']) + 1:
            data['time_points'] = data['time_points'][:-1]
            data['states'] = data['states'][:-1]
            print(f"Массивы time_points и states обрезаны (было {len(data['time_points'])+1}, стало {len(data['time_points'])})")
        elif len(data['time_points']) != len(data['controls']):
            raise ValueError(f"Несоответствие размеров массивов: time_points ({len(data['time_points'])}) и controls ({len(data['controls'])})")
        
        # Проверка структуры массива states
        if data['states'].ndim != 2:
            raise ValueError(f"Массив states должен быть двумерным, но имеет размерность {data['states'].ndim}")
        if data['states'].shape[1] < 2:
            raise ValueError(f"Массив states должен содержать как минимум два параметра (столбцов: {data['states'].shape[1]})")
        
        return data

    def get_data(self):
        return self.data

# Класс для рендеринга фазовой траектории
class PhaseTrajectory:
    def __init__(self, states, time_points, reference_position=(0,0,0), offset_x=0, colors=None):
        """
        Инициализирует фазовую траекторию
        Аргументы:
            states -- массив состояний [f, p, r]
            time_points -- массив временных точек
            reference_position -- опорная точка для построения траектории
            offset_x -- смещение вправо от опорной точки
            colors -- список цветов элементов траектории
        """
        self.states = states
        self.time_points = time_points
        self.reference_position = Vec3(*reference_position)
        self.offset_x = offset_x
        self.colors = colors if colors else ["#E2725B", "#8AABBD", "#F3D6E4", "#D9A566", "#005F73"]
        
        # Определяем размерность состояния (2D или 3D)
        self.is_3d = states.shape[1] >= 3
        
        if self.is_3d:
            # Настройки для 3D фазового портрета
            self.max_f = np.max(np.abs(states[:, 0]))
            self.max_p = np.max(np.abs(states[:, 1]))
            self.max_r = np.max(np.abs(states[:, 2]))
            self.scale_f = 0.8
            self.scale_p = 0.8
            self.scale_r = 0.8
            
            self.create_3d_trajectory()
            self.create_3d_coordinate_system()
        
        # Создаем маркер текущей точки
        self.current_marker = Entity(
            model='sphere',
            color=color.rgb(*[int(self.colors[0][i:i+2], 16)/255 for i in (1,3,5)]),
            scale=0.1,
            position=(self.reference_position.x + offset_x, 0, self.reference_position.z)
        )

    def create_3d_trajectory(self):
        """Создает точки 3D траектории"""
        vertices = []
        step = 5  # Прореживаем точки
        for i in range(0, len(self.states), step):
            state = self.states[i]
            normalized_f = state[0] / self.max_f * self.scale_f
            normalized_p = state[1] / self.max_p * self.scale_p
            normalized_r = state[2] / self.max_r * self.scale_r
            
            vertices.append((
                self.reference_position.x + self.offset_x + normalized_f,
                normalized_p,
                self.reference_position.z + normalized_r
            ))
        
        self.trajectory_points = []
        for vertex in vertices:
            point = Entity(
                model='sphere',
                color=color.rgba(1.0, 0.4, 0.1, 0.9),
                scale=0.03,
                position=vertex
            )
            self.trajectory_points.append(point)
        
        self.trajectory_parent = Entity()
        for point in self.trajectory_points:
            point.parent = self.trajectory_parent

    def create_3d_coordinate_system(self):
        """Создает оси координат для 3D фазового портрета"""
        # Оси координат
        self.f_axis = Entity(
            model='cube',
            color=color.white,
            scale=(1.8, 0.03, 0.03),
            position=(self.reference_position.x + self.offset_x, 0, self.reference_position.z)
        )
        
        self.p_axis = Entity(
            model='cube',
            color=color.white,
            scale=(0.03, 1.8, 0.03),
            position=(self.reference_position.x + self.offset_x, 0, self.reference_position.z)
        )
        
        self.r_axis = Entity(
            model='cube',
            color=color.white,
            scale=(0.03, 0.03, 1.8),
            position=(self.reference_position.x + self.offset_x, 0, self.reference_position.z)
        )
        
        # Не добавляем текстовые метки для осей, как было запрошено

    def update_marker(self, f, p, r):
        """Обновляет положение маркера текущей точки"""
        if self.is_3d:
            # Для трехмерного случая
            normalized_f = f / self.max_f * self.scale_f
            normalized_p = p / self.max_p * self.scale_p
            normalized_r = r / self.max_r * self.scale_r
            
            self.current_marker.position = (
                self.reference_position.x + self.offset_x + normalized_f,
                normalized_p,
                self.reference_position.z + normalized_r
            )

# Класс для управления симуляцией
class SimulationManager:
    def __init__(self, data_path):
        self.data_loader = DataLoader(data_path)
        self.data = self.data_loader.get_data()
        self.current_frame = 0
        self.frame_skip = 2
        
        # Проверяем размерность состояния
        self.is_3d = self.data['states'].shape[1] >= 3
        
        # Создаем фазовую траекторию
        self.phase_trajectory = PhaseTrajectory(
            self.data['states'],
            self.data['time_points'],
            reference_position=(0, 0, 0)
        )
        
        # Не создаем текстовые элементы для отображения скорости и управления

    def update(self):
        """Обновляет состояние симуляции на каждом кадре"""
        if self.current_frame < len(self.data['states']):
            current_state = self.data['states'][self.current_frame]
            
            if self.is_3d:
                # Для трехмерного случая
                self.phase_trajectory.update_marker(
                    current_state[0],
                    current_state[1],
                    current_state[2]
                )
            
            self.current_frame += self.frame_skip
        else:
            self.current_frame = 0  # Возвращаемся к началу при достижении конца данных

# Класс для настройки сцены, камеры и освещения
class SceneSetup:
    def __init__(self):
        self.lights = [
            DirectionalLight(rotation=(45, -45, 45), color=color.white, intensity=0.8),
            DirectionalLight(rotation=(-45, 45, -45), color=color.white, intensity=0.6),
            AmbientLight(color=color.rgba(0.4, 0.4, 0.45, 1))
        ]
        
        self.floor = Entity(
            model='plane',
            color=color.rgb(0.15, 0.15, 0.2),
            scale=10,
            position=(0, -1.5, 0),
            texture='white_cube',
            texture_scale=(10, 10)
        )
        
        self.player = FirstPersonController(
            gravity=0,
            position=(0, 0, -5),
            rotation=(0, 0, 0),
            speed=5
        )
        
        window.color = color.rgb(0.02, 0.03, 0.1)
        
        # Не добавляем дополнительные текстовые инструкции

    def update(self, dt):
        """Обновляет дополнительные параметры, не включенные в FirstPersonController"""
        self.player.y += (held_keys['space'] - held_keys['shift']) * self.player.speed * dt
        
        # Сброс положения и поворота
        if held_keys['z']:
            self.player.position = Vec3(0, 0, -5)
            self.player.rotation = Vec3(0, 0, 0)

    def input_handler(self, key, sim_manager):
        """Обработчик ввода для закрытия программы"""
        if key == 'q':
            application.quit()

# Путь к файлу данных - используем путь относительно местоположения скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, "simulations", "phase_data.json")

app = Ursina()  # Инициализация приложения
window_manager = WindowManager()  # Настройка окна

scene_setup = SceneSetup()  # Настройка сцены, камеры и освещения
sim_manager = SimulationManager(filepath)  # Создание менеджера симуляции

# Обновляем функцию update для использования менеджера симуляции и управления камерой
def update():
    sim_manager.update()  # Обновление симуляции
    scene_setup.update(time.dt)  # Обновление дополнительных параметров, не включенных в FirstPersonController

def input(key):  # Настройка обработчика ввода
    scene_setup.input_handler(key, sim_manager)

app.run()  # Запуск приложения
