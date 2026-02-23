"""
Generate random unique sequences (always starting with (0,1)) and search for improvements.
Uses batteries_sim to evaluate sequences and track the best one found.
"""

import itertools
import random
import sys
from batteries_sim import all_placements, simulate_sequence, summarize


def generate_random_sequence(n=8):
    """Generate a random sequence of pairs, always starting with (0,1).
    
    Returns a list of unique pairs in random order, with (0,1) always first.
    """
    all_pairs = list(itertools.combinations(range(n), 2))
    # Remove (0,1) from candidates since it's always first
    remaining = [p for p in all_pairs if p != (0, 1)]
    # Shuffle the remaining pairs
    random.shuffle(remaining)
    return [(0, 1)] + remaining


def metric_score(summary, target_k=4):
    """Compute a scalar score from summary for optimization. Lower is better.
    
    Uses mean tests to find target_k goods.
    """
    if summary[target_k]['mean'] is None:
        return float('inf')
    return summary[target_k]['mean']


def print_all_best_summaries(best_scores, best_sequences, best_summaries):
    """Print a summary of all best sequences found so far."""
    print("  --- Current best sequences for all targets ---")
    for k in (2, 3, 4):
        if best_sequences[k]:
            s = best_summaries[k][k]
            print(f"  Find {k}:{s['mean']:.4f}:{s['median']:.0f}: {best_sequences[k][:s['max']]}, min={s['min']}, max={s['max']}, not_found={s['not_found_count']}")
        else:
            print(f"  Find {k} goods: not yet found")
    print()


def count_matches_per_pair(pairs, placements):
    """Count how many placements each pair matches (both elements in placement)."""
    counts = {}
    for pair in pairs:
        a, b = pair
        count = sum(1 for placement in placements if a in placement and b in placement)
        counts[pair] = count
    return counts


def reorder_by_match_count(sequence, placements):
    """Reorder sequence by descending match count, keeping (0,1) first."""
    if not sequence or sequence[0] != (0, 1):
        return sequence
    
    counts = count_matches_per_pair(sequence, placements)
    
    # Keep (0,1) first, sort the rest by descending match count
    rest = sequence[1:]
    rest_sorted = sorted(rest, key=lambda p: counts[p], reverse=True)
    return [(0, 1)] + rest_sorted


def main():
    placements = all_placements(8, 4)
    
    # Track best sequence for each target separately
    best_scores = {2: float('inf'), 3: float('inf'), 4: float('inf')}
    best_sequences = {2: None, 3: None, 4: None}
    best_summaries = {2: None, 3: None, 4: None}
    iteration = 0
    
    print("Starting sequence optimization (Ctrl+C to stop)...")
    print("Tracking best sequences for finding 2, 3, and 4 goods separately")
    print()
    
    try:
        while True:
            iteration += 1
            
            # Generate a random sequence
            sequence = generate_random_sequence(8)
            
            # Evaluate the original sequence
            results = simulate_sequence(sequence, placements)
            summary = summarize(results)
            
            # Check for improvement on each target
            improvement_found = False
            for k in (2, 3, 4):
                score = metric_score(summary, target_k=k)
                if score < best_scores[k]:
                    best_scores[k] = score
                    best_sequences[k] = sequence
                    best_summaries[k] = summary
                    print(f"Iteration {iteration}: IMPROVED for finding {k} goods! (original order)")
                    print(f"  Score (mean tests): {score:.4f}")
                    print(f"  Sequence: {sequence}")
                    improvement_found = True
            
            # If any improvement, print all best summaries
            if improvement_found:
                print_all_best_summaries(best_scores, best_sequences, best_summaries)
            
            # Print progress every 100k iterations
            if iteration % 100000 == 0:
                print(f"Iteration {iteration}: current best scores = "
                      f"2->{best_scores[2]:.4f}, 3->{best_scores[3]:.4f}, 4->{best_scores[4]:.4f}")
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
        print(f"\nBest sequences found in {iteration} iterations:\n")
        for k in (2, 3, 4):
            if best_sequences[k]:
                print(f"Best for finding {k} goods:")
                print(f"  Sequence: {best_sequences[k]}")
                s = best_summaries[k][k]
                print(f"  Score: {best_scores[k]:.4f}")
                print(f"  Mean={s['mean']:.4f}, Median={s['median']}, "
                      f"Min={s['min']}, Max={s['max']}, Not found={s['not_found_count']}")
                print()


if __name__ == '__main__':
    main()
