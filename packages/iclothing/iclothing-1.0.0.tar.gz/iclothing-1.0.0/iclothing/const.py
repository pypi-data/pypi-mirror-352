#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def _get_func(k_b_dict):
    func_dict = {}
    for body_name, k_b_list in k_b_dict.items():
        func_list = [lambda x, k=k_b[0], b=k_b[1]: k * x + b for k_b in k_b_list]
        func_dict[body_name] = func_list
    return func_dict


def _get_cond_func(break_dict):
    cond_dict = {}
    for body_name, break_list in break_dict.items():
        if len(break_list) == 1 and break_list[0] is None:
            cond_list = [lambda x: np.ones_like(x)]
        else:
            breaks_lower = [float('-inf')] + break_list
            breaks_upper = break_list + [float('inf')]
            cond_list = [lambda x, lower=break_lower, upper=break_upper: (lower <= x) & (x < upper)
                         for break_lower, break_upper in zip(breaks_lower, breaks_upper)]
        cond_dict[body_name] = cond_list
    return cond_dict


def _get_pwl(func_dict, cond_func_dict):
    pwl_dict = {}
    for body_name in BODY_NAMES:
        func_list = func_dict[body_name]
        cond_func_list = cond_func_dict[body_name]

        def pwl(x, _cond_func_list=cond_func_list, _func_list=func_list):
            return np.piecewise(x, [cond_func(x) for cond_func in _cond_func_list], _func_list)

        pwl_dict[body_name] = pwl
    return pwl_dict


def _get_wind_corr_func(a_b_dict):
    wind_corr_dict = {}
    for body_name, a_b in a_b_dict.items():
        def wind_corr_func(x, a=a_b[0], b=a_b[1]):
            return a * np.log(x) + b

        wind_corr_dict[body_name] = wind_corr_func
    return wind_corr_dict


BODY_NAMES: list = [
    "Head", "Neck", "Chest", "Back", "Pelvis",
    "LShoulder", "LArm", "LHand",
    "RShoulder", "RArm", "RHand",
    "LThigh", "LLeg", "LFoot",
    "RThigh", "RLeg", "RFoot"]
"""List of body names."""

_K_B_DICT_GENERIC: dict = {  # [(k1, b1), (k2, b2), ...]
    "Head": [(0, 0.13)],
    "Neck": [(0, 0)],
    "Chest": [(2.958, -0.297)],
    "Back": [(2.483, -0.097), (4.626, -2.347)],
    "Pelvis": [(2.256, 0.437), (7.047, -4.617)],
    "LShoulder": [(2.221, -0.459)],
    "LArm": [(2.492, -0.840)],
    "LHand": [(0, 0)],
    "RShoulder": [(2.221, -0.459)],
    "RArm": [(2.492, -0.840)],
    "RHand": [(0, 0)],
    "LThigh": [(0.370, 0.507), (1.999, -1.274)],
    "LLeg": [(2.019, -0.552), (0.758, 0.016)],
    "LFoot": [(0.693, 0.217), (0.139, 1.146)],
    "RThigh": [(0.370, 0.507), (1.999, -1.274)],
    "RLeg": [(2.019, -0.552), (0.758, 0.016)],
    "RFoot": [(0.693, 0.217), (0.139, 1.146)],
}
"""Dictionary of k and b values of piecewise functions for generic posture (standing and seating)."""

_K_B_DICT_STANDING: dict = {  # [(k1, b1), (k2, b2), ...]
    "Head": [(0, 0.13)],
    "Neck": [(0, 0)],
    "Chest": [(2.975, -0.540)],
    "Back": [(3.668, -0.738)],
    "Pelvis": [(2.706, 0.698), (5.482, -1.846)],
    "LShoulder": [(2.230, -0.534)],
    "LArm": [(2.580, -0.907)],
    "LHand": [(0, 0)],
    "RShoulder": [(2.230, -0.534)],
    "RArm": [(2.580, -0.907)],
    "RHand": [(0, 0)],
    "LThigh": [(0.752, 0.321), (2.314, -1.849)],
    "LLeg": [(2.794, -0.825), (0.648, 0.260)],
    "LFoot": [(0.757, 0.182), (0.092, 1.240)],
    "RThigh": [(0.752, 0.321), (2.314, -1.849)],
    "RLeg": [(2.794, -0.825), (0.648, 0.260)],
    "RFoot": [(0.757, 0.182), (0.092, 1.240)],
}
"""Dictionary of k and b values of piecewise functions for standing posture."""

_FUNC_DICT_GENERIC: dict = _get_func(_K_B_DICT_GENERIC)
"""Dictionary of functions for piecewise functions for generic posture (standing and seating)."""

_FUNC_DICT_STANDING: dict = _get_func(_K_B_DICT_STANDING)
"""Dictionary of functions for piecewise functions for standing posture."""

