% Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
% Spack Project Developers. See the top-level COPYRIGHT file for details.
%
% SPDX-License-Identifier: (Apache-2.0 OR MIT)

%=============================================================================-
% Display Results
%
% This section determines what parts of the model are printed at the end
%==============================================================================

% Spec attributes
#show attr/2.
#show attr/3.
#show attr/4.
#show attr/5.

% names of optimization criteria (generated in minimize.lp)
#show opt_criterion/3. 
#show depends_on/2.
#show requirement_has_weight/2.

% error types
#show error/2.
#show error/3.
#show error/4.
#show error/5.
#show error/6.
#show error/7.

#show internal_error/1.
#show optimize_for_reuse/0. %this is necessary for requirement weight counting

#show depth/2.

#show version_weight/2.
#show build/1.

#show build_priority/2.
#show requirement_weight/2.
#show variant_not_default/3. %this is necessary for preferred providers value but not default variant count...
#show provider_weight/3.
#show provider_weight/4.

#show compiler_mismatch/2.
#show variant_default_not_used/3.
#show node_os_mismatch/2.
#show compiler_weight/2.
#show node_os_weight/2.
#show node_target_mismatch/2.
#show node_target_weight/2.

#defined literal_not_solved/1.
#show literal_not_solved/1.

#show compiler_mismatch_required/2.

%#show parent_depth/2.

% debug

%#show depends_on/2.

%node(Package) :- attr("node", Package).
%#show node/1.

%version(Package, Version) :- attr("version", Package, Version).
%#show version/2.
