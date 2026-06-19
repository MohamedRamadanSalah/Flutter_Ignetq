import 'package:equatable/equatable.dart';

class Project extends Equatable{
  final String id;
  final String name;
  final int taskCount;
  const Project({
    required this.id,
    required this.name,
    required this.taskCount,
  });

  Project copyWith({
    String? id,
    String? name,
    int? taskCount,
  }) {
    return Project(
      id: id ?? this.id,
      name: name ?? this.name,
      taskCount: taskCount ?? this.taskCount,
    );
  }

  @override
  List<Object?> get props => [id, name, taskCount];
}
