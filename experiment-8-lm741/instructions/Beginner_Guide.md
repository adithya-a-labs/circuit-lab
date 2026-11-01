# Experiment 8: LM741 macromodel reproduction guide

This revision uses National Semiconductor LM741/NS, not the earlier EDU741 substitute. The original model, copyright/distribution notice and pinned source are in models/. Two first-order POLY sources are translated algebraically into B sources for ngspice compatibility; no device coefficients are changed. See the complete report for pin order, validation and limitations.

There are 13 final transients: 12 successful circuit-behavior trials and one failed original-value bistable trial. The main waveform PDF includes the 12 passing trials. The separate Bistable_Baseline_Failure.pdf shows why 100 ohm / 0.1 uF fails with the stated trigger. Bistable trial 4 varies C to 0.22 uF to obtain the third successful configuration. Do not hide the baseline failure or call its positive voltage dip a LOW state.

Monostable trigger falling edge is 50 us, return edge 1 us, negative plateau 100 us, 50 Hz externally applied. The earlier 0.2 us edges did not trigger this slower device. Topology and handout Rd/Cd remain unchanged. Wien initialization uses a consistent operating point with plus=50 mV, then releases that constraint; no UIC for Wien. Final integration is Gear. Frequency/pulse timing comes from completed actual transient data.

## 1. Open a terminal and the existing checkout
A terminal accepts commands typed after its prompt. Copy one block at a time. Do not type the triple backticks.

```bash
cd /workspace/circuit-lab
pwd
git status --short
```

The checkout is already present; do not clone, pull, reset or create a worktree. Generated work is in `/workspace/circuit-outputs/experiment-8-lm741`, outside the checkout.

## 2. Start tools in EVERY new terminal

```bash
source /workspace/circuit-tools/startup.sh
```

`source` runs the saved script inside your current shell, preserving its PATH settings. A successful run prints ngspice and Python checks. Do not run install.sh or pip/apt: the required environment already exists. `/tmp/circuit-env` points to the retained `/workspace/circuit-tools/python-env`. If startup fails, stop and save the exact error rather than installing anything.

For a single new shell, use:

```bash
bash -lc 'source /workspace/circuit-tools/startup.sh && /tmp/circuit-env/bin/python /workspace/circuit-outputs/experiment-8-lm741/scripts/run.py --only astable_01'
```

## 3. Locate the project files

```bash
cd /workspace/circuit-outputs/experiment-8-lm741
ls
```

- `source/`: original laboratory PDF, reference report, supplied ASC files and page images.
- `models/LM741_ngspice.lib`: LM741 macromodel, pin-order comments and assumptions.
- `trials.json`: simple component-value list.
- `circuits/`: generated `.cir` netlists, one per trial.
- `simulation_data/`: text columns of actual simulation samples and logs.
- `calculations/observations.csv`: spreadsheet-friendly measured results; JSON retains detailed fields.
- `waveforms/`: 13 PNG sheets (12 passing and one diagnostic).
- `reports/`: full PDF, editable DOCX/Markdown and waveform PDF.

Downloaded ZIP users should extract the entire package. To rerun in this cloud workspace, retain the folder above. Python scripts determine their base folder from their own location; run.py regenerates absolute include/output paths for the current location. The guide's explicit commands assume the LM741 revision cloud paths. A different computer needs a separately provisioned ngspice/Python environment; this guide does not install one.

## 4. Run one circuit
After sourcing startup in the same terminal:

```bash
ngspice -b circuits/astable/astable_01.cir > simulation_data/astable_01.manual.log 2>&1
cat simulation_data/astable_01.manual.log
```

`-b` means batch mode: no graphical simulator window is required. `.control` in the circuit runs transient analysis and writes the numerical data file. The warning about missing `spinit` is known; the self-contained netlists still run. Fatal errors, missing data, or "timestep too small" are failures, not success.

The safer generator command regenerates the netlist before running it:

```bash
/tmp/circuit-env/bin/python scripts/run.py --only astable_01
```

Available names: wien_01..03, astable_01..03, monostable_01..03, bistable_01..04. Use the full name, not the two dots.

## 5. Change a resistor or capacitor without editing Python
Make a backup and open the simple configuration file:

```bash
cp trials.json trials.backup.json
nano trials.json
```

