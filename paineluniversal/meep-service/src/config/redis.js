const redis = require('redis');

// Create Redis client
const client = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  retry_strategy: (options) => {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      console.error('Redis connection refused');
      return new Error('Redis connection refused');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      console.error('Redis retry time exhausted');
      return new Error('Retry time exhausted');
    }
    if (options.attempt > 10) {
      console.error('Redis max attempts reached');
      return undefined;
    }
    // Reconnect after
    return Math.min(options.attempt * 100, 3000);
  }
});

// Handle connection events
client.on('connect', () => {
  console.log('Redis client connected');
});

client.on('ready', () => {
  console.log('Redis client ready');
});

client.on('error', (err) => {
  console.error('Redis client error:', err);
});

client.on('end', () => {
  console.log('Redis client disconnected');
});

// Connect to Redis
(async () => {
  try {
    await client.connect();
  } catch (error) {
    console.error('Failed to connect to Redis:', error);
  }
})();

// Wrapper functions with error handling
const get = async (key) => {
  try {
    return await client.get(key);
  } catch (error) {
    console.error('Redis GET error:', error);
    return null;
  }
};

const set = async (key, value, options = {}) => {
  try {
    if (options.EX) {
      return await client.setEx(key, options.EX, value);
    }
    return await client.set(key, value);
  } catch (error) {
    console.error('Redis SET error:', error);
    return null;
  }
};

const setex = async (key, seconds, value) => {
  try {
    return await client.setEx(key, seconds, value);
  } catch (error) {
    console.error('Redis SETEX error:', error);
    return null;
  }
};

const del = async (key) => {
  try {
    return await client.del(key);
  } catch (error) {
    console.error('Redis DEL error:', error);
    return null;
  }
};

const exists = async (key) => {
  try {
    return await client.exists(key);
  } catch (error) {
    console.error('Redis EXISTS error:', error);
    return false;
  }
};

const incr = async (key) => {
  try {
    return await client.incr(key);
  } catch (error) {
    console.error('Redis INCR error:', error);
    return null;
  }
};

const expire = async (key, seconds) => {
  try {
    return await client.expire(key, seconds);
  } catch (error) {
    console.error('Redis EXPIRE error:', error);
    return null;
  }
};

const hget = async (key, field) => {
  try {
    return await client.hGet(key, field);
  } catch (error) {
    console.error('Redis HGET error:', error);
    return null;
  }
};

const hset = async (key, field, value) => {
  try {
    return await client.hSet(key, field, value);
  } catch (error) {
    console.error('Redis HSET error:', error);
    return null;
  }
};

const hgetall = async (key) => {
  try {
    return await client.hGetAll(key);
  } catch (error) {
    console.error('Redis HGETALL error:', error);
    return {};
  }
};

const keys = async (pattern) => {
  try {
    return await client.keys(pattern);
  } catch (error) {
    console.error('Redis KEYS error:', error);
    return [];
  }
};

// Health check
const healthCheck = async () => {
  try {
    const start = Date.now();
    await client.ping();
    const latency = Date.now() - start;
    
    const info = await client.info('memory');
    const memoryInfo = {};
    info.split('\r\n').forEach(line => {
      if (line.includes(':')) {
        const [key, value] = line.split(':');
        memoryInfo[key] = value;
      }
    });

    return {
      status: 'healthy',
      latency: `${latency}ms`,
      memory: {
        used: memoryInfo.used_memory_human,
        peak: memoryInfo.used_memory_peak_human,
        rss: memoryInfo.used_memory_rss_human
      },
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

// Cache patterns
const cachePatterns = {
  // CPF validation cache
  cpfValidation: (cpfHash) => `cpf_validation:${cpfHash}`,
  
  // Equipment status cache
  equipmentStatus: (equipmentId) => `equipment:${equipmentId}:status`,
  
  // Analytics cache
  analytics: (type, eventId, period) => `analytics:${type}:${eventId}:${period}`,
  
  // Session cache
  session: (sessionToken) => `session:${sessionToken}`,
  
  // Rate limiting
  rateLimit: (ip, endpoint) => `rate_limit:${ip}:${endpoint}`,
  
  // User cache
  user: (userId) => `user:${userId}`,
  
  // Event cache
  event: (eventId) => `event:${eventId}`
};

module.exports = {
  client,
  get,
  set,
  setex,
  del,
  exists,
  incr,
  expire,
  hget,
  hset,
  hgetall,
  keys,
  healthCheck,
  cachePatterns
};
