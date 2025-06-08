import 'package:flutter/material.dart';
import 'employee_models.dart';
import 'employee_service.dart';

class WorkdaysScreen extends StatefulWidget {
  const WorkdaysScreen({super.key});

  @override
  State<WorkdaysScreen> createState() => _WorkdaysScreenState();
}

class _WorkdaysScreenState extends State<WorkdaysScreen> {
  final EmployeeService _service = EmployeeService();
  List<Employee> _employees = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    _employees = await _service.loadEmployees();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    // For simplicity, we just show all shifts for current year-month 2025
    final now = DateTime(2025, DateTime.now().month);
    final monthStart = DateTime(now.year, now.month);
    final nextMonth = DateTime(now.year, now.month + 1);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Рабочие дни'),
      ),
      body: SingleChildScrollView(
        child: DataTable(
          columns: const [
            DataColumn(label: Text('Сотрудник')),
            DataColumn(label: Text('Смены')),
          ],
          rows: _employees
              .map((e) {
                final shifts = e.shifts
                    .where((s) => s.start.isAfter(monthStart.subtract(const Duration(seconds: 1))) && s.start.isBefore(nextMonth))
                    .map((s) =>
                        '${s.start.toString()} - ${s.end?.toString() ?? '-'}')
                    .join('\n');
                return DataRow(cells: [
                  DataCell(Text(e.name)),
                  DataCell(Text(shifts)),
                ]);
              })
              .toList(),
        ),
      ),
    );
  }
}
