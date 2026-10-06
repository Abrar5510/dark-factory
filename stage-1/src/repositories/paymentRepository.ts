import Database from 'better-sqlite3';
import { Database as PocketfulDatabase } from '../database';
import { Payment } from '../types';
import { Utils } from '../utils';
import { errors } from '../middleware/errorHandler';

export class PaymentRepository {
  private db: Database.Database;

  constructor() {
    this.db = PocketfulDatabase.getInstance().getConnection();
  }

  // Create a payment (atomic transfer)
  create(
    fromUserId: string,
    toUserId: string,
    amount: number,
    note: string,
    visibility: 'public' | 'private',
    requestId: string | null = null,
    settlementId: string | null = null
  ): Payment {
    // Validate inputs
    if (!Utils.isValidAmount(amount)) {
      throw errors.validationFailed('Invalid amount');
    }

    if (!Utils.isValidNote(note)) {
      throw errors.validationFailed('Note exceeds 200 characters');
    }

    if (visibility !== 'public' && visibility !== 'private') {
      throw errors.validationFailed('Visibility must be "public" or "private"');
    }

    if (fromUserId === toUserId) {
      throw errors.selfPayment();
    }

    const id = Utils.generateId('p_');
    const created_at = Utils.formatDate(new Date());

    // Get user handles and currency info
    const fromUser = this.db.prepare(`
      SELECT handle FROM users WHERE id = ?
    `).get(fromUserId) as any;

    const toUser = this.db.prepare(`
      SELECT handle FROM users WHERE id = ?
    `).get(toUserId) as any;

    const serviceState = this.db.prepare(`
      SELECT currency, minor_units FROM service_state WHERE id = 1
    `).get() as any;

    if (!fromUser || !toUser) {
      throw errors.notFound('User not found');
    }

    // Atomic transfer in transaction
    this.db.transaction(() => {
      // Update sender balance (deduct)
      this.db.prepare(`
        UPDATE users 
        SET balance = balance - ? 
        WHERE id = ? AND balance >= ?
      `).run(amount, fromUserId, amount);

      const senderChanges = this.db.prepare('SELECT changes() as changes').get() as any;
      if (senderChanges.changes === 0) {
        throw errors.insufficientFunds();
      }

      // Update receiver balance (add)
      this.db.prepare(`
        UPDATE users 
        SET balance = balance + ? 
        WHERE id = ?
      `).run(amount, toUserId);

      // Create payment record
      this.db.prepare(`
        INSERT INTO payments (id, from_user_id, to_user_id, amount, note, visibility, request_id, settlement_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        id, 
        fromUserId, 
        toUserId, 
        amount, 
        note, 
        visibility, 
        requestId, 
        settlementId, 
        created_at
      );
    });

    return {
      id,
      from_user_id: fromUserId,
      from_handle: fromUser.handle,
      to_user_id: toUserId,
      to_handle: toUser.handle,
      amount,
      currency: serviceState.currency,
      note,
      visibility,
      request_id: requestId,
      settlement_id: settlementId,
      created_at
    };
  }

  // Find payment by ID
  findById(id: string): Payment | null {
    const payment = this.db.prepare(`
      SELECT 
        p.id, p.from_user_id, p.to_user_id, p.amount, p.note, p.visibility,
        p.request_id, p.settlement_id, p.created_at,
        fu.handle as from_handle,
        tu.handle as to_handle
      FROM payments p
      JOIN users fu ON p.from_user_id = fu.id
      JOIN users tu ON p.to_user_id = tu.id
      WHERE p.id = ?
    `).get(id) as any;

    if (!payment) return null;

    const serviceState = this.db.prepare(`
      SELECT currency FROM service_state WHERE id = 1
    `).get() as any;

    return {
      id: payment.id,
      from_user_id: payment.from_user_id,
      from_handle: payment.from_handle,
      to_user_id: payment.to_user_id,
      to_handle: payment.to_handle,
      amount: payment.amount,
      currency: serviceState.currency,
      note: payment.note,
      visibility: payment.visibility,
      request_id: payment.request_id,
      settlement_id: payment.settlement_id,
      created_at: payment.created_at
    };
  }

  // Get payments visible to a user (for activity feed)
  getVisibleToUser(
    userId: string,
    limit: number = 50,
    offset: number = 0
  ): { payments: Payment[], has_more: boolean } {
    // Get currency
    const serviceState = this.db.prepare(`
      SELECT currency FROM service_state WHERE id = 1
    `).get() as any;

    const payments = this.db.prepare(`
      SELECT 
        p.id, p.from_user_id, p.to_user_id, p.amount, p.note, p.visibility,
        p.request_id, p.settlement_id, p.created_at,
        fu.handle as from_handle,
        tu.handle as to_handle
      FROM payments p
      JOIN users fu ON p.from_user_id = fu.id
      JOIN users tu ON p.to_user_id = tu.id
      WHERE p.visibility = 'public' 
         OR p.from_user_id = ? 
         OR p.to_user_id = ?
      ORDER BY p.created_at DESC
      LIMIT ? OFFSET ?
    `).all(userId, userId, limit + 1, offset) as any[];

    const has_more = payments.length > limit;
    const resultPayments = payments.slice(0, limit).map(payment => ({
      id: payment.id,
      from_user_id: payment.from_user_id,
      from_handle: payment.from_handle,
      to_user_id: payment.to_user_id,
      to_handle: payment.to_handle,
      amount: payment.amount,
      currency: serviceState.currency,
      note: payment.note,
      visibility: payment.visibility,
      request_id: payment.request_id,
      settlement_id: payment.settlement_id,
      created_at: payment.created_at
    }));

    return { payments: resultPayments, has_more };
  }

  // Get payments for settlement
  getBySettlementId(settlementId: string): Payment[] {
    const serviceState = this.db.prepare(`
      SELECT currency FROM service_state WHERE id = 1
    `).get() as any;

    const payments = this.db.prepare(`
      SELECT 
        p.id, p.from_user_id, p.to_user_id, p.amount, p.note, p.visibility,
        p.request_id, p.settlement_id, p.created_at,
        fu.handle as from_handle,
        tu.handle as to_handle
      FROM payments p
      JOIN users fu ON p.from_user_id = fu.id
      JOIN users tu ON p.to_user_id = tu.id
      WHERE p.settlement_id = ?
      ORDER BY p.created_at
    `).all(settlementId) as any[];

    return payments.map(payment => ({
      id: payment.id,
      from_user_id: payment.from_user_id,
      from_handle: payment.from_handle,
      to_user_id: payment.to_user_id,
      to_handle: payment.to_handle,
      amount: payment.amount,
      currency: serviceState.currency,
      note: payment.note,
      visibility: payment.visibility,
      request_id: payment.request_id,
      settlement_id: payment.settlement_id,
      created_at: payment.created_at
    }));
  }

  // Seed payments from fixture
  seed(payments: any[]): void {
    const insertStmt = this.db.prepare(`
      INSERT OR REPLACE INTO payments 
      (id, from_user_id, to_user_id, amount, note, visibility, request_id, settlement_id, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    for (const paymentData of payments) {
      insertStmt.run(
        paymentData.id,
        paymentData.from_user_id,
        paymentData.to_user_id,
        paymentData.amount,
        paymentData.note || '',
        paymentData.visibility,
        paymentData.request_id || null,
        paymentData.settlement_id || null,
        paymentData.created_at || Utils.formatDate(new Date())
      );
    }
  }

  // Get all payments (for export)
  getAll(): Payment[] {
    const serviceState = this.db.prepare(`
      SELECT currency FROM service_state WHERE id = 1
    `).get() as any;

    const payments = this.db.prepare(`
      SELECT 
        p.id, p.from_user_id, p.to_user_id, p.amount, p.note, p.visibility,
        p.request_id, p.settlement_id, p.created_at,
        fu.handle as from_handle,
        tu.handle as to_handle
      FROM payments p
      JOIN users fu ON p.from_user_id = fu.id
      JOIN users tu ON p.to_user_id = tu.id
      ORDER BY p.created_at
    `).all() as any[];

    return payments.map(payment => ({
      id: payment.id,
      from_user_id: payment.from_user_id,
      from_handle: payment.from_handle,
      to_user_id: payment.to_user_id,
      to_handle: payment.to_handle,
      amount: payment.amount,
      currency: serviceState.currency,
      note: payment.note,
      visibility: payment.visibility,
      request_id: payment.request_id,
      settlement_id: payment.settlement_id,
      created_at: payment.created_at
    }));
  }
}

export const paymentRepository = new PaymentRepository();