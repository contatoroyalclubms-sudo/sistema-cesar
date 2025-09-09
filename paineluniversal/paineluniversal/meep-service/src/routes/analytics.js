const express = require('express');
const router = express.Router();
const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../utils/logger');

// Análise de fluxo com previsões de IA
router.get('/fluxo-previsao', async (req, res) => {
  try {
    const { evento_id, periodo = '24h' } = req.query;

    if (!evento_id) {
      return res.status(400).json({
        error: 'evento_id é obrigatório',
        timestamp: new Date().toISOString()
      });
    }

    // Cache key
    const cacheKey = `analytics:fluxo:${evento_id}:${periodo}`;
    const cached = await cache.get(cacheKey);
    
    if (cached) {
      return res.json({
        ...JSON.parse(cached),
        fonte: 'cache'
      });
    }

    // Buscar dados históricos para treinamento
    const dadosHistoricos = await db.query(`
      SELECT 
        DATE_TRUNC('hour', timestamp_validacao) as hora,
        COUNT(*) FILTER (WHERE sucesso = true) as entradas,
        AVG(COUNT(*)) OVER (
          ORDER BY DATE_TRUNC('hour', timestamp_validacao) 
          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as media_movel_7h
      FROM validacoes_acesso
      WHERE evento_id = $1 
        AND timestamp_validacao >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        AND sucesso = true
      GROUP BY DATE_TRUNC('hour', timestamp_validacao)
      ORDER BY hora
    `, [evento_id]);

    // Análise de padrões (IA simplificada)
    const previsoes = gerarPrevisoes(dadosHistoricos.rows);
    
    // Salvar previsão no banco
    await db.query(`
      INSERT INTO previsoes_ia (evento_id, tipo_previsao, dados_entrada, resultado_previsao, confiabilidade)
      VALUES ($1, $2, $3, $4, $5)
    `, [
      evento_id,
      'fluxo_horario',
      JSON.stringify(dadosHistoricos.rows),
      JSON.stringify(previsoes),
      previsoes.confiabilidade
    ]);

    const resultado = {
      evento_id: parseInt(evento_id),
      periodo,
      dados_historicos: dadosHistoricos.rows,
      previsoes,
      insights: gerarInsights(dadosHistoricos.rows, previsoes),
      timestamp: new Date().toISOString()
    };

    // Cache por 1 hora
    await cache.setex(cacheKey, 3600, JSON.stringify(resultado));

    res.json(resultado);

  } catch (error) {
    logger.error('Erro na análise de fluxo:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Função de IA para gerar previsões
function gerarPrevisoes(dadosHistoricos) {
  if (!dadosHistoricos || dadosHistoricos.length < 3) {
    return {
      proximas_horas: [],
      pico_estimado: null,
      total_estimado: 0,
      confiabilidade: 0
    };
  }

  const agora = new Date();
  const proximasHoras = [];
  
  // Análise de padrões por hora do dia
  const padroesPorHora = {};
  dadosHistoricos.forEach(registro => {
    const hora = new Date(registro.hora).getHours();
    if (!padroesPorHora[hora]) {
      padroesPorHora[hora] = [];
    }
    padroesPorHora[hora].push(parseInt(registro.entradas));
  });

  // Calcular médias e tendências
  Object.keys(padroesPorHora).forEach(hora => {
    const valores = padroesPorHora[hora];
    padroesPorHora[hora] = {
      media: valores.reduce((a, b) => a + b, 0) / valores.length,
      variacao: Math.sqrt(valores.reduce((sq, n) => sq + Math.pow(n - padroesPorHora[hora].media, 2), 0) / valores.length)
    };
  });

  // Gerar previsões para próximas 12 horas
  let totalEstimado = 0;
  let picoEstimado = { hora: null, valor: 0 };

  for (let i = 0; i < 12; i++) {
    const horaPrevisao = new Date(agora.getTime() + i * 60 * 60 * 1000);
    const horaNum = horaPrevisao.getHours();
    
    let previsaoBase = padroesPorHora[horaNum]?.media || 0;
    
    // Aplicar fatores de ajuste
    // Fator de fim de semana
    if (horaPrevisao.getDay() === 0 || horaPrevisao.getDay() === 6) {
      previsaoBase *= 1.3; // Aumento de 30% nos fins de semana
    }
    
    // Fator de horário nobre (19h-23h)
    if (horaNum >= 19 && horaNum <= 23) {
      previsaoBase *= 1.5;
    }
    
    // Fator de horário comercial (9h-18h)
    if (horaNum >= 9 && horaNum <= 18) {
      previsaoBase *= 0.8;
    }

    const previsao = Math.max(0, Math.round(previsaoBase));
    totalEstimado += previsao;

    if (previsao > picoEstimado.valor) {
      picoEstimado = {
        hora: horaPrevisao.toISOString(),
        valor: previsao
      };
    }

    proximasHoras.push({
      hora: horaPrevisao.toISOString(),
      entradas_estimadas: previsao,
      confianca: Math.min(95, Math.max(70, 95 - (padroesPorHora[horaNum]?.variacao || 10)))
    });
  }

  // Calcular confiabilidade geral
  const confiabilidadeMedia = proximasHoras.reduce((sum, p) => sum + p.confianca, 0) / proximasHoras.length;

  return {
    proximas_horas: proximasHoras,
    pico_estimado: picoEstimado,
    total_estimado: totalEstimado,
    confiabilidade: Math.round(confiabilidadeMedia)
  };
}

// Gerar insights automáticos
function gerarInsights(dadosHistoricos, previsoes) {
  const insights = [];

  if (!dadosHistoricos || dadosHistoricos.length === 0) {
    return insights;
  }

  // Análise de tendência
  const entradas = dadosHistoricos.map(d => parseInt(d.entradas));
  const tendencia = calcularTendencia(entradas);
  
  if (tendencia > 0.1) {
    insights.push({
      tipo: 'crescimento',
      mensagem: `Tendência de crescimento de ${(tendencia * 100).toFixed(1)}% no fluxo de entrada`,
      prioridade: 'alta'
    });
  } else if (tendencia < -0.1) {
    insights.push({
      tipo: 'declinio',
      mensagem: `Tendência de declínio de ${Math.abs(tendencia * 100).toFixed(1)}% no fluxo de entrada`,
      prioridade: 'media'
    });
  }

  // Análise de picos
  if (previsoes.pico_estimado && previsoes.pico_estimado.valor > 0) {
    const horaPico = new Date(previsoes.pico_estimado.hora).getHours();
    insights.push({
      tipo: 'pico_previsto',
      mensagem: `Pico de ${previsoes.pico_estimado.valor} entradas previsto para ${horaPico}h`,
      prioridade: 'alta'
    });
  }

  // Análise de capacidade
  const mediaEntradas = entradas.reduce((a, b) => a + b, 0) / entradas.length;
  if (previsoes.total_estimado > mediaEntradas * 24 * 1.5) {
    insights.push({
      tipo: 'alta_demanda',
      mensagem: 'Alta demanda prevista - considere recursos adicionais',
      prioridade: 'critica'
    });
  }

  // Análise de variabilidade
  const variabilidade = Math.sqrt(entradas.reduce((sq, n) => sq + Math.pow(n - mediaEntradas, 2), 0) / entradas.length);
  if (variabilidade > mediaEntradas * 0.5) {
    insights.push({
      tipo: 'variabilidade',
      mensagem: 'Alto nível de variabilidade no fluxo - monitoramento contínuo recomendado',
      prioridade: 'media'
    });
  }

  return insights;
}

// Calcular tendência usando regressão linear simples
function calcularTendencia(valores) {
  const n = valores.length;
  if (n < 2) return 0;

  const x = valores.map((_, i) => i);
  const y = valores;

  const somaX = x.reduce((a, b) => a + b, 0);
  const somaY = y.reduce((a, b) => a + b, 0);
  const somaXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
  const somaX2 = x.reduce((sum, xi) => sum + xi * xi, 0);

  const slope = (n * somaXY - somaX * somaY) / (n * somaX2 - somaX * somaX);
  return slope / (somaY / n); // Normalizar pela média
}

// Dashboard em tempo real
router.get('/dashboard-realtime', async (req, res) => {
  try {
    const { evento_id } = req.query;

    if (!evento_id) {
      return res.status(400).json({
        error: 'evento_id é obrigatório',
        timestamp: new Date().toISOString()
      });
    }

    // Métricas em tempo real (última hora)
    const metricas = await db.query(`
      SELECT 
        COUNT(*) FILTER (WHERE sucesso = true) as entradas_ultima_hora,
        COUNT(*) FILTER (WHERE sucesso = false) as tentativas_falharam,
        COUNT(DISTINCT ip_address) as dispositivos_unicos,
        AVG(EXTRACT(EPOCH FROM (timestamp_validacao - LAG(timestamp_validacao) OVER (ORDER BY timestamp_validacao)))) as intervalo_medio_segundos
      FROM validacoes_acesso
      WHERE evento_id = $1 
        AND timestamp_validacao >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
    `, [evento_id]);

    // Status dos equipamentos
    const equipamentos = await db.query(`
      SELECT 
        nome,
        tipo,
        status,
        ultima_atividade,
        CASE 
          WHEN ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '2 minutes' THEN 'online'
          WHEN ultima_atividade > CURRENT_TIMESTAMP - INTERVAL '10 minutes' THEN 'warning'
          ELSE 'offline'
        END as status_conexao
      FROM equipamentos_eventos
      WHERE evento_id = $1
      ORDER BY ultima_atividade DESC
    `, [evento_id]);

    // Alertas de segurança (últimas 24h)
    const alertas = await db.query(`
      SELECT 
        COUNT(*) FILTER (WHERE gravidade = 'error') as erros,
        COUNT(*) FILTER (WHERE gravidade = 'warning') as avisos,
        COUNT(*) FILTER (WHERE gravidade = 'critical') as criticos
      FROM logs_seguranca_meep
      WHERE evento_id = $1 
        AND timestamp_evento >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
    `, [evento_id]);

    // Métricas por minuto (últimos 30 minutos)
    const fluxoMinuto = await db.query(`
      SELECT 
        DATE_TRUNC('minute', timestamp_validacao) as minuto,
        COUNT(*) FILTER (WHERE sucesso = true) as entradas,
        COUNT(*) FILTER (WHERE sucesso = false) as falhas
      FROM validacoes_acesso
      WHERE evento_id = $1 
        AND timestamp_validacao >= CURRENT_TIMESTAMP - INTERVAL '30 minutes'
      GROUP BY DATE_TRUNC('minute', timestamp_validacao)
      ORDER BY minuto DESC
    `, [evento_id]);

    res.json({
      evento_id: parseInt(evento_id),
      metricas_gerais: metricas.rows[0] || {},
      equipamentos: equipamentos.rows,
      alertas_seguranca: alertas.rows[0] || {},
      fluxo_por_minuto: fluxoMinuto.rows,
      ultima_atualizacao: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro no dashboard em tempo real:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

// Relatório de performance
router.get('/performance', async (req, res) => {
  try {
    const { evento_id, periodo = '7d' } = req.query;

    let intervalo;
    switch (periodo) {
      case '1d': intervalo = "INTERVAL '1 day'"; break;
      case '7d': intervalo = "INTERVAL '7 days'"; break;
      case '30d': intervalo = "INTERVAL '30 days'"; break;
      default: intervalo = "INTERVAL '7 days'";
    }

    let whereClause = `WHERE timestamp_validacao >= CURRENT_TIMESTAMP - ${intervalo}`;
    const params = [];

    if (evento_id) {
      whereClause += ' AND evento_id = $1';
      params.push(evento_id);
    }

    // KPIs principais
    const kpis = await db.query(`
      SELECT 
        COUNT(*) as total_tentativas,
        COUNT(*) FILTER (WHERE sucesso = true) as total_sucessos,
        COUNT(DISTINCT cliente_id) as clientes_unicos,
        COUNT(DISTINCT ip_address) as dispositivos_unicos,
        ROUND(AVG(EXTRACT(EPOCH FROM (timestamp_validacao - LAG(timestamp_validacao) OVER (ORDER BY timestamp_validacao)))), 2) as intervalo_medio_segundos,
        ROUND(COUNT(*) FILTER (WHERE sucesso = true) * 100.0 / COUNT(*), 2) as taxa_sucesso_pct
      FROM validacoes_acesso
      ${whereClause}
    `, params);

    // Performance por hora do dia
    const performancePorHora = await db.query(`
      SELECT 
        EXTRACT(HOUR FROM timestamp_validacao) as hora,
        COUNT(*) as tentativas,
        COUNT(*) FILTER (WHERE sucesso = true) as sucessos,
        ROUND(COUNT(*) FILTER (WHERE sucesso = true) * 100.0 / COUNT(*), 2) as taxa_sucesso_pct
      FROM validacoes_acesso
      ${whereClause}
      GROUP BY EXTRACT(HOUR FROM timestamp_validacao)
      ORDER BY hora
    `, params);

    // Top falhas
    const topFalhas = await db.query(`
      SELECT 
        motivo_falha,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM validacoes_acesso ${whereClause} AND sucesso = false), 2) as percentual
      FROM validacoes_acesso
      ${whereClause} AND sucesso = false AND motivo_falha IS NOT NULL
      GROUP BY motivo_falha
      ORDER BY quantidade DESC
      LIMIT 10
    `, params);

    res.json({
      periodo,
      kpis: kpis.rows[0] || {},
      performance_por_hora: performancePorHora.rows,
      principais_falhas: topFalhas.rows,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Erro no relatório de performance:', error);
    res.status(500).json({
      error: 'Erro interno do servidor',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
