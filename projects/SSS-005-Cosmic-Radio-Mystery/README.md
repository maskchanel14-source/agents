# SSS-005 — Fast Radio Bursts: The Cosmic Signal Mystery

## Scientific scope

Fast radio bursts are real radio transients, often lasting milliseconds; some repeat and others have only been seen once. A Galactic magnetar produced an FRB-like burst in 2020. The origin study for FRB 20221022A supports emission close to a neutron star's magnetosphere, but it does not establish a universal source or emission mechanism for every FRB. We do not present alien origin as evidence.

- Kenzie Nimmo et al., *Magnetospheric origin of a fast radio burst constrained using scintillation*, Nature 637, 48–51 (2025), DOI <https://doi.org/10.1038/s41586-024-08297-w>.
- MIT CHIME explainer <https://news.mit.edu/2025/astronomers-detect-all-time-brightest-fast-radio-burst-0821>.

## Visuals and rights

Ten labeled AI-generated stills with camera pans/zooms are artist impressions, not experimental recordings or full object-level 3D animations. They are source PNGs in `/home/user/sss005/visuals/`, outside Git. The scientific full-sky dispersion map is a simulation, clearly labeled as such: R. M. Konietzka, *Ray-tracing Fast Radio Bursts Through IllustrisTNG: Animation Showing the Evolution of Dispersion Measures on the Full Sky* (2026), <https://doi.org/10.5281/zenodo.21431049>, **CC BY 4.0** <https://creativecommons.org/licenses/by/4.0/>. It was excerpted and resized; related publication: R. M. Konietzka et al., *The Astrophysical Journal* 1010, 122, DOI <https://doi.org/10.3847/1538-4357/ae99e8>. The source video is available via <https://github.com/ralfkonietzka/fast-radio-bursts/tree/main/full-sky-tng>.

The edit has 11 distinct visual sources (10 illustrations and one scientific simulation), each used once to avoid repetition. This deviates from the 36-shot Cinema SOP; the stills have camera motion, not true 3D object animation. The 1376x768 images are downsampled into the 1036-pixel stage. Cover is AI art. Caption segmentation is approximate; final listening and caption review by the creator remain necessary.

## Reproduce

- Install `scripts/bootstrap_media_env.sh`; place the selected-voice b1.wav..b8.wav in `/home/user/sss005/audio/` (voice IDs are session-scoped).
- Place the ten illustration PNGs and the Konietzka simulation in the input paths stated by `make_visuals.py`; run it to create `.cache/library/footage/frb/`.
- Run `python3 projects/SSS-005-Cosmic-Radio-Mystery/build_audio.py`, which creates narration, original procedural music/SFX, captions, timings and master audio. The continuous score uses the corrected SSS-004 envelope and must still be auditioned.
- Run `python3 projects/SSS-005-Cosmic-Radio-Mystery/render_ultrahd.py`; it validates the 11 sources and outputs the vertical 1080x1920/60fps master to `/home/user/deliverables/SSS-005/`.
- `publishing-kit.txt` includes source and attribution, draft description and manually posted pinned comment.
