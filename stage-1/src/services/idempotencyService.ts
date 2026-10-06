import { Database } from '../database';
import { Utils } from '../utils';
import { errors } from '../middleware/errorHandler';

export class IdempotencyService {
  private db: any;

  constructor() {
    this.db = Database.getInstance().getConnection();
  }

  // Check and record idempotency key
  async checkIdempotency(
    userId: string,
    key: string,
    method: string,
    path: string,
    requestBody: any
  ): Promise<{ isReplay: boolean; cachedResponse?: any }> {
    // Validate key format
    if (!key || key.length === 0) {
      throw errors.missingIdempotencyKey();
    }

    if (key.length < 1 || key.length > 255) {
      throw errors.validationFailed('Idempotency-Key must be 1-255 characters');
    }

    // Create hash of the request
    const requestHash = Utils.hashRequest(requestBody);

    // Check for existing key
    const existing = this.db.prepare(`
      SELECT method, path, request_hash, response_body
      FROM idempotency_keys
      WHERE user_id = ? AND key = ?
    `).get(userId, key) as any;

    if (!existing) {
      // First use of this key - reserve it (will be committed with transaction)
      this.db.prepare(`
        INSERT INTO idempotency_keys (user_id, key, method, path, request_hash, response_body)
        VALUES (?, ?, ?, ?, ?, '')
      `).run(userId, key, method, path, requestHash);
      
      return { isReplay: false };
    }

    // Check if it's a replay (same method, path, and request body)
    if (
      existing.method === method &&
      existing.path === path && 
      existing.request_hash === requestHash
    ) {
      // Replay - return cached response
      try {
        const cachedResponse = JSON.parse(existing.response_body);
        return { isReplay: true, cachedResponse };
      } catch {
        // If response can't be parsed, treat as new request
        this.db.prepare(`
          UPDATE idempotency_keys 
          SET method = ?, path = ?, request_hash = ?, response_body = ''
          WHERE user_id = ? AND key = ?
        `).run(method, path, requestHash, userId, key);
        
        return { isReplay: false };
      }
    }

    // Same key, different request - idempotency key reuse error
    throw errors.idempotencyKeyReuse();
  }

  // Store response for successful idempotent request
  storeResponse(
    userId: string,
    key: string,
    responseBody: any
  ): void {
    const responseJson = JSON.stringify(responseBody);
    
    this.db.prepare(`
      UPDATE idempotency_keys 
      SET response_body = ?
      WHERE user_id = ? AND key = ?
    `).run(responseJson, userId, key);
  }

  // Clear idempotency keys for a user (for testing)
  clearForUser(userId: string): void {
    this.db.prepare(`
      DELETE FROM idempotency_keys WHERE user_id = ?
    `).run(userId);
  }

  // Get all idempotency keys (for export)
  getAll(): Array<{
    user_id: string;
    key: string;
    method: string;
    path: string;
    request_hash: string;
    response_body: string;
    created_at: string;
  }> {
    return this.db.prepare(`
      SELECT user_id, key, method, path, request_hash, response_body, created_at
      FROM idempotency_keys
      ORDER BY created_at
    `).all() as any[];
  }

  // Seed idempotency keys (for import)
  seed(keys: any[]): void {
    const insertStmt = this.db.prepare(`
      INSERT OR REPLACE INTO idempotency_keys 
      (user_id, key, method, path, request_hash, response_body, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    for (const keyData of keys) {
      insertStmt.run(
        keyData.user_id,
        keyData.key,
        keyData.method,
        keyData.path,
        keyData.request_hash,
        keyData.response_body,
        keyData.created_at
      );
    }
  }
}

export const idempotencyService = new IdempotencyService();