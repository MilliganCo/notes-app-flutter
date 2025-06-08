import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'employee_models.dart';

class EmployeeService {
  static const _key = 'employees';

  Future<List<Employee>> loadEmployees() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_key);
    if (data == null) return [];
    final List<dynamic> list = json.decode(data);
    return list
        .map((e) => Employee.fromMap(Map<String, dynamic>.from(e)))
        .toList();
  }

  Future<void> saveEmployees(List<Employee> employees) async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString(
        _key,
        json.encode(employees.map((e) => e.toMap()).toList()),
    );
  }
}
