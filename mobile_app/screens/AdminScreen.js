import { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, ScrollView, Alert, ActivityIndicator, TouchableOpacity, Modal, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const BACKEND_URL = `${API_BASE_URL}/admin`;

const CustomDropdown = ({ label, data, selectedValue, onSelect, placeholder }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const selectedItem = data.find(item => item.value === selectedValue);

  return (
    <View style={styles.dropdownContainer}>
      <Text style={styles.label}>{label}</Text>
      <TouchableOpacity 
        style={styles.dropdownButton} 
        onPress={() => setModalVisible(true)}
      >
        <Text style={[styles.dropdownButtonText, !selectedItem && {color: '#9CA3AF'}]}>
          {selectedItem ? selectedItem.label : placeholder}
        </Text>
        <Ionicons name="chevron-down" size={20} color="#6B7280" />
      </TouchableOpacity>

      <Modal visible={modalVisible} transparent={true} animationType="fade">
        <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setModalVisible(false)}>
          <View style={styles.modalContentDropdown}>
            <ScrollView bounces={false}>
              {data.map(item => (
                <TouchableOpacity 
                  key={item.value} 
                  style={[styles.dropdownItem, selectedValue === item.value && styles.dropdownItemActive]}
                  onPress={() => {
                    onSelect(item.value);
                    setModalVisible(false);
                  }}
                >
                  <Text style={[styles.dropdownItemText, selectedValue === item.value && styles.dropdownItemTextActive]}>
                    {item.label}
                  </Text>
                  {selectedValue === item.value && <Ionicons name="checkmark" size={20} color="#10B981" />}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

export default function AdminScreen() {
  const [diseaseId, setDiseaseId] = useState('');
  const [name, setName] = useState('');
  const [plant, setPlant] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [treatment, setTreatment] = useState('');
  const [loading, setLoading] = useState(false);
  const [plantsData, setPlantsData] = useState([]);
  const [selectedPlantId, setSelectedPlantId] = useState(null);
  const [selectedAssets, setSelectedAssets] = useState([]);

  const handleAddDisease = async () => {
    if (!diseaseId || !name || !plant) {
      Alert.alert("Lỗi", "Vui lòng nhập ID, Tên bệnh và Tên cây.");
      return;
    }
    
    try {
      const payload = { id: diseaseId, name, plant, symptoms, treatment, imageUrl: "https://via.placeholder.com/300" };
      const response = await axios.post(`${BACKEND_URL}/add_disease`, payload);
      Alert.alert("Thông báo", response.data.message);
    } catch (error) {
      Alert.alert("Lỗi", "Không thể thêm bệnh mới.");
    }
  };

  const pickImages = async () => {
    if (!diseaseId) {
      Alert.alert("Lỗi", "Vui lòng chọn loại rau và bệnh trước.");
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsMultipleSelection: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setSelectedAssets(result.assets);
    }
  };

  const uploadImages = async () => {
    if (!selectedAssets || selectedAssets.length === 0) return;
    
    setLoading(true);
    try {
      let uploadedCount = 0;
      for (const asset of selectedAssets) {
        const formData = new FormData();
        const responseBlob = await fetch(asset.uri);
        const blob = await responseBlob.blob();
        
        // Generate a unique filename using timestamp and index to prevent overwrite
        const filename = `image_${Date.now()}_${uploadedCount}.jpg`;
        formData.append('file', blob, filename);

        await axios.post(`${BACKEND_URL}/upload_image?disease_id=${diseaseId}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        uploadedCount++;
      }
      Alert.alert("Thành công", `Đã tải lên ${uploadedCount} ảnh mẫu cho bệnh ${diseaseId}`);
      setSelectedAssets([]); // Clear selection after success
    } catch (error) {
      Alert.alert("Lỗi", "Quá trình tải ảnh thất bại.");
    } finally {
      setLoading(false);
    }
  };

  const handleAutoTrain = async () => {
    Alert.alert(
      "Xác nhận", 
      "Kích hoạt huấn luyện trên Kaggle? Quá trình này sẽ tốn khoảng 30 phút.",
      [
        { text: "Hủy", style: "cancel" },
        { 
          text: "Đồng ý", 
          onPress: async () => {
            try {
              const res = await axios.post(`${BACKEND_URL}/auto_train`);
              Alert.alert("Thành công", res.data.message);
            } catch (e) {
              Alert.alert("Lỗi", "Gọi API thất bại.");
            }
          }
        }
      ]
    );
  };

  const [apiKey, setApiKey] = useState('');
  const [maskedKey, setMaskedKey] = useState('');
  const [testingApi, setTestingApi] = useState(false);
  const [apiLog, setApiLog] = useState(null); // { type: 'success' | 'error', message: '' }

  useEffect(() => {
    axios.get(`${BACKEND_URL}/config_api_key`)
      .then(res => {
        if (res.data.api_key) {
          setMaskedKey(res.data.api_key); // Now returns masked key like "AIza...***gs"
        }
      })
      .catch(console.error);
      
    // Fetch danh sách rau và bệnh từ backend
    axios.get(`${API_BASE_URL}/encyclopedia`)
      .then(res => {
        if (res.data && res.data.data) {
          setPlantsData(res.data.data);
        }
      })
      .catch(console.error);
  }, []);

  const handleUpdateApiKey = async () => {
    if (!apiKey) {
      setApiLog({ type: 'error', message: 'Vui lòng nhập API Key.' });
      return;
    }
    setTestingApi(true);
    setApiLog(null); // Reset log
    try {
      const response = await axios.post(`${BACKEND_URL}/config_api_key`, { api_key: apiKey });
      if (response.data.status === 'success') {
        setApiLog({ type: 'success', message: response.data.message });
      } else {
        setApiLog({ type: 'error', message: response.data.message });
      }
    } catch (error) {
      setApiLog({ type: 'error', message: 'Không thể cấu hình API Key. Kiểm tra kết nối mạng.' });
    } finally {
      setTestingApi(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="key" size={24} color="#3B82F6" />
          <Text style={[styles.cardTitle, {color: '#3B82F6'}]}>Cấu Hình Gemini AI</Text>
        </View>
        <Text style={styles.hint}>Nhập Google Gemini API Key để hệ thống AI (Bác sĩ cây trồng) có thể hoạt động.</Text>
        <TextInput 
          style={styles.input} 
          placeholder={maskedKey ? `Hiện tại: ${maskedKey}` : "Nhập API Key bắt đầu bằng AIza..."} 
          value={apiKey} 
          onChangeText={setApiKey} 
          placeholderTextColor="#9CA3AF" 
          secureTextEntry={true}
        />
        {apiLog && (
          <View style={[styles.logContainer, apiLog.type === 'success' ? styles.logSuccess : styles.logError]}>
            <Ionicons name={apiLog.type === 'success' ? "checkmark-circle" : "alert-circle"} size={20} color={apiLog.type === 'success' ? "#059669" : "#DC2626"} />
            <Text style={[styles.logText, { color: apiLog.type === 'success' ? "#059669" : "#DC2626" }]}>{apiLog.message}</Text>
          </View>
        )}
        <TouchableOpacity style={[styles.primaryBtn, {backgroundColor: '#3B82F6', shadowColor: '#3B82F6'}]} onPress={handleUpdateApiKey} disabled={testingApi}>
          {testingApi ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Lưu & Kiểm tra API Key</Text>}
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="images" size={24} color="#F59E0B" />
          <Text style={[styles.cardTitle, {color: '#F59E0B'}]}>Bổ Sung Ảnh Thực Tế</Text>
        </View>
        <Text style={styles.hint}>Chọn loại rau và bệnh để tải ảnh thực tế lên hệ thống.</Text>
        
        <CustomDropdown 
          label="1. Chọn loại rau:" 
          data={plantsData.map(p => ({label: p.plant_name, value: p.id}))}
          selectedValue={selectedPlantId}
          onSelect={(val) => { setSelectedPlantId(val); setDiseaseId(''); }}
          placeholder="-- Nhấp để chọn loại rau --"
        />

        {selectedPlantId && (
          <CustomDropdown 
            label="2. Chọn bệnh:" 
            data={plantsData.find(p => p.id === selectedPlantId)?.diseases.map(d => ({label: d.name, value: d.id})) || []}
            selectedValue={diseaseId}
            onSelect={(val) => {
              setDiseaseId(val);
              setSelectedAssets([]); // reset images when disease changes
            }}
            placeholder="-- Nhấp để chọn bệnh --"
          />
        )}

        {selectedAssets.length > 0 && (
          <View style={styles.previewSection}>
            <Text style={styles.label}>3. Ảnh đã chọn ({selectedAssets.length}):</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.previewScroll}>
              {selectedAssets.map((asset, index) => (
                <View key={index} style={styles.previewImageContainer}>
                  <Image source={{ uri: asset.uri }} style={styles.previewImage} />
                  <TouchableOpacity 
                    style={styles.removeImageBtn}
                    onPress={() => setSelectedAssets(selectedAssets.filter((_, i) => i !== index))}
                  >
                    <Ionicons name="close-circle" size={24} color="#EF4444" />
                  </TouchableOpacity>
                </View>
              ))}
            </ScrollView>
          </View>
        )}

        {selectedAssets.length === 0 ? (
          <TouchableOpacity 
            style={[styles.primaryBtn, {backgroundColor: diseaseId ? '#3B82F6' : '#D1D5DB', shadowColor: diseaseId ? '#3B82F6' : 'transparent', marginTop: 15}]} 
            onPress={pickImages} 
            disabled={!diseaseId}
          >
            <Text style={styles.btnText}>Chọn Ảnh Từ Thiết Bị</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.actionRow}>
            <TouchableOpacity 
              style={[styles.secondaryBtn, {flex: 1, marginRight: 10}]} 
              onPress={pickImages} 
              disabled={loading}
            >
              <Text style={[styles.btnText, {color: '#4B5563'}]}>Chọn Thêm</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.primaryBtn, {backgroundColor: '#10B981', shadowColor: '#10B981', flex: 2, marginTop: 0}]} 
              onPress={uploadImages} 
              disabled={loading}
            >
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Xác Nhận Cập Nhật</Text>}
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#F9FAFB',
  },
  card: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 24,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginLeft: 10,
  },
  input: {
    backgroundColor: '#F3F4F6',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    fontSize: 15,
    color: '#111827',
  },
  hint: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 15,
    lineHeight: 20,
  },
  primaryBtn: {
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 5,
    shadowColor: '#10B981',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 5,
  },
  btnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  logContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  logSuccess: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#34D399',
  },
  logError: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#F87171',
  },
  logText: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
    flex: 1,
  },
  label: {
    fontSize: 15,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    marginTop: 5,
  },
  dropdownContainer: {
    marginBottom: 16,
  },
  dropdownButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
  },
  dropdownButtonText: {
    fontSize: 15,
    color: '#111827',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContentDropdown: {
    backgroundColor: '#fff',
    borderRadius: 16,
    width: '100%',
    maxHeight: '60%',
    overflow: 'hidden',
  },
  dropdownItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  dropdownItemActive: {
    backgroundColor: '#ECFDF5',
  },
  dropdownItemText: {
    fontSize: 16,
    color: '#374151',
  },
  dropdownItemTextActive: {
    color: '#10B981',
    fontWeight: '600',
  },
  previewSection: {
    marginTop: 10,
    marginBottom: 5,
  },
  previewScroll: {
    flexDirection: 'row',
  },
  previewImageContainer: {
    marginRight: 12,
    position: 'relative',
  },
  previewImage: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: '#E5E7EB',
  },
  removeImageBtn: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#fff',
    borderRadius: 12,
  },
  actionRow: {
    flexDirection: 'row',
    marginTop: 15,
    alignItems: 'center',
  },
  secondaryBtn: {
    backgroundColor: '#E5E7EB',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  }
});
