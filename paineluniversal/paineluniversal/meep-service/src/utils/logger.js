const winston = require('winston');
const path = require('path');

// Define log levels
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

// Define level colors
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white'
};

// Tell winston about colors
winston.addColors(colors);

// Define format for logs
const format = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Define format for console
const consoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.colorize({ all: true }),
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: ${info.message}`
  )
);

// Create logs directory if it doesn't exist
const fs = require('fs');
const logsDir = 'logs';
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Define transports
const transports = [
  // Console transport
  new winston.transports.Console({
    format: consoleFormat,
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug'
  }),
  
  // Error log file
  new winston.transports.File({
    filename: path.join(logsDir, 'error.log'),
    level: 'error',
    format: format,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  }),
  
  // Combined log file
  new winston.transports.File({
    filename: path.join(logsDir, 'combined.log'),
    format: format,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  }),
  
  // HTTP requests log
  new winston.transports.File({
    filename: path.join(logsDir, 'http.log'),
    level: 'http',
    format: format,
    maxsize: 5242880, // 5MB
    maxFiles: 3
  })
];

// Create logger
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  levels,
  format,
  transports,
  exitOnError: false
});

// Create stream object for Morgan HTTP middleware
logger.stream = {
  write: (message) => {
    logger.http(message.trim());
  }
};

// Enhanced logging methods
logger.logCPFValidation = (cpfHash, result, ip, userAgent) => {
  logger.info('CPF Validation', {
    type: 'cpf_validation',
    cpf_hash: cpfHash,
    valid: result.valido,
    source: result.fonte,
    ip: ip,
    user_agent: userAgent,
    timestamp: new Date().toISOString()
  });
};

logger.logCheckinAttempt = (eventoId, clienteId, success, reason, ip, userAgent) => {
  logger.info('Check-in Attempt', {
    type: 'checkin_attempt',
    evento_id: eventoId,
    cliente_id: clienteId,
    success: success,
    reason: reason,
    ip: ip,
    user_agent: userAgent,
    timestamp: new Date().toISOString()
  });
};

logger.logEquipmentHeartbeat = (equipmentId, status, ip) => {
  logger.info('Equipment Heartbeat', {
    type: 'equipment_heartbeat',
    equipment_id: equipmentId,
    status: status,
    ip: ip,
    timestamp: new Date().toISOString()
  });
};

logger.logSecurityEvent = (type, severity, data, ip, userAgent) => {
  logger.warn('Security Event', {
    type: 'security_event',
    event_type: type,
    severity: severity,
    data: data,
    ip: ip,
    user_agent: userAgent,
    timestamp: new Date().toISOString()
  });
};

logger.logAPICall = (method, url, statusCode, responseTime, ip, userAgent) => {
  logger.http('API Call', {
    type: 'api_call',
    method: method,
    url: url,
    status_code: statusCode,
    response_time: responseTime,
    ip: ip,
    user_agent: userAgent,
    timestamp: new Date().toISOString()
  });
};

logger.logDatabaseOperation = (operation, table, duration, rowCount) => {
  logger.debug('Database Operation', {
    type: 'database_operation',
    operation: operation,
    table: table,
    duration: duration,
    row_count: rowCount,
    timestamp: new Date().toISOString()
  });
};

logger.logCacheOperation = (operation, key, hit, duration) => {
  logger.debug('Cache Operation', {
    type: 'cache_operation',
    operation: operation,
    key: key,
    cache_hit: hit,
    duration: duration,
    timestamp: new Date().toISOString()
  });
};

logger.logAnalyticsGeneration = (type, eventId, duration, confidence) => {
  logger.info('Analytics Generation', {
    type: 'analytics_generation',
    analytics_type: type,
    event_id: eventId,
    duration: duration,
    confidence: confidence,
    timestamp: new Date().toISOString()
  });
};

// Error logging with context
logger.logError = (error, context = {}) => {
  logger.error('Application Error', {
    type: 'application_error',
    message: error.message,
    stack: error.stack,
    context: context,
    timestamp: new Date().toISOString()
  });
};

// Performance monitoring
logger.logPerformance = (operation, duration, metadata = {}) => {
  const level = duration > 5000 ? 'warn' : 'info';
  logger.log(level, 'Performance Metric', {
    type: 'performance_metric',
    operation: operation,
    duration: duration,
    metadata: metadata,
    timestamp: new Date().toISOString()
  });
};

// Business metrics
logger.logBusinessMetric = (metric, value, tags = {}) => {
  logger.info('Business Metric', {
    type: 'business_metric',
    metric: metric,
    value: value,
    tags: tags,
    timestamp: new Date().toISOString()
  });
};

module.exports = logger;
