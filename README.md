GUI:
- Load trajectory.
- Set params.
- Set x0.
- Set optimization params (max iterations, min iterations, sigma0...).
- Visualize 3D trajectories.
- Visualize 2D states.
- See optimization log messages.
- See optimization progress (eg. fitness).
...
- Set parameter scaling.
- Set dynamic model.
- Set boundaries.
- Update graphs in real-time during optimization.


Instalar CASADI en Debian para Python:
pip install casadi
sudo apt-get install libblas3 libblas-dev liblapack3 liblapack-dev gfortran
download HSL free solvers source code from http://www.hsl.rl.ac.uk/ipopt/ (personal license, ma27, ma28, etc..)
unzip
open terminal in unzipped folder
./configure LIBS="-llapack" --with-blas="-L/usr/lib -lblas" CXXFLAGS="-g -O2 -fopenmp" FCFLAGS="-g -O2 -fopenmp" CFLAGS="-g -O2 -fopenmp"
make
make install
ln -s /usr/local/lib/libcoinhsl.so /usr/local/lib/libhsl.so
para comprobar:
ldd /usr/local/lib/libhsl.so
tiene que resultar en:
    linux-vdso.so.1 (0x00007ffc2c284000)
    liblapack.so.3 => /lib/x86_64-linux-gnu/liblapack.so.3 (0x00007f51800c9000)
    libgfortran.so.5 => /lib/x86_64-linux-gnu/libgfortran.so.5 (0x00007f517fe5b000)
    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f517fcd8000)
    libgomp.so.1 => /lib/x86_64-linux-gnu/libgomp.so.1 (0x00007f517fca7000)
    libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f517fc8d000)
    libquadmath.so.0 => /lib/x86_64-linux-gnu/libquadmath.so.0 (0x00007f517fc4b000)
    libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f517fc28000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f517fa67000)
    libblas.so.3 => /lib/x86_64-linux-gnu/libblas.so.3 (0x00007f517f68d000)
    libatlas.so.3 => /lib/x86_64-linux-gnu/libatlas.so.3 (0x00007f517f2ef000)
    libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f517f0d1000)
    /lib64/ld-linux-x86-64.so.2 (0x00007f5180849000)
    libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f517f0cc000)