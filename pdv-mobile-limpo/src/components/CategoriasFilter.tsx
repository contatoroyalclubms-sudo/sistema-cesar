import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

interface CategoriasModalProps {
  visible: boolean;
  onSelectCategory: (categoria: string) => void;
  onClose: () => void;
}

const categorias = [
  { nome: 'Todas', emoji: '🏷️', count: 8 },
  { nome: 'Bebidas', emoji: '🍺', count: 3 },
  { nome: 'Lanches', emoji: '🍔', count: 1 },
  { nome: 'Acompanhamentos', emoji: '🍟', count: 1 },
  { nome: 'Pizzas', emoji: '🍕', count: 1 },
  { nome: 'Saladas', emoji: '🥗', count: 1 },
  { nome: 'Cafés', emoji: '☕', count: 1 },
];

export default function CategoriasFilter({ onSelectCategory }: { onSelectCategory: (categoria: string) => void }) {
  return (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false} 
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
    >
      {categorias.map((categoria, index) => (
        <TouchableOpacity 
          key={index} 
          style={styles.categoryCard}
          onPress={() => onSelectCategory(categoria.nome === 'Todas' ? '' : categoria.nome)}
        >
          <Text style={styles.categoryEmoji}>{categoria.emoji}</Text>
          <Text style={styles.categoryName}>{categoria.nome}</Text>
          <View style={styles.countBadge}>
            <Text style={styles.countText}>{categoria.count}</Text>
          </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    maxHeight: 120,
  },
  contentContainer: {
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  categoryCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 15,
    marginRight: 12,
    alignItems: 'center',
    minWidth: 80,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    position: 'relative',
  },
  categoryEmoji: {
    fontSize: 24,
    marginBottom: 5,
  },
  categoryName: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#374151',
    textAlign: 'center',
  },
  countBadge: {
    position: 'absolute',
    top: -5,
    right: -5,
    backgroundColor: '#3b82f6',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  countText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
});
