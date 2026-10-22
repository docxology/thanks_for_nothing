## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
analysis

## ModelAnnotation
Shared statistical protocol and diagnostic budgets. The identity tensors provide a neutral configuration carrier, not a new psychological model. Fixed mathematical control targets remain independent of these settings.

## StateSpaceBlock
A[1,1,type=float]
B[1,1,1,type=float]
C[1,type=float]
D[1,type=float]
s[1,type=float]
o[1,type=int]
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
A=[[1.0]]
B=[[[1.0]]]
C=[0.0]
D=[1.0]
settings=[{"family":"analysis","backend":"pymdp","consumer":"thanks_for_nothing.analysis_design:load_analysis","parameters":{"alpha":0.05,"statistics_seed_offset":101,"heterogeneity_seed_offset":1000,"calibration_seed_offset":7301,"diagnostic_prefixes":[16,32,64,128,256,512,1024],"notebook_replicates":8,"notebook_draws":511,"notebook_timeout_seconds":1800,"reconstruction_seed":2025,"reconstruction_agents":1000,"reconstruction_days":7,"reconstruction_steps":12,"reconstruction_audit_agents":12},"claim_boundary":"Finite statistical simulation protocol; not empirical evidence of human efficacy or realization"}]
