import matplotlib.pyplot as plt
from math import floor
from statistics import mode
from .setup import *
from ..constants import *
from ..layers import *
from ..utils import *
from ..materials import *
import gdsfactory as gf
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np

from gdsfactory.cross_section import Section
from gdsfactory.generic_tech import LAYER_STACK, LAYER


def make_sim_problem(
    path,
    wavelengths=[],
    center_wavelength=None,
    frequencies=[],
    center_frequency=None,
    sources=[],
    monitors=[],
    nres=None,
    dx=None,
    layer_stack={},
    materials={},
    study="simulation",
    dtype="float32",
    Ttrans=None,
    Tss=None,
    Tssmin=None,
    wl_res=0.01,
    margins=[[0, 0, 0], [0, 0, 0]],
    df=None,
    gpu=None,
    dorun=True,
):
    if not wavelengths:
        if not center_frequency:
            center_frequency = mode(frequencies)

    wavelengths, center_wavelength, T = adjust_wavelengths(
        wavelengths, center_wavelength, wl_res
    )

    GEOMETRY = os.path.join(path, "geometry")
    bbox = [[None, None, None], [None, None, None]]
    for material in os.listdir(GEOMETRY):
        for fn in os.listdir(os.path.join(GEOMETRY, material)):
            if fn.lower().endswith(".stl"):
                STL = os.path.join(GEOMETRY, material, fn)
                print(STL)
                pymeshfix.clean_from_file(STL, STL)
                mesh = pv.read(STL)
                for i, v, w in zip(
                    range(3), bbox[0], [mesh.bounds[i] for i in [0, 2, 4]]
                ):
                    if v is None or w < v:
                        bbox[0][i] = w
                for i, v, w in zip(
                    range(3), bbox[1], [mesh.bounds[i] for i in [1, 3, 5]]
                ):
                    if v is None or w > v:
                        bbox[1][i] = w
    bbox[0] = (np.array(bbox[0]) - np.array(margins[0])).tolist()
    bbox[1] = (np.array(bbox[1]) + np.array(margins[1])).tolist()

    bbox[1] = [a + dx * floor((b - a) / dx) for (a, b) in zip(bbox[0], bbox[1])]

    print(bbox)

    L = (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1], bbox[1][2] - bbox[0][2])
    if not Tss:
        Tss = T if len(wavelengths) > 1 else None
    prob = {
        "class": "gen",
        "sources": sources,
        "monitors": monitors,
        "nres": nres,
        "study": study,
        "dtype": dtype,
        "center_wavelength": center_wavelength,
        "layer_stack": layer_stack,
        "materials": materials,
        "L": L,
        "gpu_backend": gpu,
        "Ttrans": Ttrans,
        "Tss": Tss,
        "Tssmin": Tssmin,
        "wavelengths": wavelengths,
        "frequencies": frequencies,
        "df": df,
        "dorun": dorun,
    }
    PROB = os.path.join(path, "problem.json")
    with open(PROB, "w") as f:
        json.dump(prob, f)
    return prob

    # l = [k for k in imow if port_number(k) == pi]
    # if not l:
    #     imow[f"o{pi}@{mi}"] = []
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[i] = imow[k]
    #         del imow[k]

    # l = [k for k in imow[i] if port_number(k) == po]
    # if not l:
    #     imow[f"o{pi}@{mi}"]
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[f"o{pi}@{mn}"] = imow[k]
    #         del imow[k]

    # if po not in imow[pi]:
    #     imow[pi]["o"][po] = mo
    # else:
    #     imow[pi]["o"][po] = max(imow[pi]["o"][po], mo)
