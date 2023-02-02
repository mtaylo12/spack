# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from xml.dom import minidom
import os

class E3smScream(Package):
    """Builds dependencies for E3SM SCREAM"""

    homepage = "https://e3sm.org/"
    url = "https://github.com/E3SM-Project/scream"
    git = "https://github.com/E3SM-Project/scream.git"

    # maintainers = ["Jessicat-H", "mtaylo12"]

    version("master", branch="master", submodules=True)

    depends_on("cmake@3.18.0")
    depends_on("netcdf-fortran@4.4.4")
    depends_on("netcdf-c@4.4.1")
    depends_on("cuda")
    depends_on("parallel-netcdf@1.10.0")
    depends_on("py-poetry", type=("build", "link", "run"))
    depends_on("py-pip", type=("build", "link", "run"))
    depends_on("py-pyyaml", type=("build", "link", "run"))
    depends_on("py-pylint", type=("build", "link", "run"))
    depends_on("py-psutil", type=("build", "link", "run"))
    depends_on("perl-xml-libxml", type=("build", "link", "run"))
    depends_on("util-linux-uuid@:2.36.2", when="%intel")
    depends_on("intel-mkl@2020.0.166", when="%intel", type=("build", "link", "run"))

    conflicts("diffutils@3.8:", when="%intel")
    conflicts("netcdf-c@4.5:")

    @run_after("install")
    def gen_xml(self):

        #xml setup
        root = minidom.Document()
        xml = root.createElement('root')
        root.appendChild(xml)
        mach = root.createElement('mach')
        mach.setAttribute('name', 'machine name here')
        xml.appendChild(mach)

        #machine description entry
        desc = root.createElement('DESC')
        mach.appendChild(desc)
        desc_text = root.createTextNode('Machine description here')
        desc.appendChild(desc_text)

        #compiler entry
        compiler = root.createElement('COMPILERS')
        mach.appendChild(compiler)
        curr_compiler = self.compiler.name
        comp_text = root.createTextNode(curr_compiler)
        compiler.appendChild(comp_text)

        #mpi entry
        mpi = root.createElement('MPILIBS')
        mach.appendChild(mpi)
        mpi.appendChild(root.createTextNode(self.spec['mpi'].name))
        
        #modules
        modules = root.createElement('modules')
        modules.setAttribute('compiler',self.compiler.name)
        mach.appendChild(modules)

        comp_module = root.createElement('command')
        comp_module.setAttribute('name','load')
        comp_module.appendChild(root.createTextNode(self.compiler.name + '/' + str(self.compiler.version)))
        modules.appendChild(comp_module)
        
        #environment variables
        env_var = root.createElement('environment_variables')
        env_var.setAttribute('compiler', self.compiler.name)
        mach.appendChild(env_var)
        
        netcdf_c = root.createElement('env')
        netcdf_c.setAttribute('name',"NETCDF_C_PATH")
        netcdf_c.appendChild(root.createTextNode(self.spec["netcdf-c"].prefix))
        env_var.appendChild(netcdf_c)

        netcdf_fort = root.createElement('env')
        netcdf_fort.setAttribute('name',"NETCDF_FORTRAN_PATH")
        netcdf_fort.appendChild(root.createTextNode(self.spec["netcdf-fortran"].prefix))
        env_var.appendChild(netcdf_fort)

        p_netcdf = root.createElement('env')
        p_netcdf.setAttribute('name',"PNETCDF_PATH")
        p_netcdf.appendChild(root.createTextNode(self.spec["parallel-netcdf"].prefix))
        env_var.appendChild(p_netcdf)
        
        


        #saving to file in stage directory
        xml_str = root.toprettyxml(indent ="\t")
        save_path_file = join_path(self.stage.source_path, "machine-config.xml")
        with open(save_path_file, "w") as f:
            f.write(xml_str)



        

    def install(self, spec, prefix):
        mkdirp(prefix.lib)
