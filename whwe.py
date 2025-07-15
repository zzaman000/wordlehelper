from collections import Counter
import random
import math
from typing import List

MAX_TURNS = 6
MAX_CANDIDATES_FOR_ENTROPY = 50

def load_words(path: str) -> List[str]:
    with open(path, 'r') as file:
        words = [line.strip().lower() for line in file if len(line.strip()) == 5]
    return words

def letter_freq(words: List[str]) -> Counter:
    freq = Counter()
    for word in words:
        unique_letters = set(word)
        freq.update(unique_letters)
    return freq

def get_feedback_pattern(guess: str, target: str) -> str:
    """Generate feedback pattern for a guess against a target word"""
    feedback = ['_'] * 5
    target_chars = list(target)

    # First pass: mark greens
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = 'G'
            target_chars[i] = None  # Mark as used

    # Second pass: mark yellows
    for i in range(5):
        if feedback[i] == '_' and guess[i] in target_chars:
            feedback[i] = 'Y'
            target_chars[target_chars.index(guess[i])] = None  # Mark as used

    return ''.join(feedback)

def calculate_entropy(guess: str, candidates: List[str]) -> float:
    """Calculate expected information gain (entropy) for a guess"""
    if not candidates:
        return 0.0

    pattern_counts = Counter(get_feedback_pattern(guess, target) for target in candidates)
    total = len(candidates)

    entropy = -sum((count / total) * math.log2(count / total) for count in pattern_counts.values())
    return entropy

def pick_guess_entropy(candidates: List[str], all_words: List[str] = None, max_candidates: int = MAX_CANDIDATES_FOR_ENTROPY) -> str:
    if len(candidates) == 1:
        return candidates[0]

    guess_pool = all_words if all_words else candidates
    sample_cands = random.sample(candidates, max_candidates) if len(candidates) > max_candidates else candidates

    best_guess = None
    best_entropy = -1.0

    for guess in guess_pool:
        entropy = calculate_entropy(guess, sample_cands)
        if guess in candidates:
            entropy += 0.01  # Slight preference for guesses that could be the answer

        if entropy > best_entropy:
            best_entropy = entropy
            best_guess = guess

    return best_guess if best_guess else random.choice(candidates)

def pick_guess(candidates: List[str], all_words: List[str] = None, use_entropy: bool = True) -> str:
    if use_entropy:
        return pick_guess_entropy(candidates, all_words)

    freqs = letter_freq(candidates)
    top5_letters = set(letter for letter, _ in freqs.most_common(5))
    filtered = [word for word in candidates if top5_letters.issubset(set(word))]

    return random.choice(filtered if filtered else candidates)

def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    filtered = []
    for word in candidates:
        if all(
            (f == 'G' and word[i] == g) or
            (f == 'Y' and word[i] != g and g in word) or
            (f == '_' and ((g not in word) if feedback.count(g) == 0 else word.count(g) == feedback.count(g)))
            for i, (g, f) in enumerate(zip(guess, feedback))
        ):
            filtered.append(word)
    return filtered

def main():
    print("Wordle Helper Command Line (with Entropy)")
    wordlist_path = 'all_letters.txt'

    try:
        all_words = load_words(wordlist_path)
        candidates = all_words.copy()
        print(f"Loaded {len(all_words)} words.")
    except FileNotFoundError:
        print(f"Error: Could not find wordlist file '{wordlist_path}'")
        return

    use_entropy_input = input("Use entropy-based guessing? (y/n, default=y): ").strip().lower()
    use_entropy = use_entropy_input != 'n'

    print(f"Using {'entropy-based' if use_entropy else 'frequency-based'} strategy")

    for turn in range(1, MAX_TURNS + 1):
        if not candidates:
            print("No valid candidates remain. There might be an error in the feedback.")
            break

        guess = pick_guess(candidates, all_words, use_entropy)
        print(f"\nTurn {turn}: Try guess → {guess.upper()}")

        feedback = input("Enter feedback (G=green, Y=yellow, _=gray): ").strip().upper()
        if len(feedback) != 5 or any(c not in "GY_" for c in feedback):
            print("Invalid feedback format. Use only G, Y, or _ (e.g., G_Y__)")
            continue

        if feedback == "GGGGG":
            print("Solved in", turn, "turns!")
            break

        candidates = filter_candidates(candidates, guess, feedback)
        print(f"{len(candidates)} possible words remain.")

        if 1 < len(candidates) <= 10:
            print(f"Remaining candidates: {', '.join(candidates[:10])}")
    else:
        print("Out of turns. Try again!")

if __name__ == "__main__":
    main()
