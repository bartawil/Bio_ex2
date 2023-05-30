import random

POPULATION_SIZE = 100
NUM_OF_GENERATIONS = 100
SAMPLES_SIZE = 20
MUT_RATE = 0.02
NUM_OF_NO_CHANGES = 15
NUM_OF_ITERATIONS = 5
DARWIN_N = 5
LAMARCK_N = 5
DARWIN = False
LAMARCK = False


no_changes_counter = 0
gen_of_top_key = 0
top_score = 0
top_key = None
num_of_fitness_calls = 0

encrypted_text = ''
letter_freq = {}
pair_freq = {}
dict_words = set()
keys_list = []

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']


"""

Genetic Algorithm...

"""


def text_decoder(key):
    decoded_text = ""
    for letter in cipher_text:
        decoded_text += key.get(letter, letter)
    return decoded_text


def check_pair(text):
    current_pair_freq = {}
    # Count the frequencies of two-letter pairs in the text
    for i in range(len(text) - 1):
        pair = text[i:i + 2]
        if pair in pair_freq:
            if pair in current_pair_freq:
                current_pair_freq[pair] += 1
            else:
                current_pair_freq[pair] = 1
    counter = 0
    # Calculate the sum of all the frequencies
    for freq in current_pair_freq.values():
        counter += freq
    normalized_freq = {}
    # Calculate the normalized frequencies of the two-letter pairs
    for pair, freq in current_pair_freq.items():
        normalized_freq[pair] = freq / counter
    differences = 0
    # Calculate the sum of squared differences between the frequencies
    for letter in pair_freq:
        diff = pair_freq[letter] - normalized_freq.get(letter, 0)
        differences += pow(diff, 2)
    return differences


def check_letter(text):
    # Calculate the observed frequencies of each letter in the given text
    current_letter_freq = {}
    for letter in alphabet:
        # Count the occurrences of the letter in the text
        frequency = text.count(letter) / len(text)
        current_letter_freq[letter] = frequency
    # Calculate the sum of squared differences between the frequencies in letter_freq
    # and the observed frequencies in current_letter_freq
    counter = 0
    for letter in alphabet:
        observed_freq = current_letter_freq.get(letter, 0)
        squared_diff = pow(letter_freq[letter] - observed_freq, 2)
        counter += squared_diff
    return counter


def check_word(text):
    counter = 0
    for line in text.split("/n"):
        for word in line.split(" "):
            if word.lower() in dict_words:
                counter += 1
    return pow(counter * 0.3, 2)


def fitness(text):
    word_score = check_word(text)
    letter_score = check_letter(text)
    pair_score = check_pair(text)
    return word_score + letter_score + pair_score


def selection(fitness_scores):
    parents = []
    for i in range(POPULATION_SIZE):
        samples = random.sample(fitness_scores, SAMPLES_SIZE)
        sorted_samples = sorted(samples, key=lambda item: item[1], reverse=False)
        index, _ = sorted_samples[-1]
        parent = keys_list[index]
        parents.append(parent)
    return parents


def crossover(parent1, parent2):
    cross_point = random.choice(alphabet)
    child1 = {}
    for key in parent1:
        if key <= cross_point:
            child1[key] = parent1[key]
        else:
            child1[key] = parent2[key]

    # check first child
    child_letters = set(child1.values())
    letters_to_add = list(set(alphabet) - child_letters)
    checked_letters = set()
    for letter in alphabet:
        if child1[letter] in checked_letters:
            child1[letter] = letters_to_add.pop()
        checked_letters.add(child1[letter])

    child2 = {}
    for key in parent2:
        if key <= cross_point:
            child2[key] = parent2[key]
        else:
            child2[key] = parent1[key]

    # check second child
    child_letters = set(child2.values())
    letters_to_add = list(set(alphabet) - child_letters)
    checked_letters = set()
    for letter in alphabet:
        if child2[letter] in checked_letters:
            child2[letter] = letters_to_add.pop()
        checked_letters.add(child2[letter])

    return child1, child2


def mutation(child_key):
    for letter in alphabet:
        if random.random() < MUT_RATE:
            rand1 = random.choice(alphabet)
            rand2 = random.choice(alphabet)
            tmp = child_key[rand1]
            child_key[rand1] = child_key[rand2]
            child_key[rand2] = tmp
    return child_key


"""

Initialization Part...

"""


def parse_enc():
    global cipher_text
    with open('enc.txt', 'r') as file:
        cipher_text = file.read()
    file.close()


def parse_dict():
    with open('dict.txt', 'r') as file:
        for line in file:
            word = line.strip()
            if word:
                dict_words.add(word)
    file.close()


def get_letters_freq():
    with open('Letter_Freq.txt', 'r') as file:
        for line in file:
            freq, letter = line.strip().split('\t')
            letter_freq[letter.lower()] = float(freq)
    file.close()