If `nano` is unavailable, use the workspace text editor to open trials.json. Each pair is `[resistance_in_ohms, capacitance_in_farads]`. For example `[10000, 1e-7]` means 10 kohm and 0.1 uF. The Wien pair applies to BOTH equal resistors and BOTH equal capacitors. Other circuits vary timing/coupling R and C only. Fixed resistors, Rd and Cd remain as documented. Keep three pairs in Wien/astable/monostable and four in bistable to retain 13 trials. Preserve valid JSON commas and brackets. Do not change the `.asc` files expecting ngspice to use them.

Rerun the affected trial and then regenerate measurements/plots:

```bash
/tmp/circuit-env/bin/python scripts/run.py --only astable_01
/tmp/circuit-env/bin/python scripts/analyze.py
python3 scripts/report.py
```

For all trials:

```bash
/tmp/circuit-env/bin/python scripts/run.py
/tmp/circuit-env/bin/python scripts/analyze.py
python3 scripts/report.py
```

`python3` in the last line is the existing system Python with ReportLab and python-docx, while `/tmp/circuit-env/bin/python` supplies the verified numerical libraries. Do not install a document dependency into the working environment. An assertion failure means the changed values did not satisfy measurement requirements; do not copy old results as new ones. Startup length and trigger spacing may need engineering review for large changes. run.py rewrites generated netlists, so persistent component edits belong in trials.json.

## 6. Read or check numerical results

```bash
head -5 simulation_data/astable_01.txt
cat calculations/observations.json
```

The first column is time in seconds. The second is output voltage. In periodic circuits the third is the bridge/timing node. In monostable/bistable files columns 3, 4, 5 are trigger, inverting and noninverting voltages. The header identifies them.

At an output transition between `(t1,V1)` and `(t2,V2)`, the 0 V crossing is `t1 - V1*(t2-t1)/(V2-V1)`. Rising-to-rising gives period T; `f=1/T`. Rising-to-next-falling gives Ton; `Toff=T-Ton`; duty=`100*Ton/T`. Monostable LOW width is falling-to-next-rising; trigger is 50 Hz separately. Bistable period/frequency/duty are N/A. analyze.py averages multiple settled cycles/pulses automatically, checks enough events and reports the exact windows. Never replace the raw data with a generated sine/square array.

## 7. Generate the final PDF and editable document

```bash
/tmp/circuit-env/bin/python scripts/analyze.py
python3 scripts/report.py
ls -lh reports
```

The first command generates all 13 PNGs and the printout PDF. The second creates the full PDF, DOCX and Markdown. Run these after simulations, not instead of simulations. Model changes require rerunning every trial and revisiting the theory/assumptions before printing.

## 8. Print for the fair record
Open `reports/Experiment_8_Waveform_Printouts.pdf` from the workspace or a locally retrieved copy. Print A4, grayscale, actual size (100%), one PDF page per sheet. Sheets 1-3: Figure 1 Wien; 4-6: Figure 2 astable; 7-9: Figure 3 monostable; 10-12: Figure 4 bistable trials 2-4. Cut/paste as your professor directs, preserving circuit/trial/component labels, axes, measured captions and LM741 model/source label. Add handwritten observations in the blank space. No color printer is required.

## 9. Write the rough record
Copy from the complete report: experiment number/title; aim; apparatus; theory; original Figures 1-4 (appendix); fixed/modified component values; design equations and numerical substitutions; procedure; the four observation tables; measured results and percentage comparisons; discussion and conclusion. Include supply voltages, trigger conditions and the macromodel limitations. The professor's handout calls for monostable frequency, but the correct distinction is external trigger rate versus pulse width; state this explicitly. Do not invent bistable frequency.

## 10. Final checklist
- [ ] Three genuine waveform sheets per circuit, with correct R/C labels.
- [ ] All source models, netlists, logs and numeric data retained.
- [ ] No graphs copied from the theoretical reference report.
- [ ] Units and substitutions copied accurately.
- [ ] LM741 source/compatibility note and baseline bistable failure retained.
- [ ] Fair record has waveform printouts; rough record has full written calculations.
- [ ] No repository files committed or pushed.

```bash
git -C /workspace/circuit-lab status --short
```

The original checkout should remain clean.

## Optional numerical validation
After sourcing startup in the same shell:

```bash
/tmp/circuit-env/bin/python scripts/validate_model.py
/tmp/circuit-env/bin/python scripts/refine.py
python3 scripts/qc.py
```

Refinement reruns one passing trial per circuit at half maximum timestep. QC requires all 13 final completed transients and expects the documented bistable baseline failure. It does not turn that failure into a pass. Reproduce the full set with run.py and analyze.py before QC. Do not run the historical native loader in exploration/: it crashed this retained ngspice build.
