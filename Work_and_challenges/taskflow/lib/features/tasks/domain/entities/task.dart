import 'package:equatable/equatable.dart';

/// Pure domain entity — no Flutter, no Dio, no JSON. Just business shape.
/// This is what use cases, providers, and the UI work with.
class Task extends Equatable {
  const Task({
    required this.id,
    required this.title,
    required this.isDone,
    this.description,
    this.dueDate,
  });

  final String id;
  final String title;
  final String? description;
  final bool isDone;
  final DateTime? dueDate;

  Task copyWith({
    String? id,
    String? title,
    String? description,
    bool? isDone,
    DateTime? dueDate,
  }) {
    return Task(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      isDone: isDone ?? this.isDone,
      dueDate: dueDate ?? this.dueDate,
    );
  }

  @override
  List<Object?> get props => [id, title, description, isDone, dueDate];
}
