import mysql.connector
import database_infos
import os

def add_user(cursor, connection):
    user_username = input('Enter user username: ').strip()
    user_password = input('Enter user password: ').strip()
    user_status = input('Enter user status: ').strip()
    try:
        cursor.execute('''
            insert into users (username, password, privilege)
            values (%s, %s, %s);
        ''', (user_username, user_password, user_status))
        cursor.execute('select * from users;')
        result = cursor.fetchall()[-1]
        print(f'{result[1]} is added successfully.')
        connection.commit()
    except mysql.connector.Error as err:
        print(f'!! ERROR: {err}')


def delete_user(cursor, connection):

    user_username = input('Enter user username: ').strip()
    user_status = input('Enter user status: ').strip()
    try:
        cursor.execute('select * from users where username like %s and privilege = %s',
                       (f'%{user_username}%', user_status))
        result = cursor.fetchone()
        cursor.execute('''
        delete from users
        where username like %s and privilege = %s;
        ''', (f'%{user_username}%', user_status))
        connection.commit()
        if result:
            print(f'ID: {result[0]}, Name: {result[1]}, password: {result[2]}, Status: {result[-1]} is removed from database.')
        else:
            print('No such user found.')
    except mysql.connector.Error as err:
        print(f'!! ERROR: {err}')

def show_users(cursor, connection):
    cursor.execute('select * from users;')
    result = cursor.fetchall()
    if result:
        for item in result:
            print(f'ID: {item[0]}, Name: {item[1]}, Password: {item[2]}, Status: {item[3]}')
            # return True
    else:
        print('No user exists.')
        # return False

def logout(cursor, connection):
    print('Logged out successfully')
    main(cursor, connection)

def admin_session(cursor, connection):
    print('Successfully logged in.')
    while True:
        print('Admin menu:')
        print('\t1. Register new user')
        print('\t2. Delete existing user')
        print('\t3. show existing users')
        print('\t4. Logout')
        choice = input('Choose an option: ').strip()
        if choice == '1':
            add_user(cursor, connection)
        elif choice == '2':
            delete_user(cursor, connection)
        elif choice == '3':
            show_users(cursor, connection)
        elif choice == '4':
            logout(cursor, connection)
        else:
            print('Not a valid option.')

def teacher_session(cursor, connection):
    print('Successfully logged in.')
    while True:
        print('Teacher menu:')
        print('\t1. Mark student register')
        print('\t2. View register')
        print('\t3. Logout')
        choice = input('Choose an option: ').strip()
        if choice == '1':
            cursor.execute("""
                select username from users 
                where privilege = 'student'
            """)
            result = cursor.fetchall()
            if result:
                for item in result:
                    status = input(f'Status for: {item[0]} (P *for present* /A *for absent* /L * for late*): ')
                    cursor.execute("""
                    insert into attendance(username, status)
                    values (%s, %s)
                    """, (item[0], status))
                    connection.commit()
                    print(f'{item[0]} is marked as {status}')
            else:
                print('No student found.')
        elif choice == '2':
            cursor.execute("""
            select username, date, status from attendance
            """)
            result = cursor.fetchall()
            if cursor.rowcount < 1:
                print('No record in the database')
            else:
                for item in result:
                    print(f'{item[0]} was {item[2]} in {item[1]}')
        elif choice == '3':
            print('Logout successfully')
            main(cursor, connection)
        else:
            print('Not a valid choice')

def student_session(cursor, connection, student):
    print('Successfully logged in.')
    while True:
        print('Student menu:')
        print('\t1. View attendance')
        print('\t2. download attendance')
        print('\t3. Logout')
        choice = input('Choose an option: ').strip()
        if choice == '1':
            cursor.execute('''
            select * from attendance
            where username = %s;
            ''', (student[1], ))
            result = cursor.fetchall()
            if result:
                for item in result:
                    print(f'Name: {item[1]}, Date: {str(item[2])}, Status: {item[3]}')
            else:
                print('User not attended in any classes')
        elif choice == '2':
            os.chdir(os.getcwd() + '\\student_registers')
            with open(f'{student[1]}.txt', 'w') as file:
                cursor.execute('''
                    select * from attendance
                    where username = %s;
                ''', (student[1],))
                result = cursor.fetchall()
                if result:
                    for item in result:
                        print(f'Name: {item[1]}, Date: {item[2]}, Status: {item[-1]}')
                        file.write(str(item) + '\n')
                        print('Downloaded successfully')
                else:
                    print('User not attended in any classes')
        elif choice == '3':
            logout(cursor, connection)
        else:
            print('Not a valid option')

def auth_teacher(cursor, connection):
    print('teahcer Login\n')
    username = input('Enter your username: ').strip()
    password = input('Enter your password: ').strip()
    cursor.execute('''
    select * from users 
    where username like %s and password = %s and privilege = 'teacher'
    ''', (f'%{username}%', password))
    result = cursor.fetchone()
    if result:
        teacher_session(cursor, connection)
    else:
        print('login not recognized')


def auth_admin(cursor, connection):
    print('Admin Login\n')
    username = input('Enter your username: ').strip()
    password = input('Enter your password: ').strip()

    if username == 'root' and password == 'mehrafarin81':
        admin_session(cursor, connection)
    else:
        print('Not a valid username or password.')

def auth_student(cursor, connection):
    print('Student Login\n')
    username = input('Enter your username: ').strip()
    password = input('Enter your password: ').strip()
    cursor.execute('''
    select * from users
    where username = %s and password = %s and privilege = 'student';
    ''', (username, password))
    student = cursor.fetchone()
    if cursor.rowcount < 1:
        print('Login not recognized.')
    else:
        student_session(cursor, connection, student)

def main(cursor, connection):
    print('\nWelcome to university management system.\n')
    print('1. Login as student')
    print('2. Login as teacher')
    print('3. Login as admin')
    choice = input('choose an option: ').strip()
    if choice == '1':
        auth_student(cursor, connection)
    elif choice == '2':
        auth_teacher(cursor, connection)
    elif choice == '3':
        auth_admin(cursor, connection)
    else:
        print('Not a valid option.')


if __name__ == '__main__':
    try:
        connection = mysql.connector.connect(
            host = database_infos.host,
            user = database_infos.user,
            password = database_infos.password,
            database = database_infos.database
        )
    except mysql.connector.Error as err:
        print(f'!! ERROR: {err}')

    cursor = connection.cursor(buffered=True)

    while True:
        main(cursor, connection)
