import { drizzle } from 'drizzle-orm/mysql2';
import mysql from 'mysql2/promise';
import { Redis } from 'ioredis';
import * as schema from '../../drizzle/schema';

// Database connection pool
const pool = mysql.createPool({
  uri: process.env.DATABASE_URL,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});

export const db = drizzle(pool, { schema, mode: 'mysql' });

// Redis client for caching
export const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

redis.on('connect', () => console.log('Redis connected!'));
redis.on('error', (err) => console.error('Redis Client Error', err));

// Function to get a cached value or fetch from DB
export async function getOrSetCache<T>(key: string, ttl: number, cb: () => Promise<T>): Promise<T> {
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached) as T;
  }
  const result = await cb();
  await redis.setex(key, ttl, JSON.stringify(result));
  return result;
}
