print("Hello! Please run the following setup commands that I can't:")
print("N.B.: You should probably be logged in as root")

print("""\nCreate user and database.""")
print("""\tCREATE USER "wguser" IDENTIFIED BY "wgpass";""")
print("""\tCREATE DATABASE "wordgame";""")

print("""\nGrant permissions to user for database.""")
print("""\tGRANT ALL ON wordgame.* TO "wguser" IDENTIFIED BY "wgpass";""")


print("""\nImporting database interface as db:""")
import DBI as db

print("""\nNow we can generate the tables. \nPlease run db.half_gen(21) to generate from .log files""")
print("""Or run db.helpme() to view help for my interface and testing functions.""")


