import MyUtils as MySQL

p_usrdict = "words.txt"
p_guessdict = "guessdict.log"
p_tempsourcedict = "tmpsourcedict.log"
p_sourcedict = "sourcedict.log"
p_scores = "scores.log"

sourcelist = list()
guesslist = list()
scorelist = list()

lensource = 7
lenguess = 3
numguess = 7

config = {'DB_HOST': '127.0.0.1', 'DB_USER': 'wguser', 'DB_PASSWD': 'wgpass', 'DB': 'wordgame' }

#Access DB like so:
#with MySQL.UseDatabase(config) as cursor:
#    SQL = """[SQL COMMAND %s %s %s]"""
#    cursor.execute(SQL, ([%s1], [%s2], [%s3]))

###Dictionaries###
"""Put the dictionaries into lists"""
def load_dicts(sourcefilepath, guessfilepath):
    with open(sourcefilepath, "r") as source:
        for word in source:
            sourcelist.append(word.strip())

    with open(guessfilepath, "r") as guess:
        for word in guess:
            guesslist.append(word.strip())
    print ("Dictionaries loaded from file!")

"""Generate dictionaries"""
def generate_dicts():
    gen_guess_dict(p_usrdict)
    gen_tmpsource_dict(p_guessdict)
    gen_source_dict(p_tempsourcedict)
    print("Dictionaries generated to file!")
    load_dicts(p_sourcedict, p_guessdict)

"""Generate a file with all the possible guess words"""
def gen_guess_dict(dictionaryfilepath):
    print("Generating guesses")
    wordcount = 0
    ##open the words file
    with open (dictionaryfilepath) as words:
        ##open the dictionary
            with open (p_guessdict, "w") as guessdict:
                for word in words:
                    word = word.strip()
                    ##if it's not a stupid word
                    if "'" not in word and "é" not in word and "Å" not in word:
                        ##if it's more than 3 letters, toss it in
                        if len(word) >= lenguess:
                            print (word, file = guessdict)
                            wordcount += 1
                            if wordcount % 1000 == 0:
                                print("\t ", wordcount)
    print("Guesses done")
                            
"""Generate a file with all the long enough source words"""
def gen_tmpsource_dict(guessdictfilepath):
    print("Generating temp source")
    wordcount = 0
    ##if it's more than 7, add it to the temp
    with open (guessdictfilepath) as guessdict:
        with open (p_tempsourcedict, "w") as tempdict:
            for word in guessdict:
                word = word.strip()

                if len(word) >= lensource:
                    print (word, file = tempdict)
                    wordcount += 1
                    if wordcount % 1000 == 0:
                        print("\t ", wordcount)
                        
    print("Temp source done")

"""Generate a file with source words that have enough answers"""
def gen_source_dict(tempdictfilepath):
    print("Generating source")
    wordcount = 0
    with open (tempdictfilepath) as tempdict:
        with open (p_sourcedict, "w") as sourcedict:
                for word in tempdict:
                        word = word.strip()
                        #check that there are 7 words that make this one in the guess dictionary
                        if test_source(word):
                                #print ("Valid source found!")
                                print(word, file = sourcedict)
                                wordcount += 1
                                if wordcount % 1000 == 0:
                                    print("\t ", wordcount)
                                    
    print("Source done")

"""Checks that a source word has 7 possible answers, returns a bool"""
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


"""makes sure dictionaries are loaded into lists"""
def check_dict_lists():
    #if they're empty, load them
    if len(sourcelist) == 0 or len(guesslist) == 0:
        load_dicts(p_sourcedict, p_guessdict)
        return True
    #otherwise everything is fine
    return True

###Database interaction for dictionaries###
"""regenerates an empty database dict"""
def create_db_dict():
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""drop table dict;""")
        cursor.execute("""create table dict(dict_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, word_sn VARCHAR(24));""")
        print("Database dict created!")


"""Pulls word from guessdict(inherently includes sources) and inserts them"""
def dict_to_db():
    if check_dict_lists():
        with MySQL.UseDatabase(config) as cursor:
            #All short words of guesslist
            for guess in guesslist:
                if len(guess) < 7:
                    cursor.execute("""INSERT INTO dict(word_sn) VALUES(%s);""", (guess,))
            #Any other words in sourcelist (filtered for unwinnable)
            for source in sourcelist:
                cursor.execute("""INSERT INTO dict(word_sn) VALUES(%s);""", (source,))     
    print("Dictionaries inserted into database!")

"""checks if guess is in database"""
def check_guess(guess):
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""SELECT * from dict where word_sn = %s;""",(guess,))
        if len(cursor.fetchall()) == 0:
            return False
        else: return True
        
