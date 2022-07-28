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
#     spack install e3sm-test
#
# You can edit this file again by typing:
#
#     spack edit e3sm-test
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class E3smTest(Package):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://e3sm.org/"
    url      = "https://github.com/E3SM-Project/scream"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ['github_user1', 'github_user2']
    maintainers = ['Jessicat-H']
    # FIXME: Add proper versions here.
    # version('1.2.4')
    version('master',git="https://github.com/E3SM-Project/scream.git", branch='master',submodules=True)
    
    # FIXME: Add dependencies if required.
    # depends_on('foo')
    depends_on('cmake@3.18.0',type='build')
    depends_on('mvapich2@2.3',type=("build", "link"))
    depends_on('netcdf-fortran@4.4.4',type=("build", "link", "run"))
    depends_on('netcdf-c@4.4.1',type=("build", "link", "run"))
    depends_on('cuda')
    depends_on('parallel-netcdf@1.10.0',type=("build", "link", "run"))
    depends_on('python', type=("build", "link", "run"))
    #    depends_on('intel-mkl@2020.0.166', when='%intel')
    depends_on('py-pyyaml')
    depends_on('py-pylint')
    depends_on('py-psutil')
    depends_on('perl-xml-libxml') #,type=("build", "link", "run")) add this next time
    depends_on('util-linux-uuid@:2.36.2',when='%intel')

    conflicts('diffutils@3.8:',when='%intel')
    conflicts('netcdf-c@4.5:')
    def install(self, spec, prefix):
        # FIXME: Unknown build system
        return 0
    
