#!/usr/bin/env python3
"""
Pocketful Stage 1 - Self Test
Seeds faults into the reference implementation and confirms
that generators and invariants catch them.
"""

import sys
import json
from typing import List, Dict
from reference_model import PocketfulService, ValidationError
from generators import FixtureGenerator, PaymentGenerator, AmountGenerator, TestInput
from invariants import PocketfulInvariants, InvariantResult, InvariantSeverity

class FaultInjector:
    """Injects intentional faults into the reference implementation"""
    
    @staticmethod
    def create_money_creation_fault(service: PocketfulService) -> PocketfulService:
        """Fault: Money is created from thin air (no conservation)"""
        # Increase a balance without a corresponding decrease
        if service.users:
            first_user = list(service.users.values())[0]
            first_user.balance += 1000
        return service
    
    @staticmethod
    def create_negative_balance_fault(service: PocketfulService) -> PocketulService:
        """Fault: Negative balance is allowed"""
        if service.users:
            first_user = list(service.users.values())[0]
            first_user.balance = -100
        return service
    
    @staticmethod
    def create_double_payment_fault(service: PocketfulService) -> PocketfulService:
        """Fault: Request can be paid twice"""
        if service.requests:
            first_req = list(service.requests.values())[0]
            if first_req.status == "paid":
                # Try to create another payment for same request
                first_req.payment_id = None
                first_req.status = "pending"
        return service
    
    @staticmethod
    def create_invalid_amount_fault(service: PocketfulService) -> PocketfulService:
        """Fault: Invalid amount accepted"""
        if service.payments:
            first_payment = list(service.payments.values())[0]
            first_payment.amount = -500
        return service
    
    @staticmethod
    def create_invalid_visibility_fault(service: PocketfulService) -> PocketfulService:
        """Fault: Invalid visibility value"""
        if service.payments:
            first_payment = list(service.payments.values())[0]
            first_payment.visibility = "secret"
        return service
    
    @staticmethod
    def create_invalid_handle_fault(service: PocketfulService) -> PocketfulService:
        """Fault: Invalid handle format"""
        if service.users:
            first_user = list(service.users.values())[0]
            first_user.handle = "INVALID-HANDLE!"
        return service


