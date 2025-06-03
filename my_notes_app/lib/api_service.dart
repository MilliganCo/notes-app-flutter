import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Переопределение HTTP для игнорирования сертификатов (для тестов, не используйте в production!)
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  }
}

/// Получение записок с сервера
Future<List<Map<String, dynamic>>> getNotes(String username, double lat, double lon) async {
  final response = await http.get(
    Uri.parse('https://audioledyxxl.ru:5000/'),
    headers: {
      'Content-Type': 'application/json',
    },
  );

  if (response.statusCode == 200) {
    print("Ответ от сервера: ${response.body}");
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
  } else {
    print("Ошибка: ${response.statusCode}, тело: ${response.body}");
    return [];
  }
}

/// Сохранение записки
Future<void> saveNote(String username, String noteId) async {
  print("Пытаемся сохранить записку с note_id: $noteId");
  final response = await http.post(
    Uri.parse('https://audioledyxxl.ru:5000/save'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({"username": username, "note_id": noteId}),
  );

  print("Ответ от сервера: ${response.body}");
}

/// Удаление сохраненной записки
Future<void> deleteNote(String username, String noteId) async {
  print("Пытаемся удалить сохраненную записку с note_id: $noteId");
  final response = await http.post(
    Uri.parse('https://audioledyxxl.ru:5000/delete_saved_note'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({"username": username, "note_id": noteId}),
  );

  print("Ответ от сервера: ${response.body}");
}

/// Отправка ответа на записку
Future<void> sendReply(String noteId, String sender, String receiver, String message) async {
  print("Отправка ответа:");
  print("  note_id: $noteId");
  print("  sender: $sender");
  print("  receiver: $receiver");
  print("  content: $message");

  final response = await http.post(
    Uri.parse('https://audioledyxxl.ru:5000/message'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      "note_id": noteId,
      "sender": sender,
      "receiver": receiver,
      "content": message,
    }),
  );

  print("Ответ от сервера: ${response.body}");
}

/// Функция для отправки новой записки на сервер
Future<bool> sendNewNote(String username, String title, String content, double lat, double lon) async {
  try {
    print("Отправка новой записки:");
    print("  Заголовок: $title");
    print("  Текст: $content");
    print("  Координаты: [$lat, $lon]");

    final response = await http.post(
      Uri.parse('https://audioledyxxl.ru:5000/upload'),
      headers: {'Content-Type': 'application/json'},
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

    print("Ответ от сервера: ${response.body}");
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
