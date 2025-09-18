import os
import re

# Corrigir nomes de funcoes com hifens
routers_dir = "app/routers"

for filename in os.listdir(routers_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(routers_dir, filename)
        print(f"Processando {filepath}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substituir hifens por underscores em nomes de funcoes
        # Padrao: async def nome_funcao-com-hifen(
        content = re.sub(r'async def (\w+)-', r'async def \1_', content)
        content = re.sub(r'def (\w+)-', r'def \1_', content)

        # Corrigir casos especificos conhecidos
        content = content.replace('dashboard_tempo-real()', 'dashboard_tempo_real()')
        content = content.replace('gamificacao_pontos-ranking()', 'gamificacao_pontos_ranking()')
        content = content.replace('meep_sync-eventos()', 'meep_sync_eventos()')
        content = content.replace('meep_sync-participantes()', 'meep_sync_participantes()')
        content = content.replace('n8n_webhook-config()', 'n8n_webhook_config()')
        content = content.replace('pdv_fechar-caixa()', 'pdv_fechar_caixa()')
        content = content.replace('produtos_categorias-list()', 'produtos_categorias_list()')
        content = content.replace('relatorios_vendas-detalhado()', 'relatorios_vendas_detalhado()')
        content = content.replace('relatorios_vendas-resumo()', 'relatorios_vendas_resumo()')
        content = content.replace('transacoes_processar-pagamento()', 'transacoes_processar_pagamento()')
        content = content.replace('usuarios_reset-senha()', 'usuarios_reset_senha()')
        content = content.replace('whatsapp_enviar-mensagem()', 'whatsapp_enviar_mensagem()')
        content = content.replace('whatsapp_enviar-grupo()', 'whatsapp_enviar_grupo()')

        # Corrigir qualquer outro padrao com hifen
        content = re.sub(r'(\w+)-(\w+)\(\)', r'\1_\2()', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  OK - Corrigido!")

print("\nTodos os arquivos foram processados!")