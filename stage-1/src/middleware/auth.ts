import { Request, Response, NextFunction } from 'express';
import { Database } from '../database';
import { errors } from './errorHandler';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    display_name: string;
    handle: string;
    balance: number;
  };
}

export const authenticate = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw errors.unauthenticated();
    }

    const token = authHeader.substring(7);
    const db = Database.getInstance().getConnection();

    const user = db.prepare(`
      SELECT u.id, u.email, u.display_name, u.handle, u.balance
      FROM users u
      JOIN sessions s ON u.id = s.user_id
      WHERE s.token = ?
    `).get(token) as any;

    if (!user) {
      throw errors.unauthenticated();
    }

    req.user = {
      id: user.id,
      email: user.email,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance
    };

    next();
  } catch (error) {
    next(error);
  }
};