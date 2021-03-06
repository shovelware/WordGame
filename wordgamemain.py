import time
from string import ascii_letters
import DBI as database

lenguess = 3
numguess = 7
scoremult = 100

###Testing Words###          
"""Test guesses against source, guessdict, no dupes, not source"""
def test_guesses(source, guesses):
    errordict = {}
    count = 0

    #if we have the right number of words
    if len(guesses) < numguess or len(guesses) > numguess:
        errordict["!"] = "Incorrect number of guesses. " + str(len(guesses)) + "/" + str(numguess) + " submitted." + ""

    else:
        #check for dupes
        if len(guesses) != len(set(guesses)):
            errordict["!"] = "Duplicates in guess list."
        else:
                #loop through words, only entered if non-fatal errors
                for g in guesses:
                    ##test word isn't too short
                    if len(g) < lenguess:
                        errordict[g] ="Too few characters."
                        continue

                    #test word isn't too long
                    if len(g) > len(source):
                        errordict[g] = "Too many characters."
                        continue

                    #test word isn't in dictionary ##2.0 SQL
                    if database.check_guess(g.lower().strip()) != True:
                            errordict[g] = "Not in dictionary."
                            continue

                    #test word is source
                    if g == source:
                        errordict[g] = "Source word as guess."
                        continue

                    #test word against source
                    if contains(source, g):
                        count += 1
                    else: errordict[g]= "Not in source word."

        #return errordict which will be empty if everything is okay
    return errordict


"""Checks if container contains word"""
def contains(container, word):
    #All checks done in lowercase and stripped
    contnum = letter_count(container.lower().strip())
    wordnum = letter_count(word.lower().strip())

    #print ("\n" + container.lower())
    #print(contnum)
    #
    #print ("\n" + word.lower())
    #print(wordnum)

    for letter, count in wordnum.items():
        if contnum.get(letter, 0) < count:
            return False
    return True

"""Checks letter frequency for a single word"""
def letter_count(word):
    letters = {}
    for letter in word:
        letters.setdefault(letter, 0)
        letters[letter] += 1
    return letters

###Game Functions###
"""take a string, make them into a list delimited by non-ascii characters"""
def string_to_list(instring):
        output = []
        liststr = ""

        #step through characters
        #if we hit a non-letter, drop the word into the list and continue stepping
        #works really nice, I'm proud of it
        for c in instring:
            if (c in ascii_letters):
                liststr += c
            elif (c not in ascii_letters):
                if liststr != "":
                    output.append(liststr)
                    liststr = ""
        #last guess
        if liststr != "":
            output.append(liststr)
            liststr = ""

        return output

"""take a list, give it back as a newlined string"""
def list_to_string(lst):
        strng = ""
        for i in lst:
            strng += str(i) + "\n"

        #remove the trailing newline
        strng = strng[:-1]

        return strng

"""take a list of lists, return it as a newlined string"""
def list_list_to_string(lst):
        strng = ""
        for i in lst:
            strng += str(i[0]) + " - " + str(i[1]) + "\n"

        #remove the trailing newline
        strng = strng[:-1]

        return strng

"""preformat dict as a nice string"""
def dict_to_string(dct):
    strng = ""

    for key in dct.keys():
        strng += str(key)
        strng += " -- "
        strng += str(dct[key])
        strng += "\n"

    return strng

"""gets a source word randomly from the dictionary""" ##2.0 SQL
def get_source():
    return database.get_random_source()

"""gets a timestamp for the current time"""
def get_timestamp():
    return time.time()

"""get the difference between two timestamps"""
def calc_timetaken(timestarted, timefinished):
    return timefinished - timestarted

