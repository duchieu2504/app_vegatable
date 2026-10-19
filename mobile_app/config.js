import { Platform } from 'react-native';

// Tự động nhận diện IP máy chủ:
// - Khi chạy trên trình duyệt Web (dù máy tính hay điện thoại): lấy theo địa chỉ IP mà trình duyệt đang truy cập (window.location.hostname)
// - Khi chạy trên ứng dụng Native (Expo Go app): dùng IP Wi-Fi nội bộ của máy tính
const getServerHost = () => {
  if (Platform.OS === 'web' && typeof window !== 'undefined' && window.location && window.location.hostname) {
    return window.location.hostname;
  }
  return '192.168.43.218';
};

const SERVER_IP = getServerHost();

export const API_BASE_URL = `http://${SERVER_IP}:8000/api/v1`;
