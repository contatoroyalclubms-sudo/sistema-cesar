const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../utils/logger');

// Registrar equipamento no evento
router.post('/registrar', [
  body('evento_id')
    .isInt({ min: 1 })
    .withMessage('evento_id deve ser um número inteiro positivo'),
  body('nome')
    .notEmpty()
    .withMessage('Nome do equipamento é obrigatório'),
  body('tipo')
    .isIn(['tablet', 'qr_reader', 'printer', 'pos', 'camera', 'sensor'])
    .withMessage('Tipo de equipamento inválido'),
  body('ip_address')
    .isIP()
    .withMessage('IP address inválido'),
  body('mac_address')
    .optional()
    .matches(/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/)
    .withMessage('MAC address inválido'),
  body('localizacao')
    .optional()
    .isString()
    .withMessage('Localização deve ser uma string')
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
      evento_id, 
      nome, 
      tipo, 
      ip_address, 
      mac_address, 
      localizacao, 
      configuracao = {} 
    } = req.body;

    // Verificar se o evento existe
    const eventoExists = await db.query('SELECT id FROM eventos WHERE id = $1', [evento_id]);
    if (eventoExists.rows.length === 0) {
      return res.status(404).json({
        error: 'Evento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // Registrar equipamento
    const result = await db.query(`
      INSERT INTO equipamentos_eventos 
      (evento_id, nome, tipo, ip_address, mac_address, localizacao, configuracao, status, ultima_atividade)
      VALUES ($1, $2, $3, $4, $5, $6, $7, 'online', CURRENT_TIMESTAMP)
      ON CONFLICT (evento_id, ip_address) 
      DO UPDATE SET 
        nome = EXCLUDED.nome,
        tipo = EXCLUDED.tipo,
        mac_address = EXCLUDED.mac_address,
        localizacao = EXCLUDED.localizacao,
        configuracao = EXCLUDED.configuracao,
        status = 'online',
        ultima_atividade = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
      RETURNING id, nome, tipo, ip_address, status
    `, [evento_id, nome, tipo, ip_address, mac_address, localizacao, JSON.stringify(configuracao)]);

    logger.info('Equipamento registrado:', {
      equipamento_id: result.rows[0].id,
      evento_id,
      nome,
      tipo,
      ip_address
    });

    res.json({
      equipamento: result.rows[0],
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    if (error.code === '23505') { // Violação de constraint unique
      return res.status(409).json({
        error: 'IP address já registrado para este evento',
        timestamp: new Date().toISOString()
      });
    }

    logger.error('Erro ao registrar equipamento:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Heartbeat do equipamento
router.post('/heartbeat', [
  body('equipamento_id')
    .isInt({ min: 1 })
    .withMessage('equipamento_id deve ser um número inteiro positivo'),
  body('status')
    .optional()
    .isIn(['online', 'busy', 'maintenance', 'error'])
    .withMessage('Status inválido'),
  body('dados_status')
    .optional()
    .isObject()
    .withMessage('dados_status deve ser um objeto')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { equipamento_id, status = 'online', dados_status = {} } = req.body;
    const clientIp = req.ip || req.connection.remoteAddress;

    // Atualizar último heartbeat
    const result = await db.query(`
      UPDATE equipamentos_eventos 
      SET 
        status = $2,
        ultima_atividade = CURRENT_TIMESTAMP,
        configuracao = CASE 
          WHEN $3::jsonb != '{}'::jsonb THEN $3::jsonb
          ELSE configuracao
        END,
        updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING id, nome, tipo, status, ultima_atividade
    `, [equipamento_id, status, JSON.stringify(dados_status)]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Equipamento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // Cache do status para monitoramento rápido
    const cacheKey = `equipment:${equipamento_id}:status`;
    await cache.setex(cacheKey, 300, JSON.stringify({
      status,
      ultima_atividade: new Date().toISOString(),
      ip: clientIp,
      dados_status
    }));

    res.json({
      equipamento: result.rows[0],
      heartbeat_interval: 30, // segundos
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro no heartbeat do equipamento:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Listar equipamentos de um evento
router.get('/evento/:evento_id', async (req, res) => {
  try {
    const { evento_id } = req.params;
    const { incluir_offline = false } = req.query;

    let whereClause = 'WHERE evento_id = $1';
    const params = [evento_id];

    if (!incluir_offline) {
      whereClause += " AND status != 'offline'";
    }

    const result = await db.query(`
      SELECT 
        id,
        nome,
        tipo,
        ip_address,
        mac_address,
        status,
        localizacao,
        configuracao,
        ultima_atividade,
        responsavel_id,
        CASE 
          WHEN ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '2 minutes' THEN 'online'
          WHEN ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '10 minutes' THEN 'warning'
          ELSE 'offline'
        END as status_conexao,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ultima_atividade)) as segundos_inativo
      FROM equipamentos_eventos
      ${whereClause}
      ORDER BY ultima_atividade DESC
    `, params);

    // Enriquecer com dados do cache se disponível
    const equipamentosEnriquecidos = await Promise.all(
      result.rows.map(async (equipamento) => {
        const cacheKey = `equipment:${equipamento.id}:status`;
        const statusCache = await cache.get(cacheKey);
        
        if (statusCache) {
          const dadosCache = JSON.parse(statusCache);
          equipamento.dados_status = dadosCache.dados_status;
          equipamento.ip_atual = dadosCache.ip;
        }

        return equipamento;
      })
    );

    res.json({
      equipamentos: equipamentosEnriquecidos,
      total: equipamentosEnriquecidos.length,
      estatisticas: {
        online: equipamentosEnriquecidos.filter(e => e.status_conexao === 'online').length,
        warning: equipamentosEnriquecidos.filter(e => e.status_conexao === 'warning').length,
        offline: equipamentosEnriquecidos.filter(e => e.status_conexao === 'offline').length
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao listar equipamentos:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Obter detalhes de um equipamento específico
router.get('/:equipamento_id', async (req, res) => {
  try {
    const { equipamento_id } = req.params;

    const result = await db.query(`
      SELECT 
        eq.*,
        e.nome as evento_nome,
        u.nome as responsavel_nome,
        CASE 
          WHEN eq.ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '2 minutes' THEN 'online'
          WHEN eq.ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '10 minutes' THEN 'warning'
          ELSE 'offline'
        END as status_conexao,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - eq.ultima_atividade)) as segundos_inativo
      FROM equipamentos_eventos eq
      LEFT JOIN eventos e ON eq.evento_id = e.id
      LEFT JOIN usuarios u ON eq.responsavel_id = u.id
      WHERE eq.id = $1
    `, [equipamento_id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Equipamento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    const equipamento = result.rows[0];

    // Buscar histórico de atividade (últimas 24h)
    const historico = await db.query(`
      SELECT 
        DATE_TRUNC('hour', ultima_atividade) as hora,
        status,
        COUNT(*) as atualizacoes
      FROM equipamentos_eventos
      WHERE id = $1 
        AND ultima_atividade >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
      GROUP BY DATE_TRUNC('hour', ultima_atividade), status
      ORDER BY hora DESC
    `, [equipamento_id]);

    // Buscar dados do cache
    const cacheKey = `equipment:${equipamento_id}:status`;
    const statusCache = await cache.get(cacheKey);
    
    if (statusCache) {
      const dadosCache = JSON.parse(statusCache);
      equipamento.dados_status = dadosCache.dados_status;
      equipamento.ip_atual = dadosCache.ip;
    }

    res.json({
      equipamento,
      historico_24h: historico.rows,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao obter detalhes do equipamento:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Atualizar configuração do equipamento
router.put('/:equipamento_id/configuracao', [
  body('configuracao')
    .isObject()
    .withMessage('Configuração deve ser um objeto'),
  body('responsavel_id')
    .optional()
    .isInt({ min: 1 })
    .withMessage('responsavel_id deve ser um número inteiro positivo')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { equipamento_id } = req.params;
    const { configuracao, responsavel_id } = req.body;

    const result = await db.query(`
      UPDATE equipamentos_eventos 
      SET 
        configuracao = $2,
        responsavel_id = COALESCE($3, responsavel_id),
        updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING id, nome, tipo, configuracao, responsavel_id
    `, [equipamento_id, JSON.stringify(configuracao), responsavel_id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Equipamento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    logger.info('Configuração de equipamento atualizada:', {
      equipamento_id,
      responsavel_id
    });

    res.json({
      equipamento: result.rows[0],
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao atualizar configuração do equipamento:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Remover equipamento
router.delete('/:equipamento_id', async (req, res) => {
  try {
    const { equipamento_id } = req.params;

    const result = await db.query(`
      DELETE FROM equipamentos_eventos 
      WHERE id = $1
      RETURNING id, nome, tipo
    `, [equipamento_id]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        error: 'Equipamento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // Remover cache
    const cacheKey = `equipment:${equipamento_id}:status`;
    await cache.del(cacheKey);

    logger.info('Equipamento removido:', {
      equipamento_id,
      nome: result.rows[0].nome,
      tipo: result.rows[0].tipo
    });

    res.json({
      message: 'Equipamento removido com sucesso',
      equipamento: result.rows[0],
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro ao remover equipamento:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Descoberta automática de equipamentos na rede
router.post('/descobrir', [
  body('evento_id')
    .isInt({ min: 1 })
    .withMessage('evento_id deve ser um número inteiro positivo'),
  body('rede_ip')
    .matches(/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/)
    .withMessage('Formato de rede IP inválido (ex: 192.168.1.0/24)')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }

    const { evento_id, rede_ip } = req.body;

    // Verificar se o evento existe
    const eventoExists = await db.query('SELECT id FROM eventos WHERE id = $1', [evento_id]);
    if (eventoExists.rows.length === 0) {
      return res.status(404).json({
        error: 'Evento não encontrado',
        timestamp: new Date().toISOString()
      });
    }

    // Simular descoberta de equipamentos (em produção, usaria network scanning)
    const equipamentosEncontrados = [];
    
    // Esta é uma implementação simulada
    // Em produção, você usaria ferramentas como nmap ou bibliotecas de network scanning
    
    logger.info('Descoberta de equipamentos iniciada:', { evento_id, rede_ip });

    res.json({
      evento_id: parseInt(evento_id),
      rede_pesquisada: rede_ip,
      equipamentos_encontrados: equipamentosEncontrados,
      total_encontrados: equipamentosEncontrados.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro na descoberta de equipamentos:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
