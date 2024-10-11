from datetime import date
from pathlib import Path

import pandas as pd

import sentier_data_tools as sdt

SCRIPT_DIR = Path(__file__).resolve().parent
PATH_TO_INPUT = SCRIPT_DIR / "inputs"

PATH_TO_EFFICIENCY = PATH_TO_INPUT / "mrf_equipment_efficiency copy.csv"
PATH_TO_MRF_OTHER = PATH_TO_INPUT / "mrf_other_inputs.csv"
PATH_TO_MRF_ELECTRICITY = PATH_TO_INPUT / "mrf_electricity.csv"
PATH_TO_PROJECTED_AMOUNTS = PATH_TO_INPUT / "projected_by_linear_model_to_2050"
PATH_TO_STATE_COUNTY = PATH_TO_INPUT / "State_County.csv"
PATH_TO_COUNTY_URI = PATH_TO_INPUT / "county_to_mrf" / "counties_uris.csv"
PATH_TO_COMBINE_WASTE_WITH_URI = (
    PATH_TO_INPUT / "others" / "combined_waste_data_with_uri.csv"
)


def create_mrf_datastorage(reset: bool = True):
    if reset:
        sdt.reset_local_database()

    metadata = sdt.Datapackage(
        name="data for a material recover facility (MRF) in the US context",
        description="model for the seperation of single-stream municipal solid waste, based on the 4P model by NREL",
        contributors=[
            {
                "title": "Team Trash",
                "path": "https://dds24-tt.readthedocs.io/en/latest/",
                "role": "wrangler",
            },
        ],
        homepage="https://dds24-tt.readthedocs.io/en/latest/",
    ).metadata()
    metadata.pop("version")

    # data package for equipment efficiency
    df_eff = pd.read_csv(PATH_TO_EFFICIENCY)
    assert len(COLUMNS_EFF) == len(UNITS_EFF)
    assert len(COLUMNS_EFF) == len(df_eff.columns)
    assert len(MACHINES_EFF) == df_eff.shape[0]

    df_eff.loc[:, "equipment"] = MACHINES_EFF

    sdt.Dataset(
        name=f"material seperation efficiency data for a material recovery facility",
        dataframe=df_eff,
        product="https://vocab.sentier.dev/model-terms/generic/sorting",  # IRI of waste sorting with MRF
        columns=[{"iri": x, "unit": y} for x, y in zip(COLUMNS_EFF, UNITS_EFF)],
        metadata=metadata,
        location="https://www.geonames.org/6295630",
        version=1,
        valid_from=date(
            2002, 1, 1
        ),  # data was collected in 2012 but expected to have some longevity
        valid_to=date(2025, 1, 1),
    ).save()

    # data package for county waste streams
    df_county = pd.read_csv(PATH_TO_COMBINE_WASTE_WITH_URI)
    df_county.drop(
        labels=["County", "State", "State_County", "latitude (deg)", "longitude (deg)"],
        axis="columns",
        inplace=True,
    )
    assert len(COLUMNS_COUNTY) == len(UNITS_COUNTY)
    assert len(COLUMNS_COUNTY) == len(df_county.columns)

    ds = sdt.Dataset(
        name=f"county-level municipal solid waste, for single-stream collection, covering both observed and prospective data",
        dataframe=df_county,
        product="https://vocab.sentier.dev/model-terms/generic/sorting",  # IRI of waste sorting with MRF
        columns=[{"iri": x, "unit": y} for x, y in zip(COLUMNS_COUNTY, UNITS_COUNTY)],
        metadata=metadata,
        location="https://www.geonames.org/6295630",
        version=1,
        valid_from=date(2004, 1, 1),  # based on observations from 2000 census
        valid_to=date(2050, 1, 1),  # based on population projections
    )
    ds.save()
    return ds


