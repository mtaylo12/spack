#defined imposed_constraint/5.

depends_on(Parent, Child) :- imposed_constraint(_, "depends_on", Parent, Child, _), not virtual(Child).

conditional_depends(Parent,Child,ConditionNumber) :- condition(ConditionNumber, _),
																										 dependency_condition(ConditionNumber, Parent, Child),
                                                     not_basic(C).


not_basic(C) :- condition_requirement(C, S1, S2, S3).
not_basic(C) :- condition_requirement(C, S1, S2, S3, S4).

depends_on(Parent,Child) :- condition(C, _), condition_requirement(C, "node", _), dependency_condition(C, Parent, Child), not not_basic(C).

% for providers: condition looks like this: dependency_condition(1234,"hdf5","mpi").
% need to link all possible providers to their parent - if the interface is used there, the depth of an implementation is known, used or not
#show depends_on/2.
#show conditional_depends/3.
#show possible_provider/2.
