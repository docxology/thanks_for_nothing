## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
emptiness_practice

## ModelAnnotation
Finite prior-revisability experiment. Candidate deployments are operational representations, not states of realization. A is observation by deployment; B is identity, C neutral. GNN settings declare all task choices. Calibration and held-out observations are independent conditional on the declared context.

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
A=[[0.85,0.55,0.15],[0.15,0.45,0.85]]
B=[[[1.0],[0.0],[0.0]],[[0.0],[1.0],[0.0]],[[0.0],[0.0],[1.0]]]
C=[0.0,0.0]
D=[0.3333333333333333,0.3333333333333333,0.3333333333333333]
settings=[{"family":"emptiness_practice","backend":"pymdp","consumer":"thanks_for_nothing.emptiness_practice:build_practice_audit","parameters":{"seed":1729,"replicates":512,"calibration_samples":24,"assessment_samples":512,"bootstrap_draws":4095,"action_precision":6,"practice_cost":0.2,"examinability_preference":0.4,"previous_gain_weight":1,"metacognitive_access":1,"prior_precision":2,"deployments":[{"name":"dual_A","labels":["self","self","env"]},{"name":"dual_B","labels":["self","env","env"]},{"name":"relational_C","labels":["sensation","action","context"]}],"contexts":[{"name":"stationary","probabilities":[0.85,0.85,0.85,0.85,0.85,0.85,0.85,0.85,0.85,0.85,0.85,0.85]},{"name":"reversal","probabilities":[0.85,0.85,0.85,0.85,0.15,0.15,0.15,0.15,0.85,0.85,0.85,0.85]}],"conditions":["rigid","inquiry","no_preference","sham","no_access"]},"claim_boundary":"Finite synthetic software model, not empirical evidence of gratitude, emptiness realization, compassion or human efficacy"}]
