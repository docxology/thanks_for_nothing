## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
boundary_gaze

## ModelAnnotation
Joint scene Z and encoding H, each three-valued, ordered Z-major H-minor. Canonical A is the first diagnostic visual query over nine joint action-response outcomes. Other queries compose the admitted gaze channels and declared contingency probes. D is independent uniform; B is identity; C is neutral because queried visual utility is imported from gaze. Native structural support is inherited through the gaze consumer and its emptiness_practice declaration. Label-only and diagnostic regimes are separate assumptions.

## StateSpaceBlock
A[9,9,type=float]
B[9,9,1,type=float]
C[9,type=float]
D[9,type=float]
s[9,type=float]
o[9,type=int]
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
A=[[0.2333333333333333,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.2333333333333333,0.06666666666666667,0.2333333333333333,0.16666666666666666],[0.06666666666666667,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.06666666666666667,0.09999999999999999,0.06666666666666667,0.09999999999999999],[0.03333333333333333,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.03333333333333333,0.16666666666666666,0.03333333333333333,0.06666666666666667],[0.2333333333333333,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.2333333333333333,0.06666666666666667,0.2333333333333333,0.16666666666666666],[0.06666666666666667,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.06666666666666667,0.09999999999999999,0.06666666666666667,0.09999999999999999],[0.03333333333333333,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.03333333333333333,0.16666666666666666,0.03333333333333333,0.06666666666666667],[0.2333333333333333,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.2333333333333333,0.06666666666666667,0.2333333333333333,0.16666666666666666],[0.06666666666666667,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.09999999999999999,0.06666666666666667,0.09999999999999999,0.06666666666666667,0.09999999999999999],[0.03333333333333333,0.06666666666666667,0.16666666666666666,0.06666666666666667,0.16666666666666666,0.03333333333333333,0.16666666666666666,0.03333333333333333,0.06666666666666667]]
B=[[[1],[0],[0],[0],[0],[0],[0],[0],[0]],[[0],[1],[0],[0],[0],[0],[0],[0],[0]],[[0],[0],[1],[0],[0],[0],[0],[0],[0]],[[0],[0],[0],[1],[0],[0],[0],[0],[0]],[[0],[0],[0],[0],[1],[0],[0],[0],[0]],[[0],[0],[0],[0],[0],[1],[0],[0],[0]],[[0],[0],[0],[0],[0],[0],[1],[0],[0]],[[0],[0],[0],[0],[0],[0],[0],[1],[0]],[[0],[0],[0],[0],[0],[0],[0],[0],[1]]]
C=[0,0,0,0,0,0,0,0,0]
D=[0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111,0.1111111111111111]
settings=[{"family":"boundary_gaze","backend":"pymdp","consumer":"thanks_for_nothing.boundary_study:build_boundary_gaze","parameters":{"seed":620715,"replicates":512,"steps":24,"prefixes":[16,32,64,128,256,512],"scene_maps":[[0,1,2],[1,2,0],[2,0,1]],"probe_reliabilities":[0.65,0.8,0.95],"probe_costs":[0.02,0.05,0.1],"regimes":["diagnostic","label_only"],"conditions":["visual","integrated","boundary_only","uniform","restricted","sham"],"endpoints":["anchored_regret","boundary_brier"],"gaze_model":"gaze","anchor_mapping":0,"joint_seed":620716,"comparisons":[["integrated","visual"],["boundary_only","visual"],["uniform","visual"],["restricted","visual"],["sham","visual"],["integrated","uniform"],["integrated","boundary_only"]]},"claim_boundary":"Authored finite joint scene/encoding experiment. Anchored forecast is an explicit reference-frame intervention. No human gaze, metacognitive sensitivity, ontological boundary, gratitude efficacy or realization claim. Finite software validation; not empirical."}]

