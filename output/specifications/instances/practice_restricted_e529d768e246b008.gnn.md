## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
practice_restricted_e529d768e246b008

## ModelAnnotation
Finite deployment A with restricted D admitted by Realizing Emptiness.

## StateSpaceBlock
A[2,3,type=float]
B[3,3,1,type=float]
C[2,type=float]
D[3,type=float]
s[3,type=float]
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
A={(0.85,0.55,0.15),(0.15,0.45,0.85)}
B={((1.0),(0.0),(0.0)),((0.0),(1.0),(0.0)),((0.0),(0.0),(1.0))}
C=[0.0,0.0]
D=[0.5,0.5,0.0]
settings=[{"family":"standalone_generative","backend":"pymdp","consumer":"thanks_for_nothing.practice_inference:compare_priors","parameters":{"family":"practice_restricted","meaning":"Finite deployment A with restricted D admitted by Realizing Emptiness.","provenance":"All originating GNN source versions are bound by data/generative_models.json"},"claim_boundary":"Finite synthetic model; not empirical"}]
