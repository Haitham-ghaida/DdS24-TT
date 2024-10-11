import trash.mrf_model.flow_model as flowmodel

def test_run():

    psd = flowmodel.PlasticSD(year=[2020], verbose=1,sample_size=2)

    demands, flows = psd.run()