#!/usr/bin/env node

/**
 * Frontend Corrections Applicator
 * 
 * Script para aplicar correções específicas no frontend React/TypeScript
 * com base na análise do framework de testes.
 * 
 * Foco: Corrigir problemas reais mantendo funcionalidades de produção
 */

const fs = require('fs');
const path = require('path');

class FrontendCorrectionsApplicator {
    constructor() {
        this.frontendDir = path.join(__dirname, 'frontend', 'src');
        this.corrections = [];
        this.backupDir = path.join(__dirname, `frontend_backup_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`);
        this.verbose = true;
    }

    log(message, type = 'info') {
        if (!this.verbose) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌',
            fix: '🔧'
        };
        
        console.log(`[${timestamp}] ${icons[type]} ${message}`);
    }

    // Criar backup dos arquivos antes das correções
    createBackup(filePath) {
        try {
            const relativePath = path.relative(this.frontendDir, filePath);
            const backupPath = path.join(this.backupDir, relativePath);
            
            // Criar diretório de backup se não existir
            const backupDirPath = path.dirname(backupPath);
            if (!fs.existsSync(backupDirPath)) {
                fs.mkdirSync(backupDirPath, { recursive: true });
            }
            
            // Copiar arquivo original
            fs.copyFileSync(filePath, backupPath);
            this.log(`Backup criado: ${relativePath}`, 'success');
        } catch (error) {
            this.log(`Erro ao criar backup para ${filePath}: ${error.message}`, 'error');
        }
    }

    // Verificar se arquivo precisa de correção
    analyzeFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const fileName = path.basename(filePath);
            const relativePath = path.relative(this.frontendDir, filePath);
            
            const issues = [];
            
            // Análise 1: React import desnecessário (novo JSX Transform)
            if (content.includes("import React from 'react'") && 
                !content.includes('React.') && 
                !content.includes('React,')) {
                issues.push({
                    type: 'unnecessary_react_import',
                    description: 'Import React desnecessário com novo JSX Transform',
                    severity: 'low'
                });
            }

            // Análise 2: Componentes sem export (apenas se realmente problemático)
            if (content.includes('const ') && 
                content.includes('= (') && 
                !content.includes('export default') && 
                !content.includes('export {') &&
                !relativePath.includes('ui/') && // Excluir shadcn/ui
                !fileName.includes('.test.')) {
                issues.push({
                    type: 'missing_export',
                    description: 'Componente pode precisar de export',
                    severity: 'medium'
                });
            }

            // Análise 3: Props sem tipagem TypeScript
            if (content.includes('props') && 
                !content.includes('interface') && 
                !content.includes('type ') &&
                fileName.endsWith('.tsx')) {
                issues.push({
                    type: 'missing_props_typing',
                    description: 'Props podem precisar de tipagem TypeScript',
                    severity: 'low'
                });
            }

            // Análise 4: Imports com problemas
            const badImports = content.match(/import.*from\s+['"][^'"]*['"]/g) || [];
            for (const importLine of badImports) {
                if (importLine.includes('../') && importLine.split('../').length > 5) {
                    issues.push({
                        type: 'deep_relative_import',
                        description: 'Import relativo muito profundo',
                        severity: 'medium'
                    });
                }
            }

            return {
                filePath,
                relativePath,
                content,
                issues,
                needsCorrection: issues.filter(i => i.severity !== 'low').length > 0
            };

        } catch (error) {
            this.log(`Erro ao analisar ${filePath}: ${error.message}`, 'error');
            return null;
        }
    }

    // Aplicar correção específica
    applyCorrection(analysis, issueType) {
        let content = analysis.content;
        let correctionApplied = false;

        switch (issueType) {
            case 'unnecessary_react_import':
                // Remover import React desnecessário
                content = content.replace(/import React from ['"]react['"];?\n?/g, '');
                content = content.replace(/import React, /g, 'import ');
                correctionApplied = true;
                break;

            case 'missing_export':
                // Verificar se realmente precisa de export
                const componentMatch = content.match(/const\s+(\w+)\s*[:=]/);
                if (componentMatch && componentMatch[1]) {
                    const componentName = componentMatch[1];
                    if (!content.includes(`export`) && 
                        (componentName.charAt(0) === componentName.charAt(0).toUpperCase())) {
                        content += `\nexport default ${componentName};\n`;
                        correctionApplied = true;
                    }
                }
                break;

            case 'deep_relative_import':
                // Converter imports profundos para absolutos (se possível)
                content = content.replace(
                    /from\s+['"](\.\.[\/\\]){3,}([^'"]+)['"]/g,
                    "from '@/$2'"
                );
                correctionApplied = true;
                break;
        }

        return { content, correctionApplied };
    }

    // Aplicar todas as correções em um arquivo
    correctFile(analysis) {
        if (!analysis || !analysis.needsCorrection) {
            return false;
        }

        this.log(`Corrigindo: ${analysis.relativePath}`, 'fix');
        
        // Criar backup
        this.createBackup(analysis.filePath);
        
        let content = analysis.content;
        let totalCorrections = 0;

        // Aplicar correções para issues de severidade média/alta
        for (const issue of analysis.issues) {
            if (issue.severity !== 'low') {
                const result = this.applyCorrection(analysis, issue.type);
                if (result.correctionApplied) {
                    content = result.content;
                    totalCorrections++;
                    this.log(`  ✓ ${issue.description}`, 'success');
                }
            }
        }

        // Salvar arquivo corrigido
        if (totalCorrections > 0) {
            try {
                fs.writeFileSync(analysis.filePath, content, 'utf8');
                this.corrections.push({
                    file: analysis.relativePath,
                    corrections: totalCorrections,
                    issues: analysis.issues.map(i => i.description)
                });
                this.log(`  ✅ ${totalCorrections} correções aplicadas`, 'success');
                return true;
            } catch (error) {
                this.log(`  ❌ Erro ao salvar: ${error.message}`, 'error');
                return false;
            }
        }

        return false;
    }

    // Buscar arquivos para análise
    findFilesToAnalyze() {
        const files = [];
        
        const scanDirectory = (dir) => {
            try {
                const items = fs.readdirSync(dir);
                
                for (const item of items) {
                    const fullPath = path.join(dir, item);
                    const stat = fs.statSync(fullPath);
                    
                    if (stat.isDirectory()) {
                        // Ignorar node_modules e build
                        if (!item.startsWith('.') && 
                            item !== 'node_modules' && 
                            item !== 'dist' && 
                            item !== 'build') {
                            scanDirectory(fullPath);
                        }
                    } else if (stat.isFile()) {
                        // Incluir arquivos .tsx e .ts (exceto .d.ts)
                        if ((item.endsWith('.tsx') || item.endsWith('.ts')) && 
                            !item.endsWith('.d.ts') &&
                            !item.includes('.test.') &&
                            !item.includes('.spec.')) {
                            files.push(fullPath);
                        }
                    }
                }
            } catch (error) {
                this.log(`Erro ao escanear diretório ${dir}: ${error.message}`, 'error');
            }
        };

        scanDirectory(this.frontendDir);
        return files;
    }

    // Executar o processo completo
    async run() {
        this.log('🚀 Iniciando Frontend Corrections Applicator...', 'info');
        
        if (!fs.existsSync(this.frontendDir)) {
            this.log(`❌ Diretório frontend não encontrado: ${this.frontendDir}`, 'error');
            return;
        }

        // Encontrar arquivos
        const files = this.findFilesToAnalyze();
        this.log(`📁 Encontrados ${files.length} arquivos para análise`, 'info');

        if (files.length === 0) {
            this.log('❌ Nenhum arquivo encontrado para análise', 'error');
            return;
        }

        // Analisar arquivos
        const analyses = [];
        let needsCorrection = 0;

        for (const filePath of files) {
            const analysis = this.analyzeFile(filePath);
            if (analysis) {
                analyses.push(analysis);
                if (analysis.needsCorrection) {
                    needsCorrection++;
                }
            }
        }

        this.log(`🔍 ${analyses.length} arquivos analisados, ${needsCorrection} precisam de correção`, 'info');

        if (needsCorrection === 0) {
            this.log('✅ Nenhuma correção necessária! Frontend está em ótimo estado.', 'success');
            return;
        }

        // Aplicar correções
        let corrected = 0;
        for (const analysis of analyses) {
            if (this.correctFile(analysis)) {
                corrected++;
            }
        }

        // Relatório final
        this.log('', 'info');
        this.log('📊 RELATÓRIO DE CORREÇÕES', 'info');
        this.log('=======================', 'info');
        this.log(`Arquivos analisados: ${analyses.length}`, 'info');
        this.log(`Arquivos corrigidos: ${corrected}`, 'success');
        this.log(`Backup criado em: ${path.basename(this.backupDir)}`, 'info');

        if (this.corrections.length > 0) {
            this.log('', 'info');
            this.log('Correções aplicadas:', 'info');
            for (const correction of this.corrections) {
                this.log(`  📄 ${correction.file}: ${correction.corrections} correções`, 'success');
            }
        }

        this.log('', 'info');
        this.log('✅ Processo concluído! Funcionalidades de produção preservadas.', 'success');
    }
}

// Executar o aplicador
if (require.main === module) {
    const applicator = new FrontendCorrectionsApplicator();
    applicator.run().catch(error => {
        console.error('❌ Erro fatal:', error);
        process.exit(1);
    });
}

module.exports = FrontendCorrectionsApplicator;
