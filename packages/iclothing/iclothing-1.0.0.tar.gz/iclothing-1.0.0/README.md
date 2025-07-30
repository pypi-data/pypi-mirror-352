iclothing
=======================

iclothing is a Python package designed to estimate local clothing insulation (I<sub>cl,i</sub>) values at 17 body parts
from a given overall clothing insulation (I<sub>cl</sub>) for standing and generic postures.

In thermal comfort analysis, assuming uniform insulation across body
segments can introduce significant errors in predicting heat exchange between the human body and the environment.
The iclothing package addresses this limitation by implementing regression models derived from 240 real-world clothing
ensembles, enabling fast and accurate predictions of local insulation values.

Please cite us if you use this package: Lin, J., Jiang, Y., Xie, Y. et al. A novel method for local clothing
insulation prediction to support sustainable building and urban design. Int J Biometeorol (2025).
https://doi.org/10.1007/s00484-025-02934-3


Documentation
-----

<https://lynnjunwei.github.io/iclothing/index.html>


Dependencies
-----

- numpy


Installation
-----

```bash
pip install iclothing
```


Example
-----

```python
import iclothing

icl = 0.3
icli = iclothing.get_icl_dict(icl=icl, posture="generic")
print(icli)
```
output:
```
{
    'Head': 0.13,
    'Neck': 0.0,
    'Chest': 0.59,
    'Back': 0.648,
    'Pelvis': 1.114,
    'LShoulder': 0.207,
    'LArm': 0.0,
    'LHand': 0.0,
    'RShoulder': 0.207,
    'RArm': 0.0,
    'RHand': 0.0,
    'LThigh': 0.618,
    'LLeg': 0.054,
    'LFoot': 0.425,
    'RThigh': 0.618,
    'RLeg': 0.054,
    'RFoot': 0.425
}
```
The order of the body parts is consistent with the [JOS-3](https://github.com/TanabeLab/JOS-3) model. 


License
-----

GNU General Public License v3.0


