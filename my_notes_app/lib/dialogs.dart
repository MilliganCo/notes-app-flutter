import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:my_notes_app/api_service.dart';

/// Диалог для добавления новой записки
void openAddNoteDialog(BuildContext context, Position? position, Function fetchNotes, String username, Function addLocalNote, bool isAdmin) {
  TextEditingController titleController = TextEditingController();
  TextEditingController contentController = TextEditingController();
  TextEditingController authorController = TextEditingController();
  TextEditingController addressController = TextEditingController();
  TextEditingController metroController = TextEditingController();

  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Text(
        'Добавить записку',
        style: TextStyle(
          color: Color(0xFFB5EAD7),
          fontWeight: FontWeight.bold,
        ),
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: InputDecoration(
                labelText: 'Заголовок',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: contentController,
              maxLines: 3,
              decoration: InputDecoration(
                labelText: 'Текст',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            if (isAdmin) ...[
              SizedBox(height: 16),
              TextField(
                controller: authorController,
                decoration: InputDecoration(
                  labelText: 'Автор',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: addressController,
                decoration: InputDecoration(
                  labelText: 'Адрес',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: metroController,
                decoration: InputDecoration(
                  labelText: 'Метро',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            'Отмена',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ),
        ElevatedButton(
          onPressed: () {
            if (position == null) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Геолокация недоступна')),
              );
              return;
            }
            addLocalNote(
              isAdmin ? authorController.text : username,
              titleController.text,
              contentController.text,
              position.latitude,
              position.longitude,
              isAdmin ? addressController.text : "Локальный адрес",
              isAdmin ? metroController.text : "Локальное метро",
            );
            fetchNotes();
            Navigator.pop(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFE2F0CB),
            foregroundColor: Colors.black87,
          ),
          child: Text('Добавить локально'),
        ),
        ElevatedButton(
          onPressed: () async {
            if (position == null) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Геолокация недоступна')),
              );
              return;
            }
            var request = await sendNewNote(
              isAdmin ? authorController.text : username,
              titleController.text,
              contentController.text,
              position.latitude,
              position.longitude,
            );
            if (request) fetchNotes();
            Navigator.pop(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFB5EAD7),
            foregroundColor: Colors.black87,
          ),
          child: Text('Добавить глобально'),
        ),
      ],
    ),
  );
}

/// Диалог симуляции координат
void openSimulateDialog(BuildContext context, Function(String, String) onSimulate) {
  TextEditingController latController = TextEditingController();
  TextEditingController lonController = TextEditingController();

  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Text(
        'Сымитировать координаты',
        style: TextStyle(
          color: Color(0xFFB5EAD7),
          fontWeight: FontWeight.bold,
        ),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: latController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: 'Широта (latitude)',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: Colors.white,
            ),
          ),
          SizedBox(height: 16),
          TextField(
            controller: lonController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: 'Долгота (longitude)',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: Colors.white,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            'Отмена',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ),
        ElevatedButton(
          onPressed: () {
            onSimulate(latController.text, lonController.text);
            Navigator.pop(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFB5EAD7),
            foregroundColor: Colors.black87,
          ),
          child: Text('Применить'),
        ),
      ],
    ),
  );
}

/// Диалог ответа на записку
void openReplyDialog(BuildContext context, String noteId, String receiver,
    Function(String message) onReply) {
  TextEditingController messageController = TextEditingController();

  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Text(
        'Ответить на записку',
        style: TextStyle(
          color: Color(0xFFB5EAD7),
          fontWeight: FontWeight.bold,
        ),
      ),
      content: TextField(
        controller: messageController,
        maxLines: 3,
        decoration: InputDecoration(
          labelText: 'Текст сообщения',
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          filled: true,
          fillColor: Colors.white,
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            'Отмена',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ),
        ElevatedButton(
          onPressed: () {
            onReply(messageController.text);
            Navigator.pop(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFB5EAD7),
            foregroundColor: Colors.black87,
          ),
          child: Text('Отправить'),
        ),
      ],
    ),
  );
}
