import io
import math
import sys
import carla
import click
import typer
from typing import Optional, Annotated
import carla_utils
import utils
import carla_game

client: carla.Client = carla.Client('127.0.0.1', 2000)
app = typer.Typer(invoke_without_command=True)

@app.callback()
def main_callback(
        ctx: typer.Context,
        host: Annotated[str, typer.Option(help='CARLA host')] = '127.0.0.1',
        port: Annotated[int, typer.Option(help='CARLA port')] = 2000,
        timeout: Annotated[float, typer.Option(help='CARLA timeout')] = 1.0,
):
    global client
    client = carla.Client(host, port)
    client.set_timeout(timeout)
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())

@app.command(name='print_actors', help='Print actors tree containing pattern')
def print_actors(pattern: Annotated[str, typer.Argument(help='pattern match the role_name or type_id')] = 'vehicle'):
    global client
    client.get_world().wait_for_tick()
    actors = client.get_world().get_actors()
    carla_utils.print_actors_tree(actors, pattern)

@app.command(name='print_actor', help='Print actor specified by actor id or role_name')
def print_actor(
        actor_id: Annotated[str, typer.Argument(help='Actor id or role_name')],
        loop: Annotated[bool, typer.Option(help='Loop mode')] = False,
):
    global client
    client.get_world().wait_for_tick()
    actor = carla_utils.get_actor(actor_id, client)
    if actor is None:
        print('Actor not found')
        return
    if not loop:
        carla_utils.print_actor(actor, client)
        return
    utils.set_stdout_nonblocking()
    while True:
        snapshot = client.get_world().wait_for_tick()
        origin_stdout = sys.stdout
        buffer = io.StringIO()
        sys.stdout = buffer
        sys.stdout.write("\x1b[H\x1b[2J\x1b[3J")
        sys.stdout.flush()
        print('CARLA Frame: ', snapshot.frame)
        carla_utils.print_actor(actor,
                                client,
                                print_parent = False,
                                print_sons = False,
                                print_attributes = False,
                                print_location = True,
                                print_rotation = True,
                                print_move = True,
                                print_boundbox = False,
                                print_vehicle_wheel = True,
                                print_vehicle_control = False,
                                print_vehicle_physics = False,
                                )
        sys.stdout = origin_stdout
        sys.stdout.write(buffer.getvalue())

@app.command(name='destroy_actor', help='Destroy actor with the id')
def destroy_actor(actor_id: Annotated[str, typer.Argument(help='The actor id or role_name of the actor to destroy.')]):
    global client
    client.get_world().wait_for_tick()
    carla_utils.destroy_actor(actor_id, client)

@app.command(name='available_maps', help='Print available maps')
def available_maps():
    global client
    client.get_world().wait_for_tick()
    print(*client.get_available_maps(), sep='\n')
    current_map = client.get_world().get_map()
    print()
    print('Current Map: ', current_map)

@app.command(name='available_bp', help='Print available blueprints')
def available_bp(pattern: Annotated[Optional[str], typer.Option(help="pattern match the blueprint type")] = '*'):
    global client
    client.get_world().wait_for_tick()
    if not pattern.startswith('*'):
        pattern = '*' + pattern
    if not pattern.endswith('*'):
        pattern = pattern + '*'
    print(*client.get_world().get_blueprint_library().filter(pattern), sep='\n')

@app.command(name='print_settings', help='Print current settings')
def print_settings():
    global client
    client.get_world().wait_for_tick()
    settings = client.get_world().get_settings()
    carla_utils.print_settings(settings)

@app.command(name='move_spectator', help='Move spectator')
def move_spectator(actor_id: Annotated[int, typer.Argument(help='id of target actor')]):
    global client
    client.get_world().wait_for_tick()
    world = client.get_world()
    world.get_spectator().set_transform(world.get_actor(actor_id).get_transform())

@app.command(name='spy', help='Spy the specified actor')
def spy(actor_id: Annotated[str, typer.Argument(help='id of target actor')]):
    global client
    client.get_world().wait_for_tick()
    cg = carla_game.CarlaGame(actor_id, client)
    cg.run()

@app.command(name='pose_debug', help='Pose debug')
def pose_debug():
    global client
    client.get_world().wait_for_tick()
    spectator = carla_utils.get_actor('spectator', client)
    gnss_bp = carla_utils.get_blueprint('sensor.other.gnss', client)
    imu_bp = carla_utils.get_blueprint('sensor.other.imu', client)
    gnss: carla.Sensor = carla_utils.spawn_actor(client, gnss_bp, parent=spectator)
    imu: carla.Sensor = carla_utils.spawn_actor(client, imu_bp, parent=spectator)
    data = {'gnss': None, 'imu': None}
    gnss.listen(lambda e: data.update({'gnss': e}))
    imu.listen(lambda e: data.update({'imu': e}))
    try:
        while True:
            client.get_world().wait_for_tick()
            gnss_data: carla.GnssMeasurement = data['gnss']
            imu_data: carla.IMUMeasurement = data['imu']
            if gnss_data is None or imu_data is None:
                continue
            print('Gnss:')
            print('  Frame  :', gnss_data.frame)
            print('  lat    :', gnss_data.latitude)
            print('  lon    :', gnss_data.longitude)
            print('  alt    :', gnss_data.altitude)
            print('  X      :', gnss_data.transform.location.x)
            print('  Y      :', gnss_data.transform.location.y)
            print('  Z      :', gnss_data.transform.location.z)
            print('  roll   :', gnss_data.transform.rotation.roll)
            print('  pitch  :', gnss_data.transform.rotation.pitch)
            print('  yaw    :', gnss_data.transform.rotation.yaw)
            print('Imu:')
            print('  Frame  :', imu_data.frame)
            print('  compass:', math.degrees(imu_data.compass))
            print('  gyro.x :', imu_data.gyroscope.x)
            print('  gyro.y :', imu_data.gyroscope.y)
            print('  gyro.z :', imu_data.gyroscope.z)
            print('  acc.x  :', imu_data.accelerometer.x)
            print('  acc.y  :', imu_data.accelerometer.y)
            print('  acc.z  :', imu_data.accelerometer.z)
            print()
    finally:
        gnss.stop()
        imu.stop()
        carla_utils.destroy_actor(gnss.id, client)
        carla_utils.destroy_actor(imu.id, client)


if __name__ in "__main__":
    try:
        app()
    except RuntimeError as e:
        print(e)
