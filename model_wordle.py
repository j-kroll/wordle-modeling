import csv
import re

def get_embedding(wordle_emojis):
    embedding = []
    for line in wordle_emojis.split("\n"):
        line_embedding = []
        for char in line:
            if char in ["⬛","⬜"]:
                line_embedding.append(0)
            elif char == "🟨":
                line_embedding.append(1)
            elif char == "🟩":
                line_embedding.append(2)
            else:
                print("Warning: unknown character", char)
        embedding.append(line_embedding)
    return embedding

def main():
    num_tweets = 0
    with open("wordle-tweets.csv") as f:
        csv_reader = csv.reader(f, delimiter=",")
        headers = next(csv_reader)
        for row in csv_reader:
            wordle_id, tweet_id, tweet_date, tweet_username, tweet_text = row
            wordle_emojis = re.search("[⬛⬜🟨🟩\n]+", tweet_text).group(0).strip("\n")
            wordle_embedding = get_embedding(wordle_emojis)
            num_tweets += 1
    print("Processed {} tweets".format(num_tweets))

if __name__ == '__main__':
    main()

