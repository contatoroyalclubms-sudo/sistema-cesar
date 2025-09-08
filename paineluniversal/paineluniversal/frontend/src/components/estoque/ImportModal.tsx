import React, { useState, useCallback } from 'react';
import { Upload, Download, FileText, CheckCircle, AlertTriangle, X, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { inventoryService } from '../../services/inventory';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface UploadResult {
  operacao_id: number;
  headers: string[];
  sample_data: any[];
  total_rows: number;
  suggested_mapping: Record<string, string>;
}

interface ValidationResult {
  total_linhas: number;
  linhas_validas: number;
  linhas_com_erro: number;
  linhas_com_aviso: number;
  pode_importar: boolean;
  resumo_erros: Record<string, number>;
  detalhes: ValidationError[];
}

interface ValidationError {
  linha: number;
  campo?: string;
  tipo_validacao: string;
  status: 'VALIDO' | 'ERRO_CRITICO' | 'AVISO';
  mensagem: string;
  valor_original?: string;
  valor_sugerido?: string;
}

const STEP_NAMES = {
  1: 'Upload',
  2: 'Mapeamento',
  3: 'Validação',
  4: 'Importação'
};

const CAMPO_LABELS: Record<string, string> = {
  codigo: 'Código/SKU',
  nome: 'Nome do Produto',
  categoria: 'Categoria',
  preco_venda: 'Preço de Venda',
  codigo_barras: 'Código de Barras',
  marca: 'Marca',
  fornecedor: 'Fornecedor',
  preco_custo: 'Preço de Custo',
  estoque_atual: 'Estoque Atual',
  estoque_minimo: 'Estoque Mínimo'
};

export const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Estado do upload
  const [dragActive, setDragActive] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  
  // Estado do mapeamento
  const [fieldMapping, setFieldMapping] = useState<Record<string, string>>({});
  
  // Estado da validação
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  
  // Estado da importação
  const [importProgress, setImportProgress] = useState(0);
  const [importResult, setImportResult] = useState<any>(null);

  const resetState = () => {
    setCurrentStep(1);
    setUploadResult(null);
    setFieldMapping({});
    setValidationResult(null);
    setImportProgress(0);
    setImportResult(null);
    setError(null);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  // Etapa 1: Upload do arquivo
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const result = await inventoryService.uploadImportFile(formData);
      setUploadResult(result);
      setFieldMapping(result.suggested_mapping || {});
      setCurrentStep(2);
    } catch (error: any) {
      setError(error.message || 'Erro ao fazer upload do arquivo');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = async (format: string) => {
    try {
      setLoading(true);
      await inventoryService.downloadTemplate(format);
    } catch (error: any) {
      setError(error.message || 'Erro ao baixar template');
    } finally {
      setLoading(false);
    }
  };

  // Etapa 2: Mapeamento de campos
  const handleFieldMappingChange = (fileHeader: string, systemField: string) => {
    setFieldMapping(prev => ({
      ...prev,
      [fileHeader]: systemField
    }));
  };

  const autoMapFields = () => {
    if (uploadResult?.suggested_mapping) {
      setFieldMapping(uploadResult.suggested_mapping);
    }
  };

  const handleValidation = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!uploadResult) {
        throw new Error('Dados de upload não encontrados');
      }

      const result = await inventoryService.validateImportData(
        uploadResult.operacao_id,
        fieldMapping
      );
      
      setValidationResult(result);
      setCurrentStep(3);
    } catch (error: any) {
      setError(error.message || 'Erro durante validação');
    } finally {
      setLoading(false);
    }
  };

  // Etapa 3: Validação
  const handleImport = async () => {
    try {
      setLoading(true);
      setError(null);
      setCurrentStep(4);

      if (!uploadResult) {
        throw new Error('Dados de upload não encontrados');
      }

      // Simular progresso
      const interval = setInterval(() => {
        setImportProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const result = await inventoryService.executeImport(
        uploadResult.operacao_id,
        fieldMapping
      );
      
      clearInterval(interval);
      setImportProgress(100);
      setImportResult(result);
      
      setTimeout(() => {
        onSuccess();
        handleClose();
      }, 2000);
    } catch (error: any) {
      setError(error.message || 'Erro durante importação');
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-6">
      {[1, 2, 3, 4].map((step) => (
        <div key={step} className="flex items-center">
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
            ${step <= currentStep 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 text-gray-500'
            }
          `}>
            {step < currentStep ? <CheckCircle className="w-4 h-4" /> : step}
          </div>
          <span className={`ml-2 text-sm ${step <= currentStep ? 'text-blue-600' : 'text-gray-500'}`}>
            {STEP_NAMES[step as keyof typeof STEP_NAMES]}
          </span>
          {step < 4 && <div className={`w-12 h-0.5 mx-4 ${step < currentStep ? 'bg-blue-600' : 'bg-gray-200'}`} />}
        </div>
      ))}
    </div>
  );

  const renderUploadStep = () => (
    <div className="space-y-6">
      {/* Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Templates Disponíveis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <Button
              variant="outline"
              onClick={() => downloadTemplate('csv')}
              disabled={loading}
              className="flex flex-col items-center p-4 h-auto"
            >
              <FileText className="w-6 h-6 mb-2" />
              CSV
              <span className="text-xs text-gray-500">Modelo padrão CSV</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => downloadTemplate('xlsx')}
              disabled={loading}
              className="flex flex-col items-center p-4 h-auto"
            >
              <FileText className="w-6 h-6 mb-2" />
              Excel
              <span className="text-xs text-gray-500">Modelo Excel</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => downloadTemplate('json')}
              disabled={loading}
              className="flex flex-col items-center p-4 h-auto"
            >
              <FileText className="w-6 h-6 mb-2" />
              JSON
              <span className="text-xs text-gray-500">Estrutura JSON</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Upload Area */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
          ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          Arraste seus arquivos aqui ou clique para selecionar
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Suporte para: CSV, Excel, JSON • Máximo 10MB
        </p>
        <input
          id="file-input"
          type="file"
          className="hidden"
          accept=".csv,.xlsx,.xls,.json"
          onChange={handleFileSelect}
        />
      </div>

      {/* Instruções */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <strong>Dicas importantes:</strong>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Use os templates para garantir o formato correto</li>
            <li>Código/SKU deve ser único para cada produto</li>
            <li>Preços devem usar ponto como separador decimal</li>
            <li>Categorias devem ser exatamente como cadastradas</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  );

  const renderMappingStep = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Mapeamento de Campos</h3>
        <Button onClick={autoMapFields} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Auto-mapear
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Campos do arquivo */}
        <div>
          <h4 className="font-medium mb-4">Campos no Arquivo</h4>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {uploadResult?.headers.map((header, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded border">
                <div className="font-medium">{header}</div>
                <div className="text-sm text-gray-600">
                  Exemplo: {uploadResult.sample_data[0]?.[header] || 'N/A'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mapeamento */}
        <div>
          <h4 className="font-medium mb-4">Mapear para</h4>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {uploadResult?.headers.map((header, index) => (
              <div key={index} className="space-y-2">
                <Label htmlFor={`mapping-${index}`}>
                  {header}
                </Label>
                <Select
                  value={fieldMapping[header] || ''}
                  onValueChange={(value) => handleFieldMappingChange(header, value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecionar campo..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Não mapear</SelectItem>
                    {Object.entries(CAMPO_LABELS).map(([field, label]) => (
                      <SelectItem key={field} value={field}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setCurrentStep(1)}>
          Voltar
        </Button>
        <Button 
          onClick={handleValidation} 
          disabled={loading || Object.keys(fieldMapping).length === 0}
        >
          {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
          Validar Dados
        </Button>
      </div>
    </div>
  );

  const renderValidationStep = () => (
    <div className="space-y-6">
      {validationResult && (
        <>
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600">
                  {validationResult.total_linhas}
                </div>
                <div className="text-sm text-gray-600">Total de linhas</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600">
                  {validationResult.linhas_validas}
                </div>
                <div className="text-sm text-gray-600">Linhas válidas</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-red-600">
                  {validationResult.linhas_com_erro}
                </div>
                <div className="text-sm text-gray-600">Com erros</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-yellow-600">
                  {validationResult.linhas_com_aviso}
                </div>
                <div className="text-sm text-gray-600">Com avisos</div>
              </CardContent>
            </Card>
          </div>

          {!validationResult.pode_importar && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Existem erros críticos que impedem a importação. Corrija os problemas antes de continuar.
              </AlertDescription>
            </Alert>
          )}

          {Object.keys(validationResult.resumo_erros).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Resumo dos Erros</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(validationResult.resumo_erros).map(([tipo, quantidade]) => (
                    <div key={tipo} className="flex justify-between">
                      <span className="capitalize">{tipo.replace('_', ' ')}</span>
                      <Badge variant="destructive">{quantidade}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setCurrentStep(2)}>
              Voltar
            </Button>
            <Button 
              onClick={handleImport} 
              disabled={!validationResult.pode_importar || loading}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
              Importar Dados
            </Button>
          </div>
        </>
      )}
    </div>
  );

  const renderImportStep = () => (
    <div className="space-y-6 text-center">
      <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
        {importProgress === 100 ? (
          <CheckCircle className="w-8 h-8 text-green-600" />
        ) : (
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">
          {importProgress === 100 ? 'Importação Concluída!' : 'Importando Dados...'}
        </h3>
        <Progress value={importProgress} className="w-full max-w-md mx-auto" />
        <p className="text-sm text-gray-600 mt-2">{importProgress}% concluído</p>
      </div>

      {importResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="font-medium text-green-800">Produtos criados</div>
              <div className="text-green-600">{importResult.produtos_criados}</div>
            </div>
            <div>
              <div className="font-medium text-green-800">Tempo de processamento</div>
              <div className="text-green-600">{importResult.tempo_processamento}s</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Importar Produtos
          </DialogTitle>
          <DialogDescription>
            Importe produtos em lote usando arquivos CSV, Excel ou JSON
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {renderStepIndicator()}

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {currentStep === 1 && renderUploadStep()}
          {currentStep === 2 && renderMappingStep()}
          {currentStep === 3 && renderValidationStep()}
          {currentStep === 4 && renderImportStep()}
        </div>
      </DialogContent>
    </Dialog>
  );
};