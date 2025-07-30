#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Literal, Optional, Union
from types import FunctionType

from iclothing.const import PWL_DICT_GENERIC, PWL_DICT_STANDING, LOWER_LIMIT_DICT_GENERIC, LOWER_LIMIT_DICT_STANDING, WIND_CORR_DICT


def get_vr(met: float, va: float = 0.1) -> float:
    """
    Calculate relative air velocity.

    Relative air velocity is the sum of absolute air velocity and the walking speed, following the equation:

    .. math:: v_r = v_a + v_w

    For low metabolic rate (met < 1) which indicates behaviors without body movement, the walking speed is equal to 0:

    .. math:: v_w = 0

    For less-defined activities (e.g. conveyor belt work) (1 <= met < 1.2), the walking speed could be calculated using:

    .. math:: v_w= 0.3 \\times (met-1)

    For walking (met >= 2), the walking speed could be estimated using:

    .. math:: v_w = 0.5 \\times met - 0.1

    For other activities (1.2 <= met < 2), the walking speed could be calculated by interpolation of walking speeds for
    less-defined activities and walking:

    .. math:: v_w = 0.25 \\times (met^2 + met - 2.4)

    Args:
        met: A number of metabolic rate (in met = 58.15 W/m\ :sup:`2`).
        va: A number of absolute air velocity (in m/s).

    Returns:
        A number of relative air velocity (in m/s).
    """
    vr = va
    if met < 1:
        vr = va
    if 1 <= met < 1.2:
        vr = 0.3 * (met - 1) + va
    if 1.2 <= met < 2:
        vr = 0.25 * (met ** 2 + met - 2.4) + va
    if met >= 2:
        vr = 0.5 * met - 0.1 + va
    return vr


def _get_icl_i(icl: Union[list, np.ndarray, float],
               pwl: FunctionType,
               lower_limit: float) -> Union[np.ndarray, float]:
    """
    Get local clothing insulation for a specific body part.

    Args:
        icl: A number or a list of overall clothing insulation (in clo).
        pwl: A piecewise linear function for a specific body part.
        lower_limit: A number of lower limit of local clothing insulation for a specific body part (in clo).

    Returns:
        A number or a list of local clothing insulation for a specific body part (in clo).
    """
    icl_i = pwl(np.array(icl))
    icl_i = np.maximum(icl_i, lower_limit)
    return np.round(icl_i, decimals=3)


def get_icl_dict(icl: Union[list, np.ndarray, float],
                 posture: Literal["generic", "standing"] = "generic",
                 met: Optional[float] = None,
                 va: float = 0.1) -> dict:
    """
    Get local clothing insulation for each body part.

    The calculation models are based on the following papers:
    Lin, J., Jiang, Y., Xie, Y. et al. A novel method for local clothing
    insulation prediction to support sustainable building and urban design. Int J Biometeorol (2025).
    https://doi.org/10.1007/s00484-025-02934-3

    Args:
        icl: A number or a list of overall clothing insulation (in clo).
        posture: Posture of human object. The value should be 'generic' or 'standing'. Generic posture is based on
            data from both sitting and standing postures, while standing posture is based on data from standing posture
            only. Default is 'generic'.
        met: A number of Metabolic rate of human object (in met). If input, it will be used to calculated relative
            air velocity (in m/s). Default is None.
        va: A number of absolute air velocity (in m/s). If no met input, relative air velocity equals absolute
            air velocity. Default is 0.1 m/s, which represents static indoors.

    Returns:
        A dictionary of local clothing insulation for each body part.

    Examples:
        >>> icl = 0.3
        >>> icli = get_icl_dict(icl=icl, posture="generic")
        >>> icli
        {'Head': 0.13, 'Neck': 0.0, 'Chest': 0.59, 'Back': 0.648, 'Pelvis': 1.114, 'LShoulder': 0.207, 'LArm': 0.0,
        'LHand': 0.0, 'RShoulder': 0.207, 'RArm': 0.0, 'RHand': 0.0, 'LThigh': 0.618, 'LLeg': 0.054, 'LFoot': 0.425,
        'RThigh': 0.618, 'RLeg': 0.054, 'RFoot': 0.425}
    """
    if posture == 'generic':
        icl_dict = {body_name: _get_icl_i(icl, pwl, LOWER_LIMIT_DICT_GENERIC[body_name])
                    for body_name, pwl in PWL_DICT_GENERIC.items()}
    elif posture == 'standing':
        icl_dict = {body_name: _get_icl_i(icl, pwl, LOWER_LIMIT_DICT_STANDING[body_name])
                    for body_name, pwl in PWL_DICT_STANDING.items()}
    else:
        raise ValueError

    vr = get_vr(met, va) if met is not None else va
    if vr > 0.2:
        icl_dict = {body_name: (icl_i * WIND_CORR_DICT[body_name](vr))
                    for body_name, icl_i in icl_dict.items()}

    return {body_name: icl_i.astype(type('float', (float,), {})) for body_name, icl_i in icl_dict.items()}


if __name__ == '__main__':
    icl = 0.3
    icli = get_icl_dict(icl=icl, posture="generic")
    print(icli)
