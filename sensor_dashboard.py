import tkinter as tk
import tkinter.scrolledtext as st
import threading
import time
import sys
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scipy import ndimage
import board
import busio
import adafruit_mlx90640
import adafruit_bme680
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

# Robot modules
import pigpio
import RPi.GPIO as GPIO
from robot_config import sense, frontServo, pump
from flame_sensor import get_flame_values
from sensor_setup import u1, u2, u3
from motor_control import forward, backward, leftTurn, rightTurn, brake, delay
from extinguish import extinguish

pi = pigpio.pi()

# Redirect print() to GUI
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        self.widget.after(0, lambda: self._append_text(s))

    def _append_text(self, s):
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END)

    def flush(self):
        pass

def launch_sensor_dashboard():
    stop_event = threading.Event()

    # === Sensor setup ===
    i2c = busio.I2C(board.SCL, board.SDA)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ
    mlx_shape = (24, 32)
    mlx_interp_val = 10
    mlx_interp_shape = (mlx_shape[0]*mlx_interp_val, mlx_shape[1]*mlx_interp_val)
    frame = np.zeros(mlx_shape[0]*mlx_shape[1])
    t_array = []

    bme = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    bme.sea_level_pressure = 1013.25
    temp_offset = -5

    imu = LSM6DS(i2c)
    mag = LIS3MDL(i2c)

    max_temp = 0
    temp_lock = threading.Lock()

    def thermal_thread():
        nonlocal max_temp
        while not stop_event.is_set():
            try:
                mlx.getFrame(frame)
                with temp_lock:
                    max_temp = max(frame)
            except Exception as e:
                print("Thermal thread error:", e)
                with temp_lock:
                    max_temp = 0
            time.sleep(0.1)

    root = tk.Tk()
    root.title("Robot Sensor Dashboard")

    # Layout
    frame1 = tk.Frame(root, bg="lightgray")
    frame2 = tk.Frame(root, bg="white")
    frame3 = tk.Frame(root, bg="lightblue")
    frame4 = tk.Frame(root, bg="black")

    frame1.grid(row=0, column=0, sticky="nsew")
    frame3.grid(row=1, column=0, sticky="nsew")
    frame4.grid(row=2, column=0, columnspan=2, sticky="nsew")
    frame2.grid(row=0, column=1, rowspan=2, sticky="nsew")

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=4)

    # === Panel 1: BME680 ===
    tk.Label(frame1, text="BME680 Sensor", bg="lightgray", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
    bme_data = tk.Label(frame1, text="", bg="lightgray", justify="left", font=("Courier", 14, "bold"))
    bme_data.pack()

    def update_bme():
        try:
            bme_data.config(text=(
                f"Temperature: {bme.temperature + temp_offset:0.1f} C\n"
                f"Humidity:    {bme.relative_humidity:0.1f} %\n"
                f"Pressure:    {bme.pressure:0.1f} hPa\n"
                f"Altitude:    {bme.altitude:0.1f} m\n"
                f"Gas:         {bme.gas} Ohm"
            ))
        except:
            bme_data.config(text="BME Error")
        root.after(1000, update_bme)

    # === Panel 3: IMU ===
    tk.Label(frame3, text="IMU Sensor", bg="lightblue", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
    imu_data = tk.Label(frame3, text="", bg="lightblue", justify="left", font=("Courier", 14, "bold"))
    imu_data.pack()

    def update_imu():
        try:
            acc = imu.acceleration
            gyro = imu.gyro
            magf = mag.magnetic
            imu_data.config(text=(
                f"Accel X/Y/Z: {acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f} m/s^2\n"
                f"Gyro  X/Y/Z: {gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f} rad/s\n"
                f"Mag   X/Y/Z: {magf[0]:.2f}, {magf[1]:.2f}, {magf[2]:.2f} uT"
            ))
        except:
            imu_data.config(text="IMU Error")
        root.after(1000, update_imu)

    # === Panel 2: Thermal Camera + Colormap ===
    from tkinter import StringVar
    colormaps = ['inferno', 'plasma', 'viridis', 'magma', 'hot', 'jet', 'bwr']
    cmap_var = StringVar(value='inferno')

    tk.Label(frame2, text="Colormap:", bg="white").pack(pady=(10, 0))
    tk.OptionMenu(frame2, cmap_var, *colormaps).pack(pady=(0, 5))

    fig = plt.Figure(figsize=(6, 5), dpi=100)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(0.05, 0.05, 0.95, 0.95)
    therm1 = ax.imshow(np.zeros(mlx_interp_shape), interpolation='none',
                       cmap=plt.get_cmap(cmap_var.get()), vmin=25, vmax=45)
    cbar = fig.colorbar(therm1)
    cbar.set_label('Temperature [C]', fontsize=10)

    canvas = FigureCanvasTkAgg(fig, master=frame2)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    fig.canvas.draw()
    ax_bg = fig.canvas.copy_from_bbox(ax.bbox)

    def update_thermal():
        try:
            fig.canvas.restore_region(ax_bg)
            data_array = np.fliplr(np.flipud(np.reshape(frame, mlx_shape)))
            data_array = ndimage.zoom(data_array, mlx_interp_val)
            therm1.set_data(data_array)
            therm1.set_cmap(plt.get_cmap(cmap_var.get()))
            therm1.set_clim(np.min(data_array), np.max(data_array))
            ax.draw_artist(therm1)
            fig.canvas.blit(ax.bbox)
            fig.canvas.flush_events()
            canvas.draw()
        except Exception as e:
            print("Thermal error:", e)
        root.after(100, update_thermal)

    # === Panel 4: Terminal Output ===
    tk.Label(frame4, text="Terminal Output", bg="black", fg="white", font=("Helvetica", 12, "bold")).pack()
    output_text = st.ScrolledText(frame4, bg="black", fg="lime", font=("Courier", 10), insertbackground="white")
    output_text.pack(fill=tk.BOTH, expand=True)
    sys.stdout = TextRedirector(output_text)

    def robot_loop():
        pi.write(12, 0)
        print("Starting robot in 5 seconds...")
        time.sleep(5)
        try:
            while not stop_event.is_set():
                distance1 = u1.distance * 100  # front
                distance2 = u2.distance * 100  # left
                distance3 = u3.distance * 100  # right
                left_val, front_val, right_val = get_flame_values()

                with temp_lock:
                    temp = max_temp

                if distance1 <= 70:
                    if front_val <= 6500 or temp > 49:
                        brake()
                        print(f"F:{front_val}, T:{temp:.1f} - Flame ahead! Extinguishing...")
                        extinguish()
                        delay(1.2)
                        pi.write(12,0)
                    elif left_val <= 6500 or right_val <= 6500:
                        if left_val <= 6500:
                            pi.set_servo_pulsewidth(sense, 1000)
                            backward()
                            print(f"F:{left_val} - Flame left. Repositioning...")
                            delay(0.5)
                        elif right_val <= 6500:
                            pi.set_servo_pulsewidth(sense, 2000)
                            backward()
                            print(f"F:{right_val} - Flame right. Repositioning...")
                            delay(0.5)
                        else:
                            brake()
                        continue
                    else:
                        brake()
                        delay(0.05)
                        if distance2 > 40 or distance3 > 40:
                            if distance2 > distance3:
                                leftTurn()
                                print(f"Obstacle. Turning left. L:{distance2:.1f}, R:{distance3:.1f}")
                                delay(0.2)
                            else:
                                rightTurn()
                                print(f"Obstacle. Turning right. L:{distance2:.1f}, R:{distance3:.1f}")
                                delay(0.2)
                        else:
                            brake()
                            print("Surrounded. Stopping.")
                        continue
                elif distance1 > 70:
                    print(f"Front: {front_val}, Temp: {temp:.1f} C, Left: {left_val}, Right: {right_val}")
                    if front_val > 6500 and temp <= 50 and left_val > 6500 and right_val > 6500:
                        if front_val < left_val and front_val < right_val:
                            forward()
                            delay(0.05)
                            print("Searching for Flame")
                        elif left_val < front_val and left_val < right_val:
                            rightTurn()
                            delay(0.05)
                            print("Flame on right")
                        elif right_val < left_val and right_val < front_val:
                            leftTurn()
                            delay(0.05)
                            print("Flame on Left")
                    elif front_val <= 6500 or temp > 49:
                        brake()
                        print(f"F:{front_val}, T:{temp:.1f} - Extinguishing...")
                        extinguish()
                        delay(1.2)
                        pi.write(12,0)
                    elif left_val <= 6500 or right_val <= 6500:
                        if left_val <= 6500:
                            pi.set_servo_pulsewidth(sense, 1000)
                            backward()
                            print(f"F:{left_val} - left. Repositioning...")
                            delay(0.5)
                        elif right_val <= 6500:
                            pi.set_servo_pulsewidth(sense, 2000)
                            backward()
                            print(f"F:{right_val} - right. Repositioning...")
                            delay(0.5)
                        else:
                            brake()
                    else:
                        forward()
                        print(f"Clear path. Moving forward. F:{distance1:.1f}")
        except KeyboardInterrupt:
            print("Interrupted. Cleaning up...")
        finally:
            pi.set_servo_pulsewidth(sense, 1500)
            pi.set_servo_pulsewidth(frontServo, 1500)
            time.sleep(0.3)  # small delay to allow centering
            pi.set_servo_pulsewidth(sense, 0)         #  kill PWM output
            pi.set_servo_pulsewidth(frontServo, 0)    #  kill PWM output
            brake()
            pi.write(12, 0)
            GPIO.cleanup()

    def on_close():
        print("Closing GUI and stopping robot thread...")
        brake()
        pi.set_servo_pulsewidth(sense, 1500)
        pi.set_servo_pulsewidth(frontServo, 1500)
        time.sleep(0.3)  # small delay to allow centering
        pi.set_servo_pulsewidth(sense, 0)         # kill PWM output
        pi.set_servo_pulsewidth(frontServo, 0)    # kill PWM output
        pi.write(12, 0)
        GPIO.cleanup()
        stop_event.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    update_thermal()
    update_bme()
    update_imu()
    threading.Thread(target=thermal_thread, daemon=True).start()
    threading.Thread(target=robot_loop, daemon=True).start()
    root.mainloop()