## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
optimism_well_bb201b521bc166b4

## ModelAnnotation
News A for well mode. Trial priors enter from the assessment design.

## StateSpaceBlock
A[2,2,type=float]
B[2,2,1,type=float]
C[2,type=float]
D[2,type=float]
s[2,type=float]
o[2,type=int]
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
A={(0.6,0.2),(0.4,0.8)}
B={((0.5),(0.5)),((0.5),(0.5))}
C=[0.0,0.0]
D=[0.5,0.5]
settings=[{"family":"standalone_generative","backend":"pymdp","consumer":"thanks_for_nothing.inference:optimism","parameters":{"family":"optimism_well","meaning":"News A for well mode. Trial priors enter from the assessment design.","provenance":"All originating GNN source versions are bound by data/generative_models.json"},"claim_boundary":"Finite synthetic model; not empirical"}]
