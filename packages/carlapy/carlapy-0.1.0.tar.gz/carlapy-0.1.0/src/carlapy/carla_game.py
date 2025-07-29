import math
import carla
import threading
import numpy as np
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import carla_utils


class CarlaGame:
    def __init__(self, actor_id, c: carla.Client):
        self.stop_event = threading.Event()

        self.client = c
        self.client.get_world().wait_for_tick()
        self.actor = carla_utils.get_actor(actor_id, self.client)
        if self.actor is None:
            raise RuntimeError('Actor {} not found'.format(actor_id))

        self.sensor: carla.Sensor | None = None

        self.bp = carla_utils.get_blueprint('sensor.camera.rgb', self.client)
        self.set_sensor_bp_attribute(self.bp)

        self.sensor_transform = carla.Transform()
        self.sensor_transform.location.x = 0
        self.sensor_transform.location.y = 0
        self.sensor_transform.location.z = 0
        self.sensor_transform.rotation.roll = 0
        self.sensor_transform.rotation.pitch = 0
        self.sensor_transform.rotation.yaw = 0
        if math.isfinite(self.actor.bounding_box.location.x):
            self.sensor_transform.location.x = -self.actor.bounding_box.extent.x * 2.
            self.sensor_transform.location.z = self.actor.bounding_box.extent.z * 2.

        self.sensor_attach_type = carla.AttachmentType.SpringArmGhost

        self.sensor_updated_event = pygame.USEREVENT + 1

        pygame.init()
        pygame.key.set_repeat(300, 50)
        self.display = pygame.display.set_mode((800, 600))
        self.display.fill((255, 255, 255))
        self.surface = None

    def __del__(self):
        self.stop()

    def stop(self):
        try:
            self.stop_event.set()
            if self.sensor is not None:
                if self.sensor.is_listening:
                    self.sensor.stop()
                self.sensor.destroy()
                self.sensor = None
            pygame.quit()
        except RuntimeError as e:
            print(e)

    def set_sensor_bp_attribute(self, bp: carla.ActorBlueprint):
        bp.set_attribute('role_name', 'spy_spectator')
        bp.set_attribute('sensor_tick', '0.04')
        bp.set_attribute('image_size_x', '800')
        bp.set_attribute('image_size_y', '600')
        bp.set_attribute('fov', '90')

    def spawn_sensor(self):
        try:
            if self.sensor is not None:
                if self.sensor.is_listening:
                    self.sensor.stop()
                self.sensor.destroy()
                self.sensor = None
            self.sensor = self.client.get_world().spawn_actor(self.bp, self.sensor_transform, self.actor, self.sensor_attach_type)
            self.sensor.listen(self.sensor_callback)
        except RuntimeError as e:
            print(e)

    def sensor_callback(self, sensor_data: carla.Image):
        if self.stop_event.is_set():
            return
        sensor_data.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(sensor_data.raw_data, dtype=np.uint8)
        array = np.reshape(array, (sensor_data.height, sensor_data.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        pygame.event.post(pygame.event.Event(self.sensor_updated_event))

    def move_sensor(self, keys):
        move = 0.1
        degree = 1
        if keys[pygame.K_LSHIFT]:
            move = 0.01
            degree = 0.1
        if keys[pygame.K_s]:
            if keys[pygame.K_UP]:
                self.sensor_transform.location.x += move
            if keys[pygame.K_DOWN]:
                self.sensor_transform.location.x -= move
            if keys[pygame.K_LEFT]:
                self.sensor_transform.location.y -= move
            if keys[pygame.K_RIGHT]:
                self.sensor_transform.location.y += move
            if keys[pygame.K_a]:
                self.sensor_transform.location.z += move
            if keys[pygame.K_d]:
                self.sensor_transform.location.z -= move
        if keys[pygame.K_x]:
            if keys[pygame.K_UP]:
                self.sensor_transform.rotation.pitch += degree
            if keys[pygame.K_DOWN]:
                self.sensor_transform.rotation.pitch -= degree
            if keys[pygame.K_LEFT]:
                self.sensor_transform.rotation.yaw -= degree
            if keys[pygame.K_RIGHT]:
                self.sensor_transform.rotation.yaw += degree
        self.sensor.set_transform(self.sensor_transform)
        print('Move to:', self.sensor.get_transform())

    def run(self):
        try:
            self.spawn_sensor()
            while not self.stop_event.is_set():
                event = pygame.event.wait()
                # print(event)
                # if event.type == pygame.KEYDOWN:
                #     print(event)
                match event.type:
                    case pygame.QUIT:
                        self.stop()
                    case self.sensor_updated_event:
                        if self.surface is not None:
                            self.display.blit(self.surface, (0, 0))
                            pygame.display.flip()
                    case pygame.KEYDOWN:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_s] or keys[pygame.K_x]:
                            self.move_sensor(keys)
        except RuntimeError as e:
            print(e)
            self.stop()
        except KeyboardInterrupt:
            self.stop()
