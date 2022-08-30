import asyncio
from v3data import GammaClient
from v3data.accounts import AccountInfo
from v3data.constants import XGAMMA_ADDRESS


class UserData:
    def __init__(self, chain: str, user_address: str):
        self.chain = chain
        self.gamma_client = GammaClient(chain)
        self.gamma_client_mainnet = GammaClient("mainnet")
        self.address = user_address.lower()
        self.decimal_factor = 10**18
        self.data = {}

    async def _get_data(self):
        query = """
        query userHypervisor($userAddress: String!) {
            user(
                id: $userAddress
            ){
                accountsOwned {
                    id
                    parent { id }
                    hypervisorShares {
                        hypervisor {
                            id
                            pool{
                                token0{ decimals }
                                token1{ decimals }
                            }
                            conversion {
                                baseTokenIndex
                                priceTokenInBase
                                priceBaseInUSD
                            }
                            totalSupply
                            tvl0
                            tvl1
                            tvlUSD
                        }
                        shares
                        initialToken0
                        initialToken1
                        initialUSD
                    }
                }
            }
        }
        """
        variables = {"userAddress": self.address}

        query_xgamma = """
        query userXgamma($userAddress: String!, $rewardHypervisorAddress: String!) {
            user(
                id: $userAddress
            ){
                accountsOwned {
                    id
                    parent { id }
                    gammaDeposited
                    gammaEarnedRealized
                    rewardHypervisorShares{
                        rewardHypervisor { id }
                        shares
                    }
                }
            }
            rewardHypervisor(
                id: $rewardHypervisorAddress
            ){
                totalGamma
                totalSupply
            }
        }
        """
        variables_xgamma = {
            "userAddress": self.address,
            "rewardHypervisorAddress": XGAMMA_ADDRESS,
        }

        hypervisor_response, xgamma_response = await asyncio.gather(
            self.gamma_client.query(query, variables),
            self.gamma_client_mainnet.query(query_xgamma, variables_xgamma),
        )

        self.data = {
            "hypervisor": hypervisor_response["data"],
            "xgamma": xgamma_response["data"],
        }


class UserInfo(UserData):
    async def output(self, get_data=True):

        if get_data:
            await self._get_data()

        hypervisor_data = self.data["hypervisor"]
        xgamma_data = self.data["xgamma"]

        if not (hypervisor_data.get('user') or xgamma_data.get('user')):
            return {}

        if xgamma_data.get('user'):
            xgamma_lookup = {
                account.pop("id"): account
                for account in self.data["xgamma"]["user"]["accountsOwned"]
            }
        else:
            xgamma_lookup = {}

        accounts = {}
        for accountHypervisor in hypervisor_data["user"]["accountsOwned"]:
            account_address = accountHypervisor["id"]
            account_info = AccountInfo(self.chain, account_address)
            account_info.data = {
                "hypervisor": {"account": accountHypervisor},
                "xgamma": {
                    "account": xgamma_lookup.get(account_address),
                    "rewardHypervisor": xgamma_data["rewardHypervisor"],
                },
            }
            accounts[account_address] = await account_info.output(get_data=False)

        return accounts
