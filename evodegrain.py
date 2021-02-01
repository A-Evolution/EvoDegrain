import vapoursynth as vs
import mvsfunc as mvf #https://github.com/HomeOfVapourSynthEvolution/mvsfunc
from vsutil import depth #https://github.com/Irrational-Encoding-Wizardry/vsutil

core = vs.core

def EvoDegrain(src: vs.VideoNode, tr: int = 2, thSAD: int = 300, blksize: int = None, overlap: int = None, pel: int = None, RefineMotion: bool = True, plane: int = 0, prefilter=None) -> vs.VideoNode:
    funcName = "EvoDegrain"
    if not isinstance(src, vs.VideoNode):
        raise TypeError(f'{funcName}: This is not a clip')

    if blksize is None:
        if src.width < 1280 or src.height < 720:
            blksize = 8
        elif src.width >= 3840 or src.height >= 2160:
            blksize = 32
        else:
            blksize = 16
    
    if overlap is None:
        overlap = blksize // 2
    
    if pel is None:
        if src.width < 1280 or src.height < 720:
            pel = 2
        else:
            pel = 1
    
    if prefilter == 1:
        pfclip = core.rgsf.RemoveGrain(src, 17)
    elif prefilter == 2:
        sigma = 6
        pfclip = core.fft3dfilter.FFT3DFilter(depth(src, 16), sigma=sigma*0.8, sigma2=sigma*0.6, sigma3=sigma*0.4, sigma4=sigma*0.2, bw=16, bh=16, ow=8, oh=8, bt=1, ncpu=1)
        pfclip = depth(pfclip, 32)
    elif prefilter == 3:
        pfclip = mvf.BM3D(src, sigma=[4,4,4], radius1=1, profile1="lc")
    elif prefilter == 4:
        pfclip = core.dfttest.DFTTest(src, sigma=8, tbsize=3, sbsize=24, sosize=18)
    else:
        pfclip = prefilter if prefilter is not None else src
    
    super = core.mvsf.Super(pfclip, pel=pel, sharp=2, rfilter=4)
    
    mvbw1 = core.mvsf.Analyse(super, isb=True, delta=1, overlap=overlap, blksize=blksize)
    mvfw1 = core.mvsf.Analyse(super, isb=False, delta=1, overlap=overlap, blksize=blksize)

    if tr == 2:
        mvbw2 = core.mvsf.Analyse(super, isb=True, delta=2, overlap=overlap, blksize=blksize)
        mvfw2 = core.mvsf.Analyse(super, isb=False, delta=2, overlap=overlap, blksize=blksize)
    if tr >= 3:
        mvbw3 = core.mvsf.Analyse(super, isb=True, delta=3, overlap=overlap, blksize=blksize)
        mvfw3 = core.mvsf.Analyse(super, isb=False, delta=3, overlap=overlap, blksize=blksize)
    
    if RefineMotion:
        halflap = overlap // 2
        halfsize = blksize // 2
        halfsad = thSAD // 2

        prefilt = core.rgsf.RemoveGrain(src, 4)
        super_r = core.mvsf.Super(clip=prefilt, pel=pel, sharp=2, rfilter=4)

        mvbw1 = core.mvsf.Recalculate(super_r, mvbw1, overlap=halflap, blksize=halfsize, thsad=halfsad)
        mvfw1 = core.mvsf.Recalculate(super_r, mvfw1, overlap=halflap, blksize=halfsize, thsad=halfsad)

        if tr == 2:
            mvbw2 = core.mvsf.Recalculate(super_r, mvbw2, overlap=halflap, blksize=halfsize, thsad=halfsad)
            mvfw2 = core.mvsf.Recalculate(super_r, mvfw2, overlap=halflap, blksize=halfsize, thsad=halfsad)
        if tr >= 3:
            mvbw3 = core.mvsf.Recalculate(super_r, mvbw3, overlap=halflap, blksize=halfsize, thsad=halfsad)
            mvfw3 = core.mvsf.Recalculate(super_r, mvfw3, overlap=halflap, blksize=halfsize, thsad=halfsad)

        if tr == 1:
            filtered = core.mvsf.Degrain1(src, super=super, mvbw=mvbw1, mvfw=mvfw1, thsad=thSAD, plane=plane)
        elif tr == 2:
            filtered = core.mvsf.Degrain2(src, super=super, mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2, mvfw2=mvfw2, thsad=thSAD, plane=plane)
        elif tr >= 3:
            filtered = core.mvsf.Degrain3(src, super=super, mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2, mvfw2=mvfw2, mvbw3=mvbw3, mvfw3=mvfw3, thsad=thSAD, plane=plane)
        
        return filtered
