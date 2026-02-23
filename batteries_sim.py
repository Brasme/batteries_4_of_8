import argparse
import itertools
import json
import statistics
from pathlib import Path
import matplotlib.pyplot as plt


# Default known prefix (prepended to the pair-test order if no other prefix provided)
KNOWN_PREFIX = [] # [(6, 7), (0, 1), (3, 4), (0, 2), (1, 2), (3, 5), (4, 5)]


def all_placements(n=8, k=4):
    return list(itertools.combinations(range(n), k))


def make_default_sequence(n=8, prefix=None):
    """Return all unordered pairs (i<j) with an optional prefix prepended.

    Prefix items are validated (must be in canonical order and unique).
    """
    all_pairs = list(itertools.combinations(range(n), 2))
    prefix = prefix or []
    seen = set()
    prefix_filtered = []
    for p in prefix:
        tup = tuple(p)
        if tup in all_pairs and tup not in seen:
            prefix_filtered.append(tup)
            seen.add(tup)
    remaining = [p for p in all_pairs if p not in seen]
    return prefix_filtered + remaining


def simulate_sequence(pairs, placements):
    """Simulate the provided ordered list of pairs against all placements.

    Returns a dict mapping placement->dict of {2:tests,3:tests,4:tests} (tests is int or None).
    """
    results = {}
    for placement in placements:
        confirmed = set()
        needed = {2: None, 3: None, 4: None}
        for t, pair in enumerate(pairs, start=1):
            a, b = pair
            # test True only if both batteries are good
            if a in placement and b in placement:
                confirmed.add(a)
                confirmed.add(b)
            for k in (2, 3, 4):
                if needed[k] is None and len(confirmed) >= k:
                    needed[k] = t
            if all(v is not None for v in needed.values()):
                break
        results[placement] = needed
    return results


def summarize(results):
    summary = {}
    for k in (2, 3, 4):
        vals = [v[k] for v in results.values()]
        found = [x for x in vals if x is not None]
        missing = len(vals) - len(found)
        summary[k] = {
            'mean': statistics.mean(found) if found else None,
            'median': statistics.median(found) if found else None,
            'min': min(found) if found else None,
            'max': max(found) if found else None,
            'not_found_count': missing,
        }
    return summary


def print_summary(summary):
    for k in (2, 3, 4):
        s = summary[k]
        print(f"Find {k} goods: mean={s['mean']}, median={s['median']}, min={s['min']}, max={s['max']}, not_found={s['not_found_count']}")


def validate_prefix(prefix, n=8):
    """Validate a prefix: pairs are two distinct ints in range and no duplicates (order-insensitive)."""
    if not prefix:
        return
    normalized = []
    for p in prefix:
        if not (isinstance(p, (list, tuple)) and len(p) == 2):
            raise ValueError(f"Invalid pair {p}: must be a 2-element list/tuple")
        a, b = p
        if not (isinstance(a, int) and isinstance(b, int)):
            raise ValueError(f"Invalid pair {p}: elements must be integers")
        if not (0 <= a < n and 0 <= b < n):
            raise ValueError(f"Invalid pair {p}: indices must be in range 0..{n-1}")
        if a == b:
            raise ValueError(f"Invalid pair {p}: elements must be distinct")
        normalized.append(tuple(sorted((a, b))))
    # check duplicates ignoring order
    seen = set()
    duplicates = []
    for p in normalized:
        if p in seen:
            duplicates.append(p)
        else:
            seen.add(p)
    if duplicates:
        raise ValueError(f"Duplicate pairs in prefix (order-insensitive): {duplicates}")


def plot_per_placement_histograms(results, out_prefix):
    # results: mapping string(placement)->dict with integer keys 2,3,4
    for k in (2, 3, 4):
        counts = {}
        for v in results.values():
            # v might have string keys if loaded from JSON
            val = v.get(str(k)) if str(k) in v else v.get(k)
            if val is None:
                key = 'not_found'
            else:
                key = str(val)
            counts[key] = counts.get(key, 0) + 1

        numeric_keys = sorted([int(x) for x in counts.keys() if x != 'not_found'])
        labels = [str(x) for x in numeric_keys]
        heights = [counts[str(x)] for x in numeric_keys]
        if 'not_found' in counts:
            labels.append('not_found')
            heights.append(counts['not_found'])

        x = list(range(len(labels)))
        plt.figure(figsize=(10, 4))
        plt.bar(x, heights, color='C1')
        plt.xticks(x, labels, rotation=45)
        plt.xlabel('Tests to reach {} goods (or not_found)'.format(k))
        plt.ylabel('Count of placements')
        plt.title('Distribution of tests needed to find {} goods'.format(k))
        plt.tight_layout()
        out_path = f"{out_prefix}_find{k}.png"
        plt.savefig(out_path)
        plt.close()


