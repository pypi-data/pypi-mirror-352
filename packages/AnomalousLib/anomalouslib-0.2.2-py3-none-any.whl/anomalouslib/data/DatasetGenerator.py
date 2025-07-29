from anomalouslib.constants import params

from scipy.stats import levy_stable, pareto
from fbm import FBM
import pandas as pd
import numpy as np

class DatasetGenerator:
    def __init__(self, num_particules):
        self.num_particules = num_particules

    def changeParams(self, num_particules=None):
        # Canvia els paràmetres del generador de dades si es proporcionen nous valors
        if num_particules is not None:
            self.num_particules = num_particules

    def _format_data(self, x, y, attributes, num_passos):
        # Dona format a les dades generades per a les trajectòries
        data = []
        individual_num_steps = attributes.pop("individual_num_steps", [num_passos] * self.num_particules)
        for i in range(self.num_particules):
            coords = [x[i, :individual_num_steps[i]].tolist(), y[i, :individual_num_steps[i]].tolist()]
            trajectory_data = {
                "coords": coords,
                "num_steps": individual_num_steps[i],
                "attributes": {k: (v[i] if (isinstance(v, (list, np.ndarray)) and len(v) == self.num_particules) else v) for k, v in attributes.items()}
            }
            data.append(trajectory_data)
        return pd.DataFrame(data)
    
    def _decide_num_steps(self, num_passos):
        if isinstance(num_passos, (tuple, list)) and len(num_passos) == 2:
            min_steps, max_steps = num_passos
            steps_per_particle = np.random.randint(min_steps, max_steps + 1, size=self.num_particules)
            max_num_passos = steps_per_particle.max()
        elif isinstance(num_passos, int):
            steps_per_particle = np.full(self.num_particules, num_passos)
            max_num_passos = num_passos
        else:
            raise ValueError("num_passos ha de ser un enter o una tupla de dos enters")
        return steps_per_particle.tolist(), int(max_num_passos)


    def generate_RandomWalk(self, tipus=params.rw.default_type, random_params=False, num_passos=100):
        def _chooseMovementsRandomWalk(tipus):
            match tipus:
                case "nonstop": return params.rw.nonstop
                case "chill_stop": return params.rw.chill_stop
                case "hard_stop": return params.rw.hard_stop
                case _: raise ValueError(f"Unknown movement type: {tipus}")

        # Decideix el nombre de passos
        if isinstance(num_passos, (tuple, list)) and len(num_passos) == 2:
            min_steps, max_steps = num_passos
            steps_per_particle = np.random.randint(min_steps, max_steps + 1, size=self.num_particules)
            max_num_passos = steps_per_particle.max()
        elif isinstance(num_passos, int):
            steps_per_particle = np.full(self.num_particules, num_passos)
            max_num_passos = num_passos
        else:
            raise ValueError("num_passos ha de ser un enter o una tupla de dos enters")

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        if random_params:
            tipus_per_particle = np.random.choice(["nonstop", "chill_stop", "hard_stop"], self.num_particules).tolist()
        else:
            tipus_per_particle = [tipus] * self.num_particules

        for i in range(1, max_num_passos):
            dx = np.zeros(self.num_particules)
            dy = np.zeros(self.num_particules)
            for j in range(self.num_particules):
                if i < steps_per_particle[j]:
                    movements = _chooseMovementsRandomWalk(tipus_per_particle[j])
                    dx[j], dy[j] = movements[np.random.randint(0, len(movements))]
                else:
                    dx[j], dy[j] = 0, 0  # Si ja ha acabat, es queda quiet
            x[:, i] = x[:, i - 1] + dx
            y[:, i] = y[:, i - 1] + dy

        # Usem _format_data!
        return self._format_data(
            x, y,
            attributes={
                "trajectory_type": "Random Walk",
                "movement_type": tipus_per_particle,
                "individual_num_steps": steps_per_particle
            },
            num_passos=max_num_passos
        )
    
    def generate_BrownianMotion(self, generator_type="numpy", delta_t=params.bm.default_delta_t, sigma=params.bm.default_sigma, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            delta_t_per_particle = np.random.uniform(params.bm.min_delta_t, params.bm.max_delta_t, self.num_particules)
            sigma_per_particle = np.random.uniform(params.bm.min_sigma, params.bm.max_sigma, self.num_particules)
        else:
            delta_t_per_particle = np.full(self.num_particules, delta_t)
            sigma_per_particle = np.full(self.num_particules, sigma)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for i in range(1, max_num_passos):
            for p in range(self.num_particules):
                if i < steps_per_particle[p]:
                    scale = sigma_per_particle[p] * np.sqrt(delta_t_per_particle[p])
                    dx = np.random.normal(0, scale)
                    dy = np.random.normal(0, scale)
                    x[p, i] = x[p, i-1] + dx
                    y[p, i] = y[p, i-1] + dy
                else:
                    x[p, i] = x[p, i-1]
                    y[p, i] = y[p, i-1]

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Brownian Motion",
                "generator_type": generator_type,
                "delta_t": delta_t_per_particle.tolist(),
                "sigma": sigma_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )

    def generate_FractionalBrownianMotion(self, hurst=params.fbm.default_hurst, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            hurst_per_particle = np.random.uniform(params.fbm.min_hurst, params.fbm.max_hurst, self.num_particules)
        else:
            hurst_per_particle = np.full(self.num_particules, hurst)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for p in range(self.num_particules):
            fbm_x = FBM(n=steps_per_particle[p] - 1, hurst=hurst_per_particle[p]).fbm()
            fbm_y = FBM(n=steps_per_particle[p] - 1, hurst=hurst_per_particle[p]).fbm()
            x[p, :steps_per_particle[p]] = fbm_x
            y[p, :steps_per_particle[p]] = fbm_y

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Fractional Brownian Motion",
                "hurst": hurst_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )

    def generate_ContinuousTimeRandomWalk(self, alpha=params.ctrw.default_alpha, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            alpha_per_particle = np.random.uniform(params.ctrw.min_alpha, params.ctrw.max_alpha, self.num_particules)
        else:
            alpha_per_particle = np.full(self.num_particules, alpha)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for p in range(self.num_particules):
            wait_times = pareto.rvs(alpha_per_particle[p], size=steps_per_particle[p])
            times = np.cumsum(wait_times)
            t_norm = np.linspace(0, times[-1], steps_per_particle[p])
            x[p, :steps_per_particle[p]] = np.interp(t_norm, times, np.cumsum(np.random.randn(len(times))))
            y[p, :steps_per_particle[p]] = np.interp(t_norm, times, np.cumsum(np.random.randn(len(times))))

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Continuous Time Random Walk",
                "alpha": alpha_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )

    def generate_LevyWalks(self, alpha=params.lw.default_alpha, beta=params.lw.default_beta, speed=params.lw.default_speed, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            alpha_per_particle = np.clip(np.random.uniform(params.lw.min_alpha, params.lw.max_alpha, self.num_particules), 1.1, 2.0)
            beta_per_particle = np.random.uniform(params.lw.min_beta, params.lw.max_beta, self.num_particules)
            speed_per_particle = np.random.uniform(params.lw.min_speed, params.lw.max_speed, self.num_particules)
        else:
            alpha_per_particle = np.full(self.num_particules, alpha)
            beta_per_particle = np.full(self.num_particules, beta)
            speed_per_particle = np.full(self.num_particules, speed)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for p in range(self.num_particules):
            steps = levy_stable.rvs(alpha_per_particle[p], beta_per_particle[p], size=steps_per_particle[p])
            angles = np.random.uniform(0, 2*np.pi, steps_per_particle[p])
            dx = speed_per_particle[p] * np.abs(steps) * np.cos(angles)
            dy = speed_per_particle[p] * np.abs(steps) * np.sin(angles)
            x[p, :steps_per_particle[p]] = np.cumsum(dx)
            y[p, :steps_per_particle[p]] = np.cumsum(dy)

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Lévy Walk",
                "alpha": alpha_per_particle.tolist(),
                "beta": beta_per_particle.tolist(),
                "speed": speed_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )

    def generate_AnnealedTransitTimeModel(self, gamma_shape=params.attm.default_gamma_shape, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            gamma_shape_per_particle = np.random.uniform(params.attm.min_gamma_shape, params.attm.max_gamma_shape, self.num_particules)
        else:
            gamma_shape_per_particle = np.full(self.num_particules, gamma_shape)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for p in range(self.num_particules):
            Ds = np.random.gamma(gamma_shape_per_particle[p], size=steps_per_particle[p])
            dx = np.random.normal(0, np.sqrt(Ds))
            dy = np.random.normal(0, np.sqrt(Ds))
            x[p, :steps_per_particle[p]] = np.cumsum(dx)
            y[p, :steps_per_particle[p]] = np.cumsum(dy)

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Annealed Transient Time Model",
                "gamma_shape": gamma_shape_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )

    def generate_ScaledBrownianMotion(self, beta=params.sbm.default_beta, random_params=False, num_passos=100):
        steps_per_particle, max_num_passos = self._decide_num_steps(num_passos)

        if random_params:
            beta_per_particle = np.random.uniform(params.sbm.min_beta, params.sbm.max_beta, self.num_particules)
        else:
            beta_per_particle = np.full(self.num_particules, beta)

        x = np.zeros((self.num_particules, max_num_passos))
        y = np.zeros((self.num_particules, max_num_passos))

        for p in range(self.num_particules):
            t = np.arange(steps_per_particle[p])
            D_t = (t + 1) ** (beta_per_particle[p] - 1)
            dx = np.random.normal(0, np.sqrt(D_t))
            dy = np.random.normal(0, np.sqrt(D_t))
            x[p, :steps_per_particle[p]] = np.cumsum(dx)
            y[p, :steps_per_particle[p]] = np.cumsum(dy)

        return self._format_data(
            x, y,
            {
                "trajectory_type": "Scaled Brownian Motion",
                "beta": beta_per_particle.tolist(),
                "individual_num_steps": steps_per_particle
            },
            max_num_passos
        )