_BREAK_DICT_GENERIC: dict = {
    "Head": [None],
    "Neck": [None],
    "Chest": [None],
    "Back": [1.050],
    "Pelvis": [1.055],
    "LShoulder": [None],
    "LArm": [None],
    "LHand": [None],
    "RShoulder": [None],
    "RArm": [None],
    "RHand": [None],
    "LThigh": [1.093],
    "LLeg": [0.450],
    "LFoot": [1.677],
    "RThigh": [1.093],
    "RLeg": [0.450],
    "RFoot": [1.677],
}

_BREAK_DICT_STANDING: dict = {
    "Head": [None],
    "Neck": [None],
    "Chest": [None],
    "Back": [None],
    "Pelvis": [0.916],
    "LShoulder": [None],
    "LArm": [None],
    "LHand": [None],
    "RShoulder": [None],
    "RArm": [None],
    "RHand": [None],
    "LThigh": [1.390],
    "LLeg": [0.505],
    "LFoot": [1.590],
    "RThigh": [1.390],
    "RLeg": [0.505],
    "RFoot": [1.590],
}
"""Dictionary of break points for piecewise functions."""

_COND_FUNC_DICT_GENERIC: dict = _get_cond_func(_BREAK_DICT_GENERIC)
"""Dictionary of conditional functions for piecewise functions for generic posture (standing and seating)."""

_COND_FUNC_DICT_STANDING: dict = _get_cond_func(_BREAK_DICT_STANDING)
"""Dictionary of conditional functions for piecewise functions for standing posture."""

PWL_DICT_GENERIC: dict = _get_pwl(_FUNC_DICT_GENERIC, _COND_FUNC_DICT_GENERIC)
"""Dictionary of piecewise functions for generic posture (standing and seating)."""

PWL_DICT_STANDING: dict = _get_pwl(_FUNC_DICT_STANDING, _COND_FUNC_DICT_STANDING)
"""Dictionary of piecewise functions for standing posture."""

LOWER_LIMIT_DICT_GENERIC: dict = {
    "Head": 0,
    "Neck": 0,
    "Chest": 0.4,
    "Back": 0.22,
    "Pelvis": 0.755,
    "LShoulder": 0,
    "LArm": 0,
    "LHand": 0,
    "RShoulder": 0,
    "RArm": 0,
    "RHand": 0,
    "LThigh": 0.28,
    "LLeg": 0,
    "LFoot": 0.18,
    "RThigh": 0.28,
    "RLeg": 0,
    "RFoot": 0.18
}
"""Dictionary of lower limits of local clothing insulation for generic posture (standing and seating)."""

LOWER_LIMIT_DICT_STANDING: dict = {
    "Head": 0,
    "Neck": 0,
    "Chest": 0.4,
    "Back": 0.447,
    "Pelvis": 1.153,
    "LShoulder": 0,
    "LArm": 0,
    "LHand": 0,
    "RShoulder": 0,
    "RArm": 0,
    "RHand": 0,
    "LThigh": 0.316,
    "LLeg": 0,
    "LFoot": 0.211,
    "RThigh": 0.316,
    "RLeg": 0,
    "RFoot": 0.211
}
"""Dictionary of lower limits of local clothing insulation for standing posture."""

_A_B_DICT: dict = {
    "Head": (-0.241, 0.612),
    "Neck": (0, 1),
    "Chest": (-0.085, 0.864),
    "Back": (-0.155, 0.751),
    "Pelvis": (-0.127, 0.796),
    "LShoulder": (-0.106, 0.830),
    "LArm": (-0.046, 0.925),
    "LHand": (0, 1),
    "RShoulder": (-0.106, 0.830),
    "RArm": (-0.046, 0.925),
    "RHand": (0, 1),
    "LThigh": (-0.050, 0.920),
    "LLeg": (-0.071, 0.885),
    "LFoot": (-0.078, 0.875),
    "RThigh": (-0.050, 0.920),
    "RLeg": (-0.071, 0.885),
    "RFoot": (-0.078, 0.875),
}
"""Dictionary of a and b values of wind correction functions."""

WIND_CORR_DICT: dict = _get_wind_corr_func(_A_B_DICT)
"""Dictionary of wind correction functions."""

BSA_DICT: dict = {
    "Head": 0.100,
    "Neck": 0,
    "Chest": 0.144,
    "Back": 0.133,
    "Pelvis": 0.182,
    "LShoulder": 0.073,
    "LArm": 0.052,
    "LHand": 0.0375,
    "RShoulder": 0.073,
    "RArm": 0.052,
    "RHand": 0.0375,
    "LThigh": 0.1625,
    "LLeg": 0.089,
    "LFoot": 0.042,
    "RThigh": 0.1625,
    "RLeg": 0.089,
    "RFoot": 0.042
}
"""Dictionary of body surface area (in m\\ :sup:`2`)."""

BSA_TOTAL: float = sum(list(BSA_DICT.values()))
"""Total body surface area (in m\\ :sup:`2`)."""

BSA_RATIO_DICT: dict = {body_name: np.round(bsa / BSA_TOTAL, decimals=3).astype(type('float', (float,), {}))
                        for body_name, bsa in BSA_DICT.items()}
"""Dictionary of body surface area ratio."""

if __name__ == '__main__':
    pass
