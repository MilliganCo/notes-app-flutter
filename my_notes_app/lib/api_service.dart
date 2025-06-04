import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

/// Переопределение HTTP для игнорирования сертификатов (для тестов, не используйте в production!)
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  }
}

String? _jwtToken;

Future<String?> getToken() async {
  if (_jwtToken != null) return _jwtToken;
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString('jwt_token');
}

Future<void> saveToken(String token) async {
  _jwtToken = token;
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString('jwt_token', token);
}

Future<void> clearToken() async {
  _jwtToken = null;
  final prefs = await SharedPreferences.getInstance();
  await prefs.remove('jwt_token');
}

Future<Map<String, String>> _getHeaders() async {
  final token = await getToken();
  return {
    'Content-Type': 'application/json',
    if (token != null) 'Authorization': 'Bearer $token',
  };
}

/// Аутентификация пользователя
Future<bool> login(String username, String password) async {
  try {
    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      await saveToken(data['token']);
      return true;
    }
    return false;
  } catch (e) {
    print('Ошибка при входе: $e');
    return false;
  }
}

/// Регистрация устройства для FCM
Future<void> registerDevice(String userId) async {
  try {
    final token = await FirebaseMessaging.instance.getToken();
    if (token == null) return;

    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/register_device'),
      headers: await _getHeaders(),
      body: json.encode({
        'user_id': userId,
        'token': token,
        'platform': Platform.isAndroid ? 'android' : 'ios',
      }),
    );

    if (response.statusCode != 200) {
      print('Ошибка регистрации устройства: ${response.body}');
    }
  } catch (e) {
    print('Ошибка при регистрации устройства: $e');
  }
}

/// Получение записок с сервера
Future<List<Map<String, dynamic>>> getNotes(String username, double lat, double lon) async {
  try {
    final response = await http.get(
      Uri.parse('https://audioledyxxl.ru:5000/'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return List<Map<String, dynamic>>.from(data['data'].map((item) => {
            "note_id": item[0] is String ? item[0] : "",
            "username": item[1][0] is String ? item[1][0] : "",
            "header": item[2][0] is String ? item[2][0] : "",
            "content": item[3][0] is String ? item[3][0] : "",
            "address": item.length > 6 && item[6][0] is String ? item[6][0] : "Адрес не указан",
            "metro": item.length > 7 && item[7][0] is String ? item[7][0] : "Метро не указано",
            "isSaved": false,
          }));
    }
    return [];
  } catch (e) {
    print('Ошибка при получении записок: $e');
    return [];
  }
}

/// Сохранение записки
Future<void> saveNote(String username, String noteId) async {
  try {
    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/save'),
      headers: await _getHeaders(),
      body: json.encode({"username": username, "note_id": noteId}),
    );

    if (response.statusCode != 200) {
      print('Ошибка при сохранении записки: ${response.body}');
    }
  } catch (e) {
    print('Ошибка при сохранении записки: $e');
  }
}

/// Удаление сохраненной записки
Future<void> deleteNote(String username, String noteId) async {
  try {
    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/delete_saved_note'),
      headers: await _getHeaders(),
      body: json.encode({"username": username, "note_id": noteId}),
    );

    if (response.statusCode != 200) {
      print('Ошибка при удалении записки: ${response.body}');
    }
  } catch (e) {
    print('Ошибка при удалении записки: $e');
  }
}

/// Отправка ответа на записку
Future<void> sendReply(String noteId, String sender, String receiver, String message) async {
  try {
    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/message'),
      headers: await _getHeaders(),
      body: json.encode({
        "note_id": noteId,
        "sender": sender,
        "receiver": receiver,
        "content": message,
      }),
    );

    if (response.statusCode != 200) {
      print('Ошибка при отправке ответа: ${response.body}');
    }
  } catch (e) {
    print('Ошибка при отправке ответа: $e');
  }
}

/// Функция для отправки новой записки на сервер
Future<bool> sendNewNote(String username, String title, String content, double lat, double lon) async {
  try {
    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/upload'),
      headers: await _getHeaders(),
      body: json.encode({
        "c2array": true,
        "size": [1, 5, 1],
        "data": [
          [
            [username],
            [title],
            [content],
            [lon],
            [lat],
          ]
        ]
      }),
    );

    return response.statusCode == 200;
  } catch (e) {
    print('Ошибка при добавлении записки: $e');
    return false;
  }
}

List<Map<String, dynamic>> generateTestNotes() {
  return [
    {
      "note_id": "234",
      "username": "andr",
      "header": "Заметка",
      "content": "Текст",
      "latitude": 55.75,
      "longitude": 37.62,
      "address": "Адрес",
      "metro": "Метро",
      "isSaved": false,
    },
    {
      "note_id": "457",
      "username": "Елена",
      "header": "Прогулка",
      "content": "я пишу [b]еще текст[/b]",
      "latitude": 55.76,
      "longitude": 37.63,
      "address": "Адрес 2",
      "metro": "Метро 2",
      "isSaved": false,
    },
    // Добавьте другие тестовые записки здесь
  ];
}

List<Map<String, dynamic>> localNotes = [];

Future<void> saveLocalNotes() async {
  final prefs = await SharedPreferences.getInstance();
  prefs.setString('localNotes', json.encode(localNotes));
}

Future<void> loadLocalNotes() async {
  final prefs = await SharedPreferences.getInstance();
  final String? notesString = prefs.getString('localNotes');
  if (notesString != null) {
    localNotes = List<Map<String, dynamic>>.from(json.decode(notesString));
  }
}

void addLocalNote(String username, String title, String content, double lat, double lon, String address, String metro) {
  localNotes.add({
    "note_id": DateTime.now().millisecondsSinceEpoch.toString(),
    "username": username,
    "header": title,
    "content": content,
    "latitude": lat,
    "longitude": lon,
    "address": address,
    "metro": metro,
    "isSaved": false,
  });
  saveLocalNotes();
}
