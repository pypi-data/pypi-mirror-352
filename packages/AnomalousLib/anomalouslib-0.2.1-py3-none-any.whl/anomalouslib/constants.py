class params:
    class rw:
        default_type="nonstop"
        nonstop= [[1, 0], [-1, 0], [0, 1], [0, -1]]
        chill_stop= [[1, 0], [-1, 0], [0, 1], [0, -1], [0, 0]]
        hard_stop= [[1, 0], [-1, 0], [0, 1], [0, -1], [0, 0], [0, 0], [0, 0], [0, 0]]
    class bm:
        default_delta_t = 1
        default_sigma = 1
        min_delta_t = 0.1
        max_delta_t = 5.0
        min_sigma = 0.1
        max_sigma = 3.0
    class fbm:
        default_hurst = 0.75
        min_hurst = 0.1
        max_hurst = 0.9
    class ctrw:
        default_alpha = 1.2
        min_alpha = 1.1
        max_alpha = 2.5
    class lw:
        default_alpha = 1.8
        default_beta = 0.0
        default_speed = 1.0
        min_alpha = 1.1
        max_alpha = 2.0
        min_beta = -1.0
        max_beta = 1.0
        min_speed = 0.1
        max_speed = 5.0
    class attm:
        default_gamma_shape = 1.5
        min_gamma_shape = 0.5
        max_gamma_shape = 5.0
    class sbm:
        default_beta = 1.3
        min_beta = 0.5
        max_beta = 2.0

trajectory_types_mapping = {
    "Random Walk": params.rw,
    "Brownian Motion": params.bm,
    "Fractional Brownian Motion": params.fbm,
    "Continuous Time Random Walk": params.ctrw,
    "Lévy Walk": params.lw,
    "Annealed Transient Time Model": params.attm,
    "Scaled Brownian Motion": params.sbm,
}