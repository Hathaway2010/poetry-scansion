import re
from .models import Pronunciation
from copy import copy

newline = re.compile("\r\n|\n|\r")
disallowed = re.compile("[^A-Za-z]")

def get_stats(word):
    # get version of word without non-alphabetic characters and lowercase
    w = re.sub(disallowed, "", word)
    w = w.lower()
    # get all pronunciations of the word
    patterns = Pronunciation.objects.filter(word=w)
    # if there are none, guess the syllable count and return a list of
    # [syllables] question marks to indicate that stress pattern is unknown
    if not patterns.exists():
        return ["?" for i in range(syllables(w))]
    # if there is one, add 0.1 / popularity if it is unstressed or 0.1 * popularity if it is stressed
    elif patterns.count() == 1:
        values = []
        for char in patterns[0].stresses:
            if char == "u":
                values.append(round(0.1 / patterns[0].popularity, 2))
            else:
                values.append(2.0 * patterns[0].popularity)
        return values
    else:
        # some inspiration from https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
        # create a dictionary containing the various syllable counts the word has been judged to have
        # as keys, and a list of the various stress patterns with that syllable
        # as the value for each key
        count_dict = {}
        for pattern in patterns:
            count = len(pattern.stresses)
            if count in count_dict:
                count_dict[count].append(pattern)
            else:
                count_dict[count] = [pattern]
        # in order to find the most popular syllable count:
        # set max, representing the most popular syllable count, equal to 0 initially
        # and let the highest popularity of any syllable count, max_pop, equal 0 as well
        max = 0
        max_pop = 0
        # loop through count_dict, adding up the popularities of each pattern for a given length,
        # and making max_pop equal to the maximum sum of popularities thus far
        for length in count_dict:
            # https://stackoverflow.com/questions/25047561/finding-a-sum-in-nested-list-using-a-lambda-function
            popularity = sum(pattern.popularity for pattern in count_dict[length])
            if popularity >= max_pop:
                max_pop = popularity
                max = length
        # having found the most popular syllable count, loop through all stress patterns
        # with that syllable count for each syllable, finding the sum of popularities
        # for stressed and unstressed values of that syllable respectively
        values = []
        for i in range(max):
            stressed = 0
            unstressed = 0.01
            for pattern in count_dict[max]:
                if pattern.stresses[i] == "/":
                    stressed += pattern.popularity
                else:
                    unstressed += pattern.popularity
            # add the ratio of stressed to unstressed interpretations of each syllable
            # to the "values" list in order
            values.append(round(stressed / unstressed, 4))
        return values

def poem_stats(poem):
    # split poem into lines
    lines = newline.split(poem)
    stress_list = []
    # for each line get the stress probability (stressed / unstressed)
    # for each word and append it to stress list; for spaces, append a space
    for line in lines:
        words = line.split()
        line_list = []
        for word in words:
            stress = get_stats(word)
            line_list.extend(stress)
            line_list.append(" ")
        stress_list.append(line_list)
    return stress_list

def original_scan(poem):
    # get stress ratio for each syllble in each word, separated by spaces,
    # and organized into lines
    stress_list = poem_stats(poem)
    poem_scansion = []
    # for each line in this, compare the stress ratio for each word to the next
    for line in stress_list:
        line_scansion = ""
        # function to compare two vlues
        def comp(value1, value2):
            # if the second value is unknown, guess the first based on itself alone
            if value2 == "?":
                if value1 < 0.2:
                    return "u"
                elif value >= 1.0:
                    return "/"
                else:
                    return "?"
            # otherwise, if the first is smaller, guess unstressed, or "u"
            elif value1 < value2:
                return "u"
            # if the first is larger, guess stressed, or "/"
            elif value1 > value2:
                return "/"
            # if they are equal, decline to make a guess
            else:
                return "?"
        # check that the line is not blank (that is, a stanza break)
        if line:
            for i, value in enumerate(line):
                # for each value, if that value is non-numeric, simply add it,
                # whether it is a space (indicating a space in the poem), or a "?"
                if value in ["?", " "]:
                    line_scansion += value
                # otherwise, if we are not nearing the end of the line,
                # compare each to the next
                elif i < len(line) - 2:
                    if line[i + 1] == " ":
                        line_scansion += comp(value, line[i + 2])
                    else:
                        line_scansion += comp(value, line[i + 1])
                # finally, if we are near the end of the line,
                # compare to the previous syllable
                else:
                    if line[i - 1] != " ":
                        line_scansion += comp(value, line[i - 1])
                    else:
                        line_scansion += comp(value, line[i - 2])
        poem_scansion.append(line_scansion)
    return "\n".join(poem_scansion)

# see https://leetcode.com/problems/house-robber/discuss/156523/From-good-to-great.-How-to-approach-most-of-DP-problems.
def house_robber_scan(poem):
    # get stress pattern of poem
    stress_list = poem_stats(poem)
    poem_scansion = []
    for line in stress_list:
        # remove spaces and replace question marks with a guess of 0.3
        # add each value to a tuple containing its index as the second value
        spaceless_line = []
        for i, value in enumerate(line):
            if value != " ":
                if value == "?":
                    spaceless_line.append((0.3, i))
                else:
                    spaceless_line.append((value, i))
        # initialize two lists to represent potential stress patterns for the lines
        prev1 = []
        prev2 = []
        # iterate through spaceless line so constructed
        for pair in spaceless_line:
            tmp = copy(prev1)
            # https://stackoverflow.com/questions/25047561/finding-a-sum-in-nested-list-using-a-lambda-function
            # if the sum of stress values contained in prev1 is less than the sum
            # of stress values in prev2 + the current stress value
            # make prev1 a copy of prev2
            if sum(p[0] for p in prev1) < sum(p[0] for p in prev2) + pair[0]:
                prev2.append(pair)
                prev1 = copy(prev2)
            # either way, make the previous prev1 prev2
            prev2 = copy(tmp)
        # iterate through original line, adding to a scansion
        line_scansion = ""
        for i, value in enumerate(line):
            # carry spaces over into the scansion untouched
            if value == " ":
                line_scansion += value
            # otherwise, if a given value is an index included in prev1,
            # which is the "winner" for highest values
            # make it stressed, and if it is not, make it unstressed
            elif [pair for pair in prev1 if pair[1] == i]:
                line_scansion += "/"
            else:
                line_scansion += "u"
        poem_scansion.append(line_scansion)
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
