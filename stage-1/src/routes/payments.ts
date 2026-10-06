import { Router } from 'express';
import { authenticate, AuthenticatedRequest } from '../middleware/auth';
import { 
  requireIdempotency, 
  checkIdempotency, 
  storeIdempotencyResponse,
  IdempotentRequest 
} from '../middleware/idempotency';
import { paymentRepository } from '../repositories/paymentRepository';
import { userRepository } from '../repositories/userRepository';
import { Utils } from '../utils';
import { errors } from '../middleware/errorHandler';

const router = Router();

// POST /payments (idempotent)
router.post(
  '/',
  authenticate,
  requireIdempotency,
  checkIdempotency,
  async (req: IdempotentRequest, res, next) => {
    try {
      if (!req.user) {
        throw new Error('User not found in request');
      }

      const { to_handle, amount, note = '', visibility = 'public' } = req.body;

      // Validate required fields
      if (!to_handle || amount === undefined) {
        throw errors.validationFailed('Missing required fields: to_handle, amount');
      }

      // Validate amount
      if (!Utils.isValidAmount(amount)) {
        throw errors.validationFailed('Amount must be an integer between 1 and 1,000,000,000');
      }

      // Validate note
      if (!Utils.isValidNote(note)) {
        throw errors.validationFailed('Note exceeds 200 characters');
      }

      // Validate visibility
      if (visibility !== 'public' && visibility !== 'private') {
        throw errors.validationFailed('Visibility must be "public" or "private"');
      }

      // Find recipient
      const recipient = userRepository.findByHandle(to_handle);
      if (!recipient) {
        throw errors.notFound('User not found');
      }

      // Check for self-payment
      if (req.user.handle === to_handle) {
        throw errors.selfPayment();
      }

      // Create payment
      const payment = paymentRepository.create(
        req.user.id,
        recipient.id,
        amount,
        note,
        visibility
      );

      // Get currency and minor_units
      const { Database } = require('../database');
      const db = Database.getInstance().getConnection();
      const serviceState = db.prepare(`
        SELECT currency, minor_units FROM service_state WHERE id = 1
      `).get() as any;

      const response = {
        payment_id: payment.id,
        from_user_id: payment.from_user_id,
        from_handle: payment.from_handle,
        to_user_id: payment.to_user_id,
        to_handle: payment.to_handle,
        amount: payment.amount,
        currency: serviceState.currency,
        note: payment.note,
        visibility: payment.visibility,
        request_id: payment.request_id,
        created_at: payment.created_at
      };

      // Store response for idempotency
      storeIdempotencyResponse(201, response)(req, res, () => {
        res.status(201).json(response);
      });
    } catch (error) {
      next(error);
    }
  }
);

export { router as paymentRoutes };