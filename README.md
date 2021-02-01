# EvoDegrain
Simple MDegrain Wrapper, but it supports float input.

# How to use it?
> import evodegrain as ed
>
> degrain = ed.EvoDegrain(src)

The parameters are set automatically, except thSAD.

# Prefilters:
> prefilter = None: source clip
>
> prefilter = 1: RemoveGrain
>
> prefilter = 2: FFT3DFilter
>
> prefilter = 3: mawen1250's BM3D wrapper
>
> prefilter = 4: DFTTest
>
> else: your prefilter clip
