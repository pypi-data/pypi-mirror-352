import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=DeprecationWarning)
from matplotlib.animation import FuncAnimation
from scipy.integrate import ode

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class DynamicalSystem(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(DynamicalSystem, self).__init__(w_ratio, h_ratio, dpi, main_menu=1)

        self.fill_chapter("Dynamical System", 20, "Drag the pendulum or\nclick on the contour to\nset the initial state.\n\n"
                                                  "Click [Go] to simulate and\n[Clear] to ",
                          PACKAGE_PATH + "Logo/Logo_Ch_20.svg", None, description_coords=(535, 75, 450, 250))

        self.make_plot(8, (300, 100, 210, 300))
        # self.figure8.subplots_adjust(left=0.15, right=0.95, bottom=0.125, top=0.9)
        # self.figure8.set_tight_layout(True)
        # self.figure8.tight_layout()
        self.figure8.subplots_adjust(left=0.3, right=0.88, bottom=0.175)
        self.axis8 = self.figure8.add_subplot(1, 1, 1)
        self.axis8.set_title("Pendulum Energy")
        self.axis8.set_xlabel("Time (sec)")
        self.axis8.set_ylabel("Energy")
        self.axis8.set_xlim(0, 800)
        self.axis8.set_xticks([0, 200, 400, 600, 800])
        self.axis8.set_xticklabels(["0", "10", "20", "30", "40"])
        self.axis8.set_ylim(0, 500)
        # self.axis8.set_yscale("log")
        self.energy, self.energy_ = [], []
        self.energy_plot, = self.axis8.plot([], color="red")

        # --

        self.make_plot(9, (10, 100, 300, 300))
        # self.figure9.set_tight_layout(True)
        self.figure9.subplots_adjust(top=0.85, bottom=0.175)
        self.axis9 = self.figure9.add_subplot(1, 1, 1, polar=True)
        self.axis9.set_rmax(2)
        # self.axis9.grid(False)
        self.axis9.set_rticks([])
        self.axis9.set_theta_zero_location("S")
        self.pendulum_line, = self.axis9.plot([], color="black", linewidth=2)
        self.pendulum_point, = self.axis9.plot([], color="red", marker="*", markersize=10)
        self.angle, self.velocity = 2.1, -1.45
        self.axis9.set_xticks(np.pi / 180 * np.array([0, 90, 180, 270]))
        self.axis9.set_xticklabels(["$0$ radians", "$\pi/2$", "$\pi$ radians", "$3\pi/2$"])
        self.axis9.grid(False)
        r = np.arange(0, 2, 0.01)
        theta = [self.angle] * len(r)
        line = self.axis9.plot(theta, r)[0]
        tick = [self.axis9.get_rmax(), self.axis9.get_rmax() * 0.97]
        for t in np.deg2rad(np.arange(0, 360, 10)):
           self.axis9.plot([t, t], tick, lw=0.72, color="k")
        line.remove()
        self.draw_pendulum()
        self.ani, self.ani2, self.ani3, self.r, self.dt, self.t_end = None, None, None, None, 0.05, 40
        self.canvas9.mpl_connect('button_press_event', self.on_mouseclick)
        self.canvas9.draw()

        # --

        self.make_plot(10, (10, 410, 500, 250))
        self.figure10.subplots_adjust(bottom=0.2)
        self.axis10 = self.figure10.add_subplot(1, 1, 1)
        self.axis10.set_title("Energy Contour")
        self.axis10.set_xlabel("Angle (rad)")
        self.axis10.set_ylabel("Velocity (rad/s)")
        self.axis10.set_xlim(-15, 15)
        self.axis10.set_ylim(-3, 3)
        xx = np.arange(-15, 15, 0.01)
        yy = np.arange(-3, 3, 0.01)
        XX, YY = np.meshgrid(xx, yy)
        EE = 0.5 * 9.8 ** 2 * YY ** 2 + 9.81 * 9.8 * (1 - np.cos(XX))
        self.axis10.contour(XX, YY, EE, levels=[0, 100, 192, 300, 450, 550])
        self.energy_initial, = self.axis10.plot([], marker="*", color="red")
        self.energy_initial.set_data([self.angle], [self.velocity])
        self.energy_path, = self.axis10.plot([], color="red")
        self.energy_path_data_x, self.energy_path_data_y = [], []
        self.draw_energy_path()
        self.canvas10.mpl_connect('button_press_event', self.on_mouseclick2)
        self.canvas10.draw()

        # --

        self.make_button("run_button", "Go", (self.x_chapter_button, 265, self.w_chapter_button, self.h_chapter_button), self.run_animation)

    def ani_stop(self):
        if self.ani and self.ani.event_source:
            self.ani.event_source.stop()
        if self.ani2 and self.ani2.event_source:
            self.ani2.event_source.stop()
        if self.ani3 and self.ani3.event_source:
            self.ani3.event_source.stop()

    def on_mouseclick(self, event):
        # d_angle_click_pendulum_point = abs(self.angle - (event.xdata + 90) * np.pi / 180)
        # d_r_click_pendulum_point = abs(1.51 - event.ydata)
        # if (d_angle_click_pendulum_point + d_r_click_pendulum_point) / 2 < 0.05:
        #     print("!")
        self.ani_stop()
        self.angle = event.xdata
        self.draw_pendulum()
        self.energy_plot.set_data([], [])
        if self.angle and self.angle < -np.pi:
            self.angle += 2 * np.pi
        self.energy_initial.set_data([self.angle], [self.velocity])
        self.energy_path.set_data([], [])
        self.canvas8.draw()
        self.canvas9.draw()
        self.canvas10.draw()

    def on_mouseclick2(self, event):
        # d_angle_click_pendulum_point = abs(self.angle - (event.xdata + 90) * np.pi / 180)
        # d_r_click_pendulum_point = abs(1.51 - event.ydata)
        # if (d_angle_click_pendulum_point + d_r_click_pendulum_point) / 2 < 0.05:
        #     print("!")
        self.ani_stop()
        self.angle, self.velocity = event.xdata, event.ydata
        self.draw_pendulum()
        self.energy_plot.set_data([], [])
        # if self.angle < -np.pi:
        #     self.angle += 2 * np.pi
        self.energy_initial.set_data([self.angle], [self.velocity])
        self.energy_path.set_data([], [])
        self.canvas8.draw()
        self.canvas9.draw()
        self.canvas10.draw()

    def run_animation(self):
        self.ani_stop()
        self.ani = FuncAnimation(self.figure9, self.on_animate, init_func=self.animate_init,
                                 frames=800, interval=0, repeat=False, blit=False)
        self.ani2 = FuncAnimation(self.figure8, self.on_animate_2, init_func=self.animate_init_2,
                                  frames=800, interval=0, repeat=False, blit=True)
        self.ani3 = FuncAnimation(self.figure10, self.on_animate_3, init_func=self.animate_init_3,
                                  frames=800, interval=0, repeat=False, blit=True)
        self.canvas9.draw()
        self.canvas8.draw()
        self.canvas10.draw()

    def draw_pendulum(self):
        r = np.arange(0, 1.5, 0.01)
        theta = [self.angle] * len(r)
        self.pendulum_line.set_data(theta, r)
        self.pendulum_point.set_data([theta[0]], [r[-1] + 0.01])

    def draw_energy(self):
        self.energy.append(0.5 * 9.8 ** 2 * self.velocity ** 2 + 9.81 * 9.8 * (1 - np.cos(self.angle)))
        self.energy_plot.set_data(range(len(self.energy)), self.energy)

    def draw_energy_path(self):
        self.energy_path_data_x.append(self.angle)
        self.energy_path_data_y.append(self.velocity)
        self.energy_path.set_data(self.energy_path_data_x, self.energy_path_data_y)

    def animate_init(self):
        self.draw_pendulum()
        self.r = ode(self.pendulum_pos_vel).set_integrator("zvode")
        self.r.set_initial_value([self.angle, self.velocity], 0)
        return self.pendulum_line, self.pendulum_point

    def animate_init_2(self):
        self.energy, self.energy_ = [], []
        self.draw_energy()
        return self.energy_plot,

    def animate_init_3(self):
        self.energy_path_data_x, self.energy_path_data_y = [], []
        self.draw_energy_path()
        return self.energy_path,

    def on_animate(self, idx):
        if self.r.successful() and self.r.t < self.t_end:
            self.angle, self.velocity = self.r.integrate(self.r.t + self.dt)
        self.draw_pendulum()
        return self.pendulum_line, self.pendulum_point

    def on_animate_2(self, idx):
        self.draw_energy()
        return self.energy_plot,

    def on_animate_3(self, idx):
        self.draw_energy_path()
        return self.energy_path,

    def pendulum_pos_vel(self, t, y):
        return [y[1], -np.sin(y[0]) - 0.2 * y[1]]
