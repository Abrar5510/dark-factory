import Database from 'better-sqlite3';
// @ts-ignore - better-sqlite3 doesn't have proper TypeScript definitions
const BetterSqlite3 = Database;

export class PocketfulDatabase {
  private static instance: PocketfulDatabase;
  private db: any;

  private constructor() {
    const dbPath = process.env.DB_PATH || ':memory:';
    this.db = new BetterSqlite3(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    
    this.initializeSchema();
  }

  public static getInstance(): PocketfulDatabase {
    if (!PocketfulDatabase.instance) {
      PocketfulDatabase.instance = new PocketfulDatabase();
    }
    return PocketfulDatabase.instance;
  }

  private initializeSchema(): void {
    // Service state table (currency, minor_units, settlement operators)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS service_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        currency TEXT NOT NULL DEFAULT 'EUR',
        minor_units INTEGER NOT NULL DEFAULT 2,
        settlement_operator_ids TEXT NOT NULL DEFAULT '[]',
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
      )
    `);

    // Initialize service state if empty
    const existingState = this.db.prepare('SELECT id FROM service_state WHERE id = 1').get();
    if (!existingState) {
      this.db.prepare(`
        INSERT INTO service_state (id, currency, minor_units, settlement_operator_ids)
        VALUES (1, 'EUR', 2, '[]')
      `).run();
    }

    // Users table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        handle TEXT UNIQUE NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        CHECK (balance >= 0)
      )
    `);

    // Sessions table (bearer tokens)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);

    // Payments table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        from_user_id TEXT NOT NULL,
        to_user_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        note TEXT NOT NULL DEFAULT '',
        visibility TEXT NOT NULL CHECK (visibility IN ('public', 'private')),
        request_id TEXT,
        settlement_id TEXT,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (from_user_id) REFERENCES users(id),
        FOREIGN KEY (to_user_id) REFERENCES users(id),
        CHECK (amount > 0),
        CHECK (from_user_id != to_user_id)
      )
    `);

    // Requests table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        requester_id TEXT NOT NULL,
        payer_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        note TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'declined', 'cancelled')),
        payment_id TEXT,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (requester_id) REFERENCES users(id),
        FOREIGN KEY (payer_id) REFERENCES users(id),
        CHECK (amount > 0),
        CHECK (requester_id != payer_id)
      )
    `);

    // Splits table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS splits (
        id TEXT PRIMARY KEY,
        creator_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        note TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (creator_id) REFERENCES users(id),
        CHECK (amount > 0)
      )
    `);

    // Split participants table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS split_participants (
        split_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        PRIMARY KEY (split_id, user_id),
        FOREIGN KEY (split_id) REFERENCES splits(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id),
        CHECK (amount >= 0)
      )
    `);

    // Settlements table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS settlements (
        id TEXT PRIMARY KEY,
        operator_id TEXT NOT NULL,
        committed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (operator_id) REFERENCES users(id)
      )
    `);

    // Idempotency keys table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS idempotency_keys (
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        method TEXT NOT NULL,
        path TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_body TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        PRIMARY KEY (user_id, key),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);

    // Indexes for performance
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
      CREATE INDEX IF NOT EXISTS idx_users_handle ON users(handle);
      CREATE INDEX IF NOT EXISTS idx_payments_from_user ON payments(from_user_id);
      CREATE INDEX IF NOT EXISTS idx_payments_to_user ON payments(to_user_id);
      CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at);
      CREATE INDEX IF NOT EXISTS idx_requests_requester ON requests(requester_id);
      CREATE INDEX IF NOT EXISTS idx_requests_payer ON requests(payer_id);
      CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
      CREATE INDEX IF NOT EXISTS idx_requests_created ON requests(created_at);
      CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
      CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
    `);
  }

  public getConnection(): Database.Database {
    return this.db;
  }

  public transaction<T>(fn: (db: Database.Database) => T): T {
    const db = this.db;
    db.exec('BEGIN TRANSACTION');
    try {
      const result = fn(db);
      db.exec('COMMIT');
      return result;
    } catch (error) {
      db.exec('ROLLBACK');
      throw error;
    }
  }

  public close(): void {
    this.db.close();
  }

  public reset(seedData: any): void {
    this.db.transaction(() => {
      // Clear all tables in correct order (respecting foreign keys)
      this.db.exec('DELETE FROM idempotency_keys');
      this.db.exec('DELETE FROM split_participants');
      this.db.exec('DELETE FROM splits');
      this.db.exec('DELETE FROM payments');
      this.db.exec('DELETE FROM requests');
      this.db.exec('DELETE FROM settlements');
      this.db.exec('DELETE FROM sessions');
      this.db.exec('DELETE FROM users');
      this.db.exec('DELETE FROM service_state');

      // Insert service state
      const operatorIds = JSON.stringify(seedData.settlement_operator_ids || []);
      this.db.prepare(`
        INSERT INTO service_state (id, currency, minor_units, settlement_operator_ids)
        VALUES (1, ?, ?, ?)
      `).run(seedData.currency, seedData.minor_units, operatorIds);

      // Insert seed users
      const insertUser = this.db.prepare(`
        INSERT INTO users (id, email, password_hash, display_name, handle, balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);

      // Insert seed payments
      const insertPayment = this.db.prepare(`
        INSERT INTO payments (id, from_user_id, to_user_id, amount, note, visibility, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);

      // Insert seed requests
      const insertRequest = this.db.prepare(`
        INSERT INTO requests (id, requester_id, payer_id, amount, note, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);

      const now = new Date().toISOString();

      // Insert users (passwords need to be hashed synchronously for seed)
      for (const userData of seedData.users) {
        const bcrypt = require('bcrypt');
        const password_hash = bcrypt.hashSync(userData.password, 10);
        
        insertUser.run(
          userData.id,
          userData.email,
          password_hash,
          userData.display_name,
          userData.handle,
          userData.balance,
          now
        );
      }

      // Insert payments
      for (const paymentData of seedData.payments || []) {
        insertPayment.run(
          paymentData.id,
          paymentData.from_user_id,
          paymentData.to_user_id,
          paymentData.amount,
          paymentData.note || '',
          paymentData.visibility,
          now
        );
      }

      // Insert requests
      for (const requestData of seedData.requests || []) {
        insertRequest.run(
          requestData.id,
          requestData.requester_id,
          requestData.payer_id,
          requestData.amount,
          requestData.note || '',
          requestData.status,
          now
        );
      }
    });
  }
}

export const Database = PocketfulDatabase;