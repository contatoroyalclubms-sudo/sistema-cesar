import React, { useState, useEffect } from 'react';
import { Download, FileText, Eye, Settings, Filter } from 'lucide-react';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Checkbox } from '../ui/checkbox';
import { inventoryService } from '../../services/inventory';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ExportFormat {
  format: string;
  name: string;
  description: string;
  icon: string;
  extensions: string[];
}

interface ExportType {
  type: string;
  name: string;
  description: string;
}

interface ExportConfig {
  tipo_exportacao: string;
  formato: string;
  campos_personalizados?: string[];
  filtros?: {
    categorias?: string[];
    fornecedores?: string[];
    estoque_status?: string;
    data_inicio?: string;
    data_fim?: string;
    preco_min?: number;
    preco_max?: number;
    apenas_ativos?: boolean;
    apenas_com_estoque?: boolean;
  };
  incluir_cabecalho?: boolean;
  separador_csv?: string;
  encoding?: string;
}

interface PreviewData {
  total_registros: number;
  campos_incluidos: string[];
  primeiras_linhas: any[];
  tamanho_estimado: string;
}

const CAMPO_LABELS: Record<string, string> = {
  codigo_interno: 'Código/SKU',
  nome: 'Nome do Produto',
  categoria: 'Categoria',
  preco: 'Preço de Venda',
  estoque_atual: 'Estoque Atual',
  estoque_minimo: 'Estoque Mínimo',
  marca: 'Marca',
  fornecedor: 'Fornecedor',
  status: 'Status',
  preco_custo: 'Preço de Custo',
  margem_lucro: 'Margem de Lucro',
  codigo_barras: 'Código de Barras',
  ncm: 'NCM',
  icms: 'ICMS (%)',
  ipi: 'IPI (%)'
};

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formats, setFormats] = useState<ExportFormat[]>([]);
  const [types, setTypes] = useState<ExportType[]>([]);
  const [preview, setPreview] = useState<PreviewData | null>(null);
  
  // Configuração de exportação
  const [config, setConfig] = useState<ExportConfig>({
    tipo_exportacao: 'estoque_completo',
    formato: 'xlsx',
    incluir_cabecalho: true,
    separador_csv: ',',
    encoding: 'UTF-8',
    filtros: {
      apenas_ativos: true,
      apenas_com_estoque: false
    }
  });

  // Campos personalizados
  const [showCustomFields, setShowCustomFields] = useState(false);
  const [selectedFields, setSelectedFields] = useState<string[]>([]);

  useEffect(() => {
    if (isOpen) {
      loadExportOptions();
    }
  }, [isOpen]);

  const loadExportOptions = async () => {
    try {
      setLoading(true);
      const response = await inventoryService.getExportFormats();
      setFormats(response.formats);
      setTypes(response.types);
    } catch (error: any) {
      setError(error.message || 'Erro ao carregar opções de exportação');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [key]: value
    }));
    setPreview(null); // Reset preview when config changes
  };

  const handleFilterChange = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      filtros: {
        ...prev.filtros,
        [key]: value
      }
    }));
    setPreview(null);
  };

  const handleFieldToggle = (field: string, checked: boolean) => {
    setSelectedFields(prev => {
      if (checked) {
        return [...prev, field];
      } else {
        return prev.filter(f => f !== field);
      }
    });
  };

  const handlePreview = async () => {
    try {
      setLoading(true);
      setError(null);

      const exportConfig = {
        ...config,
        campos_personalizados: showCustomFields ? selectedFields : undefined
      };

      const previewData = await inventoryService.previewExport(exportConfig);
      setPreview(previewData);
    } catch (error: any) {
      setError(error.message || 'Erro ao gerar preview');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);

      const exportConfig = {
        ...config,
        campos_personalizados: showCustomFields ? selectedFields : undefined
      };

      await inventoryService.exportData(exportConfig);
      onClose();
    } catch (error: any) {
      setError(error.message || 'Erro durante exportação');
    } finally {
      setLoading(false);
    }
  };

  const selectedFormat = formats.find(f => f.format === config.formato);
  const selectedType = types.find(t => t.type === config.tipo_exportacao);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="w-5 h-5" />
            Exportar Estoque
          </DialogTitle>
          <DialogDescription>
            Configure e exporte seus dados de estoque em diferentes formatos
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="config" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="config">Configuração</TabsTrigger>
              <TabsTrigger value="filters">Filtros</TabsTrigger>
              <TabsTrigger value="preview">Preview</TabsTrigger>
            </TabsList>

            {/* Configuração */}
            <TabsContent value="config" className="space-y-6">
              {/* Tipo de Exportação */}
              <div className="space-y-4">
                <Label className="text-base font-semibold">Tipo de Exportação</Label>
                <div className="grid grid-cols-2 gap-4">
                  {types.map((type) => (
                    <Card 
                      key={type.type}
                      className={`cursor-pointer transition-colors ${
                        config.tipo_exportacao === type.type 
                          ? 'ring-2 ring-blue-500 bg-blue-50' 
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => handleConfigChange('tipo_exportacao', type.type)}
                    >
                      <CardContent className="p-4">
                        <h3 className="font-medium">{type.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Formato */}
              <div className="space-y-4">
                <Label className="text-base font-semibold">Formato de Arquivo</Label>
                <div className="grid grid-cols-2 gap-4">
                  {formats.map((format) => (
                    <Card 
                      key={format.format}
                      className={`cursor-pointer transition-colors ${
                        config.formato === format.format 
                          ? 'ring-2 ring-blue-500 bg-blue-50' 
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => handleConfigChange('formato', format.format)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{format.icon}</span>
                          <div>
                            <h3 className="font-medium">{format.name}</h3>
                            <p className="text-sm text-gray-600">{format.description}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Campos Personalizados */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-semibold">Campos Personalizados</Label>
                  <Switch
                    checked={showCustomFields}
                    onCheckedChange={setShowCustomFields}
                  />
                </div>

                {showCustomFields && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Selecionar Campos</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        {Object.entries(CAMPO_LABELS).map(([field, label]) => (
                          <div key={field} className="flex items-center space-x-2">
                            <Checkbox
                              id={field}
                              checked={selectedFields.includes(field)}
                              onCheckedChange={(checked) => 
                                handleFieldToggle(field, checked as boolean)
                              }
                            />
                            <Label htmlFor={field} className="text-sm">
                              {label}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Opções Avançadas */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Opções Avançadas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Incluir cabeçalho</Label>
                    <Switch
                      checked={config.incluir_cabecalho}
                      onCheckedChange={(checked) => 
                        handleConfigChange('incluir_cabecalho', checked)
                      }
                    />
                  </div>

                  {config.formato === 'csv' && (
                    <>
                      <div className="space-y-2">
                        <Label>Separador CSV</Label>
                        <Select
                          value={config.separador_csv}
                          onValueChange={(value) => 
                            handleConfigChange('separador_csv', value)
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value=",">,  (vírgula)</SelectItem>
                            <SelectItem value=";">; (ponto e vírgula)</SelectItem>
                            <SelectItem value="|">| (pipe)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Codificação</Label>
                        <Select
                          value={config.encoding}
                          onValueChange={(value) => 
                            handleConfigChange('encoding', value)
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="UTF-8">UTF-8</SelectItem>
                            <SelectItem value="ISO-8859-1">ISO-8859-1</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Filtros */}
            <TabsContent value="filters" className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Filtros Básicos</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Status do Estoque</Label>
                      <Select
                        value={config.filtros?.estoque_status || ''}
                        onValueChange={(value) => 
                          handleFilterChange('estoque_status', value || undefined)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Todos" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Todos</SelectItem>
                          <SelectItem value="normal">Normal</SelectItem>
                          <SelectItem value="baixo">Baixo</SelectItem>
                          <SelectItem value="zerado">Zerado</SelectItem>
                          <SelectItem value="excesso">Excesso</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>Apenas produtos ativos</Label>
                      <Switch
                        checked={config.filtros?.apenas_ativos}
                        onCheckedChange={(checked) => 
                          handleFilterChange('apenas_ativos', checked)
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>Apenas com estoque</Label>
                      <Switch
                        checked={config.filtros?.apenas_com_estoque}
                        onCheckedChange={(checked) => 
                          handleFilterChange('apenas_com_estoque', checked)
                        }
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Faixa de Preços</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Preço mínimo</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={config.filtros?.preco_min || ''}
                        onChange={(e) => 
                          handleFilterChange('preco_min', 
                            e.target.value ? parseFloat(e.target.value) : undefined
                          )
                        }
                        placeholder="0.00"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Preço máximo</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={config.filtros?.preco_max || ''}
                        onChange={(e) => 
                          handleFilterChange('preco_max', 
                            e.target.value ? parseFloat(e.target.value) : undefined
                          )
                        }
                        placeholder="0.00"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Preview */}
            <TabsContent value="preview" className="space-y-6">
              {!preview ? (
                <div className="text-center py-8">
                  <Button onClick={handlePreview} disabled={loading}>
                    <Eye className="w-4 h-4 mr-2" />
                    Gerar Preview
                  </Button>
                  <p className="text-sm text-gray-600 mt-2">
                    Visualize os dados que serão exportados
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Estatísticas */}
                  <div className="grid grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {preview.total_registros}
                        </div>
                        <div className="text-sm text-gray-600">Registros</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {preview.campos_incluidos.length}
                        </div>
                        <div className="text-sm text-gray-600">Campos</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4 text-center">
                        <div className="text-lg font-bold text-purple-600">
                          {selectedFormat?.name}
                        </div>
                        <div className="text-sm text-gray-600">Formato</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4 text-center">
                        <div className="text-lg font-bold text-orange-600">
                          {preview.tamanho_estimado}
                        </div>
                        <div className="text-sm text-gray-600">Tamanho</div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Campos incluídos */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Campos Incluídos</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {preview.campos_incluidos.map((campo) => (
                          <Badge key={campo} variant="secondary">
                            {CAMPO_LABELS[campo] || campo}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Preview dos dados */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Preview dos Dados (primeiras 5 linhas)</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              {preview.campos_incluidos.map((campo) => (
                                <th key={campo} className="text-left p-2 font-medium">
                                  {CAMPO_LABELS[campo] || campo}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {preview.primeiras_linhas.map((linha, index) => (
                              <tr key={index} className="border-b">
                                {preview.campos_incluidos.map((campo) => (
                                  <td key={campo} className="p-2">
                                    {linha[campo] || '-'}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>
          </Tabs>

          {/* Ações */}
          <div className="flex justify-between pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handlePreview}
                disabled={loading}
              >
                <Eye className="w-4 h-4 mr-2" />
                {preview ? 'Atualizar Preview' : 'Visualizar'}
              </Button>
              <Button 
                onClick={handleExport}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700"
              >
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};