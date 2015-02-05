p_usrdict = "/usr/share/dict/words"
p_guessdict = "guessdict.log"
p_tempsourcedict = "tmpsourcedict.log"
p_sourcedict = "sourcedict.log"


import MyUtils.py as MySQL

config = {'DB_HOST': '127.0.0.1', 'DB_USER': 'WGUser', 'DB_PASSWD': 'WGUPass', 'DB': 'WordGameDB' }

#Access DB like so:
#with MySQL.UseDatabase(config) as cursor:
#    SQL = """[SQL COMMAND %s %s %s]"""
#    cursor.execute(SQL, [%s1], [%s2], [%s3])

"""Generate dictionaries"""###2.0 REM
def generate_dicts():
    gen_guess_dict(p_usrdict)
    gen_tmpsource_dict(p_guessdict)
    gen_source_dict(p_tempsourcedict)
    print("Dictionaries generated to file!")
    load_dicts(p_sourcedict, p_guessdict)

"""Generate a file with all the possible guess words""" ###2.0 REM
def gen_guess_dict(dictionaryfilepath):
    ##open the words file
    with open (dictionaryfilepath) as words:
        ##open the dictionary
            with open (pguessdict, "w") as guessdict:
                for word in words:
                    word = word.strip()

                    ##if it's not a stupid word
                    if "'" not in word and "é" not in word and "Å" not in word:
                        ##if it's more than 3 letters, toss it in
                        if len(word) >= lenguess:
                            print (word, file = guessdict)

"""Generate a file with all the long enough source words"""###2.0 REM
def gen_tmpsource_dict(guessdictfilepath):
    ##if it's more than 7, add it to the temp
    with open (guessdictfilepath) as guessdict:
        with open (p_tempsourcedict, "w") as tempdict:
            for word in guessdict:
                word = word.strip()

                if len(word) >= lensource:
                    print (word, file = tempdict)

"""Generate a file with source words that have enough answers"""###2.0 REM
def gen_source_dict(tempdictfilepath):
    with open (tempdictfilepath) as tempdict:
        with open (p_sourcedict, "w") as sourcedict:
                for word in tempdict:
                        word = word.strip()

                        #check that there are 7 words that make this one in the guess dictionary
                        if test_source(word):
                                #print ("Valid source found!")
                                print(word, file = sourcedict)

"""Checks that a source word has 7 possible answers, returns a bool"""###2.0 REM
def test_source(source):
    #print (source)
    count = 0
    with open (p_guessdict, "r") as guessdict:
        for word in guessdict:
            word = word.strip()
            if word != source:
                if contains(source, word):
                    count += 1
                    #print (word, True)
                    if count >= numguess: return True
    return False

###MAIN FUNCTION###
def main():
#testing!
