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
#     spack install e3sm
#
# You can edit this file again by typing:
#
#     spack edit e3sm
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class E3sm(Package):
    """E3SM (Energy Exascale Earth System Model) dependency installer"""

    homepage = "https://e3sm.org/"
    url      = "https://github.com/E3SM-Project/scream"

    maintainers = ['Jessicat-H']

    version('master',git="https://github.com/E3SM-Project/scream.git", branch='master',submodules=True)

    depends_on('cmake@3.23.1',type='build')
    depends_on('openmpi@4.1.2')
    depends_on('netcdf-fortran@4.4.4')
    depends_on('netcdf-c')
    depends_on('cuda')
    depends_on('parallel-netcdf')
    depends_on('intel-mkl@2020.0.166', when='%intel')
    depends_on('py-pyyaml')
    depends_on('py-pylint')
    depends_on('py-psutil')

    def install(self, spec, prefix):
        return 0

