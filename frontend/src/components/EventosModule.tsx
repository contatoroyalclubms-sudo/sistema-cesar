import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, MapPin, Users } from 'lucide-react';

interface Evento {
  id: number;
  nome: string;
  descricao: string;
  data: string;
  local: string;
  capacidade: number;
  status: 'ativo' | 'inativo';
}

export default function EventosModule() {
  const [eventos] = useState<Evento[]>([
    {
      id: 1,
      nome: "Evento de Demonstração",
      descricao: "Um evento para demonstrar o sistema",
      data: "2024-12-01",
      local: "Centro de Convenções",
      capacidade: 500,
      status: 'ativo'
    }
  ]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Eventos</h1>
        <Button>Novo Evento</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {eventos.map((evento) => (
          <Card key={evento.id}>
            <CardHeader>
              <CardTitle>{evento.nome}</CardTitle>
              <Badge variant={evento.status === 'ativo' ? 'default' : 'secondary'}>
                {evento.status}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <Calendar className="w-4 h-4 mr-2" />
                {new Date(evento.data).toLocaleDateString('pt-BR')}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <MapPin className="w-4 h-4 mr-2" />
                {evento.local}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Users className="w-4 h-4 mr-2" />
                {evento.capacidade} pessoas
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