class SelfTestRunner:
    """Runs self-tests on the reference model and invariants"""
    
    def __init__(self):
        self.service = PocketfulService()
        self.invariants = PocketfulInvariants()
        self.results: List[Dict] = []
    
    def run_fixture_tests(self) -> bool:
        """Test that reference model accepts valid fixtures and rejects invalid ones"""
        print("\n" + "="*60)
        print("FIXTURE TESTS")
        print("="*60)
        
        all_passed = True
        
        # Test valid fixtures
        for test_input in FixtureGenerator.all_fixtures():
            service = PocketfulService()
            try:
                service.reset(test_input.data)
                print(f"  ✓ Valid fixture: {test_input.description}")
                self.results.append({
                    "test": f"fixture_valid_{test_input.description}",
                    "passed": True
                })
            except ValidationError as e:
                print(f"  ✗ Valid fixture rejected: {test_input.description}")
                print(f"    Error: {e.code} - {e.message}")
                all_passed = False
                self.results.append({
                    "test": f"fixture_valid_{test_input.description}",
                    "passed": False,
                    "error": str(e)
                })
        
        # Test invalid fixtures
        for test_input in FixtureGenerator.invalid_fixtures():
            service = PocketfulService()
            try:
                service.reset(test_input.data)
                print(f"  ✗ Invalid fixture accepted: {test_input.description}")
                all_passed = False
                self.results.append({
                    "test": f"fixture_invalid_{test_input.description}",
                    "passed": False,
                    "error": "Should have been rejected"
                })
            except ValidationError:
                print(f"  ✓ Invalid fixture rejected: {test_input.description}")
                self.results.append({
                    "test": f"fixture_invalid_{test_input.description}",
                    "passed": True
                })
        
        return all_passed
    
    def run_generator_tests(self) -> bool:
        """Test that generators produce expected outputs"""
        print("\n" + "="*60)
        print("GENERATOR TESTS")
        print("="*60)
        
        all_passed = True
        
        # Test valid amounts
        for test_input in AmountGenerator.valid_amounts():
            service = PocketfulService()
            service.reset(FixtureGenerator.valid_fixture())
            user_id = list(service.users.keys())[0]
            
            try:
                # Try to create a payment with this amount
                # (may fail due to insufficient funds, but not validation)
                status, _ = service.create_payment(
                    user_id=user_id,
                    idempotency_key=f"test_{test_input.description}",
                    to_handle=service.users[user_id].handle,  # self-payment will fail with specific error
                    amount=test_input.data,
                    note="",
                    visibility=None
                )
                print(f"  ✓ Amount processed: {test_input.description}")
                self.results.append({
                    "test": f"amount_valid_{test_input.description}",
                    "passed": True
                })
            except ValidationError as e:
                if e.code in ("self_payment", "insufficient_funds", "not_found"):
                    # These are expected, validation passed
                    print(f"  ✓ Amount valid (rejected for other reason): {test_input.description}")
                    self.results.append({
                        "test": f"amount_valid_{test_input.description}",
                        "passed": True
                    })
                else:
                    print(f"  ✗ Amount validation failed: {test_input.description}")
                    all_passed = False
                    self.results.append({
                        "test": f"amount_valid_{test_input.description}",
                        "passed": False,
                        "error": str(e)
                    })
        
        # Test invalid amounts
        for test_input in AmountGenerator.invalid_amounts():
            service = PocketfulService()
            service.reset(FixtureGenerator.valid_fixture())
            user_id = list(service.users.keys())[0]
            
            try:
                status, _ = service.create_payment(
                    user_id=user_id,
                    idempotency_key=f"test_{test_input.description}",
                    to_handle="bob" if "bob" in service.users_by_handle else service.users[user_id].handle,
                    amount=test_input.data,
                    note="",
                    visibility=None
                )
                print(f"  ✗ Invalid amount accepted: {test_input.description}")
                all_passed = False
                self.results.append({
                    "test": f"amount_invalid_{test_input.description}",
                    "passed": False,
                    "error": "Should have been rejected"
                })
            except ValidationError as e:
                if e.code == "validation_failed":
                    print(f"  ✓ Invalid amount rejected: {test_input.description}")
                    self.results.append({
                        "test": f"amount_invalid_{test_input.description}",
                        "passed": True
                    })
                else:
                    print(f"  ✗ Unexpected error: {e.code}")
                    all_passed = False
                    self.results.append({
                        "test": f"amount_invalid_{test_input.description}",
                        "passed": False,
                        "error": str(e)
                    })
        
        return all_passed
    
    def run_invariant_fault_tests(self) -> bool:
        """Test that invariants catch seeded faults"""
        print("\n" + "="*60)
        print("INVARIANT FAULT TESTS")
        print("="*60)
        
        all_passed = True
        injector = FaultInjector()
        
        faults = [
            ("money_creation", injector.create_money_creation_fault, "money_conservation"),
            ("negative_balance", injector.create_negative_balance_fault, "no_negative_balances"),
            ("invalid_amount", injector.create_invalid_amount_fault, "amount_integrity"),
            ("invalid_visibility", injector.create_invalid_visibility_fault, "payment_visibility"),
            ("invalid_handle", injector.create_invalid_handle_fault, "handle_format"),
        ]
        
        for fault_name, fault_fn, expected_invariant in faults:
            # Set up clean service
            service = PocketfulService()
            service.reset(FixtureGenerator.valid_fixture())
            
            # Inject fault
            try:
                fault_fn(service)
            except Exception as e:
                print(f"  ⚠ Could not inject fault '{fault_name}': {e}")
                continue
            
            # Export state
            export = service.export_state()
            state = export["state"]
            
            # Check invariants
            results = self.invariants.check_all(state)
            
            # Find the expected invariant
            matching = [r for r in results if r.name == expected_invariant]
            
            if matching and not matching[0].passed:
                print(f"  ✓ Fault '{fault_name}' caught by {expected_invariant}")
                self.results.append({
                    "test": f"fault_{fault_name}",
                    "passed": True
                })
            else:
                print(f"  ✗ Fault '{fault_name}' NOT caught by {expected_invariant}")
                all_passed = False
                self.results.append({
                    "test": f"fault_{fault_name}",
                    "passed": False,
                    "error": f"Expected {expected_invariant} to fail"
                })
        
        return all_passed
    
    def run_state_consistency_tests(self) -> bool:
        """Test export/import roundtrip"""
        print("\n" + "="*60)
        print("STATE CONSISTENCY TESTS")
        print("="*60)
        
        all_passed = True
        
        # Test export/import roundtrip
        service1 = PocketfulService()
        service1.reset(FixtureGenerator.valid_fixture())
        
        # Perform some operations
        user_ids = list(service1.users.keys())
        if len(user_ids) >= 2:
            service1.create_payment(
                user_id=user_ids[0],
                idempotency_key="test_payment_1",
                to_handle=service1.users[user_ids[1]].handle,
                amount=100,
                note="Test payment",
                visibility="public"
            )
        
        # Export
        export = service1.export_state()
        
        # Import into new service
        service2 = PocketfulService()
        service2.import_state(export)
        
        # Check that state matches
        export2 = service2.export_state()
        
        if export == export2:
            print("  ✓ Export/import roundtrip successful")
            self.results.append({
                "test": "export_import_roundtrip",
                "passed": True
            })
        else:
            print("  ✗ Export/import roundtrip failed")
            all_passed = False
            self.results.append({
                "test": "export_import_roundtrip",
                "passed": False,
                "error": "States don't match after roundtrip"
            })
        
        # Check invariants after roundtrip
        results = self.invariants.check_all(export2["state"])
        failed = [r for r in results if not r.passed]
        
        if not failed:
            print("  ✓ Invariants hold after roundtrip")
            self.results.append({
                "test": "invariants_after_roundtrip",
                "passed": True
            })
        else:
            print(f"  ✗ Invariants violated after roundtrip: {[r.name for r in failed]}")
            all_passed = False
            self.results.append({
                "test": "invariants_after_roundtrip",
                "passed": False,
                "error": f"Failed: {[r.name for r in failed]}"
            })
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all self-tests"""
        print("\n" + "="*60)
        print("POCKETFUL STAGE 1 - SELF TEST")
        print("="*60)
        
        results = []
        results.append(("Fixture Tests", self.run_fixture_tests()))
        results.append(("Generator Tests", self.run_generator_tests()))
        results.append(("Invariant Fault Tests", self.run_invariant_fault_tests()))
        results.append(("State Consistency Tests", self.run_state_consistency_tests()))
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        all_passed = all(r[1] for r in results)
        
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  [{status}] {name}")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get("passed"))
        failed_tests = total_tests - passed_tests
        
        print(f"\n  Total: {total_tests} tests")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        
        if all_passed:
            print("\n  ✓ ALL TESTS PASSED")
            print("\n  The conformance kit can catch faults in the reference model.")
            print("  It is ready for use by the Referee.")
        else:
            print("\n  ✗ SOME TESTS FAILED")
            print("\n  The kit rejected its own reference implementation.")
            print("  Review and fix the issues before using for verification.")
        
        return all_passed


def main():
    runner = SelfTestRunner()
    passed = runner.run_all_tests()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
