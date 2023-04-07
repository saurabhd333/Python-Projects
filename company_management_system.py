import sqlite3


class Employee: # abstract class
    def __init__(self, emp_id, name, age, department):
        self.emp_id = emp_id
        self.name = name
        self.age = age
        self.department = department

    def cal_annual_salary(self): # abstract method
        raise NotImplementedError("Child class must implement this abstract method.")


class HourlyEmployee(Employee):
    def __init__(self, emp_id, name, age, department, hourly_pay, working_hrs_per_week):
        Employee.__init__(self,emp_id, name, age, department)
        self.hourly_pay = hourly_pay
        self.working_hours_per_week = working_hrs_per_week

    # method to calculate salary
    def cal_annual_salary(self):
        self.annual_salary = self.working_hours_per_week * self.hourly_pay * 52
        return round(self.annual_salary, 2)


class SalariedEmployee(Employee):
    def __init__(self, emp_id, name, age, department, weekly_pay):
        Employee.__init__(self,emp_id, name, age, department)
        self.weekly_pay = weekly_pay

    # method to calculate salary
    def cal_annual_salary(self):
        self.annual_salary = self.weekly_pay * 52
        return round(self.annual_salary, 2)


class Manager(Employee):
    def __init__(self, emp_id, name, age, department, weekly_pay, manages_num_of_emp):
        Employee.__init__(self,emp_id, name, age, department)
        self.weekly_pay = weekly_pay
        self.manages_num_of_emp = manages_num_of_emp # no of emplyees who are gonna work under manager

    # calculating annual salary for manager
    def cal_annual_salary(self):
        salaried_emp = SalariedEmployee(self.emp_id, self.name, self.age, self.department, self.weekly_pay)
        self.manager_salary = salaried_emp.cal_annual_salary()
        return round(self.manager_salary, 2)


class Executive(Employee):
    def __init__(self, emp_id, name, age, department, weekly_pay, manages_num_of_emp):
        Employee.__init__(self,emp_id, name, age, department)
        self.weekly_pay = weekly_pay
        self.manages_num_of_emp = manages_num_of_emp # no of emplyees who are gonna work under executive

    # calculating annual salary for executive
    def cal_annual_salary(self):
        salaried_emp = SalariedEmployee(self.emp_id, self.name, self.age, self.department, self.weekly_pay)
        self.executive_bonus = 100 # extra bonus for executive
        self.executive_salary = salaried_emp.cal_annual_salary() + self.executive_bonus
        return round(self.executive_salary, 2)


class DBbase:
    _conn = None
    _cursor = None

    def __init__(self, db_name):
        self._db_name = db_name
        self.connect()

    def connect(self):
        self._conn = sqlite3.connect(self._db_name)
        self._cursor = self._conn.cursor()

    def execute_script(self, sql_string):
        self._cursor.executescript(sql_string)

    @property
    def get_cursor(self):
        return self._cursor

    @property
    def get_connection(self):
        return self._conn

    def close_db(self):
        self._conn.close()

    def reset_database(self):
        raise NotImplementedError("Must be implemented in the derived class")


