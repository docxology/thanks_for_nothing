## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
gaze

## ModelAnnotation
Active sampling of a thirteen-location scene through three declared regional channels. A is the positive-region observation channel over the same three candidates admitted by the emptiness_practice declaration; settings specify the other conditional channels. B preserves the candidate within each independently reset episode. C expresses observation preference. Original-source replication, learned recall transfer and authored active inquiry are separate experiments. Image registration is display geometry, not measured gaze.

## StateSpaceBlock
A[3,3,type=float]
B[3,3,1,type=float]
C[3,type=float]
D[3,type=float]
s[3,type=float]
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
A=[[0.7,0.5,0.2],[0.2,0.3,0.3],[0.1,0.2,0.5]]
B=[[[1.0],[0.0],[0.0]],[[0.0],[1.0],[0.0]],[[0.0],[0.0],[1.0]]]
C=[2.0,0.0,-2.0]
D=[0.3333333333333333,0.3333333333333333,0.3333333333333333]
settings=[{"family":"gaze","backend":"pymdp","consumer":"thanks_for_nothing.gaze:build_gaze_audit","parameters":{"seed":91073,"source_seed":42,"source_steps":1000,"source_runs":5,"transfer_steps":128,"transfer_ambiguity_weight":0.5,"transfer_precision":1.5,"trajectory_steps":20,"example_strata":[0.3,0.7],"replicates":512,"steps":48,"bootstrap_draws":4095,"joint":{"seed":91074,"draws":16383,"confidence":0.95,"monte_carlo_confidence":0.99,"calibration_experiments":4096,"calibration_units":64,"calibration_draws":1023},"action_precision":4,"information_weight":4,"saccade_cost":0.2,"structural_model":"emptiness_practice","initial_location":10,"coordinates":[[0.14285714285714285,0.8571428571428571],[0.2857142857142857,0.8571428571428571],[0.14285714285714285,0.7142857142857143],[0.2857142857142857,0.7142857142857143],[0.21428571428571427,0.8571428571428571],[0.7142857142857143,0.14285714285714285],[0.8571428571428571,0.14285714285714285],[0.7142857142857143,0.2857142857142857],[0.8571428571428571,0.2857142857142857],[0.7857142857142857,0.21428571428571427],[0.2857142857142857,0.2857142857142857],[0.14285714285714285,0.42857142857142855],[0.2857142857142857,0.21428571428571427]],"regions":[0,0,0,0,0,1,1,1,1,1,2,2,2],"channels":[[[0.7,0.5,0.2],[0.2,0.3,0.3],[0.1,0.2,0.5]],[[0.1,0.2,0.5],[0.2,0.3,0.3],[0.7,0.5,0.2]],[[0.3333333333333333,0.3333333333333333,0.9],[0.3333333333333333,0.3333333333333333,0.05],[0.3333333333333333,0.3333333333333333,0.05]]],"contexts":[{"name":"stationary","candidates":[0,0,0]},{"name":"reversal","candidates":[0,2,0]}],"conditions":["pragmatic_restricted","pragmatic_open","inquiry_open","inquiry_restricted","sham","uniform_open"],"example_window":1,"transfer_state_map":[[1,1,1,1,1,0,0,0,0,0,0.5,0.5,0.5],[0,0,0,0,0,1,1,1,1,1,0.5,0.5,0.5]],"transfer_comparisons":[["positive_recall","no_recall"],["matched_random_recall","no_recall"],["absence_appreciation","no_recall"],["positive_recall","matched_random_recall"]],"comparisons":[["pragmatic_open","pragmatic_restricted"],["inquiry_open","pragmatic_restricted"],["inquiry_restricted","pragmatic_restricted"],["sham","pragmatic_restricted"],["uniform_open","pragmatic_restricted"],["inquiry_open","pragmatic_open"],["inquiry_open","uniform_open"]]},"claim_boundary":"Finite software model; not empirical evidence. Synthetic sampled locations and exact scene risk, not human eye tracking, gratitude efficacy or realization"}]

