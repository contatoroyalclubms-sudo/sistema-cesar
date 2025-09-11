import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { toast } from '../../hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '../ui/alert';
import { 
  Upload,
  Download,
  FileText,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileSpreadsheet
} from 'lucide-react';
import { produtoService } from '../../services/api';
import { ImportResult } from '../../types/produto';

interface ProductImportModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ProductImportModal: React.FC<ProductImportModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileSelect = (selectedFile: File) => {
    // Validar tipo de arquivo
    const validTypes = ['.csv', '.xlsx', '.xls'];
    const fileExtension = selectedFile.name.toLowerCase().substr(selectedFile.name.lastIndexOf('.'));
    
    if (!validTypes.includes(fileExtension)) {
      toast({
        title: "Formato inválido",
        description: "Selecione um arquivo CSV ou Excel (.xlsx, .xls)",
        variant: "destructive",
      });
      return;
    }

    // Validar tamanho (máximo 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      toast({
        title: "Arquivo muito grande",
        description: "O arquivo deve ter no máximo 10MB",
        variant: "destructive",
      });
      return;
    }

    setFile(selectedFile);
    setResult(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleImport = async () => {
    if (!file) {
      toast({
        title: "Nenhum arquivo selecionado",
        description: "Selecione um arquivo para importar",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);
    try {
      const importResult = await produtoService.import(file);
      setResult(importResult);
      
      if (importResult.produtos_criados > 0) {
        toast({
          title: "Importação concluída",
          description: `${importResult.produtos_criados} produtos importados com sucesso!`,
        });
        onSuccess(); // Recarregar lista de produtos
      } else {
        toast({
          title: "Nenhum produto importado",
          description: "Verifique os erros abaixo e corrija o arquivo",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error('Erro na importação:', error);
      toast({
        title: "Erro na importação",
        description: error.response?.data?.detail || "Erro inesperado ao importar produtos",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const template = await produtoService.downloadTemplate();
      
      // Criar e baixar arquivo
      const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'template_importacao_produtos.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: "Template baixado",
        description: "Use este template como exemplo para importação",
      });
    } catch (error) {
      toast({
        title: "Erro ao baixar template",
        description: "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const handleClose = () => {
    setFile(null);
    setResult(null);
    setUploading(false);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Importar Produtos
          </DialogTitle>
          <DialogDescription>
            Importe produtos em lote usando arquivo CSV ou Excel. 
            Baixe o template para ver o formato correto.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Template Download */}
          <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileSpreadsheet className="h-8 w-8 text-blue-600" />
              <div>
                <h4 className="font-medium text-blue-900">Template de Importação</h4>
                <p className="text-sm text-blue-600">
                  Baixe o modelo com os campos corretos para importação
                </p>
              </div>
            </div>
            <Button variant="outline" onClick={handleDownloadTemplate}>
              <Download className="h-4 w-4 mr-2" />
              Baixar Template
            </Button>
          </div>

          {/* File Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragOver 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
          >
            {file ? (
              <div className="space-y-2">
                <FileText className="h-12 w-12 text-green-600 mx-auto" />
                <h3 className="text-lg font-medium text-green-900">{file.name}</h3>
                <p className="text-sm text-gray-600">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFile(null)}
                >
                  Remover arquivo
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Arraste o arquivo aqui
                  </h3>
                  <p className="text-gray-600">ou clique para selecionar</p>
                </div>
                <Input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileInput}
                  className="max-w-xs mx-auto"
                />
                <p className="text-xs text-gray-500">
                  Formatos suportados: CSV, Excel (.xlsx, .xls) - Máximo 10MB
                </p>
              </div>
            )}
          </div>

          {/* Campos Suportados */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Campos Suportados:</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm text-gray-600">
              <div>• nome (obrigatório)</div>
              <div>• preco (obrigatório)</div>
              <div>• categoria</div>
              <div>• codigo_interno</div>
              <div>• estoque_atual</div>
              <div>• descricao</div>
              <div>• tipo</div>
              <div>• habilitado</div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              O sistema detecta automaticamente variações nos nomes das colunas
            </p>
          </div>

          {/* Resultado da Importação */}
          {result && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {result.total_linhas}
                  </div>
                  <div className="text-sm text-blue-600">Total de linhas</div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {result.produtos_criados}
                  </div>
                  <div className="text-sm text-green-600">Produtos criados</div>
                </div>
                <div className="p-4 bg-red-50 rounded-lg text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {result.produtos_com_erro}
                  </div>
                  <div className="text-sm text-red-600">Com erro</div>
                </div>
              </div>

              {/* Sucessos */}
              {result.detalhes_criados.length > 0 && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertTitle>Produtos Criados com Sucesso</AlertTitle>
                  <AlertDescription>
                    <div className="max-h-32 overflow-y-auto space-y-1 mt-2">
                      {result.detalhes_criados.slice(0, 10).map((produto, index) => (
                        <div key={index} className="text-sm">
                          Linha {produto.linha}: {produto.nome}
                        </div>
                      ))}
                      {result.detalhes_criados.length > 10 && (
                        <div className="text-sm text-gray-500">
                          ... e mais {result.detalhes_criados.length - 10} produtos
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              {/* Erros */}
              {result.detalhes_erros.length > 0 && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertTitle>Erros Encontrados</AlertTitle>
                  <AlertDescription>
                    <div className="max-h-32 overflow-y-auto space-y-1 mt-2">
                      {result.detalhes_erros.slice(0, 10).map((erro, index) => (
                        <div key={index} className="text-sm">
                          Linha {erro.linha}: {erro.erro}
                        </div>
                      ))}
                      {result.detalhes_erros.length > 10 && (
                        <div className="text-sm">
                          ... e mais {result.detalhes_erros.length - 10} erros
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              {/* Campos Detectados */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Campos Detectados:</h4>
                <div className="flex flex-wrap gap-2">
                  {result.campos_detectados.map((campo, index) => (
                    <span 
                      key={index} 
                      className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded"
                    >
                      {campo}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            {result ? 'Fechar' : 'Cancelar'}
          </Button>
          {!result && (
            <Button 
              onClick={handleImport} 
              disabled={!file || uploading}
            >
              {uploading ? 'Importando...' : 'Importar Produtos'}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ProductImportModal;
