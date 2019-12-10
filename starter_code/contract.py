"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class MTMContract(Contract):
    """
    Created a new MTMContract for a specific Phoneline.
    """

    def __init__(self, start: datetime.date) -> None:
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates('MTMContract', float(0.05))
        self.bill.add_fixed_cost(float(50))


class TermContract(Contract):
    """
    Subclass of Contract, specifically for TermContract.
    === Public Attributes ===
    end:
        The end date of a contract
    months_passed:
        The number of months that have passed since the start date
    """
    end: datetime.datetime
    months_passed: int

    def __init__(self, start: datetime.date, end: datetime.datetime) -> None:
        """
        creates a new termcontract for a phoneline.
        """
        Contract.__init__(self, start)
        self.end = end
        self.months_passed = 0

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates('TermContract', float(0.1))
        if self.start.month == month and self.start.year == year:
            self.bill.add_fixed_cost(300)
        self.bill.add_fixed_cost(float(20))
        self.months_passed += 1

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        k = 0
        s = 100
        if self.bill.free_min < 100 and (
                ceil(call.duration / 60.0)) <= 100:
            self.bill.add_free_minutes((ceil(call.duration / 60.0)))
            k += (ceil(call.duration / 60.0))
        elif self.bill.free_min < 100 and (
                ceil(call.duration / 60.0)) > s:
            self.bill.add_free_minutes(100 - k)
            self.bill.add_billed_minutes(ceil(call.duration / 60.0) - 100)
        elif self.bill.free_min > 100:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None

        if self.months_passed >= 6:
            return 300 - self.bill.get_cost()
        else:
            return float(self.bill.get_cost())


class PrepaidContract(Contract):
    """
    Subclass of Contract, specific for PrepaidContract
        === Public Attributes ===
    Balance:
        The balance of the customer
    """
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        """
        Creates a new PrepaidContract for a phoneline
        """
        Contract.__init__(self, start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates('PrepaidContract', float(0.025))
        self.balance = self.balance + self.bill.get_cost()
        self.bill.add_fixed_cost(self.balance)
        if -10 < self.balance:
            # self.bill.add_fixed_cost(25)
            self.balance = self.balance - 25

    # self.bill.add_fixed_cost(-self.balance)
    # if -10 < self.bill.get_cost() < 0:
    #     self.bill.add_fixed_cost(25) #changed from .getcost to fixed
    # return None

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        if self.bill.get_cost() + self.balance < 0:
            return 0
        else:
            return self.bill.get_cost()


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
