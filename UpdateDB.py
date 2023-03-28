import sqlite3

banco = sqlite3.connect('primeiro_banco.db')

cursor = banco.cursor()

# cursor.execute("CREATE TABLE waifus (id integer, nome text, anime integer, level integer, afinidade integer, EXP integer)")

cursor.execute("INSERT INTO waifus VALUES('129', 'Maki Oze', 'Fire Force', 1, 0, 1)")

banco.commit()
# banco.close()
# print('Os dados foram removidos com sucesso!!')
# except sqlite3.Error as erro:
# print("Erro ao excluir: ", erro)

cursor.execute('''SELECT * FROM waifus''')
print(cursor.fetchall())