def load_sequences(filepath):
    p = Path(filepath)
    if not p.exists():
        return {}
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    out = {}
    for name, pairs in data.items():
        out[name] = [tuple(p) for p in pairs]
    return out


def save_sequence(name, pairs, filepath):
    p = Path(filepath)
    data = {}
    if p.exists():
        data = json.loads(p.read_text(encoding='utf-8'))
    data[name] = [list(t) for t in pairs]
    p.write_text(json.dumps(data, indent=2), encoding='utf-8')


def parse_pairs_arg(s):
    # expect a JSON array of 2-element arrays, e.g. [[6,7],[0,1]]
    if not s:
        return []
    try:
        arr = json.loads(s)
        return [tuple(p) for p in arr]
    except Exception:
        raise argparse.ArgumentTypeError('pairs must be a JSON array like [[6,7],[0,1]]')


def main():
    parser = argparse.ArgumentParser(description='Simulate pair-tests on 8 batteries (4 good).')
    parser.add_argument('--sequences-file', default='sequences.json', help='JSON file storing named sequences')
    parser.add_argument('--list', action='store_true', help='List named sequences in the sequences file')
    parser.add_argument('--save-name', help='Save provided pairs under NAME in sequences file')
    parser.add_argument('--use-name', help='Use named sequence (as prefix) from sequences file')
    parser.add_argument('--pairs', type=parse_pairs_arg, help='Ad-hoc prefix pairs as JSON list, e.g. "[[6,7],[0,1]]"')
    parser.add_argument('--dump-per-placement', help='Write per-placement results to JSON file')
    parser.add_argument('--plot-dump', help='Read per-placement JSON and plot histograms')
    parser.add_argument('--plot-out', default='plot', help='Output filename prefix for plots produced from --plot-dump')
    args = parser.parse_args()

    placements = all_placements(8, 4)

    sequences = load_sequences(args.sequences_file)
    if args.list:
        if sequences:
            print('Named sequences in', args.sequences_file)
            for name, pairs in sequences.items():
                print(f"- {name}: {pairs}")
        else:
            print('No named sequences in', args.sequences_file)
        return

    # determine prefix preference
    if args.pairs:
        prefix = args.pairs
    elif args.use_name:
        if args.use_name not in sequences:
            print(f"Named sequence '{args.use_name}' not found in {args.sequences_file}")
            return
        prefix = sequences[args.use_name]
    else:
        prefix = KNOWN_PREFIX

    # validate prefix for duplicates and valid indices
    try:
        validate_prefix(prefix, n=8)
    except ValueError as e:
        print('Invalid prefix:', e)
        return

    if args.save_name:
        save_sequence(args.save_name, prefix, args.sequences_file)
        print(f"Saved sequence '{args.save_name}' to {args.sequences_file}")

    full_pairs = make_default_sequence(8, prefix=prefix)

    print(f"Total placements: {len(placements)}. Total possible pair-tests: {len(full_pairs)}")
    results = simulate_sequence(full_pairs, placements)
    summary = summarize(results)
    print("\nPair order results:")
    print_summary(summary)

    if args.dump_per_placement:
        out = {str(k): v for k, v in results.items()}
        Path(args.dump_per_placement).write_text(json.dumps(out, indent=2), encoding='utf-8')
        print(f"Wrote per-placement results to {args.dump_per_placement}")
    if args.plot_dump:
        p = Path(args.plot_dump)
        if not p.exists():
            print(f"Plot input file not found: {args.plot_dump}")
        else:
            data = json.loads(p.read_text(encoding='utf-8'))
            plot_per_placement_histograms(data, args.plot_out)
            print(f"Wrote per-placement histograms with prefix {args.plot_out}")


if __name__ == '__main__':
    main()
