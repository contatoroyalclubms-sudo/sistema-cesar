const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const crypto = require('crypto');
const axios = require('axios');
const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../utils/logger');

// Validação matemática do CPF
function validarCPF(cpf) {
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) {
    return false;
  }

  // Validação do primeiro dígito
  let soma = 0;
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpf.charAt(i)) * (10 - i);
  }
  let resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpf.charAt(9))) return false;

  // Validação do segundo dígito
  soma = 0;
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpf.charAt(i)) * (11 - i);
  }
  resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpf.charAt(10))) return false;

  return true;
}

// Hash do CPF para cache (LGPD compliance)
function hashCPF(cpf) {
  const salt = process.env.CPF_SALT || 'default_salt';
  return crypto.createHash('sha256').update(cpf + salt).digest('hex');
}

// Validação com Receita Federal
async function validarCPFReceitaFederal(cpf) {
  try {
    const response = await axios.get(
      `${process.env.API_RECEITA_FEDERAL_URL}/cpf/${cpf}`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.API_RECEITA_TOKEN}`,
          'User-Agent': 'MEEP-System/1.0'
        },
        timeout: 5000
      }
    );

    return {
      valido: response.data.situacao === 'REGULAR',
      nome: response.data.nome,
      situacao: response.data.situacao,
      fonte: 'receita_federal'
    };
  } catch (error) {
    logger.warn('Erro na validação com Receita Federal:', {
      cpf: hashCPF(cpf),
      error: error.message
    });
    
    // Fallback para validação matemática apenas
    return {
      valido: validarCPF(cpf),
      nome: null,
      situacao: 'INDISPONIVEL',
      fonte: 'validacao_matematica'
    };
  }
}

// POST /api/meep/cpf/validar
router.post('/validar', [
  body('cpf')
    .isLength({ min: 11, max: 11 })
    .isNumeric()
    .withMessage('CPF deve conter 11 dígitos numéricos'),
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

    const { cpf, evento_id } = req.body;
    const cpfHash = hashCPF(cpf);
    const clientIp = req.ip || req.connection.remoteAddress;

    // Log da tentativa de validação
    await db.query(`
      INSERT INTO logs_seguranca_meep (tipo_evento, gravidade, ip_address, dados_evento)
      VALUES ($1, $2, $3, $4)
    `, [
      'validacao_cpf',
      'info',
      clientIp,
      JSON.stringify({
        cpf_hash: cpfHash,
        evento_id,
        timestamp: new Date().toISOString()
      })
    ]);

    // Verificar cache primeiro
    const cacheKey = `cpf_validation:${cpfHash}`;
    let validationResult = await cache.get(cacheKey);

    if (validationResult) {
      logger.info('CPF validation from cache', { cpf_hash: cpfHash });
      
      return res.json({
        ...JSON.parse(validationResult),
        fonte: 'cache',
        timestamp: new Date().toISOString()
      });
    }

    // Validar CPF
    const resultado = await validarCPFReceitaFederal(cpf);

    // Cache do resultado por 24 horas
    await cache.setex(cacheKey, 86400, JSON.stringify(resultado));

    // Salvar ou atualizar cliente se válido
    if (resultado.valido && resultado.nome) {
      await db.query(`
        INSERT INTO clientes_eventos (cpf, nome_completo)
        VALUES ($1, $2)
        ON CONFLICT (cpf) 
        DO UPDATE SET 
          nome_completo = EXCLUDED.nome_completo,
          updated_at = CURRENT_TIMESTAMP
      `, [cpf, resultado.nome]);
    }

    logger.info('CPF validation completed', {
      cpf_hash: cpfHash,
      valido: resultado.valido,
      fonte: resultado.fonte
    });

    res.json({
      ...resultado,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro na validação de CPF:', {
      error: error.message,
      stack: error.stack,
      cpf_hash: hashCPF(req.body.cpf || '')
    });

    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// GET /api/meep/cpf/validacoes-recentes
router.get('/validacoes-recentes', async (req, res) => {
  try {
    const { evento_id, limit = 50 } = req.query;

    let query = `
      SELECT 
        l.id,
        l.tipo_evento,
        l.gravidade,
        l.ip_address,
        l.timestamp_evento,
        l.dados_evento,
        e.nome as evento_nome
      FROM logs_seguranca_meep l
      LEFT JOIN eventos e ON (l.dados_evento->>'evento_id')::int = e.id
      WHERE l.tipo_evento = 'validacao_cpf'
    `;
    
    const params = [];
    
    if (evento_id) {
      query += ` AND (l.dados_evento->>'evento_id')::int = $1`;
      params.push(evento_id);
    }
    
    query += ` ORDER BY l.timestamp_evento DESC LIMIT $${params.length + 1}`;
    params.push(limit);

    const result = await db.query(query, params);

    res.json({
      validacoes: result.rows,
      total: result.rows.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar validações recentes:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// GET /api/meep/cpf/stats
router.get('/stats', async (req, res) => {
  try {
    const { evento_id, periodo = '7d' } = req.query;

    // Determinar intervalo baseado no período
    let intervalo;
    switch (periodo) {
      case '1d': intervalo = "INTERVAL '1 day'"; break;
      case '7d': intervalo = "INTERVAL '7 days'"; break;
      case '30d': intervalo = "INTERVAL '30 days'"; break;
      default: intervalo = "INTERVAL '7 days'";
    }

    let whereClause = `WHERE l.tipo_evento = 'validacao_cpf' AND l.timestamp_evento >= CURRENT_TIMESTAMP - ${intervalo}`;
    const params = [];

    if (evento_id) {
      whereClause += ` AND (l.dados_evento->>'evento_id')::int = $1`;
      params.push(evento_id);
    }

    const statsQuery = `
      SELECT 
        COUNT(*) as total_validacoes,
        COUNT(*) FILTER (WHERE l.gravidade = 'error') as validacoes_erro,
        COUNT(DISTINCT l.ip_address) as ips_unicos,
        DATE_TRUNC('hour', l.timestamp_evento) as hora,
        COUNT(*) as validacoes_por_hora
      FROM logs_seguranca_meep l
      ${whereClause}
      GROUP BY DATE_TRUNC('hour', l.timestamp_evento)
      ORDER BY hora DESC
    `;

    const result = await db.query(statsQuery, params);

    // Calcular estatísticas agregadas
    const totalValidacoes = result.rows.reduce((sum, row) => sum + parseInt(row.validacoes_por_hora), 0);
    const totalErros = result.rows.reduce((sum, row) => sum + parseInt(row.validacoes_erro), 0);
    const taxaSucesso = totalValidacoes > 0 ? ((totalValidacoes - totalErros) / totalValidacoes * 100) : 0;

    res.json({
      periodo,
      estatisticas: {
        total_validacoes: totalValidacoes,
        total_erros: totalErros,
        taxa_sucesso: Math.round(taxaSucesso * 100) / 100,
        ips_unicos: new Set(result.rows.map(r => r.ip_address)).size
      },
      historico_por_hora: result.rows.map(row => ({
        hora: row.hora,
        validacoes: parseInt(row.validacoes_por_hora),
        erros: parseInt(row.validacoes_erro)
      })),
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar estatísticas de CPF:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
