import { useState, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, ActivityIndicator, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function HistoryScreen() {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [historyRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/history?limit=50`),
        axios.get(`${API_BASE_URL}/history/stats`),
      ]);
      setHistory(historyRes.data?.data || []);
      setStats(statsRes.data?.data || null);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Refresh data when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchData();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.85) return '#10B981';
    if (confidence >= 0.6) return '#F59E0B';
    return '#EF4444';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr + 'Z');
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const hours = d.getHours().toString().padStart(2, '0');
    const mins = d.getMinutes().toString().padStart(2, '0');
    return `${day}/${month} ${hours}:${mins}`;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Đang tải lịch sử...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#10B981" />}
      >
        {/* Stats Cards */}
        {stats && (
          <View style={styles.statsRow}>
            <View style={[styles.statCard, { backgroundColor: '#EFF6FF' }]}>
              <Ionicons name="analytics" size={22} color="#3B82F6" />
              <Text style={styles.statNumber}>{stats.total_diagnoses}</Text>
              <Text style={styles.statLabel}>Tổng chẩn đoán</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#FEF2F2' }]}>
              <Ionicons name="bug" size={22} color="#EF4444" />
              <Text style={styles.statNumber}>{stats.diseased_count}</Text>
              <Text style={styles.statLabel}>Có bệnh</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#ECFDF5' }]}>
              <Ionicons name="checkmark-circle" size={22} color="#10B981" />
              <Text style={styles.statNumber}>{stats.healthy_count}</Text>
              <Text style={styles.statLabel}>Khỏe mạnh</Text>
            </View>
          </View>
        )}

        {/* Top Diseases */}
        {stats?.top_diseases?.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="trending-up" size={20} color="#F59E0B" />
              <Text style={styles.sectionTitle}>Bệnh phát hiện nhiều nhất</Text>
            </View>
            {stats.top_diseases.map((d, i) => (
              <View key={i} style={styles.topDiseaseRow}>
                <View style={[styles.rankBadge, i === 0 && { backgroundColor: '#FEF3C7' }]}>
                  <Text style={styles.rankText}>#{i + 1}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.topDiseaseName}>{d.disease_name}</Text>
                  <Text style={styles.topDiseasePlant}>{d.plant_name}</Text>
                </View>
                <Text style={styles.topDiseaseCount}>{d.count} lần</Text>
              </View>
            ))}
          </View>
        )}

        {/* History List */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="time" size={20} color="#6366F1" />
            <Text style={styles.sectionTitle}>Lịch sử gần đây</Text>
          </View>

          {history.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="camera-outline" size={48} color="#D1D5DB" />
              <Text style={styles.emptyText}>Chưa có lịch sử chẩn đoán</Text>
              <Text style={styles.emptySubtext}>Hãy chụp ảnh lá rau tại tab "Chẩn đoán" để bắt đầu</Text>
            </View>
          ) : (
            history.map((record, index) => (
              <View key={record.id || index} style={styles.historyCard}>
                <View style={styles.historyCardHeader}>
                  <View style={styles.historyIconWrapper}>
                    <Ionicons
                      name={record.is_healthy ? 'checkmark-circle' : 'alert-circle'}
                      size={24}
                      color={record.is_healthy ? '#10B981' : '#EF4444'}
                    />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.historyDiseaseName}>{record.disease_name}</Text>
                    <Text style={styles.historyPlantName}>{record.plant_name}</Text>
                  </View>
                  <Text style={styles.historyDate}>{formatDate(record.diagnosed_at)}</Text>
                </View>
                <View style={styles.historyCardFooter}>
                  <View style={[styles.confidenceBadge, { backgroundColor: getConfidenceColor(record.confidence) + '20' }]}>
                    <View style={[styles.confidenceDot, { backgroundColor: getConfidenceColor(record.confidence) }]} />
                    <Text style={[styles.confidenceText, { color: getConfidenceColor(record.confidence) }]}>
                      {(record.confidence * 100).toFixed(1)}%
                    </Text>
                  </View>
                  {record.image_filename ? (
                    <Text style={styles.historyFilename} numberOfLines={1}>
                      📷 {record.image_filename}
                    </Text>
                  ) : null}
                </View>
              </View>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: '#6B7280',
  },

  // Stats Cards
  statsRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    borderRadius: 14,
    padding: 14,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 6,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1F2937',
    marginTop: 6,
  },
  statLabel: {
    fontSize: 11,
    color: '#6B7280',
    marginTop: 2,
    fontWeight: '500',
  },

  // Sections
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
    gap: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F2937',
  },

  // Top Diseases
  topDiseaseRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    gap: 10,
  },
  rankBadge: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  rankText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#6B7280',
  },
  topDiseaseName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  topDiseasePlant: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 1,
  },
  topDiseaseCount: {
    fontSize: 13,
    fontWeight: '700',
    color: '#6366F1',
  },

  // Empty State
  emptyState: {
    alignItems: 'center',
    paddingVertical: 30,
  },
  emptyText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#9CA3AF',
    marginTop: 12,
  },
  emptySubtext: {
    fontSize: 13,
    color: '#D1D5DB',
    marginTop: 4,
    textAlign: 'center',
  },

  // History Cards
  historyCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#F3F4F6',
  },
  historyCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  historyIconWrapper: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 1 },
    shadowRadius: 3,
    elevation: 1,
  },
  historyDiseaseName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  historyPlantName: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 1,
  },
  historyDate: {
    fontSize: 12,
    color: '#9CA3AF',
    fontWeight: '500',
  },
  historyCardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    gap: 10,
  },
  confidenceBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    gap: 5,
  },
  confidenceDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  confidenceText: {
    fontSize: 12,
    fontWeight: '700',
  },
  historyFilename: {
    fontSize: 11,
    color: '#9CA3AF',
    flex: 1,
  },
});
