#!/usr/bin/env python3
"""
Pocketful Stage 1 - Input Generators
Generates test inputs across stated ranges, edges and orderings.
"""

import random
import string
from typing import Dict, List, Any, Generator, Tuple
from dataclasses import dataclass

@dataclass
class TestInput:
    """A single test input with description"""
    description: str
    data: Any

class FixtureGenerator:
    """Generates valid and invalid fixtures for reset"""
    
    VALID_CURRENCIES = ["EUR", "USD", "JPY", "BHD"]
    VALID_MINOR_UNITS = [0, 2, 3]
    
    @staticmethod
    def valid_fixture() -> Dict:
        return {
            "currency": "EUR",
            "minor_units": 2,
            "users": [
                {
                    "id": "u_ada",
                    "email": "ada@example.com",
                    "password": "correct horse",
                    "display_name": "Ada",
                    "handle": "ada",
                    "balance": 10000
                },
                {
                    "id": "u_bob",
                    "email": "bob@example.com",
                    "password": "correct horse",
                    "display_name": "Bob",
                    "handle": "bob",
                    "balance": 2500
                }
            ],
            "payments": [
                {
                    "id": "p_1",
                    "from_user_id": "u_ada",
                    "to_user_id": "u_bob",
                    "amount": 500,
                    "note": "coffee",
                    "visibility": "public"
                }
            ],
            "requests": [
                {
                    "id": "rq_1",
                    "requester_id": "u_bob",
                    "payer_id": "u_ada",
                    "amount": 1200,
                    "note": "taxi",
                    "status": "pending"
                }
            ],
            "settlement_operator_ids": ["u_ada"]
        }
    
    @classmethod
    def all_fixtures(cls) -> Generator[TestInput, None, None]:
        """Generate various fixture scenarios"""
        # Valid minimal fixture
        yield TestInput("minimal valid fixture", {
            "currency": "EUR",
            "minor_units": 2,
            "users": []
        })
        
        # Valid with different currencies
        for currency, minor_units in [("JPY", 0), ("BHD", 3)]:
            yield TestInput(f"{currency} with {minor_units} minor units", {
                "currency": currency,
                "minor_units": minor_units,
                "users": [
                    {
                        "id": "u_test",
                        "email": "test@example.com",
                        "password": "password123",
                        "display_name": "Test",
                        "handle": "test",
                        "balance": 1000
                    }
                ]
            })
        
        # Many users
        many_users = []
        for i in range(100):
            many_users.append({
                "id": f"u_{i}",
                "email": f"user{i}@example.com",
                "password": "password123",
                "display_name": f"User {i}",
                "handle": f"user{i:03d}",
                "balance": i * 100
            })
        yield TestInput("100 users", {
            "currency": "EUR",
            "minor_units": 2,
            "users": many_users
        })
        
        # Zero balance user
        yield TestInput("zero balance user", {
            "currency": "EUR",
            "minor_units": 2,
            "users": [
                {
                    "id": "u_zero",
                    "email": "zero@example.com",
                    "password": "password123",
                    "display_name": "Zero",
                    "handle": "zero",
                    "balance": 0
                }
            ]
        })
        
        # Maximum allowed balance (close to 2^53)
        yield TestInput("large balance at limit", {
            "currency": "EUR",
            "minor_units": 2,
            "users": [
                {
                    "id": "u_rich",
                    "email": "rich@example.com",
                    "password": "password123",
                    "display_name": "Rich",
                    "handle": "rich",
                    "balance": 9007199254740991  # 2^53 - 1
                }
            ]
        })
    
    @classmethod
    def invalid_fixtures(cls) -> Generator[TestInput, None, None]:
        """Generate invalid fixtures that should fail validation"""
        valid = cls.valid_fixture()
        
        # Missing currency
        yield TestInput("missing currency", {k: v for k, v in valid.items() if k != "currency"})
        
        # Missing minor_units
        yield TestInput("missing minor_units", {k: v for k, v in valid.items() if k != "minor_units"})
        
        # Invalid minor_units
        for mu in [-1, 1, 4]:
            invalid = dict(valid)
            invalid["minor_units"] = mu
            yield TestInput(f"invalid minor_units: {mu}", invalid)
        
        # Negative balance
        invalid = dict(valid)
        invalid["users"] = [dict(valid["users"][0])]
        invalid["users"][0]["balance"] = -100
        yield TestInput("negative balance", invalid)
        
        # Balance exceeds max
        invalid = dict(valid)
        invalid["users"] = [dict(valid["users"][0])]
        invalid["users"][0]["balance"] = 2**53
        yield TestInput("balance exceeds max", invalid)


