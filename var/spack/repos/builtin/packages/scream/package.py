# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install scream
#
# You can edit this file again by typing:
#
#     spack edit scream
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Scream(CMakePackage):
    """E3SM Scream Package"""

    homepage = "https://github.com/E3SM-Project/scream"
    url      = "https://github.com/E3SM-Project/scream/archive/refs/tags/scream-v1.0.0-alpha.0.1.tar.gz"
    

    # maintainers = ['github_user1', 'github_user2']                                                                                                                               

    version('1.0.0-alpha.0.1',git="https://github.com/E3SM-Project/scream.git", tag="scream-v1.0.0-alpha.0.1",submodules=True)

    depends_on('cmake@3.23.1',type='build')
    depends_on('openmpi@4.1.2%intel@19.0.4.227')
    depends_on('netcdf-fortran@4.4.4')
    depends_on('netcdf-c')
    depends_on('cuda')
    depends_on('parallel-netcdf')
    depends_on('intel-mkl@2020.0.166')
    
    root_cmakelists_dir='components/scream'

    install_targets = ['install', 'baseline']
    
    conflicts('util-linux-uuid@2.36.3:', when='%intel')
    conflicts('diffutils@3.8:',when='%intel')

    def cmake_args(self):
        args = [
            '-D CMAKE_BUILD_TYPE=Debug',
            '-D Kokkos_ENABLE_DEBUG=TRUE',
            '-D Kokkos_ENABLE_AGGRESSIVE_VECTORIZATION=TRUE',
            '-D Kokkos_ENABLE_SERIAL=ON',
            '-D Kokkos_ENABLE_OPENMP=TRUE',
            '-D Kokkos_ENABLE_PROFILING=OFF',
            '-D Kokkos_ENABLE_DEPRECATED_CODE=OFF',
            '-D KOKKOS_ENABLE_ETI:BOOL=OFF',
            '-D CMAKE_C_COMPILER=mpicc',
            '-D CMAKE_CXX_COMPILER=mpicxx',
            '-D CMAKE_Fortran_COMPILER=mpif90',
            '-D Kokkos_ARGCH_BDW=ON',
            '-DCMAKE_CXX_FLAGS=-w -cxxlib=/usr/tce/packages/gcc/gcc-8.3.1/rh',
            '-DCMAKE_EXE_LINKER_FLAGS=-L/usr/tce/packages/gcc/gcc-8.3.1/rh/lib/gcc/x86_64-redhat-linux/8/ -mkl',
            '-D SCREAM_MPIRUN_EXE=mpiexec',
            '-D SCREAM_MPI_NP_FLAG=-n',
            '-D SCREAM_INPUT_ROOT=/usr/gdata/climdat/ccsm3data/inputdata'
        ]
        return args

    # def install_scripts(self):
    #     mkdirp(self.prefix.bin)
    #     with working_dir(self.scripts_directory):
    #         install('test-all-scream', self.prefix.bin)
    #         install('scripts-tests', self.prefix.bin)

        

