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
    """FIXME: Put a proper description of your package here."""

# FIXME: Add a proper url for your package's homepage here.                                                                                                                    
    homepage = "https://github.com/E3SM-Project/scream"
    url      = "https://github.com/E3SM-Project/scream/archive/refs/tags/scream-v1.0.0-alpha.0.1.tar.gz"

    # FIXME: Add a list of GitHub accounts to                                                                                                                                      
    # notify when the package is updated.                                                                                                                                          
    # maintainers = ['github_user1', 'github_user2']                                                                                                                               

    version('1.0.0-alpha.0.1',git="https://github.com/E3SM-Project/scream.git", tag="scream-v1.0.0-alpha.0.1",submodules=True)
    #sha256='45e9293d36a7505283378f3d98206e593e963115b5c8624effda3859538b2515')                                                                                                    

    # FIXME: Add dependencies if required.


    depends_on('cmake@3.23.1',type='build')
    depends_on('openmpi@4.1.2%intel@19.0.4.227')
    #depends_on('mvapich2%intel@19.0.4.227')
    depends_on('netcdf-fortran@4.4.4%intel@19.0.4.227')
    depends_on('netcdf-c%intel@19.0.4.227')
    depends_on('cuda')
    depends_on('parallel-netcdf')

    
    root_cmakelists_dir='components/scream'
    install_targets = ['baseline']

    conflicts('util-linux-uuid@2.36.3:', when='%intel')
    conflicts('diffutils@3.8:',when='%intel')

    def cmake_args(self):
        # FIXME: Add arguments other than
        # FIXME: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE
        # FIXME: If not needed delete this function
        args = [
        '-D CMAKE_BUILD_TYPE=Debug',
                '-D Kokkos_ENABLE_DEBUG=TRUE',
                '-D Kokkos_ENABLE_AGGRESSIVE_VECTORIZATION=OFF',
                '-D Kokkos_ENABLE_SERIAL=ON',
                '-D Kokkos_ENABLE_OPENMP=ON',
                '-D Kokkos_ENABLE_PROFILING=OFF',
                '-D Kokkos_ENABLE_DEPRECATED_CODE=OFF',
                '-D KOKKOS_ENABLE_ETI:BOOL=OFF',
                '-D CMAKE_C_COMPILER=mpicc',
                '-D CMAKE_CXX_COMPILER=mpicxx',
                '-D CMAKE_Fortran_COMPILER=mpif90',
                '-D SCREAM_INPUT_ROOT=/usr/gdata/climdat/ccsm3data/inputdata/'
        ]
        return args
