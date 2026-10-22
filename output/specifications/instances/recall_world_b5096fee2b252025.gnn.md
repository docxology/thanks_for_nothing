## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
recall_world_b5096fee2b252025

## ModelAnnotation
IID exogenous states: every B column equals D. Paired conditions share A.

## StateSpaceBlock
A[3,2,type=float]
B[2,2,1,type=float]
C[3,type=float]
D[2,type=float]
s[2,type=float]
o[3,type=int]
u[1,type=int]

## Connections
D>s
s>A
A>o
s>B
u>B
B>s
C>u

## InitialParameterization
A={(0.7,0.2),(0.1,0.1),(0.2,0.7)}
B={((0.9),(0.9)),((0.09999999999999998),(0.09999999999999998))}
C=[0.0,0.0,0.0]
D=[0.9,0.09999999999999998]
settings=[{"family":"standalone_generative","backend":"pymdp","consumer":"thanks_for_nothing.experiments:sample_world","parameters":{"family":"recall_world","meaning":"IID exogenous states: every B column equals D. Paired conditions share A.","provenance":"All originating GNN source versions are bound by data/generative_models.json"},"claim_boundary":"Finite synthetic model; not empirical"}]
