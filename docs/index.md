# MRF

This is a `Sentier` model of an _material recover facility_ (MRF) in the US context. These facilities receive mixed municipal solid waste and through different means separate recyclables. The composition of the recyclables depends on the composition of the waste stream coming in. We have different waste compositions per county in US. As part of the model. 

The model is a subset of the [CELAVI](https://github.com/NREL/celavi) model by NREL

```{mermaid}
flowchart TD
	MSW-->Vacuum
	Vacuum--> disc_screen_1[disc screen 1]
	Vacuum--film bale--> film_recycling[[film recycling]]
	disc_screen_1--cardboard bale-->cardboard_recycling[[cardboard recycling]]
    disc_screen_1-->glass_br[glass breaker]
    glass_br--glass bale-->glass_rc[[glass recycling]]
    glass_br-->disc_screen_2[disc screen 2]
    disc_screen_2-->nir_pet[NIR PET]
    nir_pet-->nir_hdpe[NIR HDPE]
    nir_pet--PET bale-->pet_rec[[PET recycling]]
    nir_hdpe-->magnet
    nir_hdpe--HDPE bale-->hdpe_rec[[HDPE recycling]]
    magnet--iron bale-->iron_recycling[[iron recycling]]
    magnet-->Eddy
    Eddy--aluminium-->al_recycling[[aluminium recycling]]
    Eddy-->Landfill
```

```{button-link} https://docs.brightway.dev
:color: info
:expand:
{octicon}`light-bulb;1em` tt is a specialized package of the Brightway Software Framework
```

```{toctree}
---
hidden:
maxdepth: 1
---
self
content/usage
content/api/index
content/codeofconduct
content/contributing
content/license
content/changelog
```
