# MAORIS

MAORIS map segmentation in rust and with python bindings.

![Image of a segmentation](https://raw.githubusercontent.com/MalcolmMielle/maoris/ICRA2018/Images/maoris_NLB_straighten_color.png)
![Image of another segmentation](https://raw.githubusercontent.com/MalcolmMielle/maoris/ICRA2018/Images/maoris_Freiburg101_scan_straighten_color.png)

Paper: [ArXiv](https://arxiv.org/abs/1709.09899), [IEEE](https://ieeexplore.ieee.org/abstract/document/8461128)

```bibtex
@inproceedings{mielle2018method,
  title={A method to segment maps from different modalities using free space layout maoris: map of ripples segmentation},
  author={Mielle, Malcolm and Magnusson, Martin and Lilienthal, Achim J},
  booktitle={2018 IEEE International Conference on Robotics and Automation (ICRA)},
  pages={4993--4999},
  year={2018},
  organization={IEEE}
}
```

## Build

To build the rust backend, use `cargo build` in the root folder.
To buidld the python package only, run `maturin build` in the "maoris-py" folder.

## Python usage

```python
import maoris_py

maoris = maoris_py.maoris("path/to/image.png", "output_path")
```
