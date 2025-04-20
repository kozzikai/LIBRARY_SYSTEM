"""
 pre_processing.py initializes the database using the schema provided and
 populates the Library database from the given books and borrowers csv files

 Usage(Update the environment variables in variables.env): python3 <Absolute path to pre_processing.py>
"""
import pymysql
from load_env import *

logger = logging.getLogger("PRE-PROCESSING")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
try:
    con = pymysql.connect(host=DB_HOST,
                          user=DB_USERNAME,
                          password=DB_PASSWORD,
                          unix_socket="/tmp/mysql.sock")
    cur = con.cursor()
    logger.info("Successfully connected to MySQL Server")
except:
    logger.error(
        "Failed to connect to MySQL Server. Please check credentials given in environment file"
    )
    exit(1)


def count_starting_quotes(str):
    count = 0
    for char in str:
        if char == '"':
            count += 1
        else:
            break
    return count


def balance_quotes(str):
    # Ensure the string starts and ends with a double quote
    if not str.startswith('"'):
        str = '"' + str
    if not str.endswith('"'):
        str = str + '"'

    if str.count('"') % 2 != 0:
        if count_starting_quotes(str) % 2 != 0:
            str = str + '"'
        else:
            str = '"' + str
    # Double every inner quote
    inner_string = str[1:-1].replace('"', '""')

    return '"' + inner_string + '"'


def main():
    with open(DB_SCHEMA_FILE, 'r') as file:
        sql_script = file.read()
        commands = sql_script.split(
            ';')  # Split by ';' to get individual commands

        for command in commands:
            if command.strip():  # Check if command is not empty
                logger.info(f"\nExecuting query '{command}'")
                cur.execute(command)

    con.commit()

    print("\n\n\n********* Database Initialization Done *********\n\n\n")

    book_file_obj = open(BOOKS_CSV_FILE, 'r', encoding="utf-8")
    book_file_text = list(book_file_obj)
    author_id = 0
    author_dict = {}

    for line in book_file_text[1:]:
        book_authors = []
        line = line.strip()
        column_list = line.split('\t')

        isbn10 = column_list[0]
        title = balance_quotes(column_list[2])
        authors = column_list[3]

        query = f"INSERT INTO {BOOK_TABLE} VALUES (\"{isbn10}\",{title})"
        logger.info(f"Executing insert query '{query}'")
        cur.execute(query)

        authors = authors.split(',')
        for author in authors:
            author_name = balance_quotes(author)
            if (author_name in author_dict.keys()):
                # Deal with duplicate author
                logger.info(f"Author Name {author_name}  already exists")
                # Lookup existing author_id and populate author_id variable
            else:
                # Add author to list
                author_id += 1
                author_dict[author_name] = author_id

                # Be sure to look up existing author if applicable
                query = f"INSERT INTO {AUTHOR_TABLE} VALUES (\"{str(author_id)}\",{author_name})"
                logger.info(f"Executing insert query '{query}'")
                cur.execute(query)

            if author_name not in book_authors:
                query = f"INSERT INTO {BOOK_AUTHOR_TABLE} VALUES (\"{str(author_dict[author_name])}\",\"{isbn10}\")"
                logger.info(f"Executing insert query '{query}'")
                cur.execute(query)
                book_authors.append(author_name)

    print(
        "\n\n\n********* BOOK, AUTHORS and BOOK_AUTHORS Tables Population Done *********\n\n\n"
    )
    con.commit()
    book_file_obj.close()

    borrower_file_obj = open(BORROWERS_CSV_FILE, 'r', encoding="utf-8")
    borrower_file_text = list(borrower_file_obj)

    for line in borrower_file_text[1:]:
        line = line.strip()
        column_list = line.split(',')

        card_id = column_list[0]
        ssn = column_list[1]
        name = balance_quotes(f"{column_list[2]} {column_list[3]}")
        address = balance_quotes(
            f"{column_list[5]}, {column_list[6]}, {column_list[7]}")
        phone = column_list[8]

        insert_query = f"INSERT INTO {BORROWER_TABLE} (Card_id, Ssn, Bname, Address, Phone) VALUES (\"{card_id}\",\"{ssn}\",{name},{address},\"{phone}\")"
        logger.info(f"Executing insert query '{insert_query}'")
        cur.execute(insert_query)

    con.commit()
    borrower_file_obj.close()

    print("\n\n\n********* BORROWER Table Population Done *********\n\n\n")


if __name__ == "__main__":
    main()
