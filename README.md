## Batteries 4-of-8 Pair-test Simulator

Purpose: simulate pairwise tests on 8 batteries where exactly 4 are good. A pair-test returns True only when both batteries in the pair are good.

**Files:**
- `batteries_sim.py`: simulation script that enumerates all 70 placements of 4 good batteries among 8 positions and evaluates an ordered sequence of pair-tests.
- `sequences.json`: optional file (created when you save sequences) that stores named prefixes (see format below).

**Quick start:**
Run the simulator with Python:

```bash
python batteries_sim.py
```

**CLI overview:**
- `--list` : list named sequences in `sequences.json` (if present).
- `--pairs '[[a,b],[c,d]]'` : supply an ad-hoc prefix (JSON array) used as the start of the test order.
- `--use-name NAME` : use a saved named prefix from `sequences.json`.
- `--save-name NAME` : save the chosen prefix to `sequences.json` under `NAME`.
- `--sequences-file FILE` : use a different sequences file path.
- `--dump-per-placement FILE` : write per-placement results to `FILE` as JSON.

Examples:

- Run using the built-in known prefix (default):
	```bash
	python batteries_sim.py
	```
- Run with an ad-hoc prefix and save it as `myseq`:
	```bash
	python batteries_sim.py --pairs '[[6,7],[0,1]]' --save-name myseq
	```
- Run using a saved sequence:
	```bash
	python batteries_sim.py --use-name myseq
	```

**Sequences file format (`sequences.json`):**
JSON object mapping names to arrays-of-pairs. Example:

```json
{
	"known": [[6,7],[0,1],[3,4],[0,2],[1,2],[3,5],[4,5]]
}
```

**Validation rules (applied to any provided or saved prefix):**
- Each pair must be two distinct integers in the range `0..7`.
- Pairs are considered order-insensitive during validation — `[1,0]` is treated the same as `[0,1]`.
- Duplicate pairs (ignoring order) are rejected; the script will print an error and exit when duplicates are detected.

If you prefer automatic canonicalization (e.g. convert `[1,0]` to `[0,1]`) instead of rejection, the script can be updated to do that.

**Output summary:**
- The simulator reports, for all 70 placements, how many tests (in order) were required to first identify at least 2, 3 and 4 good batteries respectively.
- Summary statistics: mean, median, min, max, and count of placements not reaching the target (should be zero for valid full sequences).

**Extending / modifying:**
- Change the built-in prefix in `batteries_sim.py` by editing `KNOWN_PREFIX`.
- Use `--pairs` to test arbitrary prefixes without saving.

If you want, I can add an example `sequences.json` containing the built-in known prefix and include a short section showing expected sample output.
