# ChemFH chemical frequent hitter detection

ChemFH is an integrated model for the detection of frequent hitters in chemical screening across various parameters, including colloidal aggregates, firefly luciferase reporter enzyme inhibition, fluorescence, chemical reactivity, and promiscuity, as well as classical PAINS alerts and others. ChemFH contains ChemProp models as well as rule-based filters based on liable substructures.

This model was incorporated on 2025-08-23.


## Information
### Identifiers
- **Ersilia Identifier:** `eos7ye0`
- **Slug:** `chemfh`

### Domain
- **Task:** `Annotation`
- **Subtask:** `Property calculation or prediction`
- **Biomedical Area:** `Any`
- **Target Organism:** `Any`
- **Tags:** `Frequent hitter`

### Input
- **Input:** `Compound`
- **Input Dimension:** `1`

### Output
- **Output Dimension:** `17`
- **Output Consistency:** `Fixed`
- **Interpretation:** Probability scores range from 0 to 1, with higher values indicating a greater likelihood of being a frequent hitter. A threshold of 0.5 is commonly used to classify compounds as frequent hitters (scores >= 0.5) or non-frequent hitters (scores < 0.5).

Below are the **Output Columns** of the model:
| Name | Type | Direction | Description |
|------|------|-----------|-------------|
| colloidal_aggregator | float | high | Probability score of being aggregators |
| fluc_inhibitor | float | high | Probability score of being a Firefly luciferase (FLuc) inhibitor |
| blue_fluorescence | float | high | Probability score of being flue fluorescent |
| green_fluorescence | float | high | Probability score of being green fluorescent |
| reactive | float | high | Probability score of being a reactive compound |
| promiscuous | float | high | Probability score of being a promiscuous compound |
| other_assay_interference | float | high | Probability score of causing an assay intererence |
| alarm_nmr_rule | integer | high | Thiol reactive compounds based on 75 substructures |
| bms_rule | integer | high | Undesirable reactive compounds based on 176 substructures |
| chelator_rule | integer | high | Chelators based on 55 substructures |

_10 of 17 columns are shown_
### Source and Deployment
- **Source:** `Local`
- **Source Type:** `External`
- **S3 Storage**: [https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos7ye0.zip](https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos7ye0.zip)

### Resource Consumption
- **Model Size (Mb):** `298`
- **Environment Size (Mb):** `6699`


### References
- **Source Code**: [https://github.com/antwiser/ChemFH](https://github.com/antwiser/ChemFH)
- **Publication**: [https://academic.oup.com/nar/article/52/W1/W439/7680615](https://academic.oup.com/nar/article/52/W1/W439/7680615)
- **Publication Type:** `Peer reviewed`
- **Publication Year:** `2025`
- **Ersilia Contributor:** [miquelduranfrigola](https://github.com/miquelduranfrigola)

### License
This package is licensed under a [GPL-3.0](https://github.com/ersilia-os/ersilia/blob/master/LICENSE) license. The model contained within this package is licensed under a [MIT](LICENSE) license.

**Notice**: Ersilia grants access to models _as is_, directly from the original authors, please refer to the original code repository and/or publication if you use the model in your research.


## Use
To use this model locally, you need to have the [Ersilia CLI](https://github.com/ersilia-os/ersilia) installed.
The model can be **fetched** using the following command:
```bash
# fetch model from the Ersilia Model Hub
ersilia fetch eos7ye0
```
Then, you can **serve**, **run** and **close** the model as follows:
```bash
# serve the model
ersilia serve eos7ye0
# generate an example file
ersilia example -n 3 -f my_input.csv
# run the model
ersilia run -i my_input.csv -o my_output.csv
# close the model
ersilia close
```

## About Ersilia
The [Ersilia Open Source Initiative](https://ersilia.io) is a tech non-profit organization fueling sustainable research in the Global South.
Please [cite](https://github.com/ersilia-os/ersilia/blob/master/CITATION.cff) the Ersilia Model Hub if you've found this model to be useful. Always [let us know](https://github.com/ersilia-os/ersilia/issues) if you experience any issues while trying to run it.
If you want to contribute to our mission, consider [donating](https://www.ersilia.io/donate) to Ersilia!