class UserGenerator:
    """Generates user-related test inputs"""
    
    HANDLE_CHARS = string.ascii_lowercase + string.digits + "_"
    
    @classmethod
    def valid_handles(cls) -> Generator[TestInput, None, None]:
        """Generate valid handles"""
        yield TestInput("simple handle", "ada")
        yield TestInput("handle with numbers", "user123")
        yield TestInput("handle with underscore", "ada_lovelace")
        yield TestInput("single character", "a")
        yield TestInput("max length 20", "a" * 20)
        yield TestInput("mixed alphanumeric", "user_123_test")
    
    @classmethod
    def invalid_handles(cls) -> Generator[TestInput, None, None]:
        """Generate invalid handles"""
        yield TestInput("empty string", "")
        yield TestInput("too long (21)", "a" * 21)
        yield TestInput("uppercase", "Ada")
        yield TestInput("hyphen", "ada-lovelace")
        yield TestInput("space", "ada lovelace")
        yield TestInput("special chars", "ada@example")
    
    @classmethod
    def valid_emails(cls) -> Generator[TestInput, None, None]:
        """Generate valid emails"""
        yield TestInput("simple email", "test@example.com")
        yield TestInput("with dots", "first.last@example.com")
        yield TestInput("with plus", "user+tag@example.com")
        yield TestInput("long local part", "a" * 50 + "@example.com")
    
    @classmethod
    def invalid_emails(cls) -> Generator[TestInput, None, None]:
        """Generate invalid emails"""
        yield TestInput("no @", "notanemail")
        yield TestInput("empty local", "@example.com")
        yield TestInput("empty domain", "user@")
    
    @classmethod
    def valid_passwords(cls) -> Generator[TestInput, None, None]:
        """Generate valid passwords"""
        yield TestInput("exactly 8 chars", "password")
        yield TestInput("long password", "correct horse battery staple")
        yield TestInput("with numbers", "pass123word456")
        yield TestInput("with special", "p@$$w0rd!2024")
    
    @classmethod
    def invalid_passwords(cls) -> Generator[TestInput, None, None]:
        """Generate invalid passwords"""
        yield TestInput("empty", "")
        yield TestInput("7 chars", "1234567")
        yield TestInput("single char", "x")


class AmountGenerator:
    """Generates amount values for testing"""
    
    MAX_AMOUNT = 1000000000
    
    @classmethod
    def valid_amounts(cls) -> Generator[TestInput, None, None]:
        """Generate valid amounts"""
        yield TestInput("minimum (1)", 1)
        yield TestInput("small amount", 100)
        yield TestInput("medium amount", 10000)
        yield TestInput("as float integer", 1000.0)
        yield TestInput("scientific notation integer", 1e3)  # 1000.0
        yield TestInput("maximum", cls.MAX_AMOUNT)
        yield TestInput("zero for offset", 0)
    
    @classmethod
    def invalid_amounts(cls) -> Generator[TestInput, None, None]:
        """Generate invalid amounts"""
        yield TestInput("negative", -1)
        yield TestInput("zero", 0)
        yield TestInput("exceeds max", cls.MAX_AMOUNT + 1)
        yield TestInput("as string", "1000")
        yield TestInput("as boolean", True)
        yield TestInput("as null", None)
        yield TestInput("float non-integer", 100.5)


class PaymentGenerator:
    """Generates payment creation inputs"""
    
    @classmethod
    def valid_payments(cls, to_handle: str = "bob", amount: int = 1000) -> Generator[TestInput, None, None]:
        """Generate valid payment bodies"""
        yield TestInput("minimal", {
            "to_handle": to_handle,
            "amount": amount
        })
        
        yield TestInput("with note", {
            "to_handle": to_handle,
            "amount": amount,
            "note": "Thanks for dinner!"
        })
        
        yield TestInput("with visibility private", {
            "to_handle": to_handle,
            "amount": amount,
            "visibility": "private"
        })
        
        yield TestInput("with visibility public", {
            "to_handle": to_handle,
            "amount": amount,
            "visibility": "public"
        })
        
        yield TestInput("complete", {
            "to_handle": to_handle,
            "amount": amount,
            "note": "Dinner",
            "visibility": "private"
        })
        
        yield TestInput("empty note", {
            "to_handle": to_handle,
            "amount": amount,
            "note": ""
        })
    
    @classmethod
    def invalid_payments(cls, valid_handle: str = "bob") -> Generator[TestInput, None, None]:
        """Generate invalid payment bodies"""
        yield TestInput("self payment", {
            "to_handle": valid_handle,
            "amount": 1000  # when valid_handle is the caller
        })
        
        yield TestInput("unknown handle", {
            "to_handle": "nonexistent_user_xyz",
            "amount": 1000
        })
        
        yield TestInput("note too long", {
            "to_handle": valid_handle,
            "amount": 1000,
            "note": "x" * 201
        })
        
        yield TestInput("invalid visibility", {
            "to_handle": valid_handle,
            "amount": 1000,
            "visibility": "secret"
        })
        
        yield TestInput("missing to_handle", {
            "amount": 1000
        })
        
        yield TestInput("missing amount", {
            "to_handle": valid_handle
        })


