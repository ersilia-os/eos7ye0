"""Ersilia: make ChemFH's Monte Carlo dropout reproducible.

The authors predict with Chemprop's ``--uncertainty_method dropout``: 10 passes
with dropout on (p=0.1), returning the mean. The passes are unseeded, so outputs
change from run to run. This patch keeps that method but draws the dropout masks
of each molecule from a fixed seed (base seed + pass number), one molecule at a
time, so a molecule's output depends only on the molecule, not on the run or on
the other molecules in the input.
"""
import torch
import chemprop.uncertainty.uncertainty_predictor as up
from chemprop.data import MoleculeDataset, MoleculeDataLoader
from chemprop.train.predict import predict as _predict

BASE_SEED = 0
_pass = {"n": 0}


def _seeded_predict(model, data_loader, scaler=None, atom_bond_scaler=None,
                    return_unc_parameters=False, dropout_prob=0.0, **kwargs):
    if dropout_prob <= 0.0:
        return _predict(model=model, data_loader=data_loader, scaler=scaler,
                        atom_bond_scaler=atom_bond_scaler,
                        return_unc_parameters=return_unc_parameters,
                        dropout_prob=dropout_prob, **kwargs)
    seed = BASE_SEED + _pass["n"]
    _pass["n"] += 1
    preds = []
    for datapoint in data_loader.dataset:
        loader = MoleculeDataLoader(dataset=MoleculeDataset([datapoint]),
                                    batch_size=1, num_workers=0)
        torch.manual_seed(seed)
        preds.extend(_predict(model=model, data_loader=loader, scaler=scaler,
                              atom_bond_scaler=atom_bond_scaler,
                              return_unc_parameters=return_unc_parameters,
                              dropout_prob=dropout_prob, **kwargs))
    return preds


def install():
    _pass["n"] = 0
    up.predict = _seeded_predict
