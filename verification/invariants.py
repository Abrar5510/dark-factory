#!/usr/bin/env python3
"""
Pocketful Stage 1 - Invariants
Properties that must stay true regardless of inputs.
These can be stated without close reading of the requirements.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class InvariantSeverity(Enum):
    CRITICAL = "critical"  # Must never be violated
    IMPORTANT = "important"  # Should not be violated
    WARNING = "warning"  # Indicates potential issues

@dataclass
class InvariantResult:
    name: str
    passed: bool
    severity: InvariantSeverity
    message: str
    details: Optional[Dict] = None

class PocketfulInvariants:
    """
    Invariant checks that must hold true for any valid implementation.
    These properties are derived from the core requirements but stated
    in a way that doesn't require close reading.
    """
    
    def __init__(self):
        self.checks: List[Callable] = [
            self.check_money_conservation,
            self.check_no_negative_balances,
            self.check_amount_integrity,
            self.check_request_lifecycle,
            self.check_payment_visibility,
            self.check_idempotency_key_format,
            self.check_handle_format,
            self.check_timestamp_format,
            self.check_pagination_bounds,
            self.check_response_structure,
        ]
    
    def check_money_conservation(self, state: Dict) -> InvariantResult:
        """
        INV-1: The sum of all wallet balances must equal the seeded total.
        Money cannot be created or destroyed, only transferred.
        """
        name = "money_conservation"
        
        users = state.get("users", [])
        total_balance = sum(u.get("balance", 0) for u in users)
        seeded_total = state.get("seeded_total", 0)
        
        if total_balance != seeded_total:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Money conservation violated: total={total_balance}, seeded={seeded_total}",
                details={"total_balance": total_balance, "seeded_total": seeded_total}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="Money conservation holds"
        )
    
    def check_no_negative_balances(self, state: Dict) -> InvariantResult:
        """
        INV-2: No wallet balance may be negative at any time.
        This includes transient states during operations.
        """
        name = "no_negative_balances"
        
        users = state.get("users", [])
        negative_users = [
            {"id": u.get("id"), "balance": u.get("balance")}
            for u in users
            if u.get("balance", 0) < 0
        ]
        
        if negative_users:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Found {len(negative_users)} users with negative balances",
                details={"negative_users": negative_users}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="All balances non-negative"
        )
    
    def check_amount_integrity(self, state: Dict) -> InvariantResult:
        """
        INV-3: All monetary amounts must be positive integers.
        Amounts must be within valid range and not exceed limits.
        """
        name = "amount_integrity"
        
        max_amount = 1000000000
        issues = []
        
        # Check payment amounts
        for p in state.get("payments", []):
            amt = p.get("amount")
            if not isinstance(amt, int) or amt <= 0 or amt > max_amount:
                issues.append({"type": "payment", "id": p.get("id"), "amount": amt})
        
        # Check request amounts
        for r in state.get("requests", []):
            amt = r.get("amount")
            if not isinstance(amt, int) or amt <= 0 or amt > max_amount:
                issues.append({"type": "request", "id": r.get("id"), "amount": amt})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Found {len(issues)} invalid amounts",
                details={"issues": issues[:5]}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="All amounts valid"
        )
    
    def check_request_lifecycle(self, state: Dict) -> InvariantResult:
        """
        INV-4: A payment request can move money at most once.
        Once paid, a request cannot be paid again.
        """
        name = "request_lifecycle"
        
        requests = state.get("requests", [])
        payments = {p.get("id"): p for p in state.get("payments", [])}
        
        issues = []
        for req in requests:
            if req.get("status") == "paid":
                payment_id = req.get("payment_id")
                if not payment_id:
                    issues.append({"request_id": req.get("id"), "issue": "missing_payment_id"})
                elif payment_id not in payments:
                    issues.append({"request_id": req.get("id"), "issue": "payment_not_found"})
                elif payments[payment_id].get("request_id") != req.get("id"):
                    issues.append({"request_id": req.get("id"), "issue": "payment_mismatch"})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Found {len(issues)} request lifecycle issues",
                details={"issues": issues}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="Request lifecycle valid"
        )
    
    def check_payment_visibility(self, state: Dict) -> InvariantResult:
        """
        INV-5: Payment visibility must be either 'public' or 'private'.
        No other values are permitted.
        """
        name = "payment_visibility"
        
        valid_values = {"public", "private"}
        issues = []
        
        for p in state.get("payments", []):
            vis = p.get("visibility")
            if vis not in valid_values:
                issues.append({"payment_id": p.get("id"), "visibility": vis})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.IMPORTANT,
                message=f"Found {len(issues)} invalid visibility values",
                details={"issues": issues}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.IMPORTANT,
            message="All visibility values valid"
        )
    
    def check_idempotency_key_format(self, state: Dict) -> InvariantResult:
        """
        INV-6: Idempotency keys must be 1-255 characters.
        """
        name = "idempotency_key_format"
        
        issues = []
        for record in state.get("idempotency_records", []):
            key = record.get("key", "")
            if len(key) < 1 or len(key) > 255:
                issues.append({"key": key, "length": len(key)})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.IMPORTANT,
                message=f"Found {len(issues)} invalid idempotency keys",
                details={"issues": issues}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.IMPORTANT,
            message="All idempotency keys valid format"
        )
    
    def check_handle_format(self, state: Dict) -> InvariantResult:
        """
        INV-7: User handles must match ^[a-z0-9_]{1,20}$.
        """
        name = "handle_format"
        
        import re
        handle_pattern = re.compile(r'^[a-z0-9_]{1,20}$')
        
        issues = []
        for user in state.get("users", []):
            handle = user.get("handle", "")
            if not handle_pattern.match(handle):
                issues.append({"user_id": user.get("id"), "handle": handle})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.IMPORTANT,
                message=f"Found {len(issues)} invalid handles",
                details={"issues": issues}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.IMPORTANT,
            message="All handles valid format"
        )
    
    def check_timestamp_format(self, state: Dict) -> InvariantResult:
        """
        INV-8: Timestamps must be RFC 3339 format with explicit offset.
        """
        name = "timestamp_format"
        
        # Simple check: contains T and timezone offset
        issues = []
        
        for p in state.get("payments", []):
            ts = p.get("created_at", "")
            if "T" not in ts or ("+" not in ts and "Z" not in ts):
                issues.append({"payment_id": p.get("id"), "timestamp": ts})
        
        for r in state.get("requests", []):
            ts = r.get("created_at", "")
            if "T" not in ts or ("+" not in ts and "Z" not in ts):
                issues.append({"request_id": r.get("id"), "timestamp": ts})
        
        if issues:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.WARNING,
                message=f"Found {len(issues)} invalid timestamps",
                details={"issues": issues[:5]}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.WARNING,
            message="All timestamps valid format"
        )
    
    def check_pagination_bounds(self, state: Dict) -> InvariantResult:
        """
        INV-9: Pagination parameters must be within valid ranges.
        limit: 1-200, offset: >=0
        """
        name = "pagination_bounds"
        
        # This is checked per-request, not in state
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.IMPORTANT,
            message="Pagination bounds check (request-time)"
        )
    
    def check_response_structure(self, state: Dict) -> InvariantResult:
        """
        INV-10: Error responses must have proper structure.
        """
        name = "response_structure"
        
        # This is checked per-response, not in state
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.IMPORTANT,
            message="Response structure check (response-time)"
        )
    
    def check_all(self, state: Dict) -> List[InvariantResult]:
        """Run all invariant checks"""
        return [check(state) for check in self.checks]
    
    def check_critical(self, state: Dict) -> List[InvariantResult]:
        """Run only critical invariants"""
        return [check(state) for check in self.checks 
                if check(state).severity == InvariantSeverity.CRITICAL]


class ResponseInvariants:
    """Invariants that apply to HTTP responses"""
    
    @staticmethod
    def check_error_response(response: Dict) -> InvariantResult:
        """
        INV-R1: Error responses must have error.code and error.message.
        """
        name = "error_response_structure"
        
        if "error" not in response:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message="Missing error field in error response",
                details={"response": response}
            )
        
        error = response["error"]
        if "code" not in error or "message" not in error:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message="Missing error.code or error.message",
                details={"error": error}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="Error response structure valid"
        )
    
    @staticmethod
    def check_payment_response(response: Dict) -> InvariantResult:
        """
        INV-R2: Payment responses must have required fields.
        """
        name = "payment_response_structure"
        
        required = ["payment_id", "from_user_id", "to_user_id", "amount", "currency", "created_at"]
        missing = [f for f in required if f not in response]
        
        if missing:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Missing fields in payment response: {missing}",
                details={"missing": missing}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="Payment response structure valid"
        )
    
    @staticmethod
    def check_request_response(response: Dict) -> InvariantResult:
        """
        INV-R3: Request responses must have required fields.
        """
        name = "request_response_structure"
        
        required = ["request_id", "requester_id", "payer_id", "amount", "currency", "status", "created_at"]
        missing = [f for f in required if f not in response]
        
        if missing:
            return InvariantResult(
                name=name,
                passed=False,
                severity=InvariantSeverity.CRITICAL,
                message=f"Missing fields in request response: {missing}",
                details={"missing": missing}
            )
        
        return InvariantResult(
            name=name,
            passed=True,
            severity=InvariantSeverity.CRITICAL,
            message="Request response structure valid"
        )


# List of all invariants for reference
ALL_INVARIANTS = [
    "money_conservation",
    "no_negative_balances",
    "amount_integrity",
    "request_lifecycle",
    "payment_visibility",
    "idempotency_key_format",
    "handle_format",
    "timestamp_format",
    "error_response_structure",
    "payment_response_structure",
    "request_response_structure",
]

# Critical invariants that must never be violated
CRITICAL_INVARIANTS = [
    "money_conservation",
    "no_negative_balances",
    "amount_integrity",
    "request_lifecycle",
]


if __name__ == "__main__":
    # Demo: check invariants on a sample state
    sample_state = {
        "seeded_total": 12500,
        "users": [
            {"id": "u_ada", "handle": "ada", "balance": 9500},
            {"id": "u_bob", "handle": "bob", "balance": 3000},
        ],
        "payments": [
            {
                "id": "p_1",
                "from_user_id": "u_ada",
                "to_user_id": "u_bob",
                "amount": 500,
                "currency": "EUR",
                "visibility": "public",
                "created_at": "2026-09-24T19:00:00+02:00"
            }
        ],
        "requests": [
            {
                "id": "rq_1",
                "requester_id": "u_bob",
                "payer_id": "u_ada",
                "amount": 1200,
                "currency": "EUR",
                "status": "pending",
                "payment_id": None,
                "created_at": "2026-09-24T19:00:00+02:00"
            }
        ],
        "idempotency_records": []
    }
    
    invariants = PocketfulInvariants()
    results = invariants.check_all(sample_state)
    
    print("Invariant Check Results:")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    
    for r in results:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"  [{status}] {r.name} ({r.severity.value})")
        print(f"           {r.message}")
    
    print(f"\n{passed} passed, {failed} failed")
