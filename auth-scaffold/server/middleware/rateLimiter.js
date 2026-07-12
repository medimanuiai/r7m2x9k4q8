'use strict';

const rateLimit = require('express-rate-limit');

/**
 * Configurable rate-limiter stub.
 * TODO: Swap `store` for RedisStore (rate-limit-redis) in production:
 *   const RedisStore = require('rate-limit-redis');
 *   store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) })
 */
const rateLimiter = rateLimit({
  windowMs : parseInt(process.env.RATE_LIMIT_WINDOW_MS  || String(15 * 60 * 1000), 10), // 15 min
  max      : parseInt(process.env.RATE_LIMIT_MAX        || '20',                    10),
  standardHeaders: true,
  legacyHeaders  : false,
  message: { error: 'Too many requests. Please wait a few minutes and try again.' },
  skip: () => process.env.NODE_ENV === 'test', // disable during Jest runs
});

module.exports = { rateLimiter };
