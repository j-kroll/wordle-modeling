import csv
import matplotlib.pyplot as plt
import re

def get_embedding(wordle_emojis):
    embedding = []
    for line in wordle_emojis.split("\n"):
        line_embedding = ""
        for char in line:
            if char in ["⬛","⬜"]:
                line_embedding += "0"
            elif char == "🟨":
                line_embedding += "1"
            elif char == "🟩":
                line_embedding += "2"
            else:
                print("Warning: unknown character", char)
        embedding.append(line_embedding)
    return embedding

def get_solution_word(wordle_id, solutions):
    return solutions[wordle_id].lower()

def get_associations(word, associations):
    if word in associations:
        return [(k, v) for k, v in sorted(associations[word].items(), key=lambda w: w[1], reverse=True)]
    else:
        print("Warning: no associations for", word)
        return []

def plot_relationship(x, y, x_lab, y_lab, title, words):
    plt.scatter(x, y)
    for i, label in enumerate(words):
        plt.annotate(label, (x[i], y[i]))
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.title(title)
    plt.show()

def main():

    # Read tweets, counting average number of guesses
    num_tweets = 0
    embeddings = []
    guess_counts = {}
    with open("wordle-tweets.csv") as f:
        csv_reader = csv.reader(f, delimiter=",")
        headers = next(csv_reader)
        for row in csv_reader:
            wordle_id, tweet_id, tweet_date, tweet_username, tweet_text = row
            wordle_emojis = re.search("[⬛⬜🟨🟩\n]+", tweet_text).group(0).strip("\n")
            num_guesses = len(wordle_emojis.split("\n"))
            wordle_embedding = get_embedding(wordle_emojis)
            embeddings.append(wordle_embedding)
            if wordle_id not in guess_counts:
                guess_counts[wordle_id] = []
            guess_counts[wordle_id].append(num_guesses)
            num_tweets += 1
    print("Processed {} tweets".format(num_tweets))

    # Read solutions
    solutions = {}
    with open("wordle-answers.csv") as f:
        for line in f.readlines()[1:]:
            date, wordle_id, word = line.strip("\n").split("\t")
            solutions[wordle_id] = word
    print("Processed {} solutions".format(len(solutions)))

    # Construct dictionary for transition matrix
    chain = {}
    num_transitions = 0
    for emb in embeddings:
        for i in range(len(emb) + 1):
            start_state = "<START>" if i == 0 else emb[i - 1]
            end_state = "<END>" if i == len(emb) else emb[i]
            if not start_state in chain:
                chain[start_state] = {}
            if not end_state in chain[start_state]:
                chain[start_state][end_state] = 0
                num_transitions += 1
            chain[start_state][end_state] += 1
    print("Found {} unique state transitions".format(num_transitions))

    # Read backward word associations
    associations = {}
    with open("SWOW-EN-complete.csv") as f:
        csv_reader = csv.reader(f, delimiter=",")
        headers = next(csv_reader)
        for row in csv_reader:
            _, _, _, _, _, _, _, _, _, _, _, cue, _, _, _, r1, r2, r3 = row
            for r in [r1, r2, r3]:
                if r not in associations:
                    associations[r] = {}
                if cue not in associations[r]:
                    associations[r][cue] = 0
                associations[r][cue] += 1

    # Count associations for each solution
    solution_association_counts = {}
    TOTAL = "total"
    UNIQUE = "unique"
    for wordle_id in list(solutions.keys()):
        word = get_solution_word(wordle_id, solutions)
        solution_associations = get_associations(word, associations)
        num_total_associations = sum([p[1] for p in solution_associations])
        num_unique_associations = len(solution_associations)
        solution_association_counts[wordle_id] = {}
        solution_association_counts[wordle_id][TOTAL] = num_total_associations
        solution_association_counts[wordle_id][UNIQUE] = num_unique_associations

    # Compute average number of guesses per puzzle
    guess_averages = {}
    for wordle_id in list(guess_counts.keys()):
        guess_averages[wordle_id] = sum(guess_counts[wordle_id]) / len(guess_counts[wordle_id])

    # Put it all together
    total_assoc = []
    uniq_assoc = []
    avg_g = []
    wds = []
    for wordle_id in list(solutions.keys()):
        if wordle_id in guess_averages:
            word = get_solution_word(wordle_id, solutions)
            total_associations = solution_association_counts[wordle_id][TOTAL]
            unique_associations = solution_association_counts[wordle_id][UNIQUE]
            avg_guesses = guess_averages[wordle_id]
            total_assoc.append(total_associations)
            uniq_assoc.append(unique_associations)
            avg_g.append(avg_guesses)
            wds.append(word)
            print(word.upper() + " -- Associations: {} unique, {} total; average guesses: {}".format(unique_associations, total_associations, avg_guesses))

    # Plot relationship between word associations and ease of solving each word
    plot_relationship(avg_g, uniq_assoc, "Average number of guesses", "Number of unique associations", "Unique associations versus average guesses", wds)
    plot_relationship(avg_g, total_assoc, "Average number of guesses", "Number of total associations", "Total associations versus average guesses", wds)
    plot_relationship(total_assoc, uniq_assoc, "Number of total associations", "Number of unique associations", "Unique versus total associations", wds)

if __name__ == '__main__':
    main()

