from collections import Counter
import random

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

def pick_guess(cands):    
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
    print("Wordle Helper Command Line")
    wordlist_path = 'all_letters.txt'  # replace with your actual word list path

    try:
        candidates = load_words(wordlist_path)
        print(f"Loaded {len(candidates)} words.")
    except FileNotFoundError:
        print(f"Error: Could not find wordlist file '{wordlist_path}'")
        return

    for turn in range(1, 7):
        if not candidates:
            print("No valid candidates remain. There might be an error in the feedback.")
            break
            
        guess = pick_guess(candidates)
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
    else:
        print("Out of turns. Try again!")

if __name__ == "__main__":
    main()