#!/usr/bin/env python3
"""
Pocketful Stage 1 - Reference Implementation
Independent executable reference model for the payment and settlement service.
This model answers any input the requirements describe.
"""

import json
import re
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from copy import deepcopy

class ValidationError(Exception):
    """Raised when validation fails"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    display_name: str
    handle: str
    balance: int

@dataclass
class Payment:
    id: str
    from_user_id: str
    from_handle: str
    to_user_id: str
    to_handle: str
    amount: int
    currency: str
    note: str
    visibility: str
    request_id: Optional[str]
    settlement_id: Optional[str]
    created_at: str

@dataclass
class PaymentRequest:
    id: str
    requester_id: str
    requester_handle: str
    payer_id: str
    payer_handle: str
    amount: int
    currency: str
    note: str
    status: str
    payment_id: Optional[str]
    created_at: str

@dataclass
class Settlement:
    id: str
    operator_id: str
    transfers: List[Dict]
    payments: List[str]
    committed_at: str

@dataclass
class IdempotencyRecord:
    key: str
    user_id: str
    method: str
    path: str
    body_hash: str
    response: Dict
    status_code: int

class PocketfulService:
    """Reference implementation of the Pocketful service"""
    
    HANDLE_REGEX = re.compile(r'^[a-z0-9_]{1,20}$')
    EMAIL_REGEX = re.compile(r'^[^@]+@[^@]+$')
    MAX_ID_LEN = 64
    MAX_AMOUNT = 1000000000
    MAX_BALANCE = 2**53 - 1
    MIN_BALANCE = -(2**53)
    
    def __init__(self):
        self.currency: str = "EUR"
        self.minor_units: int = 2
        self.users: Dict[str, User] = {}
        self.users_by_handle: Dict[str, User] = {}
        self.users_by_email: Dict[str, User] = {}
        self.payments: Dict[str, Payment] = {}
        self.requests: Dict[str, PaymentRequest] = {}
        self.settlements: Dict[str, Settlement] = {}
        self.tokens: Dict[str, str] = {}
        self.idempotency_records: Dict[str, IdempotencyRecord] = {}
        self.settlement_operator_ids: set = set()
        self.payment_counter: int = 0
        self.request_counter: int = 0
        self.user_counter: int = 0
        self.settlement_counter: int = 0
        self.split_counter: int = 0
        self._seeded_total: int = 0
    
    def reset(self, fixture: Dict) -> None:
        """Reset all state to the given fixture"""
        self.__init__()
        
        if "currency" not in fixture:
            raise ValidationError("validation_failed", "Missing currency")
        if "minor_units" not in fixture:
            raise ValidationError("validation_failed", "Missing minor_units")
        
        self.currency = fixture["currency"]
        self.minor_units = fixture["minor_units"]
        
        if self.minor_units not in (0, 2, 3):
            raise ValidationError("validation_failed", "Invalid minor_units")
        
        for user_data in fixture.get("users", []):
            balance = user_data.get("balance", 0)
            if balance < 0:
                raise ValidationError("validation_failed", "Negative balance in fixture")
            if balance > self.MAX_BALANCE:
                raise ValidationError("validation_failed", "Balance exceeds max")
            
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                password_hash=self._hash_password(user_data["password"]),
                display_name=user_data["display_name"],
                handle=user_data["handle"],
                balance=balance
            )
            self._add_user(user)
            self._seeded_total += balance
        
        for payment_data in fixture.get("payments", []):
            payment = Payment(
                id=payment_data["id"],
                from_user_id=payment_data["from_user_id"],
                from_handle=self.users[payment_data["from_user_id"]].handle,
                to_user_id=payment_data["to_user_id"],
                to_handle=self.users[payment_data["to_user_id"]].handle,
                amount=payment_data["amount"],
                currency=self.currency,
                note=payment_data.get("note", ""),
                visibility=payment_data.get("visibility", "public"),
                request_id=payment_data.get("request_id"),
                settlement_id=None,
                created_at=payment_data.get("created_at", self._now())
            )
            self.payments[payment.id] = payment
        
        for request_data in fixture.get("requests", []):
            req = PaymentRequest(
                id=request_data["id"],
                requester_id=request_data["requester_id"],
                requester_handle=self.users[request_data["requester_id"]].handle,
                payer_id=request_data["payer_id"],
                payer_handle=self.users[request_data["payer_id"]].handle,
                amount=request_data["amount"],
                currency=self.currency,
                note=request_data.get("note", ""),
                status=request_data.get("status", "pending"),
                payment_id=request_data.get("payment_id"),
                created_at=request_data.get("created_at", self._now())
            )
            self.requests[req.id] = req
        
        self.settlement_operator_ids = set(fixture.get("settlement_operator_ids", []))
    
    def export_state(self) -> Dict:
        return {
            "track": "pocketful",
            "format_version": 1,
            "state": {
                "currency": self.currency,
                "minor_units": self.minor_units,
                "users": [
                    {
                        "id": u.id,
                        "email": u.email,
                        "password_hash": u.password_hash,
                        "display_name": u.display_name,
                        "handle": u.handle,
                        "balance": u.balance
                    }
                    for u in self.users.values()
                ],
                "payments": [
                    {
                        "id": p.id,
                        "from_user_id": p.from_user_id,
                        "to_user_id": p.to_user_id,
                        "amount": p.amount,
                        "note": p.note,
                        "visibility": p.visibility,
                        "request_id": p.request_id,
                        "settlement_id": p.settlement_id,
                        "created_at": p.created_at
                    }
                    for p in self.payments.values()
                ],
                "requests": [
                    {
                        "id": r.id,
                        "requester_id": r.requester_id,
                        "payer_id": r.payer_id,
                        "amount": r.amount,
                        "note": r.note,
                        "status": r.status,
                        "payment_id": r.payment_id,
                        "created_at": r.created_at
                    }
                    for r in self.requests.values()
                ],
                "settlements": [
                    {
                        "id": s.id,
                        "operator_id": s.operator_id,
                        "transfers": s.transfers,
                        "payments": s.payments,
                        "committed_at": s.committed_at
                    }
                    for s in self.settlements.values()
                ],
                "tokens": self.tokens,
                "idempotency_records": [
                    {
                        "key": rec.key,
                        "user_id": rec.user_id,
                        "method": rec.method,
                        "path": rec.path,
                        "body_hash": rec.body_hash,
                        "response": rec.response,
                        "status_code": rec.status_code
                    }
                    for rec in self.idempotency_records.values()
                ],
                "settlement_operator_ids": list(self.settlement_operator_ids),
                "counters": {
                    "payment": self.payment_counter,
                    "request": self.request_counter,
                    "user": self.user_counter,
                    "settlement": self.settlement_counter,
                    "split": self.split_counter
                },
                "seeded_total": self._seeded_total
            }
        }
    
    def import_state(self, data: Dict) -> None:
        if data.get("track") != "pocketful":
            raise ValidationError("validation_failed", "Invalid track")
        if data.get("format_version") != 1:
            raise ValidationError("validation_failed", "Invalid format_version")
        
        state = data["state"]
        self.__init__()
        
        self.currency = state["currency"]
        self.minor_units = state["minor_units"]
        
        for u_data in state["users"]:
            user = User(
                id=u_data["id"],
                email=u_data["email"],
                password_hash=u_data["password_hash"],
                display_name=u_data["display_name"],
                handle=u_data["handle"],
                balance=u_data["balance"]
            )
            self._add_user(user)
        
        for p_data in state["payments"]:
            payment = Payment(
                id=p_data["id"],
                from_user_id=p_data["from_user_id"],
                from_handle=self.users[p_data["from_user_id"]].handle,
                to_user_id=p_data["to_user_id"],
                to_handle=self.users[p_data["to_user_id"]].handle,
                amount=p_data["amount"],
                currency=self.currency,
                note=p_data["note"],
                visibility=p_data["visibility"],
                request_id=p_data.get("request_id"),
                settlement_id=p_data.get("settlement_id"),
                created_at=p_data["created_at"]
            )
            self.payments[payment.id] = payment
        
        for r_data in state["requests"]:
            req = PaymentRequest(
                id=r_data["id"],
                requester_id=r_data["requester_id"],
                requester_handle=self.users[r_data["requester_id"]].handle,
                payer_id=r_data["payer_id"],
                payer_handle=self.users[r_data["payer_id"]].handle,
                amount=r_data["amount"],
                currency=self.currency,
                note=r_data["note"],
                status=r_data["status"],
                payment_id=r_data.get("payment_id"),
                created_at=r_data["created_at"]
            )
            self.requests[req.id] = req
        
        for s_data in state.get("settlements", []):
            settlement = Settlement(
                id=s_data["id"],
                operator_id=s_data["operator_id"],
                transfers=s_data["transfers"],
                payments=s_data["payments"],
                committed_at=s_data["committed_at"]
            )
            self.settlements[settlement.id] = settlement
        
        self.tokens = state.get("tokens", {})
        self.settlement_operator_ids = set(state.get("settlement_operator_ids", []))
        
        counters = state.get("counters", {})
        self.payment_counter = counters.get("payment", 0)
        self.request_counter = counters.get("request", 0)
        self.user_counter = counters.get("user", 0)
        self.settlement_counter = counters.get("settlement", 0)
        self.split_counter = counters.get("split", 0)
        self._seeded_total = state.get("seeded_total", 0)
    
    def _add_user(self, user: User) -> None:
        self.users[user.id] = user
        self.users_by_handle[user.handle] = user
        self.users_by_email[user.email] = user
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_password(self, password: str, password_hash: str) -> bool:
        return self._hash_password(password) == password_hash
    
    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    
    def _generate_id(self, prefix: str, counter: int) -> str:
        return f"{prefix}_{counter}"
    
    def _generate_token(self, user_id: str) -> str:
        token = hashlib.sha256(f"{user_id}:{self._now()}".encode()).hexdigest()[:32]
        self.tokens[token] = user_id
        return token
    
    def _validate_handle(self, handle: str, field_name: str = "handle") -> None:
        if not isinstance(handle, str):
            raise ValidationError("validation_failed", f"{field_name} must be string")
        if not self.HANDLE_REGEX.match(handle):
            raise ValidationError("validation_failed", f"Invalid {field_name}")
    
    def _validate_email(self, email: str) -> None:
        if not isinstance(email, str):
            raise ValidationError("validation_failed", "email must be string")
        if not self.EMAIL_REGEX.match(email):
            raise ValidationError("validation_failed", "Invalid email")
    
    def _validate_amount(self, amount: Any, min_val: int = 1, max_val: int = None) -> int:
        if max_val is None:
            max_val = self.MAX_AMOUNT
        
        if isinstance(amount, bool):
            raise ValidationError("validation_failed", "amount must be numeric")
        if isinstance(amount, str):
            raise ValidationError("validation_failed", "amount must be numeric")
        
        try:
            if isinstance(amount, float):
                if not amount.is_integer():
                    raise ValidationError("validation_failed", "amount must be integer")
                amount = int(amount)
            else:
                amount = int(amount)
        except (TypeError, ValueError):
            raise ValidationError("validation_failed", "amount must be numeric")
        
        if amount < min_val or amount > max_val:
            raise ValidationError("validation_failed", "amount out of range")
        
        return amount
    
    def _validate_note(self, note: Any) -> str:
        if note is None:
            return ""
        if not isinstance(note, str):
            raise ValidationError("validation_failed", "note must be string")
        if len(note) > 200:
            raise ValidationError("validation_failed", "note too long")
        return note
    
    def _validate_visibility(self, visibility: Any) -> str:
        if visibility is None:
            return "public"
        if visibility not in ("public", "private"):
            raise ValidationError("validation_failed", "Invalid visibility")
        return visibility
    
    def _derive_handle_from_email(self, email: str) -> str:
        local_part = email.split("@")[0].lower()
        handle = "".join(c if c.isalnum() or c == "_" else "_" for c in local_part)[:20]
        return handle
    
    def _check_idempotency(self, user_id: str, key: str, method: str, path: str, body: Dict) -> Optional[Tuple[int, Dict]]:
        if not key:
            raise ValidationError("missing_idempotency_key", "Missing idempotency key")
        
        if len(key) < 1 or len(key) > 255:
            raise ValidationError("validation_failed", "Invalid idempotency key length")
        
        record_key = f"{user_id}:{key}"
        body_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        
        if record_key in self.idempotency_records:
            record = self.idempotency_records[record_key]
            if record.body_hash != body_hash:
                raise ValidationError("idempotency_key_reuse", "Key reused with different body")
            return (record.status_code, deepcopy(record.response))
        
        return None
    
    def _save_idempotency(self, user_id: str, key: str, method: str, path: str, body: Dict, status_code: int, response: Dict) -> None:
        record_key = f"{user_id}:{key}"
        body_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        self.idempotency_records[record_key] = IdempotencyRecord(
            key=key, user_id=user_id, method=method, path=path,
            body_hash=body_hash, response=deepcopy(response), status_code=status_code
        )
    
    # ============ Public API Methods ============
    
    def health(self) -> Dict:
        return {"status": "ok"}
    
    def signup(self, email: str, password: str, display_name: str) -> Dict:
        self._validate_email(email)
        
        if len(password) < 8:
            raise ValidationError("validation_failed", "Password too short")
        
        if email in self.users_by_email:
            raise ValidationError("email_taken", "Email already registered")
        
        handle = self._derive_handle_from_email(email)
        if handle in self.users_by_handle:
            raise ValidationError("handle_taken", "Handle already taken")
        
        self.user_counter += 1
        user_id = self._generate_id("u", self.user_counter)
        
        user = User(
            id=user_id,
            email=email,
            password_hash=self._hash_password(password),
            display_name=display_name,
            handle=handle,
            balance=0
        )
        self._add_user(user)
        
        token = self._generate_token(user_id)
        
        return {
            "user_id": user_id,
            "display_name": display_name,
            "token": token
        }
    
    def login(self, email: str, password: str) -> Dict:
        self._validate_email(email)
        
        user = self.users_by_email.get(email)
        if not user or not self._check_password(password, user.password_hash):
            raise ValidationError("unauthenticated", "Invalid credentials")
        
        token = self._generate_token(user.id)
        
        return {
            "user_id": user.id,
            "display_name": user.display_name,
            "token": token
        }
    
    def get_me(self, user_id: str) -> Dict:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        return {
            "user_id": user.id,
            "display_name": user.display_name,
            "handle": user.handle,
            "balance": user.balance,
            "currency": self.currency,
            "minor_units": self.minor_units
        }
    
    def create_payment(self, user_id: str, idempotency_key: str, to_handle: str, 
                       amount: Any, note: Any, visibility: Any) -> Tuple[int, Dict]:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        body = {"to_handle": to_handle, "amount": amount, "note": note, "visibility": visibility}
        replay = self._check_idempotency(user_id, idempotency_key, "POST", "/payments", body)
        if replay:
            return replay
        
        self._validate_handle(to_handle, "to_handle")
        amount = self._validate_amount(amount)
        note = self._validate_note(note)
        visibility = self._validate_visibility(visibility)
        
        if to_handle == user.handle:
            raise ValidationError("self_payment", "Cannot pay yourself")
        
        recipient = self.users_by_handle.get(to_handle)
        if not recipient:
            raise ValidationError("not_found", "User not found")
        
        if user.balance < amount:
            raise ValidationError("insufficient_funds", "Insufficient funds")
        
        self.payment_counter += 1
        payment_id = self._generate_id("p", self.payment_counter)
        now = self._now()
        
        user.balance -= amount
        recipient.balance += amount
        
        payment = Payment(
            id=payment_id,
            from_user_id=user.id,
            from_handle=user.handle,
            to_user_id=recipient.id,
            to_handle=recipient.handle,
            amount=amount,
            currency=self.currency,
            note=note,
            visibility=visibility,
            request_id=None,
            settlement_id=None,
            created_at=now
        )
        self.payments[payment_id] = payment
        
        response = {
            "payment_id": payment_id,
            "from_user_id": user.id,
            "from_handle": user.handle,
            "to_user_id": recipient.id,
            "to_handle": recipient.handle,
            "amount": amount,
            "currency": self.currency,
            "note": note,
            "visibility": visibility,
            "request_id": None,
            "created_at": now
        }
        
        self._save_idempotency(user_id, idempotency_key, "POST", "/payments", body, 201, response)
        return (201, response)
    
    def create_request(self, user_id: str, idempotency_key: str, payer_handle: str,
                       amount: Any, note: Any) -> Tuple[int, Dict]:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        body = {"payer_handle": payer_handle, "amount": amount, "note": note}
        replay = self._check_idempotency(user_id, idempotency_key, "POST", "/requests", body)
        if replay:
            return replay
        
        self._validate_handle(payer_handle, "payer_handle")
        amount = self._validate_amount(amount)
        note = self._validate_note(note)
        
        if payer_handle == user.handle:
            raise ValidationError("self_request", "Cannot request from yourself")
        
        payer = self.users_by_handle.get(payer_handle)
        if not payer:
            raise ValidationError("not_found", "User not found")
        
        self.request_counter += 1
        request_id = self._generate_id("rq", self.request_counter)
        now = self._now()
        
        req = PaymentRequest(
            id=request_id,
            requester_id=user.id,
            requester_handle=user.handle,
            payer_id=payer.id,
            payer_handle=payer.handle,
            amount=amount,
            currency=self.currency,
            note=note,
            status="pending",
            payment_id=None,
            created_at=now
        )
        self.requests[request_id] = req
        
        response = {
            "request_id": request_id,
            "requester_id": user.id,
            "requester_handle": user.handle,
            "payer_id": payer.id,
            "payer_handle": payer.handle,
            "amount": amount,
            "currency": self.currency,
            "note": note,
            "status": "pending",
            "payment_id": None,
            "created_at": now
        }
        
        self._save_idempotency(user_id, idempotency_key, "POST", "/requests", body, 201, response)
        return (201, response)
    
    def pay_request(self, user_id: str, idempotency_key: str, request_id: str,
                    visibility: Any) -> Tuple[int, Dict]:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        body = {"visibility": visibility}
        replay = self._check_idempotency(user_id, idempotency_key, "POST", f"/requests/{request_id}/pay", body)
        if replay:
            return replay
        
        visibility = self._validate_visibility(visibility)
        
        req = self.requests.get(request_id)
        if not req:
            raise ValidationError("not_found", "Request not found")
        
        if req.payer_id != user_id:
            raise ValidationError("forbidden", "Not authorized")
        
        if req.status != "pending":
            raise ValidationError("request_not_pending", "Request not pending")
        
        if user.balance < req.amount:
            raise ValidationError("insufficient_funds", "Insufficient funds")
        
        self.payment_counter += 1
        payment_id = self._generate_id("p", self.payment_counter)
        now = self._now()
        
        recipient = self.users[req.requester_id]
        
        user.balance -= req.amount
        recipient.balance += req.amount
        
        payment = Payment(
            id=payment_id,
            from_user_id=user.id,
            from_handle=user.handle,
            to_user_id=recipient.id,
            to_handle=recipient.handle,
            amount=req.amount,
            currency=self.currency,
            note=req.note,
            visibility=visibility,
            request_id=request_id,
            settlement_id=None,
            created_at=now
        )
        self.payments[payment_id] = payment
        
        req.status = "paid"
        req.payment_id = payment_id
        
        response = {
            "payment_id": payment_id,
            "from_user_id": user.id,
            "from_handle": user.handle,
            "to_user_id": recipient.id,
            "to_handle": recipient.handle,
            "amount": req.amount,
            "currency": self.currency,
            "note": req.note,
            "visibility": visibility,
            "request_id": request_id,
            "created_at": now
        }
        
        self._save_idempotency(user_id, idempotency_key, "POST", f"/requests/{request_id}/pay", body, 201, response)
        return (201, response)
    
    def decline_request(self, user_id: str, request_id: str) -> Dict:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        req = self.requests.get(request_id)
        if not req:
            raise ValidationError("not_found", "Request not found")
        
        if req.payer_id != user_id:
            raise ValidationError("forbidden", "Not authorized")
        
        if req.status == "declined":
            return self._request_to_dict(req)
        
        if req.status != "pending":
            raise ValidationError("request_not_pending", "Request not pending")
        
        req.status = "declined"
        return self._request_to_dict(req)
    
    def cancel_request(self, user_id: str, request_id: str) -> Dict:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        req = self.requests.get(request_id)
        if not req:
            raise ValidationError("not_found", "Request not found")
        
        if req.requester_id != user_id:
            raise ValidationError("forbidden", "Not authorized")
        
        if req.status == "cancelled":
            return self._request_to_dict(req)
        
        if req.status != "pending":
            raise ValidationError("request_not_pending", "Request not pending")
        
        req.status = "cancelled"
        return self._request_to_dict(req)
    
    def _request_to_dict(self, req: PaymentRequest) -> Dict:
        return {
            "request_id": req.id,
            "requester_id": req.requester_id,
            "requester_handle": req.requester_handle,
            "payer_id": req.payer_id,
            "payer_handle": req.payer_handle,
            "amount": req.amount,
            "currency": req.currency,
            "note": req.note,
            "status": req.status,
            "payment_id": req.payment_id,
            "created_at": req.created_at
        }
    
    def list_requests(self, user_id: str, direction: Optional[str], status: Optional[str],
                      limit: int, offset: int) -> Dict:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        if limit < 1 or limit > 200:
            raise ValidationError("validation_failed", "Invalid limit")
        if offset < 0:
            raise ValidationError("validation_failed", "Invalid offset")
        
        if direction is not None and direction not in ("incoming", "outgoing"):
            raise ValidationError("validation_failed", "Invalid direction")
        
        if status is not None and status not in ("pending", "paid", "declined", "cancelled"):
            raise ValidationError("validation_failed", "Invalid status")
        
        results = []
        for req in self.requests.values():
            if direction == "incoming" and req.payer_id != user_id:
                continue
            if direction == "outgoing" and req.requester_id != user_id:
                continue
            if direction is None and req.requester_id != user_id and req.payer_id != user_id:
                continue
            
            if status and req.status != status:
                continue
            
            results.append(req)
        
        results.sort(key=lambda r: r.created_at, reverse=True)
        
        total = len(results)
        paginated = results[offset:offset + limit]
        has_more = offset + len(paginated) < total
        
        return {
            "requests": [self._request_to_dict(r) for r in paginated],
            "has_more": has_more
        }
    
    def _calculate_shares(self, amount: int, n: int) -> List[int]:
        base_share = amount // n
        remainder = amount % n
        shares = []
        for i in range(n):
            share_amount = base_share + (1 if i < remainder else 0)
            shares.append(share_amount)
        return shares
    
    def create_split(self, user_id: str, idempotency_key: str, amount: Any,
                     participant_handles: List[str], note: Any) -> Tuple[int, Dict]:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        body = {"amount": amount, "participant_handles": participant_handles, "note": note}
        replay = self._check_idempotency(user_id, idempotency_key, "POST", "/splits", body)
        if replay:
            return replay
        
        amount = self._validate_amount(amount)
        note = self._validate_note(note)
        
        if not participant_handles:
            raise ValidationError("validation_failed", "Empty participants")
        
        if len(participant_handles) != len(set(participant_handles)):
            raise ValidationError("validation_failed", "Duplicate handles")
        
        resolved_users = []
        for handle in participant_handles:
            self._validate_handle(handle)
            u = self.users_by_handle.get(handle)
            if not u:
                raise ValidationError("not_found", f"User not found: {handle}")
            resolved_users.append(u)
        
        shares = self._calculate_shares(amount, len(participant_handles))
        
        share_objects = []
        for i, u in enumerate(resolved_users):
            share_objects.append({"handle": u.handle, "amount": shares[i]})
        
        request_ids = []
        requests = []
        now = self._now()
        
        for i, u in enumerate(resolved_users):
            if u.id == user_id:
                continue
            
            self.request_counter += 1
            request_id = self._generate_id("rq", self.request_counter)
            
            req = PaymentRequest(
                id=request_id,
                requester_id=user_id,
                requester_handle=user.handle,
                payer_id=u.id,
                payer_handle=u.handle,
                amount=shares[i],
                currency=self.currency,
                note=note,
                status="pending",
                payment_id=None,
                created_at=now
            )
            self.requests[request_id] = req
            request_ids.append(request_id)
            requests.append(self._request_to_dict(req))
        
        self.split_counter += 1
        split_id = self._generate_id("sp", self.split_counter)
        
        response = {
            "split_id": split_id,
            "amount": amount,
            "currency": self.currency,
            "note": note,
            "shares": share_objects,
            "requests": requests,
            "created_at": now
        }
        
        self._save_idempotency(user_id, idempotency_key, "POST", "/splits", body, 201, response)
        return (201, response)
    
    def list_activity(self, user_id: str, limit: int, offset: int) -> Dict:
        user = self.users.get(user_id)
        if not user:
            raise ValidationError("unauthenticated", "Invalid user")
        
        if limit < 1 or limit > 200:
            raise ValidationError("validation_failed", "Invalid limit")
        if offset < 0:
            raise ValidationError("validation_failed", "Invalid offset")
        
        results = []
        for payment in self.payments.values():
            if payment.visibility == "public" or payment.from_user_id == user_id or payment.to_user_id == user_id:
                results.append(payment)
        
        results.sort(key=lambda p: p.created_at, reverse=True)
        
        total = len(results)
        paginated = results[offset:offset + limit]
        has_more = offset + len(paginated) < total
        
        return {
            "payments": [self._payment_to_dict(p) for p in paginated],
            "has_more": has_more
        }
    
    def _payment_to_dict(self, payment: Payment) -> Dict:
        return {
            "payment_id": payment.id,
            "from_user_id": payment.from_user_id,
            "from_handle": payment.from_handle,
            "to_user_id": payment.to_user_id,
            "to_handle": payment.to_handle,
            "amount": payment.amount,
            "currency": payment.currency,
            "note": payment.note,
            "visibility": payment.visibility,
            "request_id": payment.request_id,
            "settlement_id": payment.settlement_id,
            "created_at": payment.created_at
        }
    
    def create_settlement(self, operator_id: str, idempotency_key: str, 
                          transfers: List[Dict]) -> Tuple[int, Dict]:
        operator = self.users.get(operator_id)
        if not operator:
            raise ValidationError("unauthenticated", "Invalid user")
        
        if operator_id not in self.settlement_operator_ids:
            raise ValidationError("forbidden", "Not an operator")
        
        body = {"transfers": transfers}
        replay = self._check_idempotency(operator_id, idempotency_key, "POST", "/settlements", body)
        if replay:
            return replay
        
        if not transfers or len(transfers) > 32:
            raise ValidationError("validation_failed", "Invalid transfer count")
        
        transfer_details = []
        for t in transfers:
            if not isinstance(t, dict):
                raise ValidationError("validation_failed", "Invalid transfer")
            
            from_handle = t.get("from_handle")
            to_handle = t.get("to_handle")
            amount = t.get("amount")
            note = t.get("note")
            visibility = t.get("visibility")
            
            self._validate_handle(from_handle, "from_handle")
            self._validate_handle(to_handle, "to_handle")
            amount = self._validate_amount(amount)
            note = self._validate_note(note)
            visibility = self._validate_visibility(visibility)
            
            if from_handle == to_handle:
                raise ValidationError("self_payment", "Cannot transfer to self")
            
            from_user = self.users_by_handle.get(from_handle)
            to_user = self.users_by_handle.get(to_handle)
            
            if not from_user:
                raise ValidationError("not_found", f"User not found: {from_handle}")
            if not to_user:
                raise ValidationError("not_found", f"User not found: {to_handle}")
            
            transfer_details.append({
                "from_user": from_user,
                "to_user": to_user,
                "amount": amount,
                "note": note,
                "visibility": visibility
            })
        
        # Check collective sufficiency
        balance_changes: Dict[str, int] = {}
        for td in transfer_details:
            from_id = td["from_user"].id
            to_id = td["to_user"].id
            amt = td["amount"]
            
            balance_changes[from_id] = balance_changes.get(from_id, 0) - amt
            balance_changes[to_id] = balance_changes.get(to_id, 0) + amt
        
        for user_id, change in balance_changes.items():
            user = self.users[user_id]
            if user.balance + change < 0:
                raise ValidationError("insufficient_funds", "Insufficient collective funds")
        
        # Execute all transfers atomically
        self.settlement_counter += 1
        settlement_id = self._generate_id("st", self.settlement_counter)
        now = self._now()
        
        payment_ids = []
        payments = []
        
        for td in transfer_details:
            from_user = td["from_user"]
            to_user = td["to_user"]
            
            from_user.balance -= td["amount"]
            to_user.balance += td["amount"]
            
            self.payment_counter += 1
            payment_id = self._generate_id("p", self.payment_counter)
            payment_ids.append(payment_id)
            
            payment = Payment(
                id=payment_id,
                from_user_id=from_user.id,
                from_handle=from_user.handle,
                to_user_id=to_user.id,
                to_handle=to_user.handle,
                amount=td["amount"],
                currency=self.currency,
                note=td["note"],
                visibility=td["visibility"],
                request_id=None,
                settlement_id=settlement_id,
                created_at=now
            )
            self.payments[payment_id] = payment
            payments.append(self._payment_to_dict(payment))
        
        settlement = Settlement(
            id=settlement_id,
            operator_id=operator_id,
            transfers=transfers,
            payments=payment_ids,
            committed_at=now
        )
        self.settlements[settlement_id] = settlement
        
        response = {
            "settlement_id": settlement_id,
            "committed_at": now,
            "payments": payments
        }
        
        self._save_idempotency(operator_id, idempotency_key, "POST", "/settlements", body, 201, response)
        return (201, response)
    
    # ============ Invariant Checks ============
    
    def check_total_balance_invariant(self) -> bool:
        """Sum of wallet balances equals the total seeded by last reset."""
        total = sum(u.balance for u in self.users.values())
        return total == self._seeded_total
    
    def check_no_negative_balances_invariant(self) -> bool:
        """No wallet balance may be negative."""
        return all(u.balance >= 0 for u in self.users.values())
    
    def check_request_once_paid_invariant(self) -> bool:
        """A request may move money at most once."""
        for req in self.requests.values():
            if req.status == "paid":
                if not req.payment_id:
                    return False
                payment = self.payments.get(req.payment_id)
                if not payment or payment.request_id != req.id:
                    return False
        return True
    
    def get_total_balance(self) -> int:
        return sum(u.balance for u in self.users.values())
    
    def get_seeded_total(self) -> int:
        return self._seeded_total

