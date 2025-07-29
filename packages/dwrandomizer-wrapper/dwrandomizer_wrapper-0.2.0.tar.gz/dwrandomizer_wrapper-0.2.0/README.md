# DWRandomizer-Wrapper

This package is for use with [Archipelago](https://github.com/Serpikmin/Archipelago-DragonWarrior), for Dragon Warrior (NES) development. It wraps a modified fork of [juef's unofficial Dragon Warrior randomizer](https://github.com/Serpikmin/dwrandomizer) (written in C) with Cython in order to run the randomizer natively for AP.

To use, install the package and then write:
```
import dwr

dwr.py_dwr_randomize(filepath, seed, flags, outpath)
```

where:
filepath = bytes(str)
seed = long
flags = bytes(str)
outpath = bytes(str)