class RequestGenerator:
    """Generates payment request inputs"""
    
    @classmethod
    def valid_requests(cls, payer_handle: str = "bob", amount: int = 1000) -> Generator[TestInput, None, None]:
        """Generate valid request bodies"""
        yield TestInput("minimal", {
            "payer_handle": payer_handle,
            "amount": amount
        })
        
        yield TestInput("with note", {
            "payer_handle": payer_handle,
            "amount": amount,
            "note": "Please pay me back"
        })
        
        yield TestInput("large amount", {
            "payer_handle": payer_handle,
            "amount": 1000000
        })
    
    @classmethod
    def invalid_requests(cls, valid_handle: str = "bob") -> Generator[TestInput, None, None]:
        """Generate invalid request bodies"""
        yield TestInput("self request", {
            "payer_handle": valid_handle,
            "amount": 1000
        })
        
        yield TestInput("unknown handle", {
            "payer_handle": "nonexistent_xyz",
            "amount": 1000
        })


class SplitGenerator:
    """Generates bill split inputs"""
    
    @classmethod
    def valid_splits(cls, handles: List[str] = None) -> Generator[TestInput, None, None]:
        """Generate valid split bodies"""
        if handles is None:
            handles = ["ada", "bob", "cy"]
        
        yield TestInput("simple equal split", {
            "amount": 3000,
            "participant_handles": handles
        })
        
        yield TestInput("uneven split", {
            "amount": 1000,
            "participant_handles": handles
        })
        
        yield TestInput("with note", {
            "amount": 3000,
            "participant_handles": handles,
            "note": "Dinner bill"
        })
        
        yield TestInput("two participants", {
            "amount": 100,
            "participant_handles": handles[:2]
        })
        
        yield TestInput("single participant (caller only)", {
            "amount": 100,
            "participant_handles": [handles[0]]
        })
        
        yield TestInput("amount 1 with 3 people", {
            "amount": 1,
            "participant_handles": handles
        })
    
    @classmethod
    def invalid_splits(cls) -> Generator[TestInput, None, None]:
        """Generate invalid split bodies"""
        yield TestInput("empty participants", {
            "amount": 1000,
            "participant_handles": []
        })
        
        yield TestInput("duplicate handles", {
            "amount": 1000,
            "participant_handles": ["ada", "ada", "bob"]
        })
        
        yield TestInput("unknown handle", {
            "amount": 1000,
            "participant_handles": ["ada", "nonexistent_xyz"]
        })


class SettlementGenerator:
    """Generates settlement inputs"""
    
    @classmethod
    def valid_settlements(cls) -> Generator[TestInput, None, None]:
        """Generate valid settlement bodies"""
        yield TestInput("single transfer", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "bob", "amount": 100}
            ]
        })
        
        yield TestInput("multiple transfers", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "bob", "amount": 100},
                {"from_handle": "bob", "to_handle": "cy", "amount": 50}
            ]
        })
        
        yield TestInput("with note and visibility", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "bob", "amount": 100, 
                 "note": "Settlement", "visibility": "private"}
            ]
        })
        
        yield TestInput("circular transfer", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "bob", "amount": 100},
                {"from_handle": "bob", "to_handle": "ada", "amount": 100}
            ]
        })
    
    @classmethod
    def invalid_settlements(cls) -> Generator[TestInput, None, None]:
        """Generate invalid settlement bodies"""
        yield TestInput("empty transfers", {
            "transfers": []
        })
        
        yield TestInput("too many transfers (33)", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "bob", "amount": 1}
                for _ in range(33)
            ]
        })
        
        yield TestInput("self transfer", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "ada", "amount": 100}
            ]
        })
        
        yield TestInput("unknown handle", {
            "transfers": [
                {"from_handle": "ada", "to_handle": "nonexistent_xyz", "amount": 100}
            ]
        })


