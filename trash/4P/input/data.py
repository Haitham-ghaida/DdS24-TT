from datetime import date
from pathlib import Path

import pandas as pd

import sentier_data_tools as sdt

mrf_prefix = "https://vocab.example.org/mrf-equipment/"

def create_mrf_datastorage(reset: bool = True):
    if reset:
        sdt.reset_local_database()

    df = pd.read_csv(Path(__file__).parent / "mrf_equipment_efficiency.csv")
    assert len(COLUMNS) == len(UNITS)
    assert len(COLUMNS) == len(df.columns)

    metadata = sdt.Datapackage(
        name="data for a material recover facility (MRF) in the US context",
        description="model for the seperation of single-stream municipal solid waste, based on the 4P model by NREL",
        contributors=[], 
        # [
        #     {
        #         "title": "Karin Treyer",
        #         "path": "https://www.psi.ch/en/ta/people/karin-treyer",
        #         "role": "author",
        #     },
        #     {
        #         "title": "Chris Mutel",
        #         "path": "https://chris.mutel.org/",
        #         "role": "wrangler",
        #     },
        # ],
        homepage= "https://dds24-tt.readthedocs.io/en/latest/",
    ).metadata()
    metadata.pop("version")

    sdt.Dataset(
        name=f"material seperation efficiency data for a material recovery facility",
        dataframe=df,
        product="X", # IRI of waste sorting with MRF
        columns=[{"iri": x, "unit": y} for x, y in zip(COLUMNS, UNITS)],
        metadata=metadata,
        location="https://sws.geonames.org/6255148/",
        version=1,
        valid_from=date(2018, 1, 1),
        valid_to=date(2028, 1, 1),
    ).save()

COLUMNS = [
    "http://data.europa.eu/xsp/cn2024/847410000080", # Sorting, screening, separating or washing machines
    "https://vocab.sentier.dev/model-terms/generic/sequence", # sequence
    "http://data.europa.eu/xsp/cn2024/392010230080", # Polyethylene film, of a thickness of 20 micrometres or more but not exceeding 40 micrometres, for the production of photoresist film used in the manufacture of semiconductors or printed circuits (under waste)
    "http://data.europa.eu/xsp/cn2024/470710000080", # Unbleached kraft paper or paperboard or corrugated paper or paperboard (under waste)
    "http://data.europa.eu/xsp/cn2024/700100000080", # Cullet and other waste and scrap of glass, excluding glass from cathode-ray tubes or other activated glass of heading 8549; glass in the mass
    "http://data.europa.eu/xsp/cn2024/470730000080", # Paper or paperboard made mainly of mechanical pulp (for example, newspapers, journals and similar printed matter)
    "http://data.europa.eu/xsp/cn2024/391510100080", # Having a specific gravity of less than 0,94 (for example, PE-LD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/391510200080", # Having a specific gravity of 0,94 or more (for example, PE-HD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/720400000080", # Ferrous waste and scrap; remelting scrap ingots of iron or steel
    "http://data.europa.eu/xsp/cn2024/760200110010", # Waste (under: Aluminium waste and scrap)
    "http://data.europa.eu/ehl/cpa21/381131", # Non-recyclable non-hazardous municipal waste; taxonomy can be accessed here: https://op.europa.eu/s/zXfR
]

UNITS = [
    "https://vocab.sentier.dev/units/unit/NUM",
    "https://vocab.sentier.dev/units/quantity-kind/Count",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/FRACTION",
]

MACHINES = [
    "",
]

create_mrf_datastorage()