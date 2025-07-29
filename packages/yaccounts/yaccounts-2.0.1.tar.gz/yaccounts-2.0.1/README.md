# yaccounts-wd Package
#### Scripts for generating BYU accounting reports with the new Workday system

## Installation
It is recommended that you first create a Python virtual environment to avoid conflicts with other packages. 

    python3 -m venv venv

Activate the virtual environment in your terminal (this needs to be done each time you open a new terminal session):
- On Windows:
    ```
    venv\Scripts\activate
    ```
- On macOS/Linux:
    ```
    source venv/bin/activate
    ```

Then install the package using pip:

    pip install yaccounts


## Command-Line Usage

1. **First run Chrome.**  This will run chrome with a remote debugging port open, and uses a new user profile so that it does not interfere with your normal Chrome profile.  When this window opens, you will need to log in to Workday with your BYU credentials, then return to the terminal and hit enter to continue.
    
        yaccounts run-chrome

2. **Actual Report**. Then you can run the following to collect month-by-month actuals for a given grant.  You may want to look at the next step and run the payroll data collection first.

        yaccounts report-actuals GR01410

3. **Payroll Data**. You can add payroll data to your report by first running the the following command to collect payroll data for all of your grants for the year, which will generate a file called *payroll_2025.pkl*.

        yaccounts get-payroll

    Provide this payroll data to the actuals report by running:

        yaccounts report-actuals GR01410 --payroll_pkl payroll_2025.pkl

## Python Usage

You can also use the package in Python code.  First, install the package as described above, then you can use it like this:

```python

from yaccounts_wd import Account, PayrollData, run_chrome, get_chrome_webdriver


def main():
    run_chrome()

    dr = get_chrome_webdriver()

    payroll = PayrollData(2025)
    payroll.get_workday_data(dr)

    account = Account("GR00227", 2025)
    account.get_workday_data(dr)
    account.add_payroll_data(payroll)
    account.to_excel()
```