export interface User {
  id: string;
  email: string;
  password_hash: string;
  display_name: string;
  handle: string;
  balance: number;
  created_at: string;
}

export interface Payment {
  id: string;
  from_user_id: string;
  from_handle: string;
  to_user_id: string;
  to_handle: string;
  amount: number;
  currency: string;
  note: string;
  visibility: 'public' | 'private';
  request_id: string | null;
  settlement_id: string | null;
  created_at: string;
}

export interface Request {
  id: string;
  requester_id: string;
  requester_handle: string;
  payer_id: string;
  payer_handle: string;
  amount: number;
  currency: string;
  note: string;
  status: 'pending' | 'paid' | 'declined' | 'cancelled';
  payment_id: string | null;
  created_at: string;
}

export interface Split {
  id: string;
  amount: number;
  currency: string;
  note: string;
  shares: Array<{ handle: string; amount: number }>;
  requests: Request[];
  created_at: string;
}

export interface Settlement {
  id: string;
  committed_at: string;
  payments: Payment[];
}

export interface AuthenticationRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface PaymentRequest {
  to_handle: string;
  amount: number;
  note?: string;
  visibility?: 'public' | 'private';
}

export interface RequestCreate {
  payer_handle: string;
  amount: number;
  note?: string;
}

export interface SplitCreate {
  amount: number;
  participant_handles: string[];
  note?: string;
}

export interface SettlementCreate {
  transfers: Array<{
    from_handle: string;
    to_handle: string;
    amount: number;
    note?: string;
    visibility?: 'public' | 'private';
  }>;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

export type Fixture = {
  currency: string;
  minor_units: number;
  users: Array<{
    id: string;
    email: string;
    password: string;
    display_name: string;
    handle: string;
    balance: number;
  }>;
  payments: Array<{
    id: string;
    from_user_id: string;
    to_user_id: string;
    amount: number;
    note: string;
    visibility: 'public' | 'private';
  }>;
  requests: Array<{
    id: string;
    requester_id: string;
    payer_id: string;
    amount: number;
    note: string;
    status: 'pending' | 'paid' | 'declined' | 'cancelled';
  }>;
  settlement_operator_ids?: string[];
};