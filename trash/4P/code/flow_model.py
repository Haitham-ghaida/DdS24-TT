import pandas as pd
import numpy as np
import sys
import glob
import os
import shutil
import logging
import yaml
from datetime import date
from typing import Optional, List, Tuple, Dict
from icecream import ic

from sentier_data_tools import (
    DatasetKind,
    Demand,
    Flow,
    FlowIRI,
    GeonamesIRI,
    ModelTermIRI,
    ProductIRI,
    SentierModel,
    RunConfig,
    UnitIRI,
)


class PlasticSD(SentierModel):
    provides = [ProductIRI("http://example.com/ontology/WasteSorting")]
    aliases = {
        ProductIRI("http://data.europa.eu/xsp/cn2024/760200110010"): "aluminum",
        ProductIRI("http://data.europa.eu/xsp/cn2024/470710000080"): "cardboard",
        ProductIRI("http://data.europa.eu/xsp/cn2024/720400000080"): "iron",
        ProductIRI("http://data.europa.eu/xsp/cn2024/700100000080"): "glass",
        ProductIRI("http://data.europa.eu/xsp/cn2024/391510200080"): "hdpe",
        ProductIRI("http://data.europa.eu/xsp/cn2024/470730000080"): "paper",
        ProductIRI("http://data.europa.eu/xsp/cn2024/391510100080"): "pet",
        ProductIRI("http://data.europa.eu/xsp/cn2024/392010230080"): "film",
        ProductIRI("http://data.europa.eu/ehl/cpa21/381131"): "other",
    }

    def __init__(self, year: list[int] = 2020, verbose=0):
        # Create a dummy Demand object and RunConfig
        dummy_demand = Demand(
            product_iri=ProductIRI("http://example.com/ontology/WasteSorting"),
            unit_iri=UnitIRI("https://vocab.sentier.dev/units/unit/KiloGM"),
            amount=1.0,
            spatial_context=GeonamesIRI("http://sws.geonames.org/6252001/"),  # USA
            begin_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
        )
        run_config = RunConfig(num_samples=1000)

        super().__init__(demand=dummy_demand, run_config=run_config)

        self.verbose = verbose
        self.recycle_stream_material = [
            "aluminum",
            "cardboard",
            "iron",
            "glass",
            "hdpe",
            "paper",
            "pet",
            "film",
            "other",
        ]
        self.outputs = [
            "film_bale",
            "cardboard_bale",
            "glass_bale",
            "pet_bale",
            "hdpe_bale",
            "iron_bale",
            "aluminum_bale",
        ]
        self.unit_ops = [
            "vacuum",
            "disc_screen1",
            "glass_breaker",
            "disc_screen2",
            "nir_pet",
            "nir_hdpe",
            "magnet",
            "eddy",
        ]
        self.flow = {}
        self.year = year
        self.parameters = None
        self.mrf_equipment_efficiency = None
        self.reg_df_data = None
        self.county_uris = self.load_county_uris()

    def prepare(self) -> None:
        self.load_mrf_equipment_efficiency()
        self.load_region_data()
        self.clean_output_directory()


    def load_mrf_equipment_efficiency(self):
        parameters = pd.read_csv("./input/core_data_files/mrf_equipment_efficiency.csv")
        mrf_equipment_efficiency = parameters[
            ["year"]
            + [
                col
                for col in parameters.columns
                if any(op in col for op in self.unit_ops)
            ]
        ]
        mrf_equipment_efficiency = mrf_equipment_efficiency.melt(
            id_vars=["year"],
            var_name="year-source-targetmaterial",
            value_name="efficiency",
        )
        mrf_equipment_efficiency["year-source-targetmaterial"] = (
            mrf_equipment_efficiency["year"].astype(str)
            + " "
            + mrf_equipment_efficiency["year-source-targetmaterial"].astype(str)
        )
        mrf_equipment_efficiency = mrf_equipment_efficiency[
            ["year-source-targetmaterial", "efficiency"]
        ]
        self.mrf_equipment_efficiency = mrf_equipment_efficiency.set_index(
            "year-source-targetmaterial"
        )["efficiency"].to_dict()

        for y in self.year:
            for r in self.recycle_stream_material:
                for u in self.unit_ops:
                    key = f"{y} {u} {r}"
                    if key not in self.mrf_equipment_efficiency:
                        self.mrf_equipment_efficiency[key] = 0

        self.parameters = parameters.set_index("year")

    def load_region_data(self):
        self.reg_df_data = pd.read_csv("./input/core_data_files/State_County.csv")
        self.reg_df_data = self.reg_df_data.sample(20)

    def clean_output_directory(self):
        r = glob.glob("./output/*")
        for i in r:
            os.remove(i)

    def process_region(self, row):
        for mat in self.recycle_stream_material:
            data_df = pd.read_csv(
                f"./input/core_data_files/projected_by_linear_model_to_2050/{mat}projected_amounts_to_relog_grouped_2050.csv"
            )
            data_df = data_df[data_df["State_County"] == row["State_County"]]
            for y in self.year:
                if len(data_df) > 1:
                    logging.warning("Issue with dataframe size")
                else:
                    data_df = data_df.reset_index()
                self.flow[(y, mat, "consumer", "vacuum")] = float(
                    data_df.loc[0, str(float(y))]
                )

        reg_df = [row["State_County"]]
        return self.mrf_sorting(reg_df)

    def mrf_sorting(self, reg_df):
        for i in self.year:
            qc = self.parameters.loc[i, "quality_control_mrf"]
            self.general_unitops(i, "consumer", "vacuum", "disc_screen1", "film_bale")
            self.general_unitops(
                i, "vacuum", "disc_screen1", "glass_breaker", "cardboard_bale"
            )
            self.general_unitops(
                i, "disc_screen1", "glass_breaker", "disc_screen2", "glass_bale"
            )
            self.general_unitops(
                i, "glass_breaker", "disc_screen2", "nir_pet", "paper_bale"
            )
            self.general_unitops(i, "disc_screen2", "nir_pet", "nir_hdpe", "pet_bale")
            self.general_unitops(i, "nir_pet", "nir_hdpe", "magnet", "hdpe_bale")
            self.general_unitops(i, "nir_hdpe", "magnet", "eddy", "iron_bale")
            self.general_unitops(i, "magnet", "eddy", "exit", "aluminum_bale")

        return self.flow

    def general_unitops(self, i, source, unit_ops, destination, output):
        for m in self.recycle_stream_material:
            efficiency_key = f"{i} {unit_ops} {m}"
            efficiency = self.mrf_equipment_efficiency.get(efficiency_key, 0)

            input_flow = self.flow.get((i, m, source, unit_ops), 0)
            self.flow[(i, m, unit_ops, destination)] = input_flow * (1 - efficiency)
            self.flow[(i, m, unit_ops, output)] = input_flow * efficiency

    def calculate_energy_usage(self, row, flow_result):
        df_energy = pd.read_csv("./input/core_data_files/mrf_electricity.csv")
        df_other_inputs = pd.read_csv("./input/core_data_files/mrf_other_inputs.csv")

        ops_list = []
        value_list_elec = []
        for u in self.unit_ops:
            total = sum(flow_result[key] for key in flow_result if key[3] == u)
            ops_list.append(u)
            value_list_elec.append(total)

        total_mrf_flow = sum(
            flow_result[key] for key in flow_result if key[3] == "vacuum"
        )
        time = total_mrf_flow / df_other_inputs["MRF throughput t"][0]

        electricity_df = pd.DataFrame(
            {"ops_list": ops_list, "total_flow": value_list_elec, "time": time}
        )

        df_energy = df_energy.merge(
            electricity_df, left_on=["Equipment"], right_on=["ops_list"]
        )
        df_energy["electricity kwh"] = (
            df_energy["Rated motor capacity (kW)"]
            / df_energy["Fraction of equipment capacity utilized "]
            * df_energy["time"]
        )
        df_energy["diesel_l"] = df_other_inputs["Diesel L/t"][0] * total_mrf_flow
        df_energy["baling wire kg"] = (
            df_other_inputs["Baling Wire kg/t"][0] * total_mrf_flow
        )
        df_energy["region"] = row["State_County"]

        for column in [
            "Building, Hall, Steel Construction m2",
            "Building, Multi-Storey m3",
            "Polyethylene, High Density, Granulate kg",
            "Road, Company, Internal m2/year",
            "Steel, Chromium Steel 18/8, Hot Rolled kg",
            "Steel, Low-Alloyed, Hot Rolled kg",
        ]:
            df_energy[column] = df_other_inputs[column][0] * total_mrf_flow

        return df_energy

    def load_county_uris(self):
        county_uris_df = pd.read_csv("../counties_uris.csv")
        return {
            f"{row['adminName1']}_{row['toponymName'].replace(' County', '')}": row[
                "uri"
            ]
            for _, row in county_uris_df.iterrows()
        }

    def get_county_uri(self, state_county):
        uri = self.county_uris.get(state_county)
        if uri is None:
            logging.warning(f"No URI found for {state_county}")
            return f"http://example.com/county/{state_county}"
        return uri

    def run(self) -> Tuple[List[Demand], List[Flow]]:
        self.prepare()

        demands = []
        flows = []
        electricity_df_result = pd.DataFrame()
        bale_data = []

        for _, row in self.reg_df_data.iterrows():
            flow_result = self.process_region(row)
            df_energy = self.calculate_energy_usage(row, flow_result)
            electricity_df_result = pd.concat([electricity_df_result, df_energy])

            for o_bales in self.outputs:
                for key, value in flow_result.items():
                    if key[3] == o_bales:
                        bale_data.append(
                            {
                                "location": row["State_County"],
                                "year": key[0],
                                "bale": o_bales,
                                "material": key[1],
                                "value": value,
                            }
                        )

            # Generate Demand objects
            for material in self.recycle_stream_material:
                for year in self.year:
                    material_uri = next(
                        uri for uri, alias in self.aliases.items() if alias == material
                    )

                    # Sum up the flow values for all bale types for this material
                    flow_value = sum(
                        flow_result.get((year, material, unit_op, bale_type), 0)
                        for unit_op in self.unit_ops
                        for bale_type in self.outputs
                        if (year, material, unit_op, bale_type) in flow_result
                    )

                    county_uri = self.get_county_uri(row["State_County"])

                    demand = Demand(
                        product_iri=material_uri,
                        unit_iri=UnitIRI("https://vocab.sentier.dev/units/unit/KiloGM"),
                        amount=flow_value,
                        spatial_context=GeonamesIRI(county_uri),
                        begin_date=date(year, 1, 1),
                        end_date=date(year, 12, 31),
                    )
                    demands.append(demand)

                    print(
                        f"Created Demand for {material} in {row['State_County']} with amount: {flow_value}"
                    )

        pd.DataFrame(bale_data).to_csv("./output/bale_output.csv", index=False)
        electricity_df_result.to_csv("./output/lci_output.csv", index=False)
        return demands, flows


if __name__ == "__main__":
    # Change working directory
    os.chdir(os.path.join(os.getcwd(), "trash", "4P"))
    print("Current working directory:", os.getcwd())

    # Create and run PlasticSD instance
    psd = PlasticSD(year = [2020], verbose=1)
    demands, flows = psd.run()

    # Process results
    print(f"Generated {len(demands)} demands and {len(flows)} flows")

    # Example: Print first demand and flow
    # if demands:
    #     print("First Demand:", demands[0])
    # if flows:
    #     print("First Flow:", flows[0])
    # ic(demands)
    # ic(demands)