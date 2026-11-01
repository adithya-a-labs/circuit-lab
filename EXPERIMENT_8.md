# Experiment 8: Oscillator and Multivibrator Circuits

This package contains genuine ngspice simulations using the National Semiconductor LM741/NS macromodel, with documented source, copying permission and two algebraically equivalent compatibility translations.

**Results: 12 successful circuit-behavior trials out of 13 final transients.** Each circuit has three successful component configurations. The original 100 ohm / 0.1 uF bistable baseline fails to switch with the stated trigger; it is retained, with a separate diagnostic sheet. An additional 100 ohm / 0.22 uF trial demonstrates switching. These are macromodel results, not physical hardware measurements.

## Reports and printouts

- [Complete report (PDF)](experiment-8-lm741/reports/Experiment_8_Complete_Report.pdf)
- [Editable report (DOCX)](experiment-8-lm741/reports/Experiment_8_Complete_Report.docx)
- [Editable report (Markdown)](experiment-8-lm741/reports/Experiment_8_Complete_Report.md)
- [12 successful A4 waveform sheets](experiment-8-lm741/reports/Experiment_8_Waveform_Printouts.pdf)
- [Failed original bistable baseline](experiment-8-lm741/reports/Bistable_Baseline_Failure.pdf)
- [Beginner reproduction and record guide](experiment-8-lm741/instructions/Beginner_Guide.md)
- [Observation tables](experiment-8-lm741/calculations/observations.csv)
- [Model provenance](experiment-8-lm741/models/PROVENANCE.txt)
- [Quality-control evidence](experiment-8-lm741/QC.json)

## Contents and reproduction

`experiment-8-lm741/` includes all source documents, models, netlists, raw simulation data, waveform PNGs, scripts, calculations and historical failed attempts. The 86 MB standalone ZIP is not duplicated here; GitHub's **Code → Download ZIP** retrieves the repository contents.

The guide records the original cloud artifact paths. To rerun from this checkout in the already configured cloud environment:

```bash
source /workspace/circuit-tools/startup.sh
cd /workspace/circuit-lab/experiment-8-lm741
/tmp/circuit-env/bin/python scripts/run.py
/tmp/circuit-env/bin/python scripts/analyze.py
python3 scripts/report.py
```

The generator derives its root from its location and regenerates absolute include/output paths. The independent validation netlist and historical refinement netlists retain the original artifact paths; their validation evidence refers to the original run. `QC.json` records the clean repository status **before publication**, not the state while adding this package to Git.

The original model's copyright and distribution notice are retained. Copying/distribution is permitted by its notice; resale is prohibited. See the complete report for compatibility, convergence, startup and trigger details.