def get_pair_freq():
    with open('Letter2_Freq.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if line.isalpha():
                freq, pair = line.strip().split('\t')
                pair_freq[pair.lower()] = float(freq)
    file.close()


"""

Create Population...

"""


def generate_keys():
    global keys_list
    keys_list.clear()
    for i in range(POPULATION_SIZE):
        tmp_alphabet = alphabet.copy()
        random.shuffle(tmp_alphabet)
        key = {}
        for i in range(26):
            key[alphabet[i]] = tmp_alphabet[i]
        keys_list.append(key)


"""

Get Answer Files...

"""


def write_ans_files(key):
    with open("plain.txt", "w") as file:
        file.write(text_decoder(key))
    file.close()

    with open("perm.txt", "w") as file:
        for i in range(26):
            file.write(f"{alphabet[i]}: {list(key.values())[i]}\n")
    file.close()


"""

Part 2 - lamarck AND da

"""


def lamarck(keys):
    global num_of_fitness_calls
    children = keys
    for i in range(POPULATION_SIZE):
        # save current fitness
        decoded_text = text_decoder(children[i])
        num_of_fitness_calls += 1
        score = int(fitness(decoded_text))
        # check muted child fitness
        tmp_child = children[i].copy()
        for j in range(LAMARCK_N):
            # make mutation
            rand1 = random.choice(alphabet)
            rand2 = random.choice(alphabet)
            tmp = tmp_child[rand1]
            tmp_child[rand1] = tmp_child[rand2]
            tmp_child[rand2] = tmp
            # check fitness
            decoded_text = text_decoder(tmp_child)
            num_of_fitness_calls += 1
            new_score = int(fitness(decoded_text))
            if new_score > score:
                children[i] = tmp_child
    return children


def darwin(keys, gen):
    global top_score, num_of_fitness_calls, top_key, \
        gen_of_top_key, no_changes_counter
    children = keys
    for i in range(POPULATION_SIZE):
        for j in range(DARWIN_N):
            # make mutation
            rand1 = random.choice(alphabet)
            rand2 = random.choice(alphabet)
            tmp = children[i][rand1]
            children[i][rand1] = children[i][rand2]
            children[i][rand2] = tmp
            # check fitness
            decoded_text = text_decoder(children[i])
            num_of_fitness_calls += 1
            new_score = int(fitness(decoded_text))
            if new_score > top_score:
                top_score = new_score
                gen_of_top_key = gen
                top_key = children[i]
                no_changes_counter = 0


def genetic_algorithm():
    global no_changes_counter, gen_of_top_key, top_score, top_key, num_of_fitness_calls, keys_list

    no_changes_counter = 0
    gen_of_top_key = 0
    top_score = 0
    top_key = None
    num_of_fitness_calls = 0

    for gen in range(NUM_OF_GENERATIONS):
        # sort the keys by the fitness score by coupling score to key index
        fitness_scores = []
        for i, key in enumerate(keys_list):
            decoded_text = text_decoder(key)
            num_of_fitness_calls += 1
            score = int(fitness(decoded_text))
            fitness_scores.append((i, score))
        fitness_scores = sorted(fitness_scores, key=lambda item: item[1], reverse=False)

        key_index, fitness_score = fitness_scores[-1]
        if fitness_score > top_score:
            top_score = fitness_score
            gen_of_top_key = gen
            top_key = keys_list[key_index]
            no_changes_counter = 0
        else:
            if no_changes_counter == NUM_OF_NO_CHANGES:
                break
            no_changes_counter += 1

        parents = selection(fitness_scores)

        children = [top_key]
        for i in range(int(POPULATION_SIZE/2)):
            if (i < len(parents)) and ((i + 1) < len(parents)):
                parent1 = parents[i]
                parent2 = parents[i + 1]
                i += 2
                child1, child2 = crossover(parent1, parent2)
                children.append(mutation(child1))
                children.append(mutation(child2))
        children = children[:POPULATION_SIZE]

        if LAMARCK:
            children = lamarck(children)

        if DARWIN:
            darwin(children, gen)

        keys_list = children


if __name__ == '__main__':
    # initialization
    parse_enc()
    parse_dict()
    get_letters_freq()
    get_pair_freq()

    # ask user which algorithm to run
    print("Algorithm Options:")
    print("1. Genetic Algorithm")
    print("2. Lamarck Algorithm")
    print("3. Darwin Algorithm")

    choice = input("Enter the number of your chosen algorithm\n")

    if int(choice) == 1:
        pass
    elif int(choice) == 2:
        LAMARCK = True
    elif int(choice) == 3:
        DARWIN = True
    else:
        print("You chose wrong number")

    global_num_of_fitness_calls = 0
    global_top_score = 0
    global_gen_of_top_key = 0
    global_top_key = None
    iteration_number = 0
    for i in range(NUM_OF_ITERATIONS):
        # init population
        print("Genetic Algorithm - Iteration " + str(i+1) + "/" + str(NUM_OF_ITERATIONS))
        generate_keys()
        # run the algorithm
        genetic_algorithm()
        # print("top fitness " + str(top_score))
        if top_score > global_top_score:
            global_num_of_fitness_calls = num_of_fitness_calls
            global_top_score = top_score
            global_gen_of_top_key = gen_of_top_key
            global_top_key = top_key
            iteration_number = i+1

    print("Best Key In Iteration " + str(iteration_number) + ":")
    print("Num of fitness calls: " + str(global_num_of_fitness_calls))
    print("Top fitness score: " + str(global_top_score))
    print("Gen of top score: " + str(global_gen_of_top_key))
    write_ans_files(global_top_key)
    input("Press Enter to exit...")
