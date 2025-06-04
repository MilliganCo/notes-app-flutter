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
    final theme = Theme.of(context);
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isCurrentUser ? Color(0xFFB5EAD7) : Color(0xFFFFDAC1),
          width: 2,
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: isCurrentUser ? Color(0xFFE2F0CB) : Colors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    note['header'],
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      color: Colors.black87,
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(
                    note['isSaved'] ? Icons.bookmark : Icons.bookmark_border,
                    color: note['isSaved'] ? Color(0xFFFFDAC1) : Colors.grey,
                  ),
                  onPressed: note['isSaved'] ? onDelete : onSave,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              note['content'],
              style: TextStyle(
                fontSize: 16,
                color: Colors.black87,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Color(0xFFF7F7F7),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.person, size: 16, color: Colors.grey[600]),
                      SizedBox(width: 4),
                      Text(
                        note['username'],
                        style: TextStyle(
                          color: Colors.grey[700],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.location_on, size: 16, color: Colors.grey[600]),
                      SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          note['address'],
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (note['metro'] != null && note['metro'].isNotEmpty) ...[
                    SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.directions_subway, size: 16, color: Colors.grey[600]),
                        SizedBox(width: 4),
                        Text(
                          note['metro'],
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: onReply,
                icon: Icon(Icons.reply, color: Color(0xFFB5EAD7)),
                label: Text(
                  'Ответить',
                  style: TextStyle(color: Color(0xFFB5EAD7)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
