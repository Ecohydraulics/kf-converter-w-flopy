# kf-converter-w-flopy
Computes the hydraulic conductivity of the hyporheic zone using a modflow model via flopy.

Contributors: Lydia Seitz, Beatriz Negreiros, Daniel Beetz, Alcides Galdos

## Welcome
This repository contains codes for running a calibrated MODFLOW model via Python with the flopy library for determining hydraulic conductivity values in the hyporheic zone. The input data consist of slurping rates, measured according to [Seitz (2022)](https://henry.baw.de/bitstream/20.500.11970/107414/1/276_Mitteilungen_UniStuttgart_Seitz.pdf). 

The model files living in *002_kf_wert_bestimmung* are se solely for the consiguration of the filter pipes developed according to the aforementioned Thesis (e.g., pipe diameter, perforation diameters and meshes). The codes are on the other hand re-usable if the model files are adjusted accordingly.

## Running the code
At first, checkout the *requirements.txt* file and install the necessary dependencies before moving forward.

Navigate to *compute_kf.py* and adjust the necessary input parameters for the function compute_kf. Necessary input data are read from the *input-data.xlsx* table:
- Slurping rates (in m³/s)
- Lz: Sediment depth + Water level (in m)
- Th_pm: Sediment depth (in m) of the measurement
- Parameters **a** and **b** for the Forchheimer Equation, see *compute_kf.py* example for computing **a** and **b**. Input parameters here are the dm and the estimated hydraulic conductivity calculated with the Kozeny-Carman Equation.
