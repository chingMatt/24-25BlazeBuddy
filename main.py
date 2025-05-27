from sensor_dashboard import launch_sensor_dashboard

try:
    launch_sensor_dashboard()
except KeyboardInterrupt:
    print("Keyboard interrupt received. Exiting...")