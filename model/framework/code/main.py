import os
import sys
import csv
import logging
import traceback

import pandas as pd


logger = logging.getLogger("chemfh")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


ROOT = os.path.dirname(os.path.abspath(__file__))
CHEMFH_DIR = os.path.join(ROOT, "ChemFH")
if CHEMFH_DIR not in sys.path:
    sys.path.insert(0, CHEMFH_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChemFH.settings")
try:
    import django
    django.setup()
    from django.conf import settings as dj_settings
    dj_settings.SITE_ROOT = CHEMFH_DIR
    os.chdir(CHEMFH_DIR)
    logger.info("django setup ok, SITE_ROOT=%s, cwd=%s", dj_settings.SITE_ROOT, os.getcwd())
except Exception:
    logger.error("django setup failed\n%s", traceback.format_exc())
    raise

from service.views import wash_input_mol


ALL_RULE = [
    "Aggregators",
    "Fluc",
    "Blue_fluorescence",
    "Green_fluorescence",
    "Reactive",
    "Other_assay_interference",
    "Promiscuous",
    "ALARM_NMR",
    "BMS",
    "Chelator_Rule",
    "GST_FHs_Rule",
    "His_FHs_Rule",
    "Luciferase_Inhibitor_Rule",
    "NTD",
    "PAINS",
    "Potential_Electrophilic_Rule",
    "Lilly",
]


def chemfh_infer(smiles_input):
    if isinstance(smiles_input, str):
        original_smiles = [smiles_input]
    else:
        original_smiles = list(smiles_input)

    smiles_list, invalidIdx = wash_input_mol(
        smiles_input,
        issmiles=True,
        invalidStr="invalid",
        returnInvalidIdx=True,
    )

    if True not in invalidIdx:
        raise RuntimeError("invalid molecule!")
    if len(smiles_list) > 5000:
        raise RuntimeError("Excessive number of requested molecules!")

    from static.media.chemprop.scripts.predict import predict
    import static.media.rule.filter_rule as fr

    result, unResult = predict(smiles_list)
    result = result.round(3)
    unResult = unResult.round(6)

    out1, out2, out3, out4 = fr.filter_rule(smiles_list, ALL_RULE)

    result = pd.concat([result, unResult, out4], axis=1)
    result = pd.concat([pd.DataFrame(smiles_list, columns=["smiles"]), result], axis=1)

    for idx, flag in enumerate(invalidIdx):
        if not flag:
            new_row = pd.DataFrame([{
                col: ("Invalid Molecule" if col != "smiles" else original_smiles[idx])
                for col in result.columns
            }])
            result = pd.concat([result.iloc[:idx], new_row, result.iloc[idx:]]).reset_index(drop=True)

    return result.to_dict(orient="records")


def main():
    if len(sys.argv) < 3:
        raise RuntimeError("usage: python main.py <input_csv> <output_csv>")

    input_file = os.path.abspath(sys.argv[1])
    output_file = os.path.abspath(sys.argv[2])

    logger.info("input=%s", input_file)
    logger.info("output=%s", output_file)

    if not os.path.exists(input_file):
        raise FileNotFoundError(input_file)

    with open(input_file, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        smiles_list = [r[0] for r in reader if r]

    logger.info("smiles loaded: %d", len(smiles_list))
    if not smiles_list:
        raise RuntimeError("no smiles found in input")

    data = []
    batch_size = 50

    for start in range(0, len(smiles_list), batch_size):
        batch = smiles_list[start:start + batch_size]
        logger.info("batch %d-%d (%d)", start, min(start + batch_size, len(smiles_list)), len(batch))
        batch_data = chemfh_infer(batch)
        logger.info("batch returned %d rows", len(batch_data))
        data.extend(batch_data)

    logger.info("total rows: %d", len(data))

    columns_0 = [
        "Colloidal aggregators",
        "FLuc inhibitors",
        "Blue fluorescence",
        "Green fluorescence",
        "Reactive compounds",
        "Promiscuous compounds",
        "Other assay interference",
    ]

    columns_1 = [
        "ALARM_NMR_index",
        "BMS_index",
        "Chelator_Rule_index",
        "GST_FHs_Rule_index",
        "His_FHs_Rule_index",
        "Luciferase_Inhibitor_Rule_index",
        "NTD_index",
        "PAINS_index",
        "Potential_Electrophilic_Rule_index",
        "Lilly_index",
    ]

    run_columns_file = os.path.abspath(os.path.join(ROOT, "..", "columns", "run_columns.csv"))
    logger.info("run_columns=%s", run_columns_file)

    if not os.path.exists(run_columns_file):
        raise FileNotFoundError(run_columns_file)

    header = []
    with open(run_columns_file, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if r:
                header.append(r[0])

    logger.info("header cols: %d", len(header))

    R = []
    for idx, d in enumerate(data):
        try:
            r = [d[c] for c in columns_0]
            for c in columns_1:
                r.append(len(d.get(c, [])))
            R.append(r)
        except Exception:
            logger.error("row build failed at idx=%d keys=%s\n%s", idx, list(d.keys()), traceback.format_exc())
            raise

    if len(smiles_list) != len(R):
        raise RuntimeError(f"length mismatch input={len(smiles_list)} output={len(R)}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(R)

    logger.info("done, wrote %d rows to %s", len(R), output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error("failed\n%s", traceback.format_exc())
        sys.exit(1)
