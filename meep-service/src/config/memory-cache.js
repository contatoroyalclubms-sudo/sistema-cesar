/**
 * Memory Cache - Alternativa ao Redis para desenvolvimento
 * Implementa a mesma interface do Redis mas armazena em memória
 */

class MemoryCache {
    constructor() {
        this.store = new Map();
        this.timers = new Map();
        console.log('[MemoryCache] Inicializado - Cache em memória ativo');
    }

    // Simular conexão
    async connect() {
        console.log('[MemoryCache] Conectado (simulado)');
        return true;
    }

    // GET
    async get(key) {
        const data = this.store.get(key);
        if (data) {
            if (data.expireAt && Date.now() > data.expireAt) {
                this.store.delete(key);
                this.timers.delete(key);
                return null;
            }
            return data.value;
        }
        return null;
    }

    // SET
    async set(key, value, options = {}) {
        // Limpar timer anterior se existir
        if (this.timers.has(key)) {
            clearTimeout(this.timers.get(key));
        }

        const data = {
            value: typeof value === 'object' ? JSON.stringify(value) : value,
            createdAt: Date.now()
        };

        if (options.EX) {
            data.expireAt = Date.now() + (options.EX * 1000);
            // Configurar auto-delete
            const timer = setTimeout(() => {
                this.store.delete(key);
                this.timers.delete(key);
            }, options.EX * 1000);
            this.timers.set(key, timer);
        }

        this.store.set(key, data);
        return 'OK';
    }

    // SETEX
    async setex(key, seconds, value) {
        return this.set(key, value, { EX: seconds });
    }

    // DEL
    async del(key) {
        if (this.timers.has(key)) {
            clearTimeout(this.timers.get(key));
            this.timers.delete(key);
        }
        return this.store.delete(key) ? 1 : 0;
    }

    // EXISTS
    async exists(key) {
        if (this.store.has(key)) {
            const data = this.store.get(key);
            if (data.expireAt && Date.now() > data.expireAt) {
                this.store.delete(key);
                this.timers.delete(key);
                return 0;
            }
            return 1;
        }
        return 0;
    }

    // INCR
    async incr(key) {
        const value = await this.get(key);
        const newValue = (parseInt(value) || 0) + 1;
        await this.set(key, newValue.toString());
        return newValue;
    }

    // EXPIRE
    async expire(key, seconds) {
        if (this.store.has(key)) {
            const data = this.store.get(key);
            data.expireAt = Date.now() + (seconds * 1000);
            
            // Limpar timer anterior
            if (this.timers.has(key)) {
                clearTimeout(this.timers.get(key));
            }
            
            // Configurar novo timer
            const timer = setTimeout(() => {
                this.store.delete(key);
                this.timers.delete(key);
            }, seconds * 1000);
            this.timers.set(key, timer);
            
            return 1;
        }
        return 0;
    }

    // HGET
    async hGet(key, field) {
        const data = await this.get(key);
        if (data) {
            try {
                const hash = JSON.parse(data);
                return hash[field] || null;
            } catch {
                return null;
            }
        }
        return null;
    }

    // HSET
    async hSet(key, field, value) {
        let hash = {};
        const data = await this.get(key);
        if (data) {
            try {
                hash = JSON.parse(data);
            } catch {
                hash = {};
            }
        }
        hash[field] = value;
        await this.set(key, JSON.stringify(hash));
        return 1;
    }

    // HGETALL
    async hGetAll(key) {
        const data = await this.get(key);
        if (data) {
            try {
                return JSON.parse(data);
            } catch {
                return {};
            }
        }
        return {};
    }

    // KEYS
    async keys(pattern) {
        const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'));
        const matchingKeys = [];
        
        for (const [key, data] of this.store.entries()) {
            // Verificar expiração
            if (data.expireAt && Date.now() > data.expireAt) {
                this.store.delete(key);
                this.timers.delete(key);
                continue;
            }
            
            if (regex.test(key)) {
                matchingKeys.push(key);
            }
        }
        
        return matchingKeys;
    }

    // PING
    async ping() {
        return 'PONG';
    }

    // INFO
    async info() {
        return `# Memory Cache Stats
used_memory:${this.store.size}
used_memory_human:${this.store.size} keys
total_keys:${this.store.size}
expired_keys:${this.timers.size}`;
    }

    // Health check
    async healthCheck() {
        return {
            status: 'healthy',
            latency: '0ms',
            memory: {
                used: `${this.store.size} keys`,
                peak: 'N/A',
                rss: 'N/A'
            },
            timestamp: new Date().toISOString()
        };
    }

    // Limpar cache
    clear() {
        // Limpar todos os timers
        for (const timer of this.timers.values()) {
            clearTimeout(timer);
        }
        this.store.clear();
        this.timers.clear();
        console.log('[MemoryCache] Cache limpo');
    }

    // Estatísticas
    stats() {
        let expiredCount = 0;
        const now = Date.now();
        
        for (const [key, data] of this.store.entries()) {
            if (data.expireAt && now > data.expireAt) {
                expiredCount++;
            }
        }
        
        return {
            totalKeys: this.store.size,
            activeTimers: this.timers.size,
            expiredKeys: expiredCount,
            memoryUsage: process.memoryUsage().heapUsed
        };
    }
}

// Singleton
let instance = null;

function createMemoryCache() {
    if (!instance) {
        instance = new MemoryCache();
    }
    return instance;
}

// Exportar com interface compatível com redis.js
const cache = createMemoryCache();

module.exports = {
    client: cache,
    get: (key) => cache.get(key),
    set: (key, value, options) => cache.set(key, value, options),
    setex: (key, seconds, value) => cache.setex(key, seconds, value),
    del: (key) => cache.del(key),
    exists: (key) => cache.exists(key),
    incr: (key) => cache.incr(key),
    expire: (key, seconds) => cache.expire(key, seconds),
    hget: (key, field) => cache.hGet(key, field),
    hset: (key, field, value) => cache.hSet(key, field, value),
    hgetall: (key) => cache.hGetAll(key),
    keys: (pattern) => cache.keys(pattern),
    healthCheck: () => cache.healthCheck(),
    cachePatterns: {
        cpfValidation: (cpfHash) => `cpf_validation:${cpfHash}`,
        equipmentStatus: (equipmentId) => `equipment:${equipmentId}:status`,
        analytics: (type, eventId, period) => `analytics:${type}:${eventId}:${period}`,
        session: (sessionToken) => `session:${sessionToken}`,
        rateLimit: (ip, endpoint) => `rate_limit:${ip}:${endpoint}`,
        user: (userId) => `user:${userId}`,
        event: (eventId) => `event:${eventId}`
    }
};