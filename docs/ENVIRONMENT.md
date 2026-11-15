# Environment

Tested with Python 3.12, NumPy 2.2.1, SciPy 1.18.1, scikit-learn 1.6.1,
and pytest 8.3.4. `requirements.txt` pins this executed environment. A fresh
installation was not tested because this workstation could not reach PyPI.

On macOS Accelerate, set `VECLIB_MAXIMUM_THREADS=1` before Python starts.
The local Accelerate/NumPy combination emits floating-point warnings during some
large matrix operations, even with this setting. The tests pass, outputs remain
finite, and independent distance/inertia/PCA checks are included. Treat the current
figures as provisional until cross-platform reproduction resolves these warnings;
no claim of a warning-free numerical run is made.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export VECLIB_MAXIMUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
```

Original files are preserved separately from new code. Reconstructed code was
AI-assisted in November 2026 and should be understood and reviewed by Sahil.
The repository does not represent the new implementation as original 2023 code.
