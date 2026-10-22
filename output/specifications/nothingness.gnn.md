## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
nothingness

## ModelAnnotation
Finite synthetic experiment; A axes observation,state and B axes next,previous,action. Not empirical.

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
A=[[0.9,0.2],[0.1,0.8]]
B=[[[1.0],[0.0]],[[0.0],[1.0]]]
C=[0.0,-1.0]
D=[0.6,0.4]
settings=[{"family":"nothingness","backend":"pymdp","consumer":"thanks_for_nothing.nothingness:build_nothingness_audit","parameters":{"reference_hazard":0.3,"harm_cost":1.0,"blackwell_grid_steps":11},"claim_boundary":"Finite synthetic software model; not empirical evidence of gratitude, well-being or attainment"}]
