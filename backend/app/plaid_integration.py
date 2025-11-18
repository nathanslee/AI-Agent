import os
from typing import Dict, Any, List
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class PlaidIntegration:
    """Plaid banking integration for importing transactions"""

    def __init__(self):
        configuration = plaid.Configuration(
            host=self._get_plaid_environment(),
            api_key={
                'clientId': os.getenv("PLAID_CLIENT_ID"),
                'secret': os.getenv("PLAID_SECRET"),
            }
        )

        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_plaid_environment(self):
        """Get Plaid environment based on config"""
        env = os.getenv("PLAID_ENV", "sandbox")

        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "development": plaid.Environment.Development,
            "production": plaid.Environment.Production
        }

        return env_map.get(env, plaid.Environment.Sandbox)

    def create_link_token(self, user_id: str) -> str:
        """
        Create a Plaid Link token for the user to connect their bank.

        Args:
            user_id: User's unique ID

        Returns:
            Link token string
        """
        try:
            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="AI Database Assistant",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                )
            )

            response = self.client.link_token_create(request)
            return response.link_token

        except plaid.ApiException as e:
            raise Exception(f"Plaid API error: {e}")

    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """
        Exchange public token for access token.

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Dict with access_token and item_id
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = self.client.item_public_token_exchange(request)

            return {
                "access_token": response.access_token,
                "item_id": response.item_id
            }

        except plaid.ApiException as e:
            raise Exception(f"Plaid API error: {e}")

    def get_transactions(
        self,
        access_token: str,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get transactions from Plaid.

        Args:
            access_token: Plaid access token
            start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
            end_date: End date (YYYY-MM-DD), defaults to today

        Returns:
            List of transaction dicts
        """
        try:
            # Default to last 30 days
            if not end_date:
                end_date = datetime.now().date()
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    count=100
                )
            )

            response = self.client.transactions_get(request)

            # Convert to simple dicts
            transactions = []
            for txn in response.transactions:
                transactions.append({
                    "transaction_id": txn.transaction_id,
                    "name": txn.name,
                    "amount": float(txn.amount),
                    "date": str(txn.date),
                    "category": txn.category[0] if txn.category else "Other",
                    "pending": txn.pending,
                    "merchant_name": txn.merchant_name,
                })

            return transactions

        except plaid.ApiException as e:
            raise Exception(f"Plaid API error: {e}")


# Global Plaid integration instance
plaid_integration = PlaidIntegration()
