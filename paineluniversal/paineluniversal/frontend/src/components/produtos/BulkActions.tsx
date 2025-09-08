import React from 'react';
import { Trash2, Check, X, Eye, EyeOff } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/alert-dialog';

interface BulkActionsProps {
  selectedCount: number;
  onBulkDelete: () => void;
  onBulkEnable: () => void;
  onBulkDisable: () => void;
}

const BulkActions: React.FC<BulkActionsProps> = ({
  selectedCount,
  onBulkDelete,
  onBulkEnable,
  onBulkDisable,
}) => {
  return (
    <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {selectedCount} produto{selectedCount !== 1 ? 's' : ''} selecionado{selectedCount !== 1 ? 's' : ''}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Selecione uma ação para aplicar em lote:
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Habilitar em lote */}
          <Button
            variant="outline"
            size="sm"
            onClick={onBulkEnable}
            className="gap-2 text-green-600 border-green-600 hover:bg-green-50 dark:hover:bg-green-950/20"
          >
            <Check className="h-4 w-4" />
            Habilitar
          </Button>
          
          {/* Desabilitar em lote */}
          <Button
            variant="outline"
            size="sm"
            onClick={onBulkDisable}
            className="gap-2 text-orange-600 border-orange-600 hover:bg-orange-50 dark:hover:bg-orange-950/20"
          >
            <EyeOff className="h-4 w-4" />
            Desabilitar
          </Button>
          
          {/* Excluir em lote */}
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
              >
                <Trash2 className="h-4 w-4" />
                Excluir
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Confirmar exclusão em lote</AlertDialogTitle>
                <AlertDialogDescription>
                  Tem certeza que deseja excluir {selectedCount} produto{selectedCount !== 1 ? 's' : ''}? 
                  Esta ação não pode ser desfeita.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction 
                  onClick={onBulkDelete}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Excluir {selectedCount} produto{selectedCount !== 1 ? 's' : ''}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>
    </div>
  );
};

export default BulkActions;