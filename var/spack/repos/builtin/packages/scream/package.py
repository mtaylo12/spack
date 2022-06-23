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
    """E3SM Scream Model"""

    homepage = "https://github.com/E3SM-Project/scream"
    url      = "https://github.com/E3SM-Project/scream/archive/refs/tags/SCREAMv2.0.0-beta.3.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ['github_user1', 'github_user2']

    
    version('2.0.0-beta.3', git="https://github.com/E3SM-Project/scream.git", tag="2.0.0-beta.3")
    #sha256='71324f8d8290e7ef1143e2443e6e7b1a1ca8bcefb9168f418102e04053007780')

    # FIXME: Add dependencies if required.
    depends_on('cmake@3.23.1',type='build')

    depends_on('m4@1.4.19%intel@2021.6.0 cflags="-gcc-name=/usr/tce/packages/gcc/gcc-10.2.1/bin/gcc"')
    depends_on('tar@1.34%intel@2021.6.0  cflags="-gcc-name=/usr/tce/packages/gcc/gcc-10.2.1/bin/gcc"')
    depends_on('mpich')
    depends_on('netcdf-fortran')
    depends_on('netcdf-c')
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
        args = ['-D CMAKE_BUILD_TYPE=Debug',
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
                '-C ${SCREAM_SRC_DIR}/components/scream/cmake/machine-files/${HOSTNAME}.cmake',
                ]
        return 
