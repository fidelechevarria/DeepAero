# For installation: "python setup.py install"
from distutils.core import setup, Extension

# Nombre del módulo y archivos que contienen el código fuente.
module1 = Extension("optimcore",
                    define_macros=[('MAJOR_VERSION', '0'),
                                   ('MINOR_VERSION', '1')],
                    include_dirs = ['OptimCore/include'],
                    sources=["optimcoremodule.cpp", 
                             "OptimCore/source/dynamicModel.cpp"])

# Nombre del paquete, versión, descripción y una lista con las extensiones.
setup(name="optimcore",
      version="0.1",
      description="Evolutionary optimization library for parameter estimation.",
      author="Fidel Echevarria Corrales",
      url="https://fidelechevarria.github.io/",
      ext_modules=[module1],
      long_description='''
      Evolutionary optimization library for parameter estimation.
      Bla bla bla.
      ''')
