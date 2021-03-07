import re
from .models import Pronunciation, Poem

newline = re.compile("\r\n|\n|\r")
disallowed = re.compile("[^A-Za-z]")

# I plan to separate this function into a number of independent, interacting functions
# so as to try different algorithms for scansion
def scan(poem):
    # get the ratio between the popularity of scansions for each word
    def get_stress(w):
        w = re.sub(disallowed, "", w)
        w = w.lower()
        # find all pronunciations of a word in the database
        patterns = Pronunciation.objects.filter(word=w)
        # if the word has not been entered yet, calculate a guess
        # of the number of syllables and add that many "?"s to the scansion
        if not patterns.exists():
            values = []
            for i in range(syllables(w)):
                values.append("?")
            return values
        # if the word has only been entered once, append numbers corresponding
        # to the popularity of that scansion
        elif patterns.count() == 1:
            values = []
            for char in patterns[0].stresses:
                if char == "u":
                    values.append(0.1 / patterns[0].popularity)
                else:
                    values.append(2.0 * patterns[0].popularity)
            return values
        # otherwise, find stress ratios for each syllable of the word based on
        # the most popular assigned number of syllables
        else:
            # some inspiration from https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
            # find number of patterns with a given syllable count for the word
            count_dict = {}
            for pattern in patterns:
                count = len(pattern.stresses)
                if count in count_dict:
                    count_dict[count].append(pattern)
                else:
                    count_dict[count] = [pattern]
            # find the most popular syllable count
            max = 0
            max_pop = 0
            for length in count_dict:
                # https://stackoverflow.com/questions/25047561/finding-a-sum-in-nested-list-using-a-lambda-function
                popularity = sum(pattern.popularity for pattern in count_dict[length])
                if popularity >= max_pop:
                    max_pop = popularity
                    max = length
            values = []
            # find the number of times, for that most popular number of syllables,
            # that each syllable has been marked as stressed or unstressed
            for i in range(max):
                stressed = 0
                # avoid division by 0
                unstressed = 0.01
                for pattern in count_dict[max]:
                    if pattern.stresses[i] == "/":
                        stressed += pattern.popularity
                    else:
                        unstressed += pattern.popularity
                # find the ratio between stressed and unstressed; round to two
                # to give only pronounced differences importance
                values.append(round(stressed / unstressed, 2))
            return values

    # split poem into lines and loop through the lines
    lines = newline.split(poem)
    stress_list = []
    for line in lines:
        words = line.split()
        line_list = []
        # get stress ratios for each syllable, separating separate words with spaces
        for word in words:
            stress = get_stress(word)
            line_list.extend(stress)
            line_list.append(" ")
        stress_list.append(line_list)
    # compare each syllable to the next syllable in the line and assign it
    # a stress marking ("/" or "u") based on the comparison
    poem_scansion = []
    for line in stress_list:
        line_scansion = ""
        # this is how to compare any two values
        def comp(value1, value2):
            if value2 == "?":
                if value1 < 0.2:
                    return "u"
                elif value >= 1.0:
                    return "/"
                else:
                    return "?"
            elif value1 < value2:
                return "u"
            elif value1 > value2:
                return "/"
            else:
                return "?"
        # if the line is not empty, compare each pair of values in a forward direction,
        # ignoring spaces
        if line:
            for i, value in enumerate(line):
                # if a given value is unknown, add a question mark to the scansion
                # copy spaces in untouched as well
                if value in ["?", " "]:
                    line_scansion += value
                # compare each value to the next value in the line, not counting spaces
                elif i < len(line) - 2:
                    if line[i + 1] == " ":
                        line_scansion += comp(value, line[i + 2])
                    else:
                        line_scansion += comp(value, line[i + 1])
                # compare the last syllable/value in the line to the previous
                # instead of to the nonexistent following
                else:
                    if line[i - 1] != " ":
                        line_scansion += comp(value, line[i - 1])
                    else:
                        line_scansion += comp(value, line[i - 2])
        # and the scansion to the poem's scansion list
        poem_scansion.append(line_scansion)
    # join the poem's scansion list with a newline
    return "\n".join(poem_scansion)

# record stress patterns of words scanned by a promoted user in the database
def record(poem, scansion):
    # split both poem and scansion on spaces
    words = poem.split()
    words = [re.sub(disallowed, "", word).lower() for word in words]
    scanned_words = scansion.split()
    # find each word in the database if it is there
    for i, word in enumerate(words):
        w = Pronunciation.objects.filter(word=word)
        # see if any instances of the word have the user-inputted stress pattern
        found = False
        for pron in w:
            # increment the popularity of that stress pattern if it is found
            if scanned_words[i] == pron.stresses:
                pron.popularity += 1
                pron.save()
                found = True
        # otherwise create a new instance of the word with the correct pronunciation
        if not found:
            new_pron = Pronunciation(word=word, stresses=scanned_words[i], popularity=1)
            new_pron.save()

# count the syllables in a word if it is not in the database
def syllables(word):
    vowels_or_clusters = re.compile("[AEIOUaeiouy]+")
    vowel_split = re.compile("ao|ia[^n]|iet|[^cgst]ian|io[^nu]|iu|[^gq]ua|[^gq]ue[lt]|[^q]uo|[aeiouy]ing|[aeiou]y[aiou]") # exceptions: Preus, Aida, venetian, mention, piety, Lucius, poet, luau, quilt(check if there's a q if there's a u)
    final_e = re.compile("e$")
    silent_final_ed_es = re.compile("[^aeiouydlrt]ed$|[^aeiouycghjlrsxz]es$|thes$|[aeiouylrw]led$|[aeiouylrw]les$|[aeiouyrw]res$|[aeiouyrw]red$")
    lonely = re.compile("[^aeiouy]ely$")
    audible_final_e = re.compile('[^aeiouy]le$|[aeiouy]e')
    word = word.lower()
    voc = re.findall(vowels_or_clusters, word)
    count = len(voc)
    if final_e.search(word) and not audible_final_e.search(word):
        count -= 1
    if silent_final_ed_es.search(word) or lonely.search(word):
        count -= 1
    likely_splits = re.findall(vowel_split, word)
    if likely_splits:
        count += len(likely_splits)
    if count == 0:
        count += 1
    return count
