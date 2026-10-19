import { useState, useEffect } from 'react';
import { StyleSheet, Text, View, FlatList, Image, ActivityIndicator, TouchableOpacity, Modal, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const BACKEND_URL = `${API_BASE_URL}/encyclopedia`;

export default function EncyclopediaScreen({ navigation }) {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedPlant, setExpandedPlant] = useState(null);

  useEffect(() => {
    fetchEncyclopedia();
  }, []);

  const fetchEncyclopedia = async () => {
    try {
      const response = await axios.get(BACKEND_URL);
      setPlants(response.data.data);
    } catch (error) {
      console.error(error);
      Alert.alert(
        "Lỗi kết nối", 
        "Điện thoại không thể kết nối tới máy chủ AI (Port 8000). Vui lòng kiểm tra lại IP hoặc Tắt Tường Lửa (Windows Firewall) trên máy tính."
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (plantId) => {
    if (expandedPlant === plantId) {
      setExpandedPlant(null);
    } else {
      setExpandedPlant(plantId);
    }
  };

  const renderDisease = (disease, index) => {
    // Bây giờ bệnh nào cũng có thể click vào để xem chi tiết (Auto-Fill AI)
    return (
      <TouchableOpacity 
        key={index} 
        style={[styles.diseaseItem, styles.diseaseItemClickable]}
        onPress={() => navigation.navigate('DiseaseDetail', { 
          diseaseId: disease.id, 
          diseaseName: disease.name 
        })}
      >
        <View style={styles.diseaseInfoRow}>
          <Ionicons 
            name={"medical"} 
            size={16} 
            color={"#10B981"} 
            style={{marginRight: 8}}
          />
          <Text style={[styles.diseaseNameText, styles.diseaseNameActive]}>
            {disease.name}
          </Text>
        </View>
        <View style={styles.viewDetailsBadge}>
          <Text style={styles.viewDetailsText}>Xem chi tiết</Text>
          <Ionicons name="chevron-forward" size={12} color="#10B981" />
        </View>
      </TouchableOpacity>
    );
  };

  const renderPlant = ({ item }) => {
    const isExpanded = expandedPlant === item.id;
    
    return (
      <View style={styles.plantCard}>
        <TouchableOpacity 
          style={styles.plantHeader} 
          activeOpacity={0.7} 
          onPress={() => toggleExpand(item.id)}
        >
          <View style={styles.plantHeaderLeft}>
            <View style={styles.iconContainer}>
              <Ionicons name="leaf" size={24} color="#10B981" />
            </View>
            <View>
              <Text style={styles.plantName}>{item.plant_name}</Text>
              <Text style={styles.diseaseCount}>{item.diseases.length} loại bệnh</Text>
            </View>
          </View>
          <Ionicons name={isExpanded ? "chevron-up" : "chevron-down"} size={24} color="#6B7280" />
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.diseaseListContainer}>
            {item.diseases.map((disease, index) => renderDisease(disease, index))}
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#10B981" />
        </View>
      ) : (
        <FlatList
          data={plants}
          keyExtractor={(item) => item.id}
          renderItem={renderPlant}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  plantCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
    overflow: 'hidden',
  },
  plantHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  plantHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#ECFDF5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  plantName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  diseaseCount: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '500',
  },
  diseaseListContainer: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    backgroundColor: '#FAFAFA',
  },
  diseaseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  diseaseItemClickable: {
    backgroundColor: '#ffffff',
  },
  diseaseInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  diseaseNameText: {
    fontSize: 15,
    color: '#4B5563',
    flex: 1,
  },
  diseaseNameActive: {
    color: '#111827',
    fontWeight: '600',
  },
  viewDetailsBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 12,
  },
  viewDetailsText: {
    fontSize: 11,
    color: '#10B981',
    fontWeight: '600',
    marginRight: 2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    height: '85%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },
  closeButton: {
    padding: 4,
    backgroundColor: '#F3F4F6',
    borderRadius: 20,
  },
  modalImage: {
    width: '100%',
    height: 220,
    backgroundColor: '#E5E7EB',
  },
  modalBody: {
    padding: 20,
    paddingBottom: 40,
  },
  modalDiseaseName: {
    fontSize: 24,
    fontWeight: '800',
    color: '#065F46',
    marginBottom: 24,
  },
  sectionContainer: {
    marginBottom: 24,
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 16,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#374151',
    marginLeft: 8,
  },
  sectionText: {
    fontSize: 15,
    color: '#4B5563',
    lineHeight: 24,
  }
});
