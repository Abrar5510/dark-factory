import Database from 'better-sqlite3';
import { Database as PocketfulDatabase } from '../database';
import { User } from '../types';
import { Utils } from '../utils';
import { AppError, errors } from '../middleware/errorHandler';

export class UserRepository {
  private db: Database.Database;

  constructor() {
    this.db = PocketfulDatabase.getInstance().getConnection();
  }

  // Create a new user
  async create(
    email: string, 
    password: string, 
    display_name: string
  ): Promise<User> {
    const handle = Utils.deriveHandleFromEmail(email);
    
    // Check if email already exists
    const existingEmail = this.db.prepare(
      'SELECT id FROM users WHERE email = ?'
    ).get(email) as any;
    
    if (existingEmail) {
      throw errors.emailTaken();
    }

    // Check if handle already exists
    const existingHandle = this.db.prepare(
      'SELECT id FROM users WHERE handle = ?'
    ).get(handle) as any;
    
    if (existingHandle) {
      throw errors.handleTaken();
    }

    // Validate inputs
    if (!Utils.isValidEmail(email)) {
      throw errors.validationFailed('Invalid email format');
    }

    if (password.length < 8) {
      throw errors.validationFailed('Password must be at least 8 characters');
    }

    if (display_name.length === 0) {
      throw errors.validationFailed('Display name is required');
    }

    const id = Utils.generateId('u_');
    const password_hash = await Utils.hashPassword(password);
    const created_at = Utils.formatDate(new Date());

    this.db.prepare(`
      INSERT INTO users (id, email, password_hash, display_name, handle, balance, created_at)
      VALUES (?, ?, ?, ?, ?, 0, ?)
    `).run(id, email, password_hash, display_name, handle, created_at);

    return this.findById(id);
  }

  // Find user by ID
  findById(id: string): User | null {
    const user = this.db.prepare(`
      SELECT id, email, password_hash, display_name, handle, balance, created_at
      FROM users WHERE id = ?
    `).get(id) as any;

    if (!user) return null;

    return {
      id: user.id,
      email: user.email,
      password_hash: user.password_hash,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance,
      created_at: user.created_at
    };
  }

  // Find user by email
  findByEmail(email: string): User | null {
    const user = this.db.prepare(`
      SELECT id, email, password_hash, display_name, handle, balance, created_at
      FROM users WHERE email = ?
    `).get(email) as any;

    if (!user) return null;

    return {
      id: user.id,
      email: user.email,
      password_hash: user.password_hash,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance,
      created_at: user.created_at
    };
  }

  // Find user by handle
  findByHandle(handle: string): User | null {
    const user = this.db.prepare(`
      SELECT id, email, password_hash, display_name, handle, balance, created_at
      FROM users WHERE handle = ?
    `).get(handle) as any;

    if (!user) return null;

    return {
      id: user.id,
      email: user.email,
      password_hash: user.password_hash,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance,
      created_at: user.created_at
    };
  }

  // Authenticate user
  async authenticate(email: string, password: string): Promise<User | null> {
    const user = this.findByEmail(email);
    if (!user) return null;

    const isValid = await Utils.verifyPassword(password, user.password_hash);
    return isValid ? user : null;
  }

  // Update user balance (atomically)
  updateBalance(userId: string, delta: number): void {
    this.db.prepare(`
      UPDATE users 
      SET balance = balance + ? 
      WHERE id = ? AND balance + ? >= 0
    `).run(delta, userId, delta);

    const changes = this.db.prepare('SELECT changes() as changes').get() as any;
    if (changes.changes === 0) {
      throw errors.insufficientFunds();
    }
  }

  // Create a session (bearer token)
  createSession(userId: string): string {
    const token = Utils.generateToken();
    const created_at = Utils.formatDate(new Date());

    this.db.prepare(`
      INSERT INTO sessions (token, user_id, created_at)
      VALUES (?, ?, ?)
    `).run(token, userId, created_at);

    return token;
  }

  // Get user by session token
  getUserByToken(token: string): User | null {
    const user = this.db.prepare(`
      SELECT u.id, u.email, u.password_hash, u.display_name, u.handle, u.balance, u.created_at
      FROM users u
      JOIN sessions s ON u.id = s.user_id
      WHERE s.token = ?
    `).get(token) as any;

    if (!user) return null;

    return {
      id: user.id,
      email: user.email,
      password_hash: user.password_hash,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance,
      created_at: user.created_at
    };
  }

  // Seed users from fixture
  seedFromFixture(users: any[]): void {
    const insertStmt = this.db.prepare(`
      INSERT INTO users (id, email, password_hash, display_name, handle, balance, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    for (const userData of users) {
      // In fixture, password is plaintext, we need to hash it
      Utils.hashPassword(userData.password).then(password_hash => {
        insertStmt.run(
          userData.id,
          userData.email,
          password_hash,
          userData.display_name,
          userData.handle,
          userData.balance,
          Utils.formatDate(new Date())
        );
      }).catch(error => {
        console.error('Error hashing password for seed:', error);
      });
    }
  }

  // Check if user is a settlement operator
  isSettlementOperator(userId: string, operatorIds: string[] = []): boolean {
    return operatorIds.includes(userId);
  }

  // Get total balance sum (for verification)
  getTotalBalance(): number {
    const result = this.db.prepare('SELECT SUM(balance) as total FROM users').get() as any;
    return result.total || 0;
  }

  // Get all users (for export)
  getAll(): User[] {
    const users = this.db.prepare(`
      SELECT id, email, password_hash, display_name, handle, balance, created_at
      FROM users
      ORDER BY created_at
    `).all() as any[];

    return users.map(user => ({
      id: user.id,
      email: user.email,
      password_hash: user.password_hash,
      display_name: user.display_name,
      handle: user.handle,
      balance: user.balance,
      created_at: user.created_at
    }));
  }
}

export const userRepository = new UserRepository();