class Company(DBbase):
    def __init__(self):
        super().__init__("company.sqlite")

    # hire function to add a record of a new employee in the database
    def hire(self,emp_id, name, age, department, salary, designation, manages_num_of_emp):
        try:
            super().connect()
            super().get_cursor.execute(
                """insert or ignore into Company(emp_id, name, age, 
                department, salary, designation, manages_num_of_emp) values (?,?,?,?,?,?,?);""",
                (emp_id, name, age, department, salary, designation, manages_num_of_emp))

            super().get_connection.commit()

            print("Added employee record successfully")
        except Exception as e:
            print("An error has occurred : {}".format(e))
        finally:
            super().close_db()

    # raise salary function to update the salary of a specific employee in the database
    def raise_salary(self, emp_id, salary):
        try:
            super().connect()
            super().get_cursor.execute("""update Company set salary = ?
                                        WHERE emp_id = ?;""",
                                       (salary, emp_id))

            super().get_connection.commit()
            print("Updated salary successfully!")
        except Exception as e:
            print("An error has occurred : {}".format(e))
        finally:
            super().close_db()

    # fire function to delete the record of a specific employee from the database
    def fire(self, emp_id):
        try:
            super().connect()
            super().get_cursor.execute("""delete FROM Company WHERE emp_id = ?;""", (emp_id,))
            super().get_connection.commit()
            print("Deleted employee record successfully")
            return True
        except Exception as e:
            print("An error has occurred : {}".format(e))
            return False
        finally:
            super().close_db()

    # view all or single employee's data
    def fetch_all_employee_data(self, emp_id=None):
        # if emp_id is null (or None), then get everything, else get by emp_id or get by question
        try:
            super().connect()
            if emp_id is not None:
                return super().get_cursor.execute("""SELECT * FROM Company WHERE emp_id = ? ;""",
                                                  (emp_id,)).fetchone()
            else:
                return super().get_cursor.execute("""SELECT * FROM Company;""").fetchall()
        except Exception as e:
            print("An error has occurred : {}".format(e))
        finally:
            super().close_db()

    def reset_database(self):
        sql = """
        DROP TABLE IF EXISTS Company;

        CREATE TABLE Company  (
            emp_id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            department TEXT NOT NULL,
            salary TEXT NOT NULL,
            designation TEXT NOT NULL,
            manages_num_of_emp INTEGER NOT NULL
        );
        """
        super().execute_script(sql)
        print("\ndatabase reset completed successfully!")

# calling reset_database to create the database
company = Company()
company.reset_database()


class CompanyMenu:
    def menu(self):
        # Company CRUD menu
        company = Company()

        action_menu = {
            "1": "Hire an employee",
            "2": "Raise employee's salary",
            "3": "Fire an employee",
            "4": "View the Company's employee details",
            "exit": "Exit the program"
        }
        # taking user input for action menu
        user_selection = ""
        while user_selection != "exit":
            print("********* Option List *********")
            for option in action_menu.items():
                print(option)
            user_selection = input("Select an option: ")

            # adding new employee details to the database
            if user_selection == '1':
                emp_id = int(input("Please enter the employee id of the new employee:"))
                name = input("Please enter the name of the new employee:")
                age = int(input("Please enter the age of the new employee:"))
                department = input("Please enter the department of the new employee:")
                emp_designation = input("Please enter the designation of the new employee (Manager or Executive):")
                manages_num_of_emp = int(input("Please enter the number of employees who would be managed by the new employee:"))

                # calculating employee's salary on basis of the employee's designation
                if emp_designation.lower() == 'manager':
                    weekly_pay = float(input("Please enter the weekly pay for the manager:"))
                    manager = Manager(emp_id, name, age, department, weekly_pay, manages_num_of_emp)
                    salary = "$" + str(manager.cal_annual_salary())
                else:
                    weekly_pay = float(input("Please enter the weekly pay for the executive:"))
                    executive = Executive(emp_id, name, age, department, weekly_pay, manages_num_of_emp)
                    salary = "$" + str(executive.cal_annual_salary())

                company.hire(emp_id, name, age, department, salary, emp_designation, manages_num_of_emp)
                print("********* Employee hired successfully! *********\n")

            # updating employee's salary in the database
            elif user_selection == '2':
                emp_id = int(input("Please enter the employee's id whose salary you want to update:"))
                weekly_pay = float(input("Please enter the revised weekly pay for the employee:"))
                revised_salary = weekly_pay * 52
                bonus = float(input("Please enter the annual bonus you want to give to the employee:"))
                revised_salary = "$" + str(revised_salary + bonus)
                company.raise_salary(emp_id, revised_salary)
                print("********* Employee's salary raised sucessfully! *********\n")

            # fire employee from the company
            elif user_selection == '3':
                emp_id = int(input("Please enter the employee's id whom you want to fire:"))
                company.fire(emp_id)
                print("********* Employee fired successfully! *********\n")

            # view all employees' data
            elif user_selection == '4':
                all_employee_data = company.fetch_all_employee_data()
                print(all_employee_data)
                print("********* Employees data completed! *********\n")

            else:
                if user_selection not in ['1','2','3','4','exit']:
                    print("Invalid selection. Please try again.")

cm = CompanyMenu()
cm.menu()










