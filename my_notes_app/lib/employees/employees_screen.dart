import 'package:flutter/material.dart';
import 'employee_models.dart';
import 'employee_service.dart';
import 'employee_details.dart';

class EmployeesScreen extends StatefulWidget {
  const EmployeesScreen({super.key});

  @override
  State<EmployeesScreen> createState() => _EmployeesScreenState();
}

class _EmployeesScreenState extends State<EmployeesScreen> {
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

  Future<void> _addEmployee() async {
    final controller = TextEditingController();
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Имя сотрудника'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'Имя'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('Добавить'),
          ),
        ],
      ),
    );
    if (name == null || name.isEmpty) return;
    final newEmployee = Employee(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
      shifts: [],
    );
    _employees.add(newEmployee);
    await _service.saveEmployees(_employees);
    setState(() {});
  }

  void _openEmployee(Employee employee) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EmployeeDetailsScreen(employee: employee),
      ),
    );
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Сотрудники'),
      ),
      body: ListView.builder(
        itemCount: _employees.length,
        itemBuilder: (context, index) {
          final e = _employees[index];
          return ListTile(
            title: Text(e.name),
            onTap: () => _openEmployee(e),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addEmployee,
        child: const Icon(Icons.add),
      ),
    );
  }
}
