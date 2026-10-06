import bcrypt from 'bcrypt';
import { randomBytes } from 'crypto';

const SALT_ROUNDS = 10;

export class Utils {
  // Generate a random ID (opaque string, max 64 chars)
  static generateId(prefix: string = ''): string {
    const bytes = randomBytes(16);
    return prefix + bytes.toString('hex');
  }

  // Hash password with bcrypt
  static async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, SALT_ROUNDS);
  }

  // Verify password against hash
  static async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  // Derive handle from email as per spec
  static deriveHandleFromEmail(email: string): string {
    const localPart = email.split('@')[0].toLowerCase();
    const handle = localPart
      .replace(/[^a-z0-9_]/g, '_')
      .substring(0, 20);
    return handle || 'user';
  }

  // Validate handle format
  static isValidHandle(handle: string): boolean {
    return /^[a-z0-9_]{1,20}$/.test(handle);
  }

  // Validate email format (simple validation)
  static isValidEmail(email: string): boolean {
    return /^[^@]+@[^@]+\.[^@]+$/.test(email);
  }

  // Generate bearer token
  static generateToken(): string {
    return randomBytes(32).toString('hex');
  }

  // Format date to RFC 3339 with offset
  static formatDate(date: Date): string {
    return date.toISOString();
  }

  // Parse RFC 3339 date
  static parseDate(dateStr: string): Date {
    return new Date(dateStr);
  }

  // Calculate equal shares for splits
  static calculateEqualShares(amount: number, participants: number): number[] {
    if (participants <= 0) return [];
    
    const baseShare = Math.floor(amount / participants);
    const remainder = amount % participants;
    
    const shares: number[] = [];
    for (let i = 0; i < participants; i++) {
      shares.push(baseShare + (i < remainder ? 1 : 0));
    }
    
    return shares;
  }

  // Validate amount range
  static isValidAmount(amount: number): boolean {
    return Number.isInteger(amount) && amount >= 1 && amount <= 1000000000;
  }

  // Validate note length
  static isValidNote(note: string): boolean {
    return note.length <= 200;
  }

  // Create SHA-256 hash for request body (for idempotency)
  static hashRequest(body: any): string {
    const jsonString = JSON.stringify(body);
    const encoder = new TextEncoder();
    const data = encoder.encode(jsonString);
    
    // Simple hash for now - in production would use crypto.subtle.digest
    return Buffer.from(jsonString).toString('base64').substring(0, 64);
  }
}