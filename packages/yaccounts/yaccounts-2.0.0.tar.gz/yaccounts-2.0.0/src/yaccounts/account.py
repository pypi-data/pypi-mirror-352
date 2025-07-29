from datetime import datetime
from decimal import Decimal
import enum
import pathlib

from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import SheetFormatProperties
import pandas as pd

from .payroll import PayrollData
from .config import CACHE_WORKDAY_DATA
from .run_report import run_grant_report
from .yutils import TermColors, print_color, retry, workday_str_amount_to_decimal, error


class AccountCategory(enum.Enum):
    """Enum for account categories."""

    BENEFITS = "Benefits"
    INDIRECT_COSTS = "Indirect Costs"
    SUPPLIES = "Supplies"
    WAGES = "Wages"
    STUDENT_AID = "Student Aid"
    TRAVEL = "Travel"
    TOTAL = "Total"


class _ColumnIndices(enum.Enum):
    """Enum for column indices in the DataFrame."""

    CATEGORY = 1
    BUDGET = 2
    PREV_ACTUALS = 3
    JAN = 4
    FEB = 5
    MAR = 6
    APR = 7
    MAY = 8
    JUN = 9
    JUL = 10
    AUG = 11
    SEP = 12
    OCT = 13
    NOV = 14
    DEC = 15
    TOTAL_THIS_YEAR = 16
    BALANCE = 17


_CATEGORY_ORDER = [
    AccountCategory.WAGES,
    AccountCategory.BENEFITS,
    AccountCategory.STUDENT_AID,
    AccountCategory.SUPPLIES,
    AccountCategory.TRAVEL,
    AccountCategory.INDIRECT_COSTS,
    AccountCategory.TOTAL,
]


def _workday_category_to_enum(category):
    """Convert a workday category to an AccountCategory enum."""
    lookup = {
        "BYU Grants: Benefits": AccountCategory.BENEFITS,
        "BYU Grants: Indirect Costs": AccountCategory.INDIRECT_COSTS,
        "BYU Grants: Materials and Supplies": AccountCategory.SUPPLIES,
        "BYU Grants: Salaries and Wages": AccountCategory.WAGES,
        "BYU Grants: Student Aid": AccountCategory.STUDENT_AID,
        "BYU Grants: Travel": AccountCategory.TRAVEL,
        "Total": AccountCategory.TOTAL,
    }
    if category in lookup:
        return lookup[category]
    else:
        raise ValueError(f"Unknown category: {category}. Please update the lookup.")


