import { Router } from 'express';
import { authenticate, AuthenticatedRequest } from '../middleware/auth';
import { userRepository } from '../repositories/userRepository';
import { Database } from '../database';

const router = Router();

// GET /me
router.get('/me', authenticate, async (req: AuthenticatedRequest, res, next) => {
  try {
    if (!req.user) {
      throw new Error('User not found in request');
    }

    // Get currency and minor_units from service state
    const db = Database.getInstance().getConnection();
    const serviceState = db.prepare(`
      SELECT currency, minor_units FROM service_state LIMIT 1
    `).get() as any;

    const currency = serviceState?.currency || 'EUR';
    const minor_units = serviceState?.minor_units ?? 2;

    res.status(200).json({
      user_id: req.user.id,
      display_name: req.user.display_name,
      handle: req.user.handle,
      balance: req.user.balance,
      currency: currency,
      minor_units: minor_units
    });
  } catch (error) {
    next(error);
  }
});

export { router as userRoutes };