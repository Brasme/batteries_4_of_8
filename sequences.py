"""
Generate pair sequences by partitioning 8 battery indices into groups,
then creating pairs to cover those groups.

Example partitions: (3,3,2), (2,3,3), (2,2,4), etc.
Each group is covered by pairs that span or mix indices within/across groups.
"""

import itertools
from batteries_sim import all_placements, simulate_sequence, summarize


def generate_partition_based_sequences(n=8):
    """Generate sequences by partitioning indices and creating covering pairs.
    
    Yields different sequences based on various partition strategies.
    Each sequence always starts with (0, 1).
    """
    indices = list(range(n))
    
    # Define partition schemes: tuples of group sizes that sum to 8
    partitions = [
        (3, 3, 2),
        (2, 3, 3),
        (1, 2, 3, 2),
        (2, 3, 1, 2),
        (2, 1, 1, 2, 2),
        (2, 3, 1, 2),
        (2, 2, 4),
        (4, 2, 2),
        (2, 4, 2),
        (3, 2, 3),
        (4, 4)        
    ]
    
    for partition in partitions:
        # Generate all ways to partition 8 indices into groups of sizes partition
        for groups in generate_partitions(indices, partition):
            # Generate a sequence that covers these groups
            sequence = generate_covering_sequence(groups)
            if sequence and sequence[0] == (0, 1):
                yield sequence


def generate_partitions(indices, sizes):
    """Generate all ways to partition indices into groups of given sizes.
    
    Args:
        indices: list of indices to partition
        sizes: tuple of group sizes (must sum to len(indices))
    
    Yields:
        Lists of groups, each group is a list of indices
    """
    if not sizes:
        yield []
        return
    
    size = sizes[0]
    remaining_sizes = sizes[1:]
    
    for group in itertools.combinations(indices, size):
        remaining_indices = [i for i in indices if i not in group]
        for rest in generate_partitions(remaining_indices, remaining_sizes):
            yield [list(group)] + rest


def generate_covering_sequence(groups):
    """Generate a pair sequence that covers the given groups.
    
    Strategy: Create pairs that span/connect groups sensibly.
    Try to pair indices across groups to maximize coverage.
    Always start with (0, 1) if 0 and 1 are in different groups.
    """
    all_indices = [idx for group in groups for idx in group]
    all_pairs = list(itertools.combinations(all_indices, 2))
    
    # Ensure (0, 1) is first if it exists
    sequence = []
    if (0, 1) in all_pairs:
        sequence = [(0, 1)]
        remaining_pairs = [p for p in all_pairs if p != (0, 1)]
    else:
        remaining_pairs = all_pairs
    
    # Sort remaining pairs: prioritize those crossing groups
    def crossing_count(pair):
        a, b = pair
        group_a = next((i for i, g in enumerate(groups) if a in g), -1)
        group_b = next((i for i, g in enumerate(groups) if b in g), -1)
        return 0 if group_a == group_b else 1  # Crossing pairs first
    
    remaining_pairs.sort(key=crossing_count, reverse=True)
    sequence.extend(remaining_pairs)
    
    return sequence


def evaluate_partition_sequences():
    """Generate and evaluate all partition-based sequences."""
    placements = all_placements(8, 4)
    
    results = []
    for i, sequence in enumerate(generate_partition_based_sequences(8)):
        result_dict = simulate_sequence(sequence, placements)
        summary = summarize(result_dict)
        
        results.append({
            'sequence': sequence,
            'summary': summary,
            'index': i,
        })
    
    return results


def print_results(results, top_k=10):
    """Print results sorted by mean tests for finding 4 goods."""
    # Sort by mean tests for 4 goods
    sorted_results = sorted(
        results,
        key=lambda r: r['summary'][4]['mean'] if r['summary'][4]['mean'] is not None else float('inf')
    )
    
    print(f"Generated {len(results)} partition-based sequences\n")
    print(f"Top {top_k} by mean tests to find 4 goods:\n")
    
    for rank, result in enumerate(sorted_results[:top_k], 1):
        seq = result['sequence']
        s = result['summary']
        print(f"{rank}. Sequence (first 5): {seq[:5]}...")
        print(f"   Find 2: mean={s[2]['mean']:.2f}, Find 3: mean={s[3]['mean']:.2f}, Find 4: mean={s[4]['mean']:.2f}")
        print(f"   Full sequence: {seq}")
        print()


def save_best_as_json(results, filepath, top_n=5):
    """Save top N sequences to sequences.json."""
    import json
    from pathlib import Path
    
    # Sort by mean tests for 4 goods
    sorted_results = sorted(
        results,
        key=lambda r: r['summary'][4]['mean'] if r['summary'][4]['mean'] is not None else float('inf')
    )
    
    data = {}
    for i, result in enumerate(sorted_results[:top_n], 1):
        seq = result['sequence']
        s = result['summary'][4]
        name = f"partition_top{i}"
        data[name] = [list(p) for p in seq]
    
    p = Path(filepath)
    if p.exists():
        existing = json.loads(p.read_text(encoding='utf-8'))
        data = {**existing, **data}
    
    p.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f"Saved top {top_n} sequences to {filepath}")


if __name__ == '__main__':
    import sys
    
    print("Generating and evaluating partition-based sequences...\n")
    results = evaluate_partition_sequences()
    print_results(results, top_k=15)
    
    # Optionally save to sequences.json
    if '--save' in sys.argv:
        save_best_as_json(results, 'sequences.json', top_n=5)
