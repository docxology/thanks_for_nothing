## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
practice_process_41508c8466d32151

## ModelAnnotation
Exogenous reversal Bernoulli schedule; known stage, absorbing last stage.

## StateSpaceBlock
A[2,12,type=float]
B[12,12,1,type=float]
C[2,type=float]
D[12,type=float]
s[12,type=float]
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
A={(0.85,0.85,0.85,0.85,0.15,0.15,0.15,0.15,0.85,0.85,0.85,0.85),(0.15000000000000002,0.15000000000000002,0.15000000000000002,0.15000000000000002,0.85,0.85,0.85,0.85,0.15000000000000002,0.15000000000000002,0.15000000000000002,0.15000000000000002)}
B={((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(0.0),(0.0)),((0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(0.0),(1.0),(1.0))}
C=[0.0,0.0]
D=[1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
settings=[{"family":"standalone_generative","backend":"pymdp","consumer":"thanks_for_nothing.emptiness_practice:_rows","parameters":{"family":"practice_process","meaning":"Exogenous reversal Bernoulli schedule; known stage, absorbing last stage.","provenance":"All originating GNN source versions are bound by data/generative_models.json"},"claim_boundary":"Finite synthetic model; not empirical"}]