"""selects a random source word from the database"""
def random_source():
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""SELECT word_sn FROM dict WHERE CHAR_LENGTH(word_sn) >= 7 ORDER BY RAND() LIMIT 1;""")
        return cursor.fetchall()[0][0]

###Hiscores###
"""loads all scores into a list for sorting"""
def load_scores():
    #load the scores into a list of lists as in [[name, score], [name1, score1]]
    with open(p_scores, "r") as scores:
        line = scores.read().splitlines()
        for item in line:
            if item != "":
                name, score = item.split("-")
                scorelist.append([str(name).strip(), int(score)])
    print("Scores loaded from file!")
                
def check_score_list():
    #if it's empty, load it
    if len(scorelist) == 0:
        load_scores()
        return True
    #otherwise everything is fine
    return True

###Database interaction for hiscores###
"""regenerates an empty database hiscore"""
def create_db_hiscore():
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""drop table hiscore;""")
        cursor.execute("""create table hiscore(hiscore_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, score_amt INT NOT NULL, player_sn varchar(16) NOT NULL);""")
    print("Database hiscore created!")

"""inserts all scores into dict from list"""
def hiscore_to_db():
    if check_score_list():
        with MySQL.UseDatabase(config) as cursor:
            for item in scorelist:
                cursor.execute("""INSERT INTO hiscore(player_sn, score_amt) VALUES(%s, %s);""", (item[0], item[1]))
    print("Scores inserted into database!")

"""adds a new hiscore to the db"""
def insert_hiscore(name, score):
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""INSERT INTO hiscore(player_sn, score_amt) VALUES(%s, %s);""", (str(name), int(score)))

"""pull top ten scores from database"""
def get_top_ten():
    with MySQL.UseDatabase(config) as cursor:
        cursor.execute("""SELECT player_sn, score_amt FROM hiscore ORDER BY score_amt DESC, hiscore_id ASC LIMIT 10;""")
        return cursor.fetchall();

"""preformat top ten as string"""
def top_ten_str():
    strng = ""
    for i in get_top_ten():
        strng += str(i[0]) + " - " + str(i[1]) + "\n"

    #remove the trailing newline
    strng = strng[:-1]

    return strng
    
###GENERATION FUNCTIONS: CAUTION###
def full_gen(key):
    #Protect from accidentally generation since it takes ages
    if (key != 42):
        print("ERROR INVALID KEY")
        return

    #Actual meat
    generate_dicts()
    half_gen(21)

def half_gen(key):
    #Protect from accidentally wiping and regenning dbs
    if (key != 21):
        print("ERROR INVALID KEY")
        return

    #Actual meat
    create_db_dict()
    dict_to_db()
    
    create_db_hiscore()
    hiscore_to_db()

def half_gen_dict(key):
    #Protect from accidentally wiping and regenning db
    if (key != 5):
        print("ERROR INVALID KEY")
        return
    #Actual meat
    create_db_dict()
    dict_to_db()
    
def half_gen_hiscore(key):
    #Protect from accidentally wiping and regenning db
    if (key != 10):
        print("ERROR INVALID KEY")
        return
    #Actual meat
    create_db_hiscore()
    hiscore_to_db()
    
###Main info###
"""
print("###NOTE###")
print("Assumes the following: \n\twordgame db exists.\n\twguser identified by wgupass exists.\n\tAll rights on wordgame granted to wguser")

print("\n###WORD###")
print("gen_dicts - generate dictionary.log files from words.txt")
print("create_db_dict - create empty dict database. (drops current db)")
print("dict_to_db - add the words from the list to the wordgame db")

print("\n###GAME###")
print("get_source - get a random source word")
print("check_guess(guess) - check if a guess is in the dictionary")

print("\n###SCORE###")
print("create_db_hiscore - create empty hiscore database. (drops current db)")
print("hiscore_to_db - add the scores from the lists to the wordgame db")
print("insert_hiscore(name, score) - add a new score to the wordgame db")
print("top_ten - query top ten from db")
print("top_ten_str - preformat top ten as string")

print("\n###DATABASE###")
print("full_gen(key) - run a complete regeneration of all files")
print("half_gen(key) - run generation from .log to db (assume both exist)")
print("half_gen_dict(key) - run dict generation from .log to db (assume both exist)")
print("half_gen_hiscore(key) - run score generation from .log to db (assume both exist)")
"""
