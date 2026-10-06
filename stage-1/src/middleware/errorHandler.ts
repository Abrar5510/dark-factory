import { Request, Response, NextFunction } from 'express';

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  console.error('Error:', error);

  if (error instanceof AppError) {
    res.status(error.statusCode).json({
      error: {
        code: error.code,
        message: error.message
      }
    });
    return;
  }

  // Handle validation errors, etc.
  if (error.name === 'SyntaxError' && 'body' in error) {
    res.status(400).json({
      error: {
        code: 'malformed_request',
        message: 'Invalid JSON in request body'
      }
    });
    return;
  }

  // Default error
  res.status(500).json({
    error: {
      code: 'internal_error',
      message: 'An internal error occurred'
    }
  });
};

// Helper functions to create specific errors
export const errors = {
  malformedRequest: (message = 'Invalid JSON in request body') => 
    new AppError(400, 'malformed_request', message),
  
  missingIdempotencyKey: () => 
    new AppError(400, 'missing_idempotency_key', 'Idempotency-Key header is required'),
  
  unauthenticated: () => 
    new AppError(401, 'unauthenticated', 'Authentication required'),
  
  forbidden: () => 
    new AppError(403, 'forbidden', 'You are not permitted to perform this action'),
  
  notFound: (resource = 'Resource') => 
    new AppError(404, 'not_found', `${resource} not found`),
  
  idempotencyKeyReuse: () => 
    new AppError(409, 'idempotency_key_reuse', 'Idempotency key already used with different request body'),
  
  insufficientFunds: () => 
    new AppError(409, 'insufficient_funds', 'Insufficient funds'),
  
  emailTaken: () => 
    new AppError(409, 'email_taken', 'Email already registered'),
  
  handleTaken: () => 
    new AppError(409, 'handle_taken', 'Handle already taken'),
  
  requestNotPending: () => 
    new AppError(409, 'request_not_pending', 'Request is not pending'),
  
  validationFailed: (message = 'Validation failed') => 
    new AppError(422, 'validation_failed', message),
  
  selfPayment: () => 
    new AppError(422, 'self_payment', 'Cannot send money to yourself'),
  
  selfRequest: () => 
    new AppError(422, 'self_request', 'Cannot request money from yourself')
};