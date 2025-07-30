from typing import Optional

from classiq.interface.backend.quantum_backend_providers import ProviderVendor
from classiq.interface.executor.user_budget import UserBudgets

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function

PROVIDER_MAPPER = {
    ProviderVendor.IONQ: "IONQ",
    ProviderVendor.IBM_QUANTUM: "IBMQ",
    ProviderVendor.AZURE_QUANTUM: "AZURE",
    ProviderVendor.AMAZON_BRAKET: "AMAZON",
    ProviderVendor.GOOGLE: "GOOGLE",
    ProviderVendor.ALICE_AND_BOB: "ALICE_AND_BOB",
    ProviderVendor.OQC: "OQC",
    ProviderVendor.INTEL: "INTEL",
    ProviderVendor.AQT: "AQT",
    ProviderVendor.IQCC: "IQCC",
    ProviderVendor.CLASSIQ: "CLASSIQ",
}


async def get_budget_async(
    provider_vendor: Optional[ProviderVendor] = None,
) -> UserBudgets:

    budgets_list = await ApiWrapper().call_get_all_budgets()
    if provider_vendor:
        provider = PROVIDER_MAPPER.get(provider_vendor, None)
        budgets_list = [
            budget for budget in budgets_list if budget.provider == provider
        ]

    return UserBudgets(budgets=budgets_list)


get_budget = syncify_function(get_budget_async)
