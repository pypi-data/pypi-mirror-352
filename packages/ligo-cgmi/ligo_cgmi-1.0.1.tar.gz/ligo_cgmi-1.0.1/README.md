# ligo-cgmi

This package computes a source frame coarse-grained chirp mass estimate for gravitational-wave events. This is provided in the form of the probabilities that the chirp mass falls within a set of predetermined bins. In the case of Burst events, the estimate assumes a reshift of zero. There are two types of estimates:
- `LL (Low-Latency) based`: found using the template point estimate, and in the case of CBC events, using the distance information provided by the Bayestar skymap to shift to the source frame
- `PE (Parameter Estimation) based`: found using the source frame parameter estimation samples
