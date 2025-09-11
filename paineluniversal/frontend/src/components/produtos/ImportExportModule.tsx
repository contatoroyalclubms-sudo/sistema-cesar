import React, { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Separator } from '../ui/separator';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Upload,
  Download,
  FileText,
  CheckCircle,
  AlertCircle,
  X,
  FileSpreadsheet,
  Database,
  ArrowRight,
  MapPin,
  FileX,
  Loader2
} from 'lucide-react';
import { useToast } from '../../hooks/use-toast';

interface ImportField {
  campo: string;
  label: string;
  obrigatorio: boolean;
  tipo: 'texto' | 'numero' | 'boolean' | 'data';
  exemplo?: string;
}

interface ImportResult {
  total: number;
  sucessos: number;
  erros: number;
  warnings: number;
  detalhes: {
    linha: number;
    erro?: string;
    warning?: string;
    dados?: any;
  }[];
}

const ImportExportModule: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'import' | 'export'>('import');
  const [showPreview, setShowPreview] = useState(false);
  const [importData, setImportData] = useState<any[]>([]);
  const [fieldMapping, setFieldMapping] = useState<Record<string, string>>({});
  const [processing, setProcessing] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [exportType, setExportType] = useState<'produtos' | 'categorias' | 'agendamentos'>('produtos');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const camposProdutos: ImportField[] = [
    { campo: 'nome', label: 'Nome do Produto', obrigatorio: true, tipo: 'texto', exemplo: 'Cerveja Heineken 600ml' },
    { campo: 'codigo', label: 'Código', obrigatorio: true, tipo: 'texto', exemplo: 'CERV001' },
    { campo: 'categoria_id', label: 'ID da Categoria', obrigatorio: true, tipo: 'numero', exemplo: '1' },
    { campo: 'valor', label: 'Valor', obrigatorio: true, tipo: 'numero', exemplo: '8.50' },
    { campo: 'destaque', label: 'Destaque', obrigatorio: false, tipo: 'boolean', exemplo: 'true/false' },
    { campo: 'habilitado', label: 'Habilitado', obrigatorio: false, tipo: 'boolean', exemplo: 'true/false' },
    { campo: 'promocional', label: 'Promocional', obrigatorio: false, tipo: 'boolean', exemplo: 'true/false' },
    { campo: 'descricao', label: 'Descrição', obrigatorio: false, tipo: 'texto', exemplo: 'Cerveja premium importada' },
  ];

  const camposCategorias: ImportField[] = [
    { campo: 'nome', label: 'Nome da Categoria', obrigatorio: true, tipo: 'texto', exemplo: 'Bebidas' },
    { campo: 'codigo', label: 'Código', obrigatorio: true, tipo: 'texto', exemplo: 'BEB' },
    { campo: 'cor', label: 'Cor', obrigatorio: false, tipo: 'texto', exemplo: '#3B82F6' },
    { campo: 'ativo', label: 'Ativo', obrigatorio: false, tipo: 'boolean', exemplo: 'true/false' },
    { campo: 'descricao', label: 'Descrição', obrigatorio: false, tipo: 'texto', exemplo: 'Categoria para bebidas' },
  ];

  const getCurrentFields = (): ImportField[] => {
    switch (exportType) {
      case 'produtos':
        return camposProdutos;
      case 'categorias':
        return camposCategorias;
      default:
        return camposProdutos;
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!validTypes.includes(file.type)) {
      toast({
        title: "Arquivo inválido",
        description: "Selecione um arquivo CSV ou Excel (.xls, .xlsx)",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
    parseFile(file);
  };

  const parseFile = async (file: File) => {
    setProcessing(true);
    
    try {
      // TODO: Implementar parser real para CSV/Excel
      // Para desenvolvimento, simular dados
      const mockData = [
        {
          'Nome do Produto': 'Cerveja Brahma 350ml',
          'Código': 'CERV002',
          'Categoria': 'Bebidas',
          'Valor': '4.50',
          'Destaque': 'false'
        },
        {
          'Nome do Produto': 'Vodka Absolut',
          'Código': 'VOD001',
          'Categoria': 'Destilados',
          'Valor': '85.00',
          'Destaque': 'true'
        },
        {
          'Nome do Produto': 'Açaí 500ml',
          'Código': 'ACAI002',
          'Categoria': 'Sobremesas',
          'Valor': '12.00',
          'Destaque': 'false'
        }
      ];

      setImportData(mockData);
      setShowPreview(true);
      
      toast({
        title: "Arquivo carregado",
        description: `${mockData.length} registros encontrados`,
      });
    } catch (error) {
      toast({
        title: "Erro ao processar arquivo",
        description: "Verifique se o arquivo está no formato correto",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleImport = async () => {
    setProcessing(true);
    
    try {
      // TODO: Implementar chamada para API de importação
      // Simular processamento
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const result: ImportResult = {
        total: importData.length,
        sucessos: importData.length - 1,
        erros: 1,
        warnings: 0,
        detalhes: [
          {
            linha: 2,
            erro: 'Categoria "Destilados" não encontrada'
          }
        ]
      };
      
      setImportResult(result);
      
      toast({
        title: "Importação concluída",
        description: `${result.sucessos} de ${result.total} registros importados com sucesso`,
      });
    } catch (error) {
      toast({
        title: "Erro na importação",
        description: "Ocorreu um erro durante a importação",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleExport = async () => {
    setProcessing(true);
    
    try {
      // TODO: Implementar export real
      // Simular download
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const csvContent = generateMockCSV();
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `${exportType}_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: "Export realizado",
        description: `Arquivo de ${exportType} baixado com sucesso`,
      });
    } catch (error) {
      toast({
        title: "Erro no export",
        description: "Ocorreu um erro durante o export",
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const generateMockCSV = (): string => {
    const headers = getCurrentFields().map(field => field.label).join(',');
    const rows = [
      'Cerveja Heineken 600ml,CERV001,1,8.50,true,true,false,Cerveja premium importada',
      'Caipirinha de Cachaça,DRINK001,2,12.00,false,true,true,Drink tradicional brasileiro',
      'Açaí Especial,ACAI001,3,15.00,true,true,false,Açaí com frutas e granola'
    ];
    
    return [headers, ...rows].join('\n');
  };

  const resetImport = () => {
    setSelectedFile(null);
    setImportData([]);
    setFieldMapping({});
    setShowPreview(false);
    setImportResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Import/Export</h1>
          <p className="text-muted-foreground">
            Importe e exporte dados do sistema em massa
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveTab('import')}
          className={`px-4 py-2 font-medium rounded-t-lg ${
            activeTab === 'import'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Upload className="inline-block w-4 h-4 mr-2" />
          Importar Dados
        </button>
        <button
          onClick={() => setActiveTab('export')}
          className={`px-4 py-2 font-medium rounded-t-lg ${
            activeTab === 'export'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Download className="inline-block w-4 h-4 mr-2" />
          Exportar Dados
        </button>
      </div>

      {/* Import Tab */}
      {activeTab === 'import' && (
        <div className="space-y-6">
          {!selectedFile && !importResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Importar Produtos/Categorias
                </CardTitle>
                <CardDescription>
                  Faça upload de um arquivo CSV ou Excel para importar dados em massa
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <FileSpreadsheet className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium">Selecione um arquivo</p>
                    <p className="text-sm text-muted-foreground">
                      CSV, XLS ou XLSX até 10MB
                    </p>
                  </div>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-4"
                    disabled={processing}
                  >
                    {processing ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="mr-2 h-4 w-4" />
                    )}
                    Escolher Arquivo
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.xls,.xlsx"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>

                <Separator />

                <div>
                  <h3 className="font-medium mb-3">Formato do Arquivo</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-green-600 mb-2">Produtos</h4>
                      <div className="text-xs space-y-1">
                        {camposProdutos.map((campo) => (
                          <div key={campo.campo} className="flex items-center gap-2">
                            <Badge variant={campo.obrigatorio ? "destructive" : "secondary"} className="text-xs">
                              {campo.obrigatorio ? 'REQ' : 'OPT'}
                            </Badge>
                            <span>{campo.label}</span>
                            {campo.exemplo && (
                              <span className="text-muted-foreground">({campo.exemplo})</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-blue-600 mb-2">Categorias</h4>
                      <div className="text-xs space-y-1">
                        {camposCategorias.map((campo) => (
                          <div key={campo.campo} className="flex items-center gap-2">
                            <Badge variant={campo.obrigatorio ? "destructive" : "secondary"} className="text-xs">
                              {campo.obrigatorio ? 'REQ' : 'OPT'}
                            </Badge>
                            <span>{campo.label}</span>
                            {campo.exemplo && (
                              <span className="text-muted-foreground">({campo.exemplo})</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Preview dos dados */}
          {showPreview && !importResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Preview dos Dados
                  </div>
                  <Button variant="outline" size="sm" onClick={resetImport}>
                    <X className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                </CardTitle>
                <CardDescription>
                  Verifique os dados antes de importar • {importData.length} registros
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Mapeamento de campos */}
                <div>
                  <h3 className="font-medium mb-3">Mapeamento de Campos</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.keys(importData[0] || {}).map((coluna) => (
                      <div key={coluna} className="flex items-center gap-2">
                        <Label className="text-xs min-w-[120px]">{coluna}</Label>
                        <ArrowRight className="h-3 w-3 text-muted-foreground" />
                        <Select
                          value={fieldMapping[coluna] || ''}
                          onValueChange={(value) => setFieldMapping(prev => ({ ...prev, [coluna]: value }))}
                        >
                          <SelectTrigger className="text-xs">
                            <SelectValue placeholder="Selecionar campo" />
                          </SelectTrigger>
                          <SelectContent>
                            {getCurrentFields().map((campo) => (
                              <SelectItem key={campo.campo} value={campo.campo}>
                                {campo.label}
                                {campo.obrigatorio && <span className="text-red-500 ml-1">*</span>}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Preview da tabela */}
                <div>
                  <h3 className="font-medium mb-3">Preview dos Dados</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <div className="overflow-x-auto max-h-64">
                      <table className="w-full text-xs">
                        <thead className="bg-muted/50">
                          <tr>
                            {Object.keys(importData[0] || {}).map((coluna) => (
                              <th key={coluna} className="p-2 text-left font-medium">
                                {coluna}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {importData.slice(0, 5).map((row, index) => (
                            <tr key={index} className="border-t">
                              {Object.values(row).map((value, idx) => (
                                <td key={idx} className="p-2">
                                  {String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  {importData.length > 5 && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Mostrando 5 de {importData.length} registros
                    </p>
                  )}
                </div>

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={resetImport}>
                    Cancelar
                  </Button>
                  <Button onClick={handleImport} disabled={processing}>
                    {processing ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Database className="mr-2 h-4 w-4" />
                    )}
                    Importar Dados
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resultado da importação */}
          {importResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Resultado da Importação
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{importResult.total}</div>
                    <div className="text-xs text-muted-foreground">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{importResult.sucessos}</div>
                    <div className="text-xs text-muted-foreground">Sucessos</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{importResult.erros}</div>
                    <div className="text-xs text-muted-foreground">Erros</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{importResult.warnings}</div>
                    <div className="text-xs text-muted-foreground">Avisos</div>
                  </div>
                </div>

                <Progress 
                  value={(importResult.sucessos / importResult.total) * 100} 
                  className="w-full"
                />

                {importResult.detalhes.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Detalhes dos Problemas</h4>
                    <div className="space-y-2">
                      {importResult.detalhes.map((detalhe, index) => (
                        <Alert key={index} variant={detalhe.erro ? "destructive" : "default"}>
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            <span className="font-medium">Linha {detalhe.linha}:</span> {detalhe.erro || detalhe.warning}
                          </AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={resetImport}>
                    Nova Importação
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="h-5 w-5" />
                Exportar Dados
              </CardTitle>
              <CardDescription>
                Baixe os dados do sistema em formato CSV ou Excel
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Tipo de Dados</Label>
                <Select value={exportType} onValueChange={(value: any) => setExportType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="produtos">Produtos</SelectItem>
                    <SelectItem value="categorias">Categorias</SelectItem>
                    <SelectItem value="agendamentos">Agendamentos</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <h3 className="font-medium mb-2">Campos que serão exportados:</h3>
                <div className="grid grid-cols-2 gap-2">
                  {getCurrentFields().map((campo) => (
                    <div key={campo.campo} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="h-3 w-3 text-green-600" />
                      <span>{campo.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button onClick={handleExport} disabled={processing} className="w-full">
                {processing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Exportar {exportType.charAt(0).toUpperCase() + exportType.slice(1)}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ImportExportModule;
