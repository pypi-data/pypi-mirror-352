from typing import List

def calculate_weighted_hl_value(by_point_values: List[float], last_by_point_weight: int, second_last_by_point_weight: int, by_point_weight: int) -> float:
    by_point_count = len(by_point_values)
    norm = 0.0
    sum_val = 0.0

    if by_point_count == 0:
        return 0.0  # Handle empty list case

    for x in range(by_point_count):
        if x == by_point_count - 1:
            weight = last_by_point_weight
        elif x == by_point_count - 2:
            weight = second_last_by_point_weight
        else:
            weight = by_point_weight
        
        norm += weight
        sum_val += by_point_values[x] * weight

    return sum_val / norm if norm != 0 else 0.0  # Return weighted average, handle division by zero
