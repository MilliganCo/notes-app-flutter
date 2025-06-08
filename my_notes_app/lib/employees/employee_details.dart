import 'package:flutter/material.dart';
import 'employee_models.dart';
import 'employee_service.dart';

class EmployeeDetailsScreen extends StatefulWidget {
  final Employee employee;
  const EmployeeDetailsScreen({super.key, required this.employee});

  @override
  State<EmployeeDetailsScreen> createState() => _EmployeeDetailsScreenState();
}

class _EmployeeDetailsScreenState extends State<EmployeeDetailsScreen> {
  final EmployeeService _service = EmployeeService();

  Employee get _employee => widget.employee;

  Future<void> _save() async {
    // Load all employees, update this one, and save back
    final list = await _service.loadEmployees();
    final idx = list.indexWhere((e) => e.id == _employee.id);
    if (idx >= 0) {
      list[idx] = _employee;
      await _service.saveEmployees(list);
    }
  }

  void _startShift() async {
    if (_employee.shifts.isNotEmpty && _employee.shifts.last.end == null) return;
    _employee.shifts.add(Shift(start: DateTime.now()));
    await _save();
    setState(() {});
  }

  void _endShift() async {
    if (_employee.shifts.isEmpty) return;
    final last = _employee.shifts.last;
    if (last.end != null) return;
    last.end = DateTime.now();
    await _save();
    setState(() {});
  }

  void _showShifts() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Рабочие дни'),
        content: SizedBox(
          width: double.maxFinite,
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Начало')),
              DataColumn(label: Text('Конец')),
            ],
            rows: _employee.shifts
                .map(
                  (s) => DataRow(cells: [
                        DataCell(Text(s.start.toString())),
                        DataCell(Text(s.end?.toString() ?? '-')),
                      ]),
                )
                .toList(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Закрыть'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final shiftOpen =
        _employee.shifts.isNotEmpty && _employee.shifts.last.end == null;
    return Scaffold(
      appBar: AppBar(
        title: Text(_employee.name),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: shiftOpen ? null : _startShift,
              child: const Text('Начать смену'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: shiftOpen ? _endShift : null,
              child: const Text('Закрыть смену'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _showShifts,
              child: const Text('Посмотреть рабочие дни'),
            ),
          ],
        ),
      ),
    );
  }
}