class IdempotencyKeyGenerator:
    """Generates idempotency key values"""
    
    @classmethod
    def valid_keys(cls) -> Generator[TestInput, None, None]:
        """Generate valid idempotency keys"""
        yield TestInput("simple key", "key-123")
        yield TestInput("UUID format", "550e8400-e29b-41d4-a716-446655440000")
        yield TestInput("single char", "x")
        yield TestInput("max length 255", "k" * 255)
        yield TestInput("with special chars", "key-123_abc.xyz:def")
    
    @classmethod
    def invalid_keys(cls) -> Generator[TestInput, None, None]:
        """Generate invalid idempotency keys"""
        yield TestInput("empty string", "")
        yield TestInput("too long (256)", "k" * 256)
        yield TestInput("whitespace only", "   ")


class PaginationGenerator:
    """Generates pagination parameters"""
    
    @classmethod
    def valid_params(cls) -> Generator[TestInput, None, None]:
        """Generate valid pagination params"""
        yield TestInput("default", {"limit": 50, "offset": 0})
        yield TestInput("limit 1", {"limit": 1, "offset": 0})
        yield TestInput("limit 200", {"limit": 200, "offset": 0})
        yield TestInput("offset 100", {"limit": 50, "offset": 100})
    
    @classmethod
    def invalid_params(cls) -> Generator[TestInput, None, None]:
        """Generate invalid pagination params"""
        yield TestInput("limit 0", {"limit": 0, "offset": 0})
        yield TestInput("limit 201", {"limit": 201, "offset": 0})
        yield TestInput("negative limit", {"limit": -1, "offset": 0})
        yield TestInput("negative offset", {"limit": 50, "offset": -1})


class QueryParamGenerator:
    """Generates query parameters for list endpoints"""
    
    @classmethod
    def valid_request_params(cls) -> Generator[TestInput, None, None]:
        """Generate valid request query params"""
        yield TestInput("no params", {})
        yield TestInput("direction incoming", {"direction": "incoming"})
        yield TestInput("direction outgoing", {"direction": "outgoing"})
        yield TestInput("status pending", {"status": "pending"})
        yield TestInput("status paid", {"status": "paid"})
        yield TestInput("status declined", {"status": "declined"})
        yield TestInput("status cancelled", {"status": "cancelled"})
        yield TestInput("combined", {"direction": "incoming", "status": "pending"})
    
    @classmethod
    def invalid_request_params(cls) -> Generator[TestInput, None, None]:
        """Generate invalid request query params"""
        yield TestInput("invalid direction", {"direction": "sideways"})
        yield TestInput("invalid status", {"status": "completed"})


def generate_all_inputs() -> Dict[str, List[TestInput]]:
    """Generate all test inputs organized by category"""
    return {
        "fixtures_valid": list(FixtureGenerator.all_fixtures()),
        "fixtures_invalid": list(FixtureGenerator.invalid_fixtures()),
        "handles_valid": list(UserGenerator.valid_handles()),
        "handles_invalid": list(UserGenerator.invalid_handles()),
        "emails_valid": list(UserGenerator.valid_emails()),
        "emails_invalid": list(UserGenerator.invalid_emails()),
        "passwords_valid": list(UserGenerator.valid_passwords()),
        "passwords_invalid": list(UserGenerator.invalid_passwords()),
        "amounts_valid": list(AmountGenerator.valid_amounts()),
        "amounts_invalid": list(AmountGenerator.invalid_amounts()),
        "payments_valid": list(PaymentGenerator.valid_payments()),
        "payments_invalid": list(PaymentGenerator.invalid_payments()),
        "requests_valid": list(RequestGenerator.valid_requests()),
        "requests_invalid": list(RequestGenerator.invalid_requests()),
        "splits_valid": list(SplitGenerator.valid_splits()),
        "splits_invalid": list(SplitGenerator.invalid_splits()),
        "settlements_valid": list(SettlementGenerator.valid_settlements()),
        "settlements_invalid": list(SettlementGenerator.invalid_settlements()),
        "idempotency_keys_valid": list(IdempotencyKeyGenerator.valid_keys()),
        "idempotency_keys_invalid": list(IdempotencyKeyGenerator.invalid_keys()),
        "pagination_valid": list(PaginationGenerator.valid_params()),
        "pagination_invalid": list(PaginationGenerator.invalid_params()),
        "query_params_valid": list(QueryParamGenerator.valid_request_params()),
        "query_params_invalid": list(QueryParamGenerator.invalid_request_params()),
    }


if __name__ == "__main__":
    # Demo: print all generated inputs
    all_inputs = generate_all_inputs()
    for category, inputs in all_inputs.items():
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"{'='*60}")
        for inp in inputs[:3]:  # Show first 3 of each
            print(f"  - {inp.description}")
            if isinstance(inp.data, dict):
                print(f"    Data: {str(inp.data)[:100]}...")
            else:
                print(f"    Data: {inp.data}")
        if len(inputs) > 3:
            print(f"  ... and {len(inputs) - 3} more")