class Account:
    def __init__(self, account_code, year):

        self.account_code = account_code
        if not self.account_code.startswith("GR"):
            error(
                f"Account code {self.account_code} does not start with 'GR'. "
                "Other account codes are not supported yet."
            )
        self.year = year

        self._df = None

    def get_workday_data(self, dr):
        actuals_cached_path = pathlib.Path("actuals.pkl")

        # Get actuals
        if actuals_cached_path.exists() and CACHE_WORKDAY_DATA:
            print("Loading actuals from cache...")
            self._df = pd.read_pickle(actuals_cached_path)
            # self.actuals = self.actuals_df.set_index("Category").to_dict(orient="index")
        else:
            self._get_actuals_data(dr)
            self._df.to_pickle("actuals.pkl")

        self._process_workday_data()

    def _process_workday_data(self):
        ############### Clean up actuals_df ###############
        # Map each category to an order number
        order_map = {category: idx for idx, category in enumerate(_CATEGORY_ORDER)}
        self._df["Order"] = self._df["Category"].map(order_map)

        # Sort by the order
        self._df = self._df.sort_values(by="Order").drop(columns=["Order"])
        self._df = self._df.reset_index(drop=True)

        # YTD column is the sum of all months
        self._df["YTD"] = self._df[
            [datetime(1900, month, 1).strftime("%b") for month in range(1, 13)]
        ].sum(axis=1)

        # Balance is Budget - Prev Actuals - YTD
        self._df["Balance"] = (
            self._df["Budget"] - self._df["Prev Actuals"] - self._df["YTD"]
        )

    def add_payroll_data(self, payroll_data):
        """Add payroll data to the account DataFrame."""
        print_color(TermColors.BLUE, "Adding payroll data to the actuals report")

        if not isinstance(payroll_data, PayrollData):
            error(
                "payroll_data must be an instance of PayrollData. "
                f"Got {type(payroll_data)} instead."
            )

        payroll_df = payroll_data.df

        ##################### Process payroll_df #####################
        print(f"There are {len(payroll_df)} payroll entries.")

        # Filter down to relevant grant, where 'Grant' starts with self.account_code
        payroll_df = payroll_df[
            payroll_df["Grant"].str.startswith(f"{self.account_code} ")
        ].copy()
        print(f"There are {len(payroll_df)} payroll entries for {self.account_code}.")

        # Add a 'Month' column based on 'Budget Date'
        payroll_df["Month"] = pd.to_datetime(payroll_df["Budget Date"]).dt.month

        # Clean the 'Amount' column
        payroll_df["Amount"] = payroll_df["Amount"].apply(workday_str_amount_to_decimal)

        # Step 2: Group by Employee and Month
        payroll_summary = (
            payroll_df.groupby(["Employee", "Month"])["Amount"].sum().reset_index()
        )

        # Step 3: Pivot: one row per Employee, one column per month
        # and format the month names
        payroll_pivot = payroll_summary.pivot(
            index="Employee", columns="Month", values="Amount"
        ).fillna(0)
        month_cols = [datetime(1900, m, 1).strftime("%b") for m in range(1, 13)]
        payroll_pivot.columns = [
            datetime(1900, int(m), 1).strftime("%b") for m in payroll_pivot.columns
        ]

        # Make sure all months are there
        for m in month_cols:
            if m not in payroll_pivot.columns:
                payroll_pivot[m] = Decimal(0)

        # Prepare the df for merging with actuals_df
        payroll_pivot["Budget"] = ""
        payroll_pivot["Prev Actuals"] = ""
        payroll_pivot["Balance"] = ""
        payroll_pivot["YTD"] = payroll_pivot[month_cols].sum(axis=1)
        # Intent employee names a bit
        payroll_pivot["Category"] = payroll_pivot.index.map(lambda x: f"    {x}")
        final_columns = (
            ["Category", "Budget", "Prev Actuals"] + month_cols + ["YTD", "Balance"]
        )
        payroll_pivot = payroll_pivot[final_columns]
        print(
            f"There is data for {len(payroll_pivot)} employees within these payroll entries."
        )

        # Merge with the actuals_df
        wages_index = self._df.index[self._df["Category"] == AccountCategory.WAGES][0]
        before = self._df.iloc[: wages_index + 1]
        after = self._df.iloc[wages_index + 1 :]
        self._df = pd.concat([before, payroll_pivot, after], ignore_index=True)

    def to_excel(self, output_path=None):
        if output_path is None:
            output_path = f"{self.account_code}_{self.year}.xlsx"
        print_color(TermColors.GREEN, f"Creating {output_path}")

        formatted_df = self._df.copy()

        # Convert category enum to string for Excel export
        formatted_df["Category"] = formatted_df["Category"].apply(
            lambda x: x.value if isinstance(x, AccountCategory) else str(x)
        )

        # Replace NaN values with 0
        formatted_df = formatted_df.fillna(Decimal("0.00"))

        # Convert all columns except 'Category' to float
        for col in formatted_df.columns:
            if col != "Category":
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: float(x) if x != "" else ""
                )

        formatted_df.to_excel(output_path, index=False, engine="openpyxl")
        self._format_excel(output_path)

    def _format_excel(self, excel_filename):
        """Format the Excel file with specific styles."""
        wb = load_workbook(excel_filename)
        ws = wb.active
        currency_format = "#,##0.00"

        # Insert Title Row
        ws.insert_rows(1)
        title_text = f"{self.account_code} - Year {self.year} (Generated {datetime.now().strftime('%b %d, %Y')})"
        ws.cell(row=1, column=1).value = title_text

        num_columns = ws.max_column
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_columns)

        title_cell = ws.cell(row=1, column=1)
        title_cell.font = Font(size=18, bold=True)
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        # Define a thin black border
        thin_border = Border(
            left=Side(style="thin", color="000000"),
            right=Side(style="thin", color="000000"),
            top=Side(style="thin", color="000000"),
            bottom=Side(style="thin", color="000000"),
        )

        # === Insert new header row ===
        ws.insert_rows(2)  # Insert a new row 2

        # Reassign header values manually after insert
        headers = [
            "Category",
            "Budget",
            "Prev Actuals",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
            "YTD",
            "Balance",
        ]

        for col, header_text in enumerate(headers, start=1):
            ws.cell(row=3, column=col).value = header_text

        # Add "Actuals" merged across Jan to YTD
        first_actuals_col = _ColumnIndices.JAN.value  # 4
        last_actuals_col = _ColumnIndices.TOTAL_THIS_YEAR.value  # 16
        ws.merge_cells(
            start_row=2,
            start_column=first_actuals_col,
            end_row=2,
            end_column=last_actuals_col,
        )
        actuals_cell = ws.cell(row=2, column=first_actuals_col)
        actuals_cell.value = "Actuals"
        actuals_cell.alignment = Alignment(horizontal="center", vertical="center")
        actuals_cell.font = Font(bold=True)

        # Apply borders to the merged "Actuals" cells
        for col in range(first_actuals_col, last_actuals_col + 1):
            ws.cell(row=2, column=col).border = thin_border

        # Merge vertically: Category, Budget, Prev Actuals, Balance
        for col in [
            _ColumnIndices.CATEGORY.value,
            _ColumnIndices.BUDGET.value,
            _ColumnIndices.PREV_ACTUALS.value,
            _ColumnIndices.BALANCE.value,
        ]:
            ws.merge_cells(start_row=2, start_column=col, end_row=3, end_column=col)
            merged_cell = ws.cell(row=2, column=col)
            merged_cell.value = headers[col - 1]  # Set correct text!
            merged_cell.alignment = Alignment(horizontal="center", vertical="center")
            merged_cell.font = Font(bold=True)

            # Apply borders to the merged cells
            ws.cell(row=2, column=col).border = thin_border
            ws.cell(row=3, column=col).border = (
                thin_border  # Also border the lower merged part
            )

        # Apply borders to all header cells in row 3
        for col in range(1, num_columns + 1):
            cell = ws.cell(row=3, column=col)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(bold=True)
            cell.border = thin_border

        # Merge vertically: Category, Budget, Prev Actuals, Balance
        for col in [
            _ColumnIndices.CATEGORY.value,
            _ColumnIndices.BUDGET.value,
            _ColumnIndices.PREV_ACTUALS.value,
            _ColumnIndices.BALANCE.value,
        ]:
            ws.merge_cells(start_row=2, start_column=col, end_row=3, end_column=col)
            merged_cell = ws.cell(row=2, column=col)
            merged_cell.value = headers[col - 1]  # Set correct text!
            merged_cell.alignment = Alignment(horizontal="center", vertical="center")
            merged_cell.font = Font(bold=True)

        # Style the second header row (row 3)
        for col in range(1, num_columns + 1):
            header_cell = ws.cell(row=3, column=col)
            header_cell.alignment = Alignment(horizontal="center", vertical="center")
            header_cell.font = Font(bold=True)

        # Freeze top 3 rows
        ws.freeze_panes = ws["A4"]

        # === Format the data rows ===
        fill_5 = PatternFill(
            start_color="F2F2F2", end_color="F2F2F2", fill_type="solid"
        )
        fill_15 = PatternFill(
            start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"
        )
        fill_total = PatternFill(
            start_color="595959", end_color="595959", fill_type="solid"
        )
        yellow_fill = PatternFill(
            start_color="FFFF00", end_color="FFFF00", fill_type="solid"
        )

        rows_to_group = []
        shade_toggle = True

        for idx, row in enumerate(
            ws.iter_rows(min_row=4, min_col=1), start=4
        ):  # Data now starts at row 4
            category_cell = row[0]
            is_employee = isinstance(
                category_cell.value, str
            ) and category_cell.value.startswith("    ")

            if not is_employee:
                fill = fill_5 if shade_toggle else fill_15
                for cell in row:
                    cell.fill = fill
                shade_toggle = not shade_toggle
            else:
                rows_to_group.append(idx)

            for cell in row[1:]:
                cell.number_format = currency_format

        if rows_to_group:
            start_row = min(rows_to_group)
            end_row = max(rows_to_group)
            ws.row_dimensions.group(start_row, end_row, outline_level=1, hidden=False)

        ws.sheet_format = SheetFormatProperties(outlineLevelRow=1)

        # Set column widths
        ws.column_dimensions[get_column_letter(_ColumnIndices.CATEGORY.value)].width = (
            20
        )
        ws.column_dimensions[get_column_letter(_ColumnIndices.BUDGET.value)].width = 13
        ws.column_dimensions[
            get_column_letter(_ColumnIndices.PREV_ACTUALS.value)
        ].width = 13
        ws.column_dimensions[
            get_column_letter(_ColumnIndices.TOTAL_THIS_YEAR.value)
        ].width = 13
        ws.column_dimensions[get_column_letter(_ColumnIndices.BALANCE.value)].width = 13
        for month in range(_ColumnIndices.JAN.value, _ColumnIndices.DEC.value + 1):
            ws.column_dimensions[get_column_letter(month)].width = 12

        # Highlight the total row
        total_row = len(ws["A"])
        for cell in ws[total_row]:
            cell.fill = fill_total
            cell.font = Font(bold=True, color="FFFFFF")

        balance_cell = ws.cell(row=total_row, column=_ColumnIndices.BALANCE.value)
        balance_cell.fill = yellow_fill
        balance_cell.font = Font(bold=True, color="000000")

        wb.save(excel_filename)

    def _get_actuals_data(self, dr):
        """Use workday to get actuals"""

        # Define columns: 'category', then months 1-12
        columns = (
            ["Category", "Budget", "Prev Actuals"]
            + [datetime(1900, month, 1).strftime("%b") for month in range(1, 13)]
            + ["YTD", "Balance"]
        )
        self._df = pd.DataFrame(columns=columns)

        end_month = 12 if self.year != datetime.now().year else datetime.now().month
        month_year_list = [
            datetime(self.year, month, 1) for month in range(1, end_month + 1)
        ]
        # retry(run_payroll_report, retries=3, exception=Exception, dr=dr)

        for month in month_year_list:
            budget, actuals_prev, actuals = run_grant_report(
                dr, self.account_code, month
            )

            # Covert to category enums
            budget = {_workday_category_to_enum(k): v for k, v in budget.items()}
            actuals_prev = {
                _workday_category_to_enum(k): v for k, v in actuals_prev.items()
            }
            actuals = {_workday_category_to_enum(k): v for k, v in actuals.items()}

            for category, value in actuals.items():
                # If the actuals_df does not have a row for this category, add it
                if category not in self._df["Category"].values:
                    new_row = {"Category": category}
                    self._df = pd.concat(
                        [self._df, pd.DataFrame([new_row])], ignore_index=True
                    )

                # Update the actuals_df for this category and month
                self._df.loc[self._df["Category"] == category, month.strftime("%b")] = (
                    value
                )

                # If month is January, also update budget and previous actuals
                if month.month == 1:
                    self._df.loc[self._df["Category"] == category, "Budget"] = budget[
                        category
                    ]
                    self._df.loc[self._df["Category"] == category, "Prev Actuals"] = (
                        actuals_prev[category]
                    )