COLUMNS_EFF = [
    "http://data.europa.eu/xsp/cn2024/847410000080",  # Sorting, screening, separating or washing machines
    "https://vocab.sentier.dev/model-terms/generic/sequence",  # sequence
    "http://data.europa.eu/xsp/cn2024/392010230080",  # Polyethylene film, of a thickness of 20 micrometres or more but not exceeding 40 micrometres, for the production of photoresist film used in the manufacture of semiconductors or printed circuits (under waste)
    "http://data.europa.eu/xsp/cn2024/470710000080",  # Unbleached kraft paper or paperboard or corrugated paper or paperboard (under waste)
    "http://data.europa.eu/xsp/cn2024/700100000080",  # Cullet and other waste and scrap of glass, excluding glass from cathode-ray tubes or other activated glass of heading 8549; glass in the mass
    "http://data.europa.eu/xsp/cn2024/470730000080",  # Paper or paperboard made mainly of mechanical pulp (for example, newspapers, journals and similar printed matter)
    "http://data.europa.eu/xsp/cn2024/391510100080",  # Having a specific gravity of less than 0,94 (for example, PE-LD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/391510200080",  # Having a specific gravity of 0,94 or more (for example, PE-HD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/720400000080",  # Ferrous waste and scrap; remelting scrap ingots of iron or steel
    "http://data.europa.eu/xsp/cn2024/760200110010",  # Waste (under: Aluminium waste and scrap)
    "http://data.europa.eu/ehl/cpa21/381131",  # Non-recyclable non-hazardous municipal waste; taxonomy can be accessed here: https://op.europa.eu/s/zXfR
]

UNITS_EFF = [
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

machine_prefix = "https://vocab.sentier.dev/products/material-recovery-facility"
MACHINES_EFF = [
    machine_prefix + "/vacuum",
    machine_prefix + "/disc_screen_1",
    machine_prefix + "/glass_breaker",
    machine_prefix + "/disc_screen_2",
    machine_prefix + "/NIR_PET",
    machine_prefix + "/NIR_HDPE",
    machine_prefix + "/magnet",
    machine_prefix + "/eddy",
]

COLUMNS_COUNTY = [
    "https://vocab.sentier.dev/units/unit/YR",  # year
    "https://www.geonames.org/ontology#A.ADM2",  # GeoURI
    "http://data.europa.eu/xsp/cn2024/391510100080",  # Having a specific gravity of less than 0,94 (for example, PE-LD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/470710000080",  # Unbleached kraft paper or paperboard or corrugated paper or paperboard (under waste)
    "http://data.europa.eu/ehl/cpa21/381131",  # Non-recyclable non-hazardous municipal waste; taxonomy can be accessed here: https://op.europa.eu/s/zXfR
    "http://data.europa.eu/xsp/cn2024/720400000080",  # Ferrous waste and scrap; remelting scrap ingots of iron or steel
    "http://data.europa.eu/xsp/cn2024/391510200080",  # Having a specific gravity of 0,94 or more (for example, PE-HD) (under: Waste, parings and scrap, of plastics > Of polymers of ethylene)
    "http://data.europa.eu/xsp/cn2024/700100000080",  # Cullet and other waste and scrap of glass, excluding glass from cathode-ray tubes or other activated glass of heading 8549; glass in the mass
    "http://data.europa.eu/xsp/cn2024/392010230080",  # Polyethylene film, of a thickness of 20 micrometres or more but not exceeding 40 micrometres, for the production of photoresist film used in the manufacture of semiconductors or printed circuits (under waste)
    "http://data.europa.eu/xsp/cn2024/470730000080",  # Paper or paperboard made mainly of mechanical pulp (for example, newspapers, journals and similar printed matter)
    "http://data.europa.eu/xsp/cn2024/760200110010",  # Waste (under: Aluminium waste and scrap)
]

UNITS_COUNTY = [
    "https://vocab.sentier.dev/units/unit/YR",
    "https://www.geonames.org/ontology#A.ADM2",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
    "https://vocab.sentier.dev/units/unit/KiloGM",
]

dp = create_mrf_datastorage()
print(dp.columns)
# print(dp.columns)