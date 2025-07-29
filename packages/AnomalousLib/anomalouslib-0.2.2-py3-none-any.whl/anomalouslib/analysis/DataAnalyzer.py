from matplotlib.widgets import TextBox
import matplotlib.pyplot as plt
import numpy as np

# Classe per a l'anàlisi de dades
class DataAnalyzer:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def mostrar_trajectories(self, title="Simulació de Moviment Brownià en 2D", interval=0, draw=True):
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(bottom=0.2)

        def update(_=None):
            ax.clear()
            try:
                new_interval = int(text_box.text)
            except ValueError:
                new_interval = interval

            for index, row in self.dataset.iterrows():
                x, y = row["coords"]
                ax.plot(x, y, label=f'Trajectòria {index+1}')
                if new_interval > 0:
                    for j in range(0, len(x), new_interval):
                        ax.text(x[j], y[j], f'{j}', fontsize=8, color='black')

            ax.scatter(self.dataset["coords"].apply(lambda c: c[0][0]), 
                       self.dataset["coords"].apply(lambda c: c[1][0]), 
                       color='red', marker='o', label="Inici")
            ax.scatter(self.dataset["coords"].apply(lambda c: c[0][-1]), 
                       self.dataset["coords"].apply(lambda c: c[1][-1]), 
                       color='blue', marker='x', label="Fi")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(title)
            ax.legend()
            ax.grid()
            fig.canvas.draw()

        if draw:
            ax_textbox = plt.axes([0.2, 0.05, 0.2, 0.075])
            text_box = TextBox(ax_textbox, "Interval", initial=str(interval))
            text_box.on_submit(update)
            update()
            plt.show()
        else:
            text_box = type("Dummy", (), {"text": str(interval)})()  # Simula un text_box si no usamos GUI
            update()
            return plt, fig, ax 
    
    def mostrar_evolucio(self, draw=True):
        num_passos = len(self.dataset.iloc[0]["coords"][0])
        each_range = num_passos // 25
        distances = {i: [] for i in range(each_range, num_passos+1, each_range)}
        
        for index, row in self.dataset.iterrows():
            x, y = row["coords"]
            for step in range(each_range, num_passos+1, each_range):
                distance = np.sqrt((x[step-1] - x[0])**2 + (y[step-1] - y[0])**2)
                distances[step].append(distance)

        mean_distances = {step: np.mean(distances[step]) for step in distances}

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([0] + list(mean_distances.keys()), [0] + list(mean_distances.values()), marker='o', linestyle='-', color='b')
        ax.set_title("Distància mitjana des del punt (0,0) a diferents punts finals")
        ax.set_xlabel("Punt final (n)")
        ax.set_ylabel("Distància mitjana")
        ax.grid(True)

        if draw:
            plt.show()
        else:
            return plt, fig, ax


    def mostrar_histograma(self, draw=True):
        final_points_x = self.dataset["coords"].apply(lambda c: c[0][-1])
        final_points_y = self.dataset["coords"].apply(lambda c: c[1][-1])

        hist, x_edges, y_edges = np.histogram2d(final_points_x, final_points_y, bins=[40, 40])

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        x_pos, y_pos = np.meshgrid(x_edges[:-1] + 0.5, y_edges[:-1] + 0.5)
        x_pos = x_pos.ravel()
        y_pos = y_pos.ravel()
        z_pos = np.zeros_like(x_pos)

        dz = hist.ravel()
        non_zero_indices = dz > 0
        x_pos = x_pos[non_zero_indices]
        y_pos = y_pos[non_zero_indices]
        z_pos = z_pos[non_zero_indices]
        dz = dz[non_zero_indices]

        dx = dy = (x_edges[1] - x_edges[0]) * 0.8

        ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, shade=True)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Quantitat de partícules')
        ax.set_title('Distribució de partícules al final de les trajectòries')

        if draw:
            plt.show()
        else:
            return plt, fig, ax
