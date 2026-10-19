import { useState } from 'react';
import { StyleSheet, Text, View, Image, ScrollView, ActivityIndicator, Alert, TouchableOpacity, Dimensions } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const BACKEND_URL = `${API_BASE_URL}/diagnose`;
const { height } = Dimensions.get('window');

export default function DiagnoseScreen() {
  const [imageUri, setImageUri] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert("Cần cấp quyền", "Bạn cần cấp quyền truy cập thư viện ảnh để sử dụng app.");
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      setResult(null);
    }
  };

  const takePhoto = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert("Cần cấp quyền", "Bạn cần cấp quyền truy cập Camera để chụp ảnh.");
      return;
    }

    let result = await ImagePicker.launchCameraAsync({
      allowsEditing: false,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      setResult(null);
    }
  };

  const diagnosePlant = async () => {
    if (!imageUri) return;
    setLoading(true);
    try {
      const formData = new FormData();
      const responseBlob = await fetch(imageUri);
      const blob = await responseBlob.blob();
      formData.append('file', blob, 'upload.jpg');

      const response = await axios.post(BACKEND_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setResult(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert("Lỗi", "Không thể kết nối tới Backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.mainContainer}>
      {/* Background Image Header */}
      <View style={styles.imageHeader}>
        <Image source={require('../assets/trangchu.jpg')} style={styles.headerImage} />
        {/* Overlay gradient can be added here if needed to make status bar readable */}
      </View>

      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* Transparent spacer to push content down to overlap the image */}
        <View style={styles.spacer} />

        {/* Bottom Content Area with Upward Curve */}
        <View style={styles.bottomContent}>
          <View style={styles.dragHandle} />

          <Text style={styles.welcomeTitle}>Chào mừng đến với AgriDoc AI</Text>
          <Text style={styles.welcomeSubtitle}>Hãy chụp hoặc chọn ảnh lá cây bị bệnh để AI phân tích.</Text>

          {!imageUri ? (
            <View style={styles.actionRow}>
              <TouchableOpacity style={[styles.actionCard, { marginRight: 10 }]} onPress={pickImage}>
                <Ionicons name="images-outline" size={40} color="#10B981" />
                <Text style={styles.actionText}>Thư viện ảnh</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.actionCard, { marginLeft: 10 }]} onPress={takePhoto}>
                <Ionicons name="camera-outline" size={40} color="#10B981" />
                <Text style={styles.actionText}>Chụp ảnh mới</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.imageWrapper}>
              <Image source={{ uri: imageUri }} style={styles.previewImage} />
              <View style={{ flexDirection: 'row', marginTop: 15, gap: 10, justifyContent: 'center' }}>
                <TouchableOpacity style={styles.retakeBtn} onPress={pickImage}>
                  <Ionicons name="images-outline" size={20} color="#6B7280" />
                  <Text style={styles.retakeText}>Thư viện</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.retakeBtn} onPress={takePhoto}>
                  <Ionicons name="camera-outline" size={20} color="#6B7280" />
                  <Text style={styles.retakeText}>Chụp lại</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {imageUri && !result && !loading && (
            <TouchableOpacity style={styles.primaryButton} onPress={diagnosePlant}>
              <Ionicons name="scan-outline" size={20} color="#fff" style={{ marginRight: 8 }} />
              <Text style={styles.primaryButtonText}>Phân tích Bệnh lý</Text>
            </TouchableOpacity>
          )}

          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#10B981" />
              <Text style={styles.loadingText}>Hệ thống đang phân tích rau...</Text>
            </View>
          )}

          {result && result.status === 'low_confidence' && (
            <View style={[styles.resultCard, { borderWidth: 2, borderColor: '#F59E0B' }]}>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
                <Ionicons name="alert-circle" size={28} color="#F59E0B" style={{ marginRight: 10 }} />
                <Text style={[styles.resultPlantTitle, { color: '#92400E', flex: 1 }]}>Không nhận diện được</Text>
              </View>
              <View style={[styles.sectionContainer, { backgroundColor: '#FFFBEB' }]}>
                <Text style={[styles.sectionText, { color: '#92400E' }]}>{result.llm_advice?.symptoms}</Text>
              </View>
              <View style={[styles.sectionContainer, { backgroundColor: '#FFFBEB' }]}>
                <View style={styles.sectionHeader}>
                  <Ionicons name="camera" size={20} color="#F59E0B" />
                  <Text style={styles.sectionTitle}>Gợi ý</Text>
                </View>
                <Text style={styles.sectionText}>{result.llm_advice?.treatment}</Text>
              </View>
            </View>
          )}

          {result && result.status === 'success' && (
            <View style={styles.resultCard}>
              <Text style={styles.resultPlantTitle}>
                {result.llm_advice?.plant ? `Loại Rau: ${result.llm_advice.plant}` : 'Kết quả chuẩn đoán'}
              </Text>
              <View style={styles.badgeContainer}>
                <View style={styles.badge}>
                  <Ionicons name="leaf" size={14} color="#10B981" style={{ marginRight: 4 }} />
                  <Text style={styles.badgeText}>Chuẩn đoán: {result.vision_result?.disease_name}</Text>
                </View>
                <View style={[styles.badge, { backgroundColor: '#EFF6FF' }]}>
                  <Ionicons name="analytics" size={14} color="#3B82F6" style={{ marginRight: 4 }} />
                  <Text style={[styles.badgeText, { color: '#1E40AF' }]}>Độ tin cậy: {(result.vision_result?.confidence * 100).toFixed(1)}%</Text>
                </View>
              </View>

              <View style={styles.sectionContainer}>
                <View style={styles.sectionHeader}>
                  <Ionicons name="search" size={20} color="#F59E0B" />
                  <Text style={styles.sectionTitle}>
                    {result.vision_result?.is_healthy ? 'Dấu hiệu rau khỏe mạnh' : 'Triệu chứng'}
                  </Text>
                </View>
                <Text style={styles.sectionText}>{result.llm_advice?.symptoms}</Text>
              </View>

              {!result.vision_result?.is_healthy && (
                <>
                  <View style={styles.sectionContainer}>
                    <View style={styles.sectionHeader}>
                      <Ionicons name="bug" size={20} color="#EF4444" />
                      <Text style={styles.sectionTitle}>Nguyên nhân</Text>
                    </View>
                    <Text style={styles.sectionText}>{result.llm_advice?.causes}</Text>
                  </View>

                  <View style={styles.sectionContainer}>
                    <View style={styles.sectionHeader}>
                      <Ionicons name="warning" size={20} color="#F97316" />
                      <Text style={styles.sectionTitle}>Tác hại</Text>
                    </View>
                    <Text style={styles.sectionText}>{result.llm_advice?.harm}</Text>
                  </View>
                </>
              )}

              <View style={styles.sectionContainer}>
                <View style={styles.sectionHeader}>
                  <Ionicons name="medkit" size={20} color="#10B981" />
                  <Text style={styles.sectionTitle}>
                    {result.vision_result?.is_healthy ? 'Hướng chăm sóc sắp tới' : 'Phương pháp điều trị'}
                  </Text>
                </View>
                <Text style={styles.sectionText}>{result.llm_advice?.treatment}</Text>
              </View>

              {!result.vision_result?.is_healthy && (
                <View style={styles.sectionContainer}>
                  <View style={styles.sectionHeader}>
                    <Ionicons name="time" size={20} color="#3B82F6" />
                    <Text style={styles.sectionTitle}>Thời gian phục hồi</Text>
                  </View>
                  <Text style={styles.sectionText}>{result.llm_advice?.recovery_time}</Text>
                </View>
              )}
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  imageHeader: {
    position: 'absolute',
    top: 0,
    width: '100%',
    height: height * 0.66, // Chiếm 2/3 màn hình
  },
  headerImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  scrollContainer: {
    flexGrow: 1,
  },
  spacer: {
    height: height * 0.55, // Đẩy content xuống dưới, tạo độ overlap
  },
  bottomContent: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    borderTopLeftRadius: 40, // Độ cong vồng lên trên
    borderTopRightRadius: 40,
    padding: 24,
    minHeight: height * 0.45,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: -5 },
    shadowRadius: 15,
    elevation: 10,
  },
  dragHandle: {
    width: 50,
    height: 5,
    backgroundColor: '#E5E7EB',
    borderRadius: 5,
    alignSelf: 'center',
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
    textAlign: 'center',
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 25,
  },
  actionRow: {
    flexDirection: 'row',
    width: '100%',
    justifyContent: 'space-between',
  },
  actionCard: {
    flex: 1,
    height: 140,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 3,
  },
  actionText: {
    marginTop: 12,
    fontSize: 15,
    fontWeight: '700',
    color: '#111827',
  },
  imageWrapper: {
    width: '100%',
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: 250,
    borderRadius: 20,
  },
  retakeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    backgroundColor: '#E5E7EB',
    borderRadius: 20,
  },
  retakeText: {
    marginLeft: 5,
    color: '#4B5563',
    fontWeight: '600',
  },
  primaryButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981',
    width: '100%',
    paddingVertical: 16,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 25,
    shadowColor: '#10B981',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 5,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  loadingContainer: {
    marginTop: 40,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 15,
    color: '#6B7280',
    fontWeight: '500',
  },
  resultCard: {
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 20,
    marginTop: 30,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 3,
  },
  resultPlantTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 12,
  },
  badgeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 20,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  badgeText: {
    color: '#065F46',
    fontWeight: '600',
    fontSize: 14,
  },
  sectionContainer: {
    backgroundColor: '#F9FAFB',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
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
