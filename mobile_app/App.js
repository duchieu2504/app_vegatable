import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { View, Image, Text, StyleSheet } from 'react-native';
import DiagnoseScreen from './screens/DiagnoseScreen';
import EncyclopediaScreen from './screens/EncyclopediaScreen';
import HistoryScreen from './screens/HistoryScreen';
import AdminScreen from './screens/AdminScreen';

import { createNativeStackNavigator } from '@react-navigation/native-stack';
import DiseaseDetailScreen from './screens/DiseaseDetailScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function EncyclopediaStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="EncyclopediaList"
        component={EncyclopediaScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="DiseaseDetail"
        component={DiseaseDetailScreen}
        options={({ route }) => ({ title: route.params?.diseaseName || 'Chi tiết bệnh' })}
      />
    </Stack.Navigator>
  );
}

// Custom Header Title with Logo for Diagnose tab
function DiagnoseHeaderTitle() {
  return (
    <View style={headerStyles.titleRow}>
      <Image source={require('./assets/logo.png')} style={headerStyles.logo} />
      <View>
        <Text style={headerStyles.brandName}>AgriDoc AI</Text>
        <Text style={headerStyles.brandTagline}>Chẩn đoán bệnh thực vật</Text>
      </View>
    </View>
  );
}

const headerStyles = StyleSheet.create({
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logo: {
    width: 36,
    height: 36,
    borderRadius: 10,
    marginRight: 10,
    resizeMode: 'contain',
  },
  brandName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#065F46',
    fontStyle: 'italic',
    letterSpacing: 0.5,
  },
  brandTagline: {
    fontSize: 11,
    color: '#6B7280',
    fontStyle: 'italic',
    marginTop: 1,
  },
});

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            if (route.name === 'Diagnose') iconName = focused ? 'scan-circle' : 'scan-circle-outline';
            else if (route.name === 'Encyclopedia') iconName = focused ? 'book' : 'book-outline';
            else if (route.name === 'History') iconName = focused ? 'time' : 'time-outline';
            else if (route.name === 'Admin') iconName = focused ? 'settings' : 'settings-outline';

            return <Ionicons name={iconName} size={size + 4} color={color} />;
          },
          tabBarActiveTintColor: '#10B981',
          tabBarInactiveTintColor: '#9CA3AF',
          tabBarStyle: {
            borderTopWidth: 0,
            elevation: 10,
            shadowColor: '#000',
            shadowOpacity: 0.05,
            shadowOffset: { width: 0, height: -3 },
            shadowRadius: 10,
            height: 80,
            paddingBottom: 10,
            paddingTop: 10,
            backgroundColor: '#ffffff'
          },
          headerStyle: {
            backgroundColor: '#ffffff',
            borderBottomWidth: 2,
            borderBottomColor: '#D1FAE5',
            shadowColor: '#000',
            shadowOpacity: 0.08,
            shadowOffset: { width: 0, height: 3 },
            shadowRadius: 8,
            elevation: 8,
            height: 70,
          },
          headerTintColor: '#065F46',
          headerTitleAlign: 'center',
          headerTitleStyle: {
            fontWeight: '700',
            fontSize: 17,
            fontStyle: 'italic',
            letterSpacing: 0.3,
            color: '#065F46',
          },
        })}
      >
        <Tab.Screen
          name="Diagnose"
          component={DiagnoseScreen}
          options={{
            headerTitle: () => <DiagnoseHeaderTitle />,
            tabBarLabel: 'Chẩn đoán',
          }}
        />
        <Tab.Screen
          name="Encyclopedia"
          component={EncyclopediaStack}
          options={{ title: 'Từ Điển Bệnh Học', tabBarLabel: 'Từ điển' }}
        />
        <Tab.Screen
          name="History"
          component={HistoryScreen}
          options={{ title: 'Lịch Sử Chẩn Đoán', tabBarLabel: 'Lịch sử' }}
        />
        <Tab.Screen
          name="Admin"
          component={AdminScreen}
          options={{ title: 'Quản Trị Hệ Thống', tabBarLabel: 'Quản trị' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
