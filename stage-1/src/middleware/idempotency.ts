import { Request, Response, NextFunction } from 'express';
import { idempotencyService } from '../services/idempotencyService';
import { AuthenticatedRequest } from './auth';
import { errors } from './errorHandler';

export interface IdempotentRequest extends AuthenticatedRequest {
  idempotencyKey?: string;
  idempotencyChecked?: boolean;
}

export const requireIdempotency = (
  req: IdempotentRequest,
  res: Response,
  next: NextFunction
): void => {
  const key = req.headers['idempotency-key'] as string;
  
  if (!key) {
    next(errors.missingIdempotencyKey());
    return;
  }

  req.idempotencyKey = key;
  next();
};

export const checkIdempotency = (
  req: IdempotentRequest,
  res: Response,
  next: NextFunction
): void => {
  if (!req.user || !req.idempotencyKey || req.idempotencyChecked) {
    next();
    return;
  }

  try {
    const method = req.method;
    const path = req.path;
    const requestBody = req.body;

    const result = idempotencyService.checkIdempotency(
      req.user.id,
      req.idempotencyKey,
      method,
      path,
      requestBody
    );

    if (result.isReplay && result.cachedResponse) {
      // Return cached response
      res.status(200).json(result.cachedResponse);
      return;
    }

    req.idempotencyChecked = true;
    next();
  } catch (error) {
    next(error);
  }
};

export const storeIdempotencyResponse = (
  statusCode: number,
  responseBody: any
) => {
  return (req: IdempotentRequest, res: Response, next: NextFunction): void => {
    if (!req.user || !req.idempotencyKey || !req.idempotencyChecked) {
      next();
      return;
    }

    // Only store successful responses (2xx)
    if (statusCode >= 200 && statusCode < 300) {
      idempotencyService.storeResponse(
        req.user.id,
        req.idempotencyKey,
        responseBody
      );
    }

    next();
  };
};

// Combined middleware for idempotent endpoints
export const idempotencyMiddleware = [
  requireIdempotency,
  checkIdempotency
];