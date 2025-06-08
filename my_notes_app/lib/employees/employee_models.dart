class Employee {
  final String id;
  final String name;
  List<Shift> shifts;

  Employee({required this.id, required this.name, required this.shifts});

  factory Employee.fromMap(Map<String, dynamic> map) {
    return Employee(
      id: map['id'] as String,
      name: map['name'] as String,
      shifts: (map['shifts'] as List<dynamic>? ?? [])
          .map((s) => Shift.fromMap(Map<String, dynamic>.from(s)))
          .toList(),
    );
  }

  Map<String, dynamic> toMap() => {
        'id': id,
        'name': name,
        'shifts': shifts.map((s) => s.toMap()).toList(),
      };
}

class Shift {
  final DateTime start;
  DateTime? end;

  Shift({required this.start, this.end});

  factory Shift.fromMap(Map<String, dynamic> map) {
    return Shift(
      start: DateTime.parse(map['start'] as String),
      end: map['end'] != null ? DateTime.parse(map['end'] as String) : null,
    );
  }

  Map<String, dynamic> toMap() => {
        'start': start.toIso8601String(),
        if (end != null) 'end': end!.toIso8601String(),
      };
}
