const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../utils/logger');

// Logs de validação e segurança
router.get('/logs', async (req, res) => {
  try {
    const { 
      evento_id, 
      tipo_evento, 
      gravidade, 
      page = 1, 
      limit = 50,
      data_inicio,
      data_fim 
    } = req.query;

    let whereClause = '';
    const params = [];
    let paramCount = 0;

    // Filtros
    if (evento_id) {
      whereClause += ` AND evento_id = $${++paramCount}`;
      params.push(evento_id);
    }

    if (tipo_evento) {
      whereClause += ` AND tipo_evento = $${++paramCount}`;
      params.push(tipo_evento);
    }

    if (gravidade) {
      whereClause += ` AND gravidade = $${++paramCount}`;
      params.push(gravidade);
    }

    if (data_inicio) {
      whereClause += ` AND timestamp_evento >= $${++paramCount}`;
      params.push(data_inicio);
    }

    if (data_fim) {
      whereClause += ` AND timestamp_evento <= $${++paramCount}`;
      params.push(data_fim);
    }

    const offset = (page - 1) * limit;
    params.push(limit, offset);

    const query = `
      SELECT 
        l.id,
        l.tipo_evento,
        l.gravidade,
        l.ip_address,
        l.user_agent,
        l.dados_evento,
        l.timestamp_evento,
        l.resolvido,
        e.nome as evento_nome,
        u.nome as usuario_nome
      FROM logs_seguranca_meep l
      LEFT JOIN eventos e ON l.evento_id = e.id
      LEFT JOIN usuarios u ON l.usuario_id = u.id
      WHERE 1=1 ${whereClause}
      ORDER BY l.timestamp_evento DESC
      LIMIT $${params.length - 1} OFFSET $${params.length}
    `;

    const result = await db.query(query, params);

    // Contar total
    const countQuery = `
      SELECT COUNT(*) as total
      FROM logs_seguranca_meep l
      WHERE 1=1 ${whereClause}
    `;
    
    const countResult = await db.query(countQuery, params.slice(0, -2));
    const total = parseInt(countResult.rows[0].total);

    res.json({
      logs: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / limit)
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar logs de validação:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Criar log de segurança
router.post('/logs', [
  body('tipo_evento')
    .notEmpty()
    .withMessage('Tipo de evento é obrigatório'),
  body('gravidade')
    .isIn(['info', 'warning', 'error', 'critical'])
    .withMessage('Gravidade inválida'),
  body('dados_evento')
    .isObject()
    .withMessage('Dados do evento devem ser um objeto'),
  body('evento_id')
    .optional()
    .isInt({ min: 1 })
    .withMessage('evento_id deve ser um número inteiro positivo'),
  body('usuario_id')
    .optional()
    .isInt({ min: 1 })
    .withMessage('usuario_id deve ser um número inteiro positivo')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { 
      tipo_evento, 
      gravidade, 
      dados_evento, 
      evento_id, 
      usuario_id 
    } = req.body;
    
    const clientIp = req.ip || req.connection.remoteAddress;
    const userAgent = req.get('User-Agent');

    const result = await db.query(`
      INSERT INTO logs_seguranca_meep 
      (evento_id, tipo_evento, gravidade, ip_address, user_agent, dados_evento, usuario_id)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id, timestamp_evento
    `, [
      evento_id,
      tipo_evento,
      gravidade,
      clientIp,
      userAgent,
      JSON.stringify(dados_evento),
      usuario_id
    ]);

    logger.info('Log de segurança criado:', {
      log_id: result.rows[0].id,
      tipo_evento,
      gravidade,
      evento_id
    });

    res.json({
      log_id: result.rows[0].id,
      timestamp: result.rows[0].timestamp_evento
    });

  } catch (error) {
    logger.error('Erro ao criar log de segurança:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Marcar log como resolvido
router.put('/logs/:log_id/resolver', [
  body('usuario_id')
    .optional()
    .isInt({ min: 1 })
    .withMessage('usuario_id deve ser um número inteiro positivo')
], async (req, res) => {
  try {
    const { log_id } = req.params;
    const { usuario_id } = req.body;

    const result = await db.query(`
      UPDATE logs_seguranca_meep 
      SET 
        resolvido = true,
        usuario_id = COALESCE($2, usuario_id)
      WHERE id = $1
      RETURNING id, tipo_evento, gravidade, resolvido
    `, [log_id, usuario_id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Log não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    logger.info('Log marcado como resolvido:', {
      log_id,
      usuario_id
    });

    res.json({
      log: result.rows[0],
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao resolver log:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Estatísticas de segurança
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

    let whereClause = `WHERE timestamp_evento >= CURRENT_TIMESTAMP - ${intervalo}`;
    const params = [];

    if (evento_id) {
      whereClause += ' AND evento_id = $1';
      params.push(evento_id);
    }

    // Estatísticas por gravidade
    const statsPorGravidade = await db.query(`
      SELECT 
        gravidade,
        COUNT(*) as quantidade,
        COUNT(*) FILTER (WHERE resolvido = true) as resolvidos,
        COUNT(*) FILTER (WHERE resolvido = false) as pendentes
      FROM logs_seguranca_meep
      ${whereClause}
      GROUP BY gravidade
      ORDER BY 
        CASE gravidade 
          WHEN 'critical' THEN 1
          WHEN 'error' THEN 2
          WHEN 'warning' THEN 3
          WHEN 'info' THEN 4
        END
    `, params);

    // Estatísticas por tipo de evento
    const statsPorTipo = await db.query(`
      SELECT 
        tipo_evento,
        COUNT(*) as quantidade,
        COUNT(DISTINCT ip_address) as ips_unicos
      FROM logs_seguranca_meep
      ${whereClause}
      GROUP BY tipo_evento
      ORDER BY quantidade DESC
      LIMIT 10
    `, params);

    // Tendência temporal
    const tendenciaTemporal = await db.query(`
      SELECT 
        DATE_TRUNC('hour', timestamp_evento) as hora,
        COUNT(*) as total_eventos,
        COUNT(*) FILTER (WHERE gravidade IN ('error', 'critical')) as eventos_criticos
      FROM logs_seguranca_meep
      ${whereClause}
      GROUP BY DATE_TRUNC('hour', timestamp_evento)
      ORDER BY hora DESC
      LIMIT 24
    `, params);

    // IPs mais ativos
    const ipsAtivos = await db.query(`
      SELECT 
        ip_address,
        COUNT(*) as tentativas,
        COUNT(DISTINCT tipo_evento) as tipos_evento,
        MAX(timestamp_evento) as ultima_atividade
      FROM logs_seguranca_meep
      ${whereClause}
      GROUP BY ip_address
      ORDER BY tentativas DESC
      LIMIT 10
    `, params);

    // Resumo geral
    const resumo = await db.query(`
      SELECT 
        COUNT(*) as total_eventos,
        COUNT(*) FILTER (WHERE gravidade = 'critical') as criticos,
        COUNT(*) FILTER (WHERE gravidade = 'error') as erros,
        COUNT(*) FILTER (WHERE gravidade = 'warning') as avisos,
        COUNT(*) FILTER (WHERE resolvido = true) as resolvidos,
        COUNT(DISTINCT ip_address) as ips_unicos,
        COUNT(DISTINCT tipo_evento) as tipos_evento_unicos
      FROM logs_seguranca_meep
      ${whereClause}
    `, params);

    res.json({
      periodo,
      resumo: resumo.rows[0] || {},
      por_gravidade: statsPorGravidade.rows,
      por_tipo_evento: statsPorTipo.rows,
      tendencia_temporal: tendenciaTemporal.rows,
      ips_mais_ativos: ipsAtivos.rows,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar estatísticas de segurança:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Alertas de segurança em tempo real
router.get('/alertas', async (req, res) => {
  try {
    const { evento_id } = req.query;

    let whereClause = `WHERE gravidade IN ('error', 'critical') 
                       AND resolvido = false 
                       AND timestamp_evento >= CURRENT_TIMESTAMP - INTERVAL '24 hours'`;
    const params = [];

    if (evento_id) {
      whereClause += ' AND evento_id = $1';
      params.push(evento_id);
    }

    const alertas = await db.query(`
      SELECT 
        l.id,
        l.tipo_evento,
        l.gravidade,
        l.ip_address,
        l.dados_evento,
        l.timestamp_evento,
        e.nome as evento_nome,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - l.timestamp_evento)) as segundos_desde
      FROM logs_seguranca_meep l
      LEFT JOIN eventos e ON l.evento_id = e.id
      ${whereClause}
      ORDER BY l.timestamp_evento DESC
      LIMIT 50
    `, params);

    // Classificar urgência
    const alertasComUrgencia = alertas.rows.map(alerta => {
      let urgencia = 'baixa';
      
      if (alerta.gravidade === 'critical') {
        urgencia = 'critica';
      } else if (alerta.gravidade === 'error' && alerta.segundos_desde < 3600) {
        urgencia = 'alta';
      } else if (alerta.gravidade === 'error') {
        urgencia = 'media';
      }

      return {
        ...alerta,
        urgencia,
        tempo_decorrido: formatarTempo(alerta.segundos_desde)
      };
    });

    res.json({
      alertas: alertasComUrgencia,
      total: alertasComUrgencia.length,
      estatisticas: {
        criticos: alertasComUrgencia.filter(a => a.urgencia === 'critica').length,
        altos: alertasComUrgencia.filter(a => a.urgencia === 'alta').length,
        medios: alertasComUrgencia.filter(a => a.urgencia === 'media').length,
        baixos: alertasComUrgencia.filter(a => a.urgencia === 'baixa').length
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar alertas de segurança:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Função utilitária para formatação de tempo
function formatarTempo(segundos) {
  if (segundos < 60) {
    return `${Math.floor(segundos)}s`;
  } else if (segundos < 3600) {
    return `${Math.floor(segundos / 60)}min`;
  } else if (segundos < 86400) {
    return `${Math.floor(segundos / 3600)}h`;
  } else {
    return `${Math.floor(segundos / 86400)}d`;
  }
}

// Buscar sessões ativas de operadores
router.get('/sessoes', async (req, res) => {
  try {
    const { evento_id, ativo = true } = req.query;

    let whereClause = '';
    const params = [];

    if (evento_id) {
      whereClause += ' WHERE s.evento_id = $1';
      params.push(evento_id);
    }

    if (ativo !== undefined) {
      whereClause += whereClause ? ' AND' : ' WHERE';
      whereClause += ` s.ativo = $${params.length + 1}`;
      params.push(ativo === 'true');
    }

    const sessoes = await db.query(`
      SELECT 
        s.id,
        s.token_sessao,
        s.ip_address,
        s.inicio_sessao,
        s.fim_sessao,
        s.ativo,
        s.configuracoes,
        u.nome as usuario_nome,
        u.email as usuario_email,
        e.nome as evento_nome,
        eq.nome as equipamento_nome,
        eq.tipo as equipamento_tipo,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - s.inicio_sessao)) as duracao_segundos
      FROM sessoes_operadores s
      LEFT JOIN usuarios u ON s.usuario_id = u.id
      LEFT JOIN eventos e ON s.evento_id = e.id
      LEFT JOIN equipamentos_eventos eq ON s.equipamento_id = eq.id
      ${whereClause}
      ORDER BY s.inicio_sessao DESC
    `, params);

    res.json({
      sessoes: sessoes.rows.map(sessao => ({
        ...sessao,
        duracao_formatada: formatarTempo(sessao.duracao_segundos)
      })),
      total: sessoes.rows.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao buscar sessões de operadores:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
