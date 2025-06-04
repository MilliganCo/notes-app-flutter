import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'note_card.dart';
import 'dialogs.dart';
import 'api_service.dart' as api_service;
import 'utils/location_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'firebase_options.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:convert';

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  print('Получено фоновое сообщение: ${message.messageId}');
}

Future<void> _setupNotifications() async {
  const AndroidInitializationSettings initializationSettingsAndroid =
      AndroidInitializationSettings('@mipmap/ic_launcher');
  final DarwinInitializationSettings initializationSettingsIOS =
      DarwinInitializationSettings(
    requestAlertPermission: true,
    requestBadgePermission: true,
    requestSoundPermission: true,
  );
  final InitializationSettings initializationSettings = InitializationSettings(
    android: initializationSettingsAndroid,
    iOS: initializationSettingsIOS,
  );
  await flutterLocalNotificationsPlugin.initialize(initializationSettings);
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // TODO(reenable-firebase): uncomment for release
  // await Firebase.initializeApp(
  //   options: DefaultFirebaseOptions.currentPlatform,
  // );
  // await _setupNotifications();
  // FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(NotesApp());
}

class NotesApp extends StatelessWidget {
  const NotesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Notes App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        colorScheme: ColorScheme.light(
          primary: Color(0xFFB5EAD7),
          secondary: Color(0xFFFFDAC1),
          surface: Color(0xFFE2F0CB),
          background: Color(0xFFF7F7F7),
          error: Color(0xFFFFB7B2),
        ),
        scaffoldBackgroundColor: Color(0xFFF7F7F7),
        appBarTheme: AppBarTheme(
          backgroundColor: Color(0xFFB5EAD7),
          foregroundColor: Colors.black87,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFB5EAD7),
            foregroundColor: Colors.black87,
          ),
        ),
        floatingActionButtonTheme: FloatingActionButtonThemeData(
          backgroundColor: Color(0xFFFFDAC1),
          foregroundColor: Colors.black87,
        ),
      ),
      home: LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool isLoading = false;

  Future<void> login() async {
    if (usernameController.text.isEmpty || passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пожалуйста, заполните все поля')),
      );
      return;
    }

    setState(() => isLoading = true);

    try {
      final success = await api_service.login(usernameController.text, passwordController.text);
      if (success) {
        // TODO(reenable-firebase): uncomment for release
        // await api_service.registerDevice(usernameController.text);
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => NotesScreen(username: usernameController.text)),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Неверное имя пользователя или пароль')),
        );
      }
    } finally {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Вход'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: usernameController,
              decoration: InputDecoration(
                labelText: 'Имя пользователя',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 16.0),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Пароль',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 24.0),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isLoading ? null : login,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: isLoading
                      ? CircularProgressIndicator()
                      : Text('Войти'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class NotesScreen extends StatefulWidget {
  final String username;
  const NotesScreen({required this.username, super.key});

  @override
  _NotesScreenState createState() => _NotesScreenState();
}

class _NotesScreenState extends State<NotesScreen> {
  List<Map<String, dynamic>> notes = [];
  Timer? timer;
  Position? currentPosition;
  bool isAdmin = false;

  List<Map<String, dynamic>> localNotes = [];

  Future<void> loadLocalNotes() async {
    final prefs = await SharedPreferences.getInstance();
    final String? notesString = prefs.getString('localNotes');
    if (notesString != null) {
      localNotes = List<Map<String, dynamic>>.from(json.decode(notesString));
    }
  }

  Future<void> saveLocalNotes() async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('localNotes', json.encode(localNotes));
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

  @override
  void initState() {
    super.initState();
    loadLocalNotes();
    requestLocationPermission();
    fetchLocation();
    fetchNotes();
    timer = Timer.periodic(const Duration(seconds: 10), (_) => fetchNotes());
    // TODO(reenable-firebase): uncomment for release
    // _setupFCM();
  }

  Future<void> _setupFCM() async {
    FirebaseMessaging messaging = FirebaseMessaging.instance;
    NotificationSettings settings = await messaging.requestPermission();
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        RemoteNotification? notification = message.notification;
        AndroidNotification? android = message.notification?.android;

        if (notification != null && android != null) {
          flutterLocalNotificationsPlugin.show(
            notification.hashCode,
            notification.title,
            notification.body,
            NotificationDetails(
              android: AndroidNotificationDetails(
                'high_importance_channel',
                'High Importance Notifications',
                channelDescription: 'This channel is used for important notifications.',
                importance: Importance.max,
                priority: Priority.high,
                icon: android.smallIcon,
              ),
            ),
          );
        }
      });
    }
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> requestLocationPermission() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Разрешение на геолокацию отклонено')),
        );
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Разрешение на геолокацию навсегда отклонено. Перейдите в настройки.')),
      );
      return;
    }

    currentPosition = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    setState(() {});
  }

  Future<void> fetchLocation() async {
    currentPosition = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    setState(() {});
  }

  Future<void> fetchNotes() async {
    if (currentPosition == null) return;
    final fetchedNotes = await api_service.getNotes(widget.username, currentPosition!.latitude, currentPosition!.longitude);
    final nearbyNotes = fetchedNotes.where((note) {
      final distance = Geolocator.distanceBetween(
        currentPosition!.latitude,
        currentPosition!.longitude,
        note['latitude'],
        note['longitude'],
      );
      return distance < 1000;
    }).toList();
    setState(() => notes = nearbyNotes);
  }

  Future<void> logout() async {
    await api_service.clearToken();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Записки (${widget.username})'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchLocation,
          ),
          IconButton(
            icon: const Icon(Icons.edit_location),
            onPressed: () { /* TODO: Implement location simulation or remove */ },
          ),
          IconButton(
            icon: const Icon(Icons.admin_panel_settings),
            onPressed: () {
              setState(() {
                isAdmin = !isAdmin;
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: logout,
          ),
        ],
      ),
      body: notes.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Загрузка записок...'),
                ],
              ),
            )
          : ListView.builder(
              padding: EdgeInsets.all(8),
              itemCount: notes.length,
              itemBuilder: (context, index) {
                final note = notes[index];
                final isCurrentUser = note['username'] == widget.username;

                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                  child: NoteCard(
                    note: note,
                    isCurrentUser: isCurrentUser,
                    onSave: () => api_service.saveNote(widget.username, note['note_id']),
                    onDelete: () => api_service.deleteNote(widget.username, note['note_id']),
                    onReply: () => openReplyDialog(
                      context,
                      note['note_id'],
                      note['username'],
                      (message) => api_service.sendReply(note['note_id'], widget.username, note['username'], message),
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => openAddNoteDialog(
          context,
          currentPosition,
          fetchNotes,
          widget.username,
          addLocalNote,
          isAdmin,
        ),
        child: const Icon(Icons.add),
      ),
    );
  }
}