"""calculate a score dictionary based on the number of correct guesses and time"""
def calc_score(guesses, errordict, source, totaltime):
    #convert time to seconds, multiply by correct guesses / max guesses, make a reasonable number

    #clear score
    scores = {}

    wordscorrect, wordsincorrect = sort_guesses(guesses, errordict)

    #set up vars
    totalwords = len(wordscorrect) + len(wordsincorrect)

    wordtime = totaltime / totalwords

    #correct words
    for word in wordscorrect:
        scores[word] = calc_score_word(word, source, scoremult, wordtime)

    #incorrect words
    for word in wordsincorrect:
        scores[word] = -calc_score_word(word, source, scoremult, wordtime)

    return scores

"""adds all the scores in the dictionary"""
def total_score(scoredict):
    total = 0

    for v in scoredict.keys():
        total += scoredict[v]

    return total

"""breaks guesses into two lists based on errordict"""
def sort_guesses(guesses, errordict):

        wordscorrect = guesses
        wordsincorrect = list(errordict.keys())

        for w in wordsincorrect:
            if w in wordscorrect:
                wordscorrect.remove(w)

        return (wordscorrect, wordsincorrect)

"""calculate the score for a single word"""
def calc_score_word(word, source, scoremult, wordtime):
    #(number of letters in word / number in source) multiplied by (reasonable number / time per word)
    return int(round((len(word) / len(source) * scoremult / wordtime), 0))

"""add score to score.log"""
def save_score(name, score):
    database.insert_hiscore(name, score)

"""sorts through the score table, gets the top ten, returns as a list of lists[name, score]"""###2.0 SQL
def get_top_ten():
    return database.get_top_ten_str()

###MAIN FUNCTION###
def main():
#testing!
    """
    print(test_guesses("errored", ["err", "red", "reed", "deer", "roe", "redo", "erred"]))

    print ("\nTest source is \"Admission\"\n")
    print ("Word containment testing.")
    print ("Should be true.")
    print (contains("admissioN", "sin"))
    print (contains("admisSion", "miss"))
    print (contains("admisSion", "sins"))
    print (contains("admission", "admin"))

    print ("\nShould be false.")
    print (contains("admission", "moon"))
    print (contains("admission", "dismiss"))
    print (contains("admission", "missing"))
    print (contains("admission", "soon"))

    print("\nShould return empty, that's how it's supposed to do. You made no mistakes!")
    print(test_guesses("admission", ["sin", "miss", "sins", "maid", "diss", "dim", "dam"]))

    print("\nShould return a variety of errors")
    print(test_guesses("admission", ["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"]))

    print("\nShould return not enough words")
    print(test_guesses("admission", ["mons"]))

    print("\nShould return too many words")
    print(test_guesses("admission", ["mons", "admin", "sim", "sion", "mad", "dam", "miss", "nois"]))

    print("\nShould return dupes")
    print(test_guesses("admission", ["mons", "mons", "mons", "mons", "mons", "mons", "mons"]))

    print("\nGuesses list to string")
    print(list_to_string(["sin", "miss", "sins", "maid", "diss", "dim", "dam"]))

    print("\nGuesses string to list")
    print(string_to_list("sin miss, sins\n\n\n maid,,,--'; diss dim dam"))

    print("\nErrors dict to string")
    print(dict_to_string(test_guesses("admission", ["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"])))

    print("\nSorting Guesses")
    print(sort_guesses(["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"], test_guesses("admission", ["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"])))

    print("\nCalculating Score")
    print(dict_to_string(calc_score(["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"], test_guesses("admission", ["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"]), "admission", 30)))
    print(total_score(calc_score(["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"], test_guesses("admission", ["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"]), "admission", 30)), "\n")

    print(dict_to_string(calc_score(["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"], test_guesses("admission", ["sin", "miss", "sins", "maid", "diss", "dim", "dam"]), "admission", 30)))
    print(total_score(calc_score(["mons", "sin", "sinus", "admission", "madmissions", "dm", "mad"], test_guesses("admission", ["sin", "miss", "sins", "maid", "diss", "dim", "dam"]), "admission", 30)), "\n")

    print("Should print scores as a list")
    print(get_top_ten())
    """    
