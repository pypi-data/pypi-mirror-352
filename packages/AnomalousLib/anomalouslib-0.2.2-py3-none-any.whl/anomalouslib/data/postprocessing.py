def min_max_denormalize(norm_value, min_value, max_value):
    return norm_value * (max_value - min_value) + min_value