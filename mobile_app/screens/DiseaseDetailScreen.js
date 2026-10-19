import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, ActivityIndicator, Image, TouchableOpacity, FlatList, TextInput, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const BACKEND_URL = `${API_BASE_URL}/encyclopedia`;

export default function DiseaseDetailScreen({ route, navigation }) {
  const { diseaseId, diseaseName } = route.params;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Form states
  const [symptoms, setSymptoms] = useState('');
  const [causes, setCauses] = useState('');
  const [harm, setHarm] = useState('');
  const [treatment, setTreatment] = useState('');
  const [recoveryTime, setRecoveryTime] = useState('');

  useEffect(() => {
    fetchDiseaseDetails();
  }, [diseaseId]);

  const fetchDiseaseDetails = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/${diseaseId}?name=${encodeURIComponent(diseaseName)}`);
      if (response.data.status === 'success') {
        const detail = response.data.data;
        setData(detail);
        setSymptoms(detail.symptoms || '');
        setCauses(detail.causes || '');
        setHarm(detail.harm || '');
        setTreatment(detail.treatment || '');
        setRecoveryTime(detail.recovery_time || '');
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Lỗi", "Không thể tải dữ liệu bệnh học.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        symptoms,
        causes,
        harm,
        treatment,
        recovery_time: recoveryTime
      };
      const response = await axios.put(`${BACKEND_URL}/${diseaseId}`, payload);
      if (response.data.status === 'success') {
        setData(response.data.data);
        setIsEditing(false);
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Lỗi", "Lưu thay đổi thất bại.");
    } finally {
      setSaving(false);
    }
  };

  const fetchFromAI = async () => {
    setSaving(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/${diseaseId}?name=${encodeURIComponent(diseaseName)}&force_ai=true`);
      if (response.data.status === 'success') {
        const detail = response.data.data;
        setData(detail);
        setSymptoms(detail.symptoms || '');
        setCauses(detail.causes || '');
        setHarm(detail.harm || '');
        setTreatment(detail.treatment || '');
        setRecoveryTime(detail.recovery_time || '');
        Alert.alert("Thành công", "Đã lấy thông tin mới nhất từ AI.");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Lỗi", "Lấy dữ liệu từ AI thất bại.");
    } finally {
      setSaving(false);
    }
  };

  // Header Right button for Edit/Fetch from AI
  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity 
          onPress={() => isEditing ? fetchFromAI() : setIsEditing(true)}
          style={styles.headerButton}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator size="small" color="#10B981" />
          ) : (
            <Text style={styles.headerButtonText}>{isEditing ? 'Lấy từ AI' : 'Chỉnh sửa'}</Text>
          )}
        </TouchableOpacity>
      ),
    });
  }, [navigation, isEditing, symptoms, causes, harm, treatment, recoveryTime, saving]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Đang tổng hợp thông tin từ AI...</Text>
      </View>
    );
  }

  if (!data) return null;

  const isHealthy = data.id?.toUpperCase().includes('KHOEMANH') || data.name?.toUpperCase().includes('KHOEMANH');

  const renderImageItem = ({ item }) => (
    <Image source={{ uri: item }} style={styles.carouselImage} />
  );

  const images = data.images && data.images.length > 0 ? data.images : ['https://via.placeholder.com/300x200.png?text=Chưa+có+ảnh+thực+tế'];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Image Carousel */}
      <View style={styles.carouselContainer}>
        <FlatList
          data={images}
          horizontal
          showsHorizontalScrollIndicator={false}
          keyExtractor={(item, index) => index.toString()}
          renderItem={renderImageItem}
          snapToInterval={300}
          decelerationRate="fast"
          contentContainerStyle={{ paddingHorizontal: 16 }}
        />
      </View>

      <View style={styles.contentBody}>
        <Text style={styles.title}>{data.name}</Text>
        <Text style={styles.subtitle}>Cây trồng: {data.plant}</Text>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="search" size={20} color="#F59E0B" />
            <Text style={styles.sectionTitle}>{isHealthy ? 'Dấu hiệu rau khỏe mạnh' : 'Triệu chứng'}</Text>
          </View>
          {isEditing ? (
            <TextInput
              style={styles.input}
              multiline
              value={symptoms}
              onChangeText={setSymptoms}
            />
          ) : (
            <Text style={styles.sectionText}>{symptoms}</Text>
          )}
        </View>

        {!isHealthy && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="bug" size={20} color="#EF4444" />
              <Text style={styles.sectionTitle}>Nguyên nhân</Text>
            </View>
          {isEditing ? (
            <TextInput
              style={styles.input}
              multiline
              value={causes}
              onChangeText={setCauses}
            />
          ) : (
            <Text style={styles.sectionText}>{causes}</Text>
          )}
          </View>
        )}

        {!isHealthy && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="warning" size={20} color="#F97316" />
              <Text style={styles.sectionTitle}>Tác hại</Text>
            </View>
          {isEditing ? (
            <TextInput
              style={styles.input}
              multiline
              value={harm}
              onChangeText={setHarm}
            />
          ) : (
            <Text style={styles.sectionText}>{harm}</Text>
          )}
          </View>
        )}

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="medkit" size={20} color="#10B981" />
            <Text style={styles.sectionTitle}>{isHealthy ? 'Hướng chăm sóc sắp tới' : 'Phương pháp điều trị'}</Text>
          </View>
          {isEditing ? (
            <TextInput
              style={styles.input}
              multiline
              value={treatment}
              onChangeText={setTreatment}
            />
          ) : (
            <Text style={styles.sectionText}>{treatment}</Text>
          )}
        </View>

        {!isHealthy && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="time" size={20} color="#3B82F6" />
              <Text style={styles.sectionTitle}>Dự kiến thời gian điều trị</Text>
            </View>
          {isEditing ? (
            <TextInput
              style={styles.input}
              multiline
              value={recoveryTime}
              onChangeText={setRecoveryTime}
            />
          ) : (
            <Text style={styles.sectionText}>{recoveryTime}</Text>
          )}
          </View>
        )}

        {isEditing && (
          <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={saving}>
            <Text style={styles.saveButtonText}>{saving ? 'Đang lưu...' : 'Lưu thay đổi'}</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    marginTop: 12,
    color: '#6B7280',
    fontSize: 14,
  },
  headerButton: {
    paddingHorizontal: 16,
  },
  headerButtonText: {
    color: '#10B981',
    fontWeight: '700',
    fontSize: 16,
  },
  carouselContainer: {
    marginTop: 16,
    height: 200,
  },
  carouselImage: {
    width: 280,
    height: 200,
    borderRadius: 16,
    marginRight: 12,
    backgroundColor: '#E5E7EB',
  },
  contentBody: {
    padding: 20,
    paddingBottom: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
  },
  subtitle: {
    fontSize: 15,
    color: '#6B7280',
    marginTop: 4,
    marginBottom: 24,
  },
  section: {
    backgroundColor: '#F9FAFB',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  sectionHeader: {
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
  },
  input: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    color: '#111827',
    textAlignVertical: 'top',
    minHeight: 120,
  },
  saveButton: {
    backgroundColor: '#10B981',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  }
});
