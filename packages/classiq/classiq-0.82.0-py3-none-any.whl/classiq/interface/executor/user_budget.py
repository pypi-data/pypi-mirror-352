import datetime
from collections import defaultdict
from typing import Optional

import pydantic
from pydantic import ConfigDict, Field

from classiq.interface.helpers.versioned_model import VersionedModel


class UserBudget(VersionedModel):
    provider: str
    currency_code: str
    organization: Optional[str] = Field(default=None)
    available_budget: float
    used_budget: float
    last_allocation_date: datetime.datetime

    model_config = ConfigDict(extra="ignore")


class UserBudgets(VersionedModel):
    budgets: list[UserBudget] = pydantic.Field(default=[])

    def print_budgets(self) -> None:
        def format_header() -> str:
            return f"| {'Provider':<20} | {'Available Budget':<18} | {'Used Budget':<18} | {'Currency':<8} |"

        def format_row(
            provider: str, available: float, used: float, currency: str
        ) -> str:
            return f"| {provider:<20} | {available:<18.3f} | {used:<18.3f} | {currency:<8} |"

        table_data: dict = defaultdict(
            lambda: {"used": 0.0, "available": 0.0, "currency": "USD"}
        )

        for budget in self.budgets:
            provider = budget.provider
            table_data[provider]["available"] += budget.available_budget
            table_data[provider]["used"] += budget.used_budget
            table_data[provider]["currency"] = budget.currency_code

        line = "=" * 77
        print(line)  # noqa: T201
        print(format_header())  # noqa: T201
        print(line)  # noqa: T201

        for provider, values in table_data.items():
            print(  # noqa: T201
                format_row(
                    provider, values["available"], values["used"], values["currency"]
                )
            )

        print(line)  # noqa: T201
