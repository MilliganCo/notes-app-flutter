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
      title: Text('Добавить записку'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: titleController,
            decoration: InputDecoration(labelText: 'Заголовок'),
          ),
          TextField(
            controller: contentController,
            decoration: InputDecoration(labelText: 'Текст'),
          ),
          if (isAdmin) ...[
            TextField(
              controller: authorController,
              decoration: InputDecoration(labelText: 'Автор'),
            ),
            TextField(
              controller: addressController,
              decoration: InputDecoration(labelText: 'Адрес'),
            ),
            TextField(
              controller: metroController,
              decoration: InputDecoration(labelText: 'Метро'),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Отмена'),
        ),
        TextButton(
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
          child: Text('Добавить локально'),
        ),
        TextButton(
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
      title: Text('Сымитировать координаты'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: latController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(labelText: 'Широта (latitude)'),
          ),
          TextField(
            controller: lonController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(labelText: 'Долгота (longitude)'),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Отмена'),
        ),
        TextButton(
          onPressed: () {
            onSimulate(latController.text, lonController.text);
            Navigator.pop(context);
          },
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
      title: Text('Ответить на записку'),
      content: TextField(
        controller: messageController,
        decoration: InputDecoration(labelText: 'Текст сообщения'),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: Text('Отмена')),
        TextButton(
          onPressed: () {
            onReply(messageController.text);
            Navigator.pop(context);
          },
          child: Text('Отправить'),
        ),
      ],
    ),
  );
}
