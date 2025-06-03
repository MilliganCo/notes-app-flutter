import 'package:flutter/material.dart';

class NoteCard extends StatelessWidget {
  final Map<String, dynamic> note;
  final bool isCurrentUser; // Указывает, принадлежит ли записка текущему пользователю
  final VoidCallback onSave;
  final VoidCallback onDelete;
  final VoidCallback onReply;

  const NoteCard({
    super.key,
    required this.note,
    required this.isCurrentUser,
    required this.onSave,
    required this.onDelete,
    required this.onReply,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(8.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: isCurrentUser ? Colors.green[100] : Colors.blue[50], // Цвет выделения записки
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: Colors.blue, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Заголовок: ${note['header']}',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 4),
          Text(
            'Текст: ${note['content']}',
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(height: 8),
          Text(
            'Автор: ${note['username']}',
            style: TextStyle(color: Colors.grey[700], fontSize: 13),
          ),
          Text(
            'Адрес: ${note['address']}',
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
          Text(
            'Метро: ${note['metro']}',
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              IconButton(
                icon: Icon(note['isSaved'] ? Icons.bookmark : Icons.bookmark_border),
                color: note['isSaved'] ? Colors.orange : null,
                onPressed: note['isSaved'] ? onDelete : onSave,
              ),
              IconButton(
                icon: const Icon(Icons.reply),
                onPressed: onReply,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
