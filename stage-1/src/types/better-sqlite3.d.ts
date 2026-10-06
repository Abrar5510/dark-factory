declare module 'better-sqlite3' {
  interface Database {
    prepare(sql: string): any;
    exec(sql: string): void;
    close(): void;
    pragma(sql: string): void;
  }

  export default class Database {
    constructor(path: string);
    prepare(sql: string): any;
    exec(sql: string): void;
    close(): void;
    pragma(sql: string): void;
  }
}