import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useCarrinho } from '../context/CarrinhoContext';
import { useMesa } from '../context/MesaContext';
import NFCModal from '../components/NFCModal';

export default function DashboardScreen() {
  const { getTotalItens, getTotalValor, itens } = useCarrinho();
  const { mesaAtual, comandaAtual } = useMesa();
  const [showNFCModal, setShowNFCModal] = useState(false);

  const handleNFCAction = () => {
    setShowNFCModal(true);
  };

  const handleScannerAction = () => {
    Alert.alert(
      'Scanner QR Code',
      'Funcionalidade de scanner será implementada em breve',
      [{ text: 'OK' }]
    );
  };

  const handleVerCarrinho = () => {
    if (getTotalItens() === 0) {
      Alert.alert(
        'Carrinho Vazio',
        'Adicione produtos na aba "Produtos" para começar um pedido'
      );
    } else {
      Alert.alert(
        'Carrinho Atual',
        `${getTotalItens()} itens\nTotal: R$ ${getTotalValor().toFixed(2)}`,
        [{ text: 'OK' }]
      );
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📊 DASHBOARD PDV</Text>
        <Text style={styles.subtitle}>Bem-vindo, Garçom!</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{getTotalItens()}</Text>
          <Text style={styles.statLabel}>Itens no Carrinho</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>R$ {getTotalValor().toFixed(2)}</Text>
          <Text style={styles.statLabel}>Valor Atual</Text>
        </View>
      </View>

      {mesaAtual && (
        <View style={styles.mesaContainer}>
          <Text style={styles.sectionTitle}>🏷️ Mesa/Comanda Ativa</Text>
          <View style={styles.mesaCard}>
            <View style={styles.mesaInfo}>
              <Text style={styles.mesaNumero}>Mesa {mesaAtual.numero}</Text>
              <Text style={styles.mesaStatus}>Status: {mesaAtual.status}</Text>
              {comandaAtual && (
                <>
                  <Text style={styles.comandaInfo}>Comanda: {comandaAtual.numeroComanda}</Text>
                  <Text style={styles.comandaInfo}>Cliente: {comandaAtual.clienteNome || 'Não informado'}</Text>
                </>
              )}
            </View>
            <View style={styles.mesaBadge}>
              <Text style={styles.mesaBadgeText}>NFC</Text>
            </View>
          </View>
        </View>
      )}

      {itens.length > 0 && (
        <View style={styles.currentOrderContainer}>
          <Text style={styles.sectionTitle}>🛒 Pedido Atual</Text>
          <View style={styles.orderSummary}>
            {itens.slice(0, 3).map((item) => (
              <View key={item.id} style={styles.orderItem}>
                <Text style={styles.orderItemName}>{item.nome}</Text>
                <Text style={styles.orderItemQty}>x{item.quantidade}</Text>
              </View>
            ))}
            {itens.length > 3 && (
              <Text style={styles.moreItems}>+{itens.length - 3} mais itens...</Text>
            )}
          </View>
        </View>
      )}

      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>🚀 Ações Rápidas</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={handleNFCAction}>
          <Text style={styles.actionIcon}>📱</Text>
          <Text style={styles.actionText}>Ler NFC Comanda</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={handleScannerAction}>
          <Text style={styles.actionIcon}>📷</Text>
          <Text style={styles.actionText}>Scanner QR Code</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={handleVerCarrinho}>
          <Text style={styles.actionIcon}>🛒</Text>
          <Text style={styles.actionText}>
            {getTotalItens() > 0 
              ? `Ver Carrinho (${getTotalItens()})`
              : 'Ver Carrinho'
            }
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.infoContainer}>
        <Text style={styles.sectionTitle}>ℹ️ Informações</Text>
        <Text style={styles.infoText}>Sistema: Online ✅</Text>
        <Text style={styles.infoText}>Última Sync: Agora</Text>
        <Text style={styles.infoText}>Modo: Desenvolvimento</Text>
        <Text style={styles.infoText}>Versão: PDV Mobile v2.0</Text>
      </View>

      <NFCModal 
        visible={showNFCModal}
        onClose={() => setShowNFCModal(false)}
        onSuccess={(comanda) => {
          console.log('Comanda lida:', comanda);
          Alert.alert(
            'Comanda Ativa',
            `Mesa ${mesaAtual?.numero}\nComanda: ${comanda.numeroComanda}`,
            [{ text: 'OK' }]
          );
        }}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#1f2937',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 5,
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  statLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 5,
  },
  currentOrderContainer: {
    padding: 20,
    paddingTop: 0,
  },
  orderSummary: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  orderItemName: {
    fontSize: 14,
    color: '#374151',
    flex: 1,
  },
  orderItemQty: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: 'bold',
  },
  moreItems: {
    fontSize: 12,
    color: '#9ca3af',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 8,
  },
  actionsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: '#ffffff',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionIcon: {
    fontSize: 24,
    marginRight: 15,
  },
  actionText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '600',
  },
  infoContainer: {
    padding: 20,
    paddingBottom: 40,
  },
  infoText: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 5,
  },
  mesaContainer: {
    padding: 20,
    paddingTop: 0,
  },
  mesaCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  mesaInfo: {
    flex: 1,
  },
  mesaNumero: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  mesaStatus: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 2,
  },
  comandaInfo: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 2,
  },
  mesaBadge: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  mesaBadgeText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
});
