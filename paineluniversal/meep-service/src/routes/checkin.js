const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const crypto = require('crypto');
const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../utils/logger');

// Validar acesso multi-fator (QR Code + 3 dígitos CPF)
router.post('/validate-access', [
  body('qr_code')
    .notEmpty()
    .withMessage('QR Code é obrigatório'),
  body('cpf_digits')
    .isLength({ min: 3, max: 3 })
    .isNumeric()
    .withMessage('CPF digits deve conter exatamente 3 dígitos'),
  body('evento_id')
    .optional()
    .isInt({ min: 1 })
    .withMessage('evento_id deve ser um número inteiro positivo')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { qr_code, cpf_digits, evento_id } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;
    const userAgent = req.get('User-Agent');

    let qrData;
    try {
      qrData = JSON.parse(qr_code);
    } catch (e) {
      return res.status(400).json({
        error: 'QR Code inválido - formato JSON inválido',
        timestamp: new Date().toISOString()
      });
    }

    // Validar estrutura do QR Code
    if (!qrData.cpf || !qrData.hash || !qrData.timestamp) {
      return res.status(400).json({
        error: 'QR Code inválido - campos obrigatórios ausentes',
        timestamp: new Date().toISOString()
      });
    }

    // Verificar se QR Code não expirou (máximo 5 minutos)
    const qrTimestamp = new Date(qrData.timestamp);
    const agora = new Date();
    const diferencaMinutos = (agora - qrTimestamp) / (1000 * 60);

    if (diferencaMinutos > 5) {
      await logValidationAttempt(evento_id, null, qr_code, cpf_digits, clientIp, userAgent, false, 'QR Code expirado');
      
      return res.status(400).json({
        error: 'QR Code expirado',
        timestamp: new Date().toISOString()
      });
    }

    // Verificar se os 3 dígitos do CPF correspondem
    const cpfFromQR = qrData.cpf.replace(/[^\d]/g, '');
    const expectedDigits = cpfFromQR.substring(0, 3);

    if (cpf_digits !== expectedDigits) {
      await logValidationAttempt(evento_id, null, qr_code, cpf_digits, clientIp, userAgent, false, 'Dígitos CPF incorretos');
      
      return res.status(401).json({
        error: 'Dígitos do CPF incorretos',
        timestamp: new Date().toISOString()
      });
    }

    // Verificar hash de integridade
    const expectedHash = crypto
      .createHash('sha256')
      .update(cpfFromQR + qrData.timestamp + (process.env.CPF_SALT || 'default_salt'))
      .digest('hex');

    if (qrData.hash !== expectedHash) {
      await logValidationAttempt(evento_id, null, qr_code, cpf_digits, clientIp, userAgent, false, 'Hash de integridade inválido');
      
      return res.status(401).json({
        error: 'QR Code inválido - hash incorreto',
        timestamp: new Date().toISOString()
      });
    }

    // Buscar cliente
    const clienteResult = await db.query(
      'SELECT id, nome_completo FROM clientes_eventos WHERE cpf = $1',
      [cpfFromQR]
    );

    let clienteId = null;
    if (clienteResult.rows.length === 0) {
      // Criar cliente se não existir
      const insertResult = await db.query(
        'INSERT INTO clientes_eventos (cpf, nome_completo) VALUES ($1, $2) RETURNING id',
        [cpfFromQR, 'Cliente MEEP']
      );
      clienteId = insertResult.rows[0].id;
    } else {
      clienteId = clienteResult.rows[0].id;
    }

    // Verificar se já fez check-in no evento hoje
    if (evento_id) {
      const checkInHoje = await db.query(`
        SELECT id FROM validacoes_acesso 
        WHERE evento_id = $1 
          AND cliente_id = $2 
          AND sucesso = true 
          AND DATE(timestamp_validacao) = CURRENT_DATE
      `, [evento_id, clienteId]);

      if (checkInHoje.rows.length > 0) {
        await logValidationAttempt(evento_id, clienteId, qr_code, cpf_digits, clientIp, userAgent, false, 'Check-in já realizado hoje');
        
        return res.status(409).json({
          error: 'Check-in já realizado hoje para este evento',
          timestamp: new Date().toISOString()
        });
      }
    }

    // Registrar acesso bem-sucedido
    await logValidationAttempt(evento_id, clienteId, qr_code, cpf_digits, clientIp, userAgent, true, null);

    logger.info('Check-in realizado com sucesso', {
      cliente_id: clienteId,
      evento_id,
      ip: clientIp
    });

    res.json({
      sucesso: true,
      cliente: {
        id: clienteId,
        nome: clienteResult.rows[0]?.nome_completo || 'Cliente MEEP'
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro na validação de acesso:', {
      error: error.message,
      stack: error.stack
    });

    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Função para registrar tentativas de validação
async function logValidationAttempt(eventoId, clienteId, qrCode, cpfDigits, ip, userAgent, sucesso, motivoFalha) {
  try {
    const cpfHash = crypto.createHash('sha256').update(qrCode + (process.env.CPF_SALT || 'default_salt')).digest('hex');
    
    await db.query(`
      INSERT INTO validacoes_acesso 
      (evento_id, cliente_id, cpf_hash, qr_code_data, cpf_digits, ip_address, user_agent, sucesso, motivo_falha)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `, [
      eventoId,
      clienteId,
      cpfHash,
      qrCode,
      cpfDigits,
      ip,
      userAgent,
      sucesso,
      motivoFalha
    ]);
  } catch (error) {
    logger.error('Erro ao registrar tentativa de validação:', error);
  }
}

// GET /api/meep/checkin/historico
router.get('/historico', async (req, res) => {
  try {
    const { evento_id, page = 1, limit = 50, sucesso } = req.query;

    let whereClause = '';
    const params = [];
    
    if (evento_id) {
      whereClause += ' WHERE va.evento_id = $1';
      params.push(evento_id);
    }
    
    if (sucesso !== undefined) {
      whereClause += whereClause ? ' AND' : ' WHERE';
      whereClause += ` va.sucesso = $${params.length + 1}`;
      params.push(sucesso === 'true');
    }

    const offset = (page - 1) * limit;
    params.push(limit, offset);

    const query = `
      SELECT 
        va.id,
        va.timestamp_validacao,
        va.sucesso,
        va.motivo_falha,
        va.ip_address,
        ce.nome_completo as cliente_nome,
        e.nome as evento_nome
      FROM validacoes_acesso va
      LEFT JOIN clientes_eventos ce ON va.cliente_id = ce.id
      LEFT JOIN eventos e ON va.evento_id = e.id
      ${whereClause}
      ORDER BY va.timestamp_validacao DESC
      LIMIT $${params.length - 1} OFFSET $${params.length}
    `;

    const result = await db.query(query, params);

    // Contar total
    const countQuery = `
      SELECT COUNT(*) as total
      FROM validacoes_acesso va
      ${whereClause}
    `;
    
    const countResult = await db.query(countQuery, params.slice(0, -2));
    const total = parseInt(countResult.rows[0].total);

    res.json({
      historico: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / limit)
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar histórico de check-in:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// GET /api/meep/checkin/stats
router.get('/stats', async (req, res) => {
  try {
    const { evento_id, periodo = '7d' } = req.query;

    let intervalo;
    switch (periodo) {
      case '1d': intervalo = "INTERVAL '1 day'"; break;
      case '7d': intervalo = "INTERVAL '7 days'"; break;
      case '30d': intervalo = "INTERVAL '30 days'"; break;
      default: intervalo = "INTERVAL '7 days'";
    }

    let whereClause = `WHERE va.timestamp_validacao >= CURRENT_TIMESTAMP - ${intervalo}`;
    const params = [];

    if (evento_id) {
      whereClause += ' AND va.evento_id = $1';
      params.push(evento_id);
    }

    const statsQuery = `
      SELECT 
        COUNT(*) as total_tentativas,
        COUNT(*) FILTER (WHERE va.sucesso = true) as checkins_sucesso,
        COUNT(*) FILTER (WHERE va.sucesso = false) as checkins_falha,
        COUNT(DISTINCT va.ip_address) as ips_unicos,
        COUNT(DISTINCT va.cliente_id) as clientes_unicos,
        DATE_TRUNC('hour', va.timestamp_validacao) as hora,
        COUNT(*) as tentativas_por_hora,
        COUNT(*) FILTER (WHERE va.sucesso = true) as sucessos_por_hora
      FROM validacoes_acesso va
      ${whereClause}
      GROUP BY DATE_TRUNC('hour', va.timestamp_validacao)
      ORDER BY hora DESC
    `;

    const result = await db.query(statsQuery, params);

    // Calcular estatísticas agregadas
    const totalTentativas = result.rows.reduce((sum, row) => sum + parseInt(row.tentativas_por_hora), 0);
    const totalSucessos = result.rows.reduce((sum, row) => sum + parseInt(row.sucessos_por_hora), 0);
    const taxaSucesso = totalTentativas > 0 ? (totalSucessos / totalTentativas * 100) : 0;

    // Buscar motivos de falha mais comuns
    const falhasQuery = `
      SELECT 
        motivo_falha,
        COUNT(*) as quantidade
      FROM validacoes_acesso va
      ${whereClause} AND va.sucesso = false AND va.motivo_falha IS NOT NULL
      GROUP BY motivo_falha
      ORDER BY quantidade DESC
      LIMIT 5
    `;

    const falhasResult = await db.query(falhasQuery, params);

    res.json({
      periodo,
      estatisticas: {
        total_tentativas: totalTentativas,
        checkins_sucesso: totalSucessos,
        checkins_falha: totalTentativas - totalSucessos,
        taxa_sucesso: Math.round(taxaSucesso * 100) / 100,
        clientes_unicos: new Set(result.rows.map(r => r.cliente_id)).size,
        ips_unicos: new Set(result.rows.map(r => r.ip_address)).size
      },
      historico_por_hora: result.rows.map(row => ({
        hora: row.hora,
        tentativas: parseInt(row.tentativas_por_hora),
        sucessos: parseInt(row.sucessos_por_hora),
        falhas: parseInt(row.tentativas_por_hora) - parseInt(row.sucessos_por_hora)
      })),
      principais_falhas: falhasResult.rows,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar estatísticas de check-in:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// POST /api/meep/checkin/gerar-qr
router.post('/gerar-qr', [
  body('cpf')
    .isLength({ min: 11, max: 11 })
    .isNumeric()
    .withMessage('CPF deve conter 11 dígitos numéricos')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { cpf } = req.body;
    const timestamp = new Date().toISOString();
    
    // Gerar hash de integridade
    const hash = crypto
      .createHash('sha256')
      .update(cpf + timestamp + (process.env.CPF_SALT || 'default_salt'))
      .digest('hex');

    const qrData = {
      cpf,
      timestamp,
      hash,
      version: '1.0'
    };

    res.json({
      qr_code: JSON.stringify(qrData),
      valido_ate: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 minutos
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao gerar QR Code:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
