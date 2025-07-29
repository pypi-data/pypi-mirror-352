from dataclasses import dataclass

@dataclass
class HLScoreParam:
    point_score: float = 0.0
    has_high: bool = False
    has_low: bool = False

@dataclass
class HorizontalLine:
    hl_sr_value: float
    hl_sr_start_bar_index: int
    hl_sr_end_bar_index: int
    hl_sr_by_point_weighted_count: float  # Point number with line and extra weight
    hl_sr_by_point_count1: int  # Point number within 6m
    hl_sr_by_point_count2: int  # Point number within 24-6m
    hl_sr_accum_value: float
    hl_sr_score_info: HLScoreParam
    hl_sr_score: float

    def overlap(self, threshold, new_sr_value):
        is_overlap = False

        higher_bound_y = self.hl_sr_value * (1 + threshold / 100)
        lower_bound_y = self.hl_sr_value * (1 - threshold / 100)

        if higher_bound_y >= new_sr_value >= lower_bound_y:
            is_overlap = True

        return is_overlap
