from collections import Counter
import random
import math

def load_words(path):
    with open(path, 'r') as file:
        words = [line.strip().lower() for line in file if len(line.strip()) == 5]
    return words

def letter_freq(words):
    freq = Counter()
    for word in words:
        unique_letters = set(word)
        freq.update(unique_letters)
    return freq

def get_feedback_pattern(guess, target):
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

def calculate_entropy(guess, candidates):
    """Calculate expected information gain (entropy) for a guess"""
    if not candidates:
        return 0
    
    # Count frequency of each feedback pattern
    pattern_counts = Counter()
    for target in candidates:
        pattern = get_feedback_pattern(guess, target)
        pattern_counts[pattern] += 1
    
    # Calculate entropy
    total = len(candidates)
    entropy = 0
    for count in pattern_counts.values():
        if count > 0:
            probability = count / total
            entropy -= probability * math.log2(probability)
    
    return entropy

def pick_guess_entropy(cands, all_words=None, max_candidates=50):
    """Pick guess using entropy (information theory approach)"""
    if len(cands) == 1:
        return cands[0]
    
    # Use all words as potential guesses, or just candidates if not provided
    guess_pool = all_words if all_words else cands
    
    # For performance, limit candidates if there are too many
    if len(cands) > max_candidates:
        sample_cands = random.sample(cands, max_candidates)
    else:
        sample_cands = cands
    
    best_guess = None
    best_entropy = -1
    
    # Calculate entropy for each potential guess
    for guess in guess_pool:
        entropy = calculate_entropy(guess, sample_cands)
        
        # Prefer candidates that could be the answer (tie-breaker)
        if guess in cands:
            entropy += 0.1  # Small bonus for words that could be the answer
        
        if entropy > best_entropy:
            best_entropy = entropy
            best_guess = guess
    
    return best_guess if best_guess else random.choice(cands)

def pick_guess(cands, all_words=None, use_entropy=True):    
    """Pick guess using either entropy or frequency-based approach"""
    if use_entropy:
        return pick_guess_entropy(cands, all_words)
    
    # Original frequency-based approach
    freqs = letter_freq(cands)
    top5_letters = set([letter for letter, _ in freqs.most_common(5)])
    
    # Find candidate words that contain all 5 top letters
    filtered = [word for word in cands if top5_letters.issubset(set(word))]
    
    if filtered:
        return random.choice(filtered)
    else:
        return random.choice(cands)

def filter_candidates(cands, guess, feedback):
    filtered = []
    for word in cands:
        is_valid = True

        # Handle greens first
        for i, (g_char, f_char) in enumerate(zip(guess, feedback)):
            if f_char == 'G':
                if word[i] != g_char:
                    is_valid = False
                    break
        
        if not is_valid:
            continue

        # Handle yellows and greys
        for i, (g_char, f_char) in enumerate(zip(guess, feedback)):
            if f_char == 'Y':
                # Yellow: letter is in word but not at this position
                if g_char not in word or word[i] == g_char:
                    is_valid = False
                    break
            elif f_char == '_':
                # Grey: check if this letter appears more times in word than indicated by feedback
                total_guess_count = guess.count(g_char)
                total_feedback_count = sum(
                    1 for j in range(5)
                    if guess[j] == g_char and feedback[j] in {'G', 'Y'}
                )
                
                # If this letter got no green/yellow feedback, it shouldn't be in the word
                # Unless it appears elsewhere with green/yellow feedback
                if total_feedback_count == 0:
                    if g_char in word:
                        is_valid = False
                        break
                else:
                    # If word has more of this letter than feedback indicates, it's invalid
                    if word.count(g_char) != total_feedback_count:
                        is_valid = False
                        break
        
        if is_valid:
            filtered.append(word)

    return filtered

def main():
    print("Wordle Helper Command Line (with Entropy)")
    wordlist_path = 'all_letters.txt'  # replace with your actual word list path

    try:
        all_words = load_words(wordlist_path)
        candidates = all_words.copy()
        print(f"Loaded {len(all_words)} words.")
    except FileNotFoundError:
        print(f"Error: Could not find wordlist file '{wordlist_path}'")
        return

    # Ask user for strategy preference
    use_entropy = input("Use entropy-based guessing? (y/n, default=y): ").strip().lower()
    use_entropy = use_entropy != 'n'
    
    print(f"Using {'entropy-based' if use_entropy else 'frequency-based'} strategy")

    for turn in range(1, 7):
        if not candidates:
            print("No valid candidates remain. There might be an error in the feedback.")
            break
            
        if use_entropy:
            guess = pick_guess(candidates, all_words, use_entropy=True)
        else:
            guess = pick_guess(candidates, use_entropy=False)
            
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
        
        # Show a few examples if not too many remain
        if len(candidates) <= 10 and len(candidates) > 1:
            print(f"Remaining candidates: {', '.join(candidates[:10])}")
    else:
        print("Out of turns. Try again!")

if __name__ == "__main__":
    main