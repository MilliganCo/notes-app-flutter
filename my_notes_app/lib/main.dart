import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'note_card.dart';
import 'dialogs.dart';
import 'api_service.dart';
import 'utils/location_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(NotesApp());
}

class NotesApp extends StatelessWidget {
  const NotesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Notes App',
      theme: ThemeData(primarySwatch: Colors.blue),
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

  Future<void> saveUsername(String username) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('username', username);
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('username');
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            const SizedBox(height: 16.0),
            ElevatedButton(
              onPressed: () async {
                final username = usernameController.text;
                if (username.isNotEmpty) {
                  await saveUsername(username);
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => NotesScreen(username: username)),
                  );
                }
              },
              child: const Text('Login'),
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

  @override
  void initState() {
    super.initState();
    loadLocalNotes();
    requestLocationPermission();
    fetchLocation();
    fetchNotes();
    timer = Timer.periodic(const Duration(seconds: 10), (_) => fetchNotes());
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
        print('Разрешение на геолокацию отклонено');
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      print('Разрешение на геолокацию навсегда отклонено. Перейдите в настройки.');
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
    //final prefs = await SharedPreferences.getInstance();
    //final username = prefs.getString('username') ?? 'default_user';
    //final fetchedNotes = await getNotes(username, currentPosition!.latitude, currentPosition!.longitude);
    // Используйте тестовые данные
    //setState(() => notes = fetchedNotes);
    final fetchedNotes = generateTestNotes()+localNotes;
    final nearbyNotes = fetchedNotes.where((note) {
      final distance = Geolocator.distanceBetween(
        currentPosition!.latitude,
        currentPosition!.longitude,
        note['latitude'],
        note['longitude'],
      );
      return distance < 1000; // Фильтруем записки в радиусе 1 км
    }).toList();
    setState(() => notes = nearbyNotes);
  }

  Future<void> sendReply(String username, String noteId, String receiver, String message) async {
    if (currentPosition == null) return;
    final prefs = await SharedPreferences.getInstance();
    final username = prefs.getString('username') ?? 'default_user';
    await sendReply(noteId, username, receiver, message);
  }
  
  void simulateCoordinates(double lat, double lon) {
    setState(() {
      currentPosition = Position(
        latitude: lat,
        longitude: lon,
        timestamp: DateTime.now(),
        accuracy: 0.0,
        altitude: 0.0,
        altitudeAccuracy: 0.0,
        heading: 0.0,
        headingAccuracy: 0.0,
        speed: 0.0,
        speedAccuracy: 0.0,
      );
    });
    fetchNotes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Notes (${widget.username})'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchLocation,
          ),
          IconButton(
            icon: const Icon(Icons.edit_location),
            onPressed: () => openSimulateDialog(context, (lat, lon) {
              simulateCoordinates(double.parse(lat), double.parse(lon));
            }),
          ),
          IconButton(
            icon: const Icon(Icons.admin_panel_settings),
            onPressed: () {
              setState(() {
                isAdmin = !isAdmin;
              });
            },
          ),
        ],
      ),
      body: notes.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: notes.length,
              itemBuilder: (context, index) {
                final note = notes[index];
                final isCurrentUser = note['username'] == widget.username;

                return NoteCard(
                  note: note,
                  isCurrentUser: isCurrentUser,
                  onSave: () => saveNote(widget.username, note['note_id']),
                  onDelete: () => deleteNote(widget.username, note['note_id']),
                  onReply: () => openReplyDialog(context, note['note_id'], note['username'], (message) => sendReply(note['note_id'], widget.username, note['username'], message)),